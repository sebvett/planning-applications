import json
import logging
from datetime import date, datetime
from enum import Enum
from typing import Generator, List, Optional, cast

import scrapy
from parsel import SelectorList
from scrapy.http import HtmlResponse, TextResponse

from planning_applications.items import PlanningApplication, PlanningApplicationDocument, PlanningApplicationPolygon
from planning_applications.settings import DEFAULT_DATE_FORMAT
from planning_applications.spiders.base import BaseSpider

logging.getLogger().setLevel(logging.WARNING)

DEFAULT_START_DATE = datetime.fromisocalendar(datetime.now().year, 1, 1).date()
DEFAULT_END_DATE = datetime.now().date()


class applicationStatus(Enum):
    ALL = ""
    APPEAL_DECIDED = "Appeal decided"
    APPEAL_LODGED = "Appeal lodged"
    AWAITING_DECISION = "Awaiting decision"
    DECIDED = "Decided"
    REGISTERED = "Registered"
    UNKNOWN = "Unknown"
    WITHDRAWN = "Withdrawn"


class IdoxSpider(BaseSpider):
    start_url: str
    base_url: str
    allowed_domains: List[str] = []
    arcgis_url: Optional[str] = None

    # Date to start searching from, format: YYYY-MM-DD. Default: 1st January of the current year
    start_date: date = DEFAULT_START_DATE
    # Date to stop searching at, format: YYYY-MM-DD. Default: today
    end_date: date = DEFAULT_END_DATE
    # Status to filter by
    filter_status: applicationStatus = applicationStatus.ALL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(self.start_date, str):
            self.start_date = datetime.strptime(self.start_date, DEFAULT_DATE_FORMAT).date()

        if isinstance(self.end_date, str):
            self.end_date = datetime.strptime(self.end_date, DEFAULT_DATE_FORMAT).date()

        if isinstance(self.filter_status, str):
            self.filter_status = applicationStatus(self.filter_status)

        if self.start_date > self.end_date:
            raise ValueError(f"start_date {self.start_date} must be earlier than to_date {self.end_date}")

    def start_requests(self):
        self.logger.info(
            f"Searching for {self.name} applications between {self.start_date} and {self.end_date} with status {self.filter_status == applicationStatus.ALL and 'all' or self.filter_status.value}"
        )
        yield scrapy.Request(self.start_url, callback=self.submit_form)

    def submit_form(self, response):
        self.logger.info(f"Submitting search form on {response.url}")

        formdata = {
            "_csrf": response.css("input[name='_csrf']::attr(value)").get(),
            "caseAddressType": "Application",
            "date(applicationValidatedStart)": self.formatted_start_date,
            "date(applicationValidatedEnd)": self.formatted_end_date,
            "searchType": "Application",
        }

        if self.filter_status != applicationStatus.ALL:
            formdata["caseStatus"] = self.filter_status.value

        return [scrapy.FormRequest.from_response(response, formdata=formdata, callback=self.parse_results)]

    def parse_results(self, response: HtmlResponse):
        message_box = response.css(".messagebox")

        if len(message_box) > 0:
            if "No results found" in message_box[0].extract():
                self.logger.info(f"No applications found on {response.url}")
                return

            if "Too many results found" in message_box[0].extract():
                self.logger.error(f"Too many results found on {response.url}. Make the search more specific.")
                return

        application_tools = response.css("#applicationTools")
        if len(application_tools) > 0:
            self.logger.info(f"Only one application found on {response.url}")
            yield from self.parse_details_summary_tab(response)
            return

        search_results = response.css("#searchresults")
        if len(search_results) == 0:
            self.logger.info(f"No applications found on {response.url}")
            return

        search_results = search_results[0].css(".searchresult")
        self.logger.info(f"Found {len(search_results)} applications on {response.url}")

        for result in search_results:
            self.logger.info(f"heading into {result.css("a::attr(href)").get()}")
            if self.applications_scraped >= self.limit:
                self.logger.info(f"Reached the limit of {self.limit} applications")
                return

            yield from self._parse_single_result(result, response)

        next_page = response.css(".next::attr(href)").get()
        if next_page:
            self.logger.info(f"Found next page at {next_page}")
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse_results)

    def _parse_single_result(self, result: scrapy.Selector, response: HtmlResponse):
        meta_info = self._parse_single_result_meta_info(result.css(".metaInfo"))
        summary_url = self._get_single_result_summary_url(result, response)
        details_url = self._get_single_result_details_url(result, response)
        documents_url = self._get_single_result_documents_url(result, response)
        keyval = summary_url.split("keyVal=")[1].split("&")[0] or ""
        description = result.css("a::text").get() or ""
        address = result.css(".address::text").get() or ""

        if keyval == "":
            self.logger.error(f"Failed to parse keyval from {summary_url}, can't continue")
            return

        if self.should_scrape_application:
            self.applications_scraped += 1

            yield PlanningApplication(
                meta_source_url=response.url,
                lpa=self.lpa,
                reference=meta_info["reference"],
                description=description.strip(),
                address=address.strip(),
                summary_url=summary_url,
                documents_url=documents_url,
                received_date=meta_info.get("received_date"),
                validated_date=meta_info.get("validated_date"),
                status=meta_info.get("status"),
            )

            yield scrapy.Request(
                details_url,
                callback=self.parse_details_further_information_tab,
                meta={"application_reference": meta_info["reference"]},
            )

        if self.should_scrape_document:
            yield scrapy.Request(
                documents_url,
                callback=self.parse_documents_tab,
                meta={"application_reference": meta_info["reference"]},
            )

        if self.should_scrape_comment:
            # TODO: Implement comment scraping
            pass

        self.logger.info(f"Scraping ArcGIS data for {keyval}")

        if self.should_scrape_polygon and self.arcgis_url:
            url = (
                self.arcgis_url
                + "?f=geojson&returnGeometry=true&outFields=*&outSR=4326&where=KEYVAL%3D%27"
                + keyval
                + "%27"
            )

            yield scrapy.Request(
                url,
                callback=self.parse_idox_arcgis,
                meta={"application_reference": meta_info["reference"], "keyval": keyval},
            )

    def parse_details_summary_tab(self, response: HtmlResponse):
        self.logger.info(f"Parsing results on {response.url} (parse_details_summary_tab)")

        summary_tab = response.css("#tab_summary")[0]
        summary_table = response.css("#simpleDetailsTable")[0]

        summary_url = summary_tab.attrib["href"]
        reference = self._get_horizontal_table_value(summary_table, "Reference")

        application_received = self._get_horizontal_table_value(summary_table, "Application Received")
        application_validated = self._get_horizontal_table_value(summary_table, "Application Validated")
        address = self._get_horizontal_table_value(summary_table, "Address")
        proposal = self._get_horizontal_table_value(summary_table, "Proposal")
        status = self._get_horizontal_table_value(summary_table, "Status")
        decision = self._get_horizontal_table_value(summary_table, "Decision")
        decision_issued_date = self._get_horizontal_table_value(summary_table, "Decision Issued Date")
        appeal_decision = self._get_horizontal_table_value(summary_table, "Appeal Decision")

        if not summary_url or not reference:
            self.logger.error(
                f"Failed to parse summary tab on {response.url}. Need summary_url and reference, can't continue without"
            )
            return

        # dates come in format "Thu 01 Jan 1970"
        received_date, validated_date = None, None
        if application_received:
            received_date = datetime.strptime(application_received, "%a %d %b %Y")
        if application_validated:
            validated_date = datetime.strptime(application_validated, "%a %d %b %Y")
        if decision_issued_date:
            decision_issued_date = datetime.strptime(decision_issued_date, "%a %d %b %Y")

        yield PlanningApplication(
            meta_source_url=response.url,
            lpa=self.lpa,
            reference=reference,
            description=proposal,
            address=address,
            summary_url=summary_url,
            received_date=received_date,
            validated_date=validated_date,
            status=status,
            decision=None if decision == "-" else decision,
            decided_date=decision_issued_date or None,
            appeal_decision=appeal_decision,
        )

    def parse_details_further_information_tab(self, response: HtmlResponse):
        self.logger.info(f"Parsing results on {response.url} (parse_details_further_information_tab)")

        details_table = response.css("#applicationDetails")[0]
        application_type = self._get_horizontal_table_value(details_table, "Application Type")
        decision = self._get_horizontal_table_value(details_table, "Decision")
        actual_decision_level = self._get_horizontal_table_value(details_table, "Actual Decision Level")
        case_officer_name = self._get_horizontal_table_value(details_table, "Case Officer")
        parish = self._get_horizontal_table_value(details_table, "Parish")
        ward = self._get_horizontal_table_value(details_table, "Ward")
        applicant_name = self._get_horizontal_table_value(details_table, "Applicant Name")
        district_reference = self._get_horizontal_table_value(details_table, "District Reference")
        agent_name = self._get_horizontal_table_value(details_table, "Agent Name")
        agent_company = self._get_horizontal_table_value(details_table, "Agent Company Name")
        agent_address = self._get_horizontal_table_value(details_table, "Agent Address")

        environmental_assessment_requested = self._get_horizontal_table_value(
            details_table, "Environmental Assessment Requested"
        )

        yield PlanningApplication(
            meta_source_url=response.url,
            lpa=self.lpa,
            reference=response.meta["application_reference"],
            type=application_type,
            decision=decision,
            was_delegated=actual_decision_level == "Delegated Decision",
            case_officer_name=case_officer_name,
            parish=None if parish == "-" else parish,
            ward=None if ward == "-" else ward,
            applicant_name=applicant_name,
            district_reference=district_reference,
            agent_name=agent_name,
            agent_company=agent_company,
            agent_address=agent_address,
            environmental_assessment_requested=environmental_assessment_requested == "Yes",
        )

    def parse_details_contacts_tab(self, response: HtmlResponse):
        pass

    def parse_details_important_dates_tab(self, response: HtmlResponse):
        pass

    def _get_single_result_summary_url(self, result: scrapy.Selector, response: HtmlResponse):
        return response.urljoin(result.css("a::attr(href)").get())

    def _get_single_result_details_url(self, result: scrapy.Selector, response: HtmlResponse):
        return self._get_single_result_summary_url(result, response).replace("activeTab=summary", "activeTab=details")

    def _get_single_result_documents_url(self, result: scrapy.Selector, response: HtmlResponse):
        return self._get_single_result_summary_url(result, response).replace(
            "activeTab=summary", "activeTab=documents"
        )

    # Comments
    # -------------------------------------------------------------------------

    def parse_comments_tab(self, response: HtmlResponse):
        pass

    def parse_comments_public_tab(self, response: HtmlResponse):
        pass

    def parse_comments_consultee_tab(self, response: HtmlResponse):
        pass

    # Constraints
    # -------------------------------------------------------------------------

    def parse_constraints_tab(self, response: HtmlResponse):
        pass

    # Documents
    # -------------------------------------------------------------------------

    def parse_documents_tab(self, response: HtmlResponse):
        self.logger.info(f"Parsing documents on {response.url}")

        table = response.css("#Documents")[0]
        rows = table.xpath(".//tr")[1:]

        self.logger.info(f"Found {len(rows)} documents on {response.url}")

        for row in rows:
            yield from self._parse_document_row(table, row, response)

    PARSE_DOCUMENT_ROW_COLUMN_HEADERS = {
        "date": "Date Published",
        "category": "Document Type",
        "description": "Description",
        "document_reference": "Drawing Number",
        "view_link": "View",
    }

    def _parse_document_row(self, table: scrapy.Selector, row: scrapy.Selector, response: HtmlResponse):
        date_cell = get_cell_for_column_name(table, row, self.PARSE_DOCUMENT_ROW_COLUMN_HEADERS["date"])
        category_cell = get_cell_for_column_name(table, row, self.PARSE_DOCUMENT_ROW_COLUMN_HEADERS["category"])
        description_cell = get_cell_for_column_name(table, row, self.PARSE_DOCUMENT_ROW_COLUMN_HEADERS["description"])
        view_link_cell = get_cell_for_column_name(table, row, self.PARSE_DOCUMENT_ROW_COLUMN_HEADERS["view_link"])

        datestr = date_cell.xpath("./text()").get()
        if not datestr:
            self.logger.error(f"Failed to parse date from row {row}, can't continue")
            return

        date = datetime.strptime(datestr, "%d %b %Y").strftime("%Y-%m-%d")
        category = category_cell.xpath("./text()").get()
        description = description_cell.xpath("./text()").get()
        url = response.urljoin(view_link_cell.xpath("./a/@href").get())

        yield scrapy.Request(
            url,
            callback=self.process_parsed_file,
            meta={
                "original_response": response,
                "date": date,
                "category": category,
                "description": description,
                "url": url,
            },
            cookies=cast(dict, response.headers.getlist("Set-Cookie")),
        )

    def _parse_single_result_meta_info(self, selector: SelectorList[scrapy.Selector]):
        meta_info = {}

        texts_selectors = selector.xpath("./text()")
        ref_no = texts_selectors.re(r"Ref\. No:\s*(\S+)")
        if ref_no:
            meta_info["reference"] = ref_no[0]

        texts = texts_selectors.extract()
        cleaned_texts = [t.strip() for t in texts if t.strip() != ""]

        for text in cleaned_texts:
            try:
                if "Received:" in text:
                    meta_info["received_date"] = datetime.strptime(
                        text.split(":", 1)[1].strip(), "%a %d %b %Y"
                    ).strftime("%Y-%m-%d")
                elif "Validated:" in text:
                    meta_info["validated_date"] = datetime.strptime(
                        text.split(":", 1)[1].strip(), "%a %d %b %Y"
                    ).strftime("%Y-%m-%d")
                elif "Status:" in text:
                    meta_info["status"] = text.split(":", 1)[1].strip()
            except ValueError as e:
                self.logger.error(f"Failed to parse meta info from text: {text}", e)
                continue

        return meta_info

    def _get_horizontal_table_value(self, table: scrapy.Selector, column_name: str):
        return table.xpath(f".//th[contains(text(), '{column_name}')]/following-sibling::td/text()").get()

    def process_parsed_file(self, response: HtmlResponse):
        # move this definition higher up to minimise no. of repeated calls

        # TODO: Implement this
        parsed_data = ""

        for item in parsed_data:
            return self._create_planning_application_document(item, response)

    def _create_planning_application_document(
        self, item, response: HtmlResponse
    ) -> Generator[PlanningApplicationDocument, None, None]:
        # Some of these document fields aren't included in the standard document definition
        # (application_reference, category, description, date)
        # They have been passed into storage via the metadata field instead
        metadata = json.loads(item["metadata"])
        metadata["application_reference"] = response.meta["original_response"].meta["application_reference"]
        metadata["category"] = response.meta["category"]
        metadata["description"] = response.meta["description"]
        metadata["date"] = response.meta["date"]

        yield PlanningApplicationDocument(
            meta_source_url=response.meta["original_response"].url,
            planning_application_reference=metadata["application_reference"],
            content_hash=item["content_hash"],
            file_name=item["file_name"],
            url=response.meta["url"],
            metadata=json.dumps(metadata),
            lpa=self.lpa,
            mimetype=item["mimetype"],
            body=item["body"],
        )

    # Related Cases
    # -------------------------------------------------------------------------

    def parse_related_cases_tab(self, response: HtmlResponse):
        pass

    # ArcGIS / Map
    # -------------------------------------------------------------------------

    def parse_idox_arcgis(self, response: TextResponse) -> Generator[PlanningApplicationPolygon, None, None]:
        parsed_response = json.loads(response.text)

        if parsed_response["features"] is None:
            self.logger.error(f"No features found in response from {response.url}")
            return

        if len(parsed_response["features"]) == 0:
            self.logger.error(f"No features found in response from {response.url}")
            return

        if parsed_response["features"][0]["geometry"] is None:
            self.logger.error(f"No geometry found in response from {response.url}")
            return

        if parsed_response["features"][0]["properties"] is None:
            self.logger.error(f"No geometry found in response from {response.url}")
            return

        if parsed_response["features"][0]["properties"]["KEYVAL"] is None:
            self.logger.error(f"No KEYVAL found in response from {response.url}")
            return

        if parsed_response["features"][0]["properties"]["KEYVAL"] != response.meta["keyval"]:
            self.logger.error(f"KEYVAL mismatch in response from {response.url}")
            return

        yield PlanningApplicationPolygon(
            meta_source_url=response.url,
            lpa=self.lpa,
            reference=response.meta["application_reference"],
            polygon_geojson=json.dumps(parsed_response["features"][0]),
        )

    # Helpers
    # -------------------------------------------------------------------------

    @property
    def formatted_start_date(self) -> str:
        return self.start_date.strftime("%d/%m/%Y")

    @property
    def formatted_end_date(self) -> str:
        return self.end_date.strftime("%d/%m/%Y")


def get_cell_for_column_name(table: scrapy.Selector, row: scrapy.Selector, column_name: str) -> scrapy.Selector:
    try:
        column_index = int(
            float(table.css(f"th:contains('{column_name}')").xpath("count(preceding-sibling::th)").get())
        )
    except ValueError:
        raise ValueError(f"Column '{column_name}' not found in table")

    return row.xpath(f"./td[{column_index + 1}]")
