import json
import logging
from datetime import date, datetime
from typing import Dict, Generator, List, Optional

import scrapy
import scrapy.exceptions
from parsel.selector import Selector
from scrapy.http.request import Request
from scrapy.http.response import Response
from scrapy.http.response.text import TextResponse

from planning_applications.items import (
    PlanningApplicationDetailsFurtherInformation,
    PlanningApplicationDetailsSummary,
    PlanningApplicationDocumentsDocument,
    PlanningApplicationItem,
    PlanningApplicationPolygon,
    applicationStatus,
)
from planning_applications.settings import DEFAULT_DATE_FORMAT
from planning_applications.spiders.base import BaseSpider

logging.getLogger().setLevel(logging.WARNING)

DEFAULT_START_DATE = datetime(datetime.now().year, datetime.now().month, 1)
DEFAULT_END_DATE = datetime.now()


class IdoxSpider(BaseSpider):
    start_url: str
    allowed_domains: List[str] = []
    arcgis_url: Optional[str] = None

    start_date: date = DEFAULT_START_DATE
    end_date: date = DEFAULT_END_DATE
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

    def start_requests(self) -> Generator[Request, None, None]:
        self.logger.info(
            f"Searching for {self.name} applications between {self.start_date} and {self.end_date} with status {self.filter_status.value}"
        )
        yield Request(self.start_url, callback=self.submit_form, errback=self.handle_error)

    def submit_form(self, response: Response) -> Generator[Request, None, None]:
        self.logger.info(f"Submitting search form on {response.url}")

        formdata = self._build_formdata(response)

        if self.filter_status != applicationStatus.ALL:
            formdata["caseStatus"] = self.filter_status.value

        yield from self._build_formrequest(response, formdata)

    def _build_formdata(self, response: Response) -> Dict[str, str]:
        csrf = response.css("input[name='_csrf']::attr(value)").get()
        if not csrf:
            raise ValueError("Failed to find _csrf in response")

        return {
            "_csrf": csrf,
            "caseAddressType": "Application",
            "date(applicationValidatedStart)": self.formatted_start_date,
            "date(applicationValidatedEnd)": self.formatted_end_date,
            "searchType": "Application",
        }

    def _build_formrequest(self, response: Response, formdata: dict):
        if not isinstance(response, TextResponse):
            raise ValueError("Response must be a TextResponse")

        yield scrapy.FormRequest.from_response(response, formdata=formdata, callback=self.parse_results)

    def parse_results(self, response: Response):
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
            yield Request(next_page_url, callback=self.parse_results)

    def _parse_single_result(self, result: Selector, response: Response):
        details_summary_url = result.css("a::attr(href)").get()
        if not details_summary_url:
            self.logger.error(f"Failed to parse details summary url from {result}, can't continue")
            return

        details_summary_url = response.urljoin(details_summary_url)

        keyval = details_summary_url.split("keyVal=")[1].split("&")[0] or ""
        if keyval == "":
            self.logger.error(f"Failed to parse keyval from {details_summary_url}, can't continue")
            return

        if self.should_scrape_application:
            self.applications_scraped += 1

            meta = {
                "keyval": keyval,
                "original_response": response,
                "limit": self.limit,
                "applications_scraped": self.applications_scraped,
            }

            yield Request(
                details_summary_url,
                callback=self.parse_details_summary_tab,
                meta=meta,
                errback=self.handle_error,
            )

    # Details
    # -------------------------------------------------------------------------

    def parse_details_summary_tab(self, response: Response) -> Generator[Request, None, None]:
        self.logger.info(f"Parsing results on {response.url} (parse_details_summary_tab)")

        details_summary = PlanningApplicationDetailsSummary()

        summary_table = response.css("#simpleDetailsTable")[0]

        details_summary.reference = self._get_horizontal_table_value(summary_table, "Reference")

        application_received = self._get_horizontal_table_value(summary_table, "Application Received")
        if application_received:
            details_summary.application_received = datetime.strptime(application_received, "%a %d %b %Y")

        application_validated = self._get_horizontal_table_value(summary_table, "Application Validated")
        if application_validated:
            details_summary.application_validated = datetime.strptime(application_validated, "%a %d %b %Y")

        details_summary.address = self._get_horizontal_table_value(summary_table, "Address")
        details_summary.proposal = self._get_horizontal_table_value(summary_table, "Proposal")
        details_summary.appeal_status = self._get_horizontal_table_value(summary_table, "Appeal Status")
        details_summary.appeal_decision = self._get_horizontal_table_value(summary_table, "Appeal Decision")

        meta = response.meta
        meta["details_summary"] = details_summary
        self.logger.info(f"meta after parsing details summary: {meta}")

        yield Request(
            response.url.replace("activeTab=summary", "activeTab=details"),
            callback=self.parse_details_further_information_tab,
            meta=meta,
            errback=self.handle_error,
        )

    def parse_details_further_information_tab(self, response: Response) -> Generator[Request, None, None]:
        self.logger.info(f"Parsing results on {response.url} (parse_details_further_information_tab)")

        details_further_information = PlanningApplicationDetailsFurtherInformation()

        details_table = response.css("#applicationDetails")[0]

        details_further_information.application_type = self._get_horizontal_table_value(
            details_table, "Application Type"
        )
        details_further_information.expected_decision_level = self._get_horizontal_table_value(
            details_table, "Expected Decision Level"
        )
        details_further_information.case_officer = self._get_horizontal_table_value(details_table, "Case Officer")
        details_further_information.parish = self._get_horizontal_table_value(details_table, "Parish")
        details_further_information.ward = self._get_horizontal_table_value(details_table, "Ward")
        details_further_information.applicant_name = self._get_horizontal_table_value(details_table, "Applicant Name")
        details_further_information.district_reference = self._get_horizontal_table_value(
            details_table, "District Reference"
        )
        details_further_information.applicant_name = self._get_horizontal_table_value(details_table, "Applicant Name")
        details_further_information.applicant_address = self._get_horizontal_table_value(
            details_table, "Applicant Address"
        )
        details_further_information.environmental_assessment_requested = self._get_horizontal_table_value(
            details_table, "Environmental Assessment Requested"
        )

        meta = response.meta
        meta["details_further_information"] = details_further_information
        self.logger.info(f"meta after parsing details further information: {meta}")

        yield Request(
            response.url.replace("activeTab=details", "activeTab=documents"),
            callback=self.parse_documents_tab,
            meta=meta,
            errback=self.handle_error,
        )

    # Documents
    # -------------------------------------------------------------------------

    def parse_documents_tab(self, response: Response):
        self.logger.info(f"Parsing documents on {response.url}")

        table = response.css("#Documents")[0]
        rows = table.xpath(".//tr")[1:]

        self.logger.info(f"Found {len(rows)} documents on {response.url}")

        documents = []
        for row in rows:
            documents.append(self._parse_document_row(table, row, response))

        meta = response.meta
        meta["documents"] = documents
        self.logger.info(f"meta after parsing documents: {meta}")

        print("*************************************")
        print(meta)
        print("*************************************")
        if self.arcgis_url:
            arcgis_url = (
                self.arcgis_url
                + "?f=geojson&returnGeometry=true&outFields=*&outSR=4326&where=KEYVAL%3D%27"
                + meta["keyval"]
                + "%27"
            )
            yield Request(arcgis_url, callback=self.parse_idox_arcgis, meta=meta, errback=self.handle_error)
        else:
            yield from self.create_planning_application_item(meta)

    def _parse_document_row(self, table: Selector, row: Selector, response: Response):
        self.logger.info(f"Parsing document row on {response.url}")

        url_cell = self.get_cell_for_column_name(table, row, "View")
        url = url_cell.xpath("./a/@href").get() if url_cell else None
        if not url:
            self.logger.error(f"Failed to parse url from row {row}, can't continue")
            raise ValueError(f"Failed to parse url from row {row}, can't continue")
        url = response.urljoin(url)

        date_cell = self.get_cell_for_column_name(table, row, "Date Published")
        category_cell = self.get_cell_for_column_name(table, row, "Document Type")
        drawing_number_cell = self.get_cell_for_column_name(table, row, "Drawing Number")
        description_cell = self.get_cell_for_column_name(table, row, "Description")

        datestr = date_cell.xpath("./text()").get() if date_cell else None
        date_published = datetime.strptime(datestr, "%d %b %Y").strftime("%Y-%m-%d") if datestr else None

        document_type = category_cell.xpath("./text()").get() if category_cell else None
        drawing_number = drawing_number_cell.xpath("./text()").get() if drawing_number_cell else None
        description = description_cell.xpath("./text()").get() if description_cell else None

        return PlanningApplicationDocumentsDocument(
            date_published=date_published,
            document_type=document_type,
            drawing_number=drawing_number,
            description=description,
            url=url,
        )

    # ArcGIS / Map
    # -------------------------------------------------------------------------

    def parse_idox_arcgis(self, response: Response) -> Generator[PlanningApplicationItem, None, None]:
        self.logger.info(f"Parsing ArcGIS on {response.url}")

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

        polygon = PlanningApplicationPolygon(
            reference=response.meta["details_summary"].reference,
            polygon_geojson=json.dumps(parsed_response["features"][0]),
        )

        meta = response.meta
        meta["polygon"] = polygon
        self.logger.info(f"meta after parsing polygon: {meta}")

        yield from self.create_planning_application_item(meta)

    # Helpers
    # -------------------------------------------------------------------------

    @property
    def formatted_start_date(self) -> str:
        return self.start_date.strftime("%d/%m/%Y")

    @property
    def formatted_end_date(self) -> str:
        return self.end_date.strftime("%d/%m/%Y")

    def get_cell_for_column_name(self, table: Selector, row: Selector, column_name: str) -> Optional[Selector]:
        value = table.css(f"th:contains('{column_name}')").xpath("count(preceding-sibling::th)").get()
        if value is None:
            return None
        column_index = int(float(value))
        return row.xpath(f"./td[{column_index + 1}]")[0]

    def _get_horizontal_table_value(self, table: Selector, column_name: str):
        texts = table.xpath(f".//th[contains(text(), '{column_name}')]/following-sibling::td/text()").get()
        if texts:
            return "".join(texts).strip()
        return None

    def create_planning_application_item(self, meta) -> Generator[PlanningApplicationItem, None, None]:
        self.logger.info(f"Creating planning application item with meta: {meta}")

        idox_key_val = meta["keyval"]
        details_summary = meta["details_summary"]
        details_further_information = meta["details_further_information"]
        documents = meta["documents"]
        polygon = meta["polygon"]

        item = PlanningApplicationItem(
            lpa=self.name,
            idox_key_val=idox_key_val,
            reference=details_summary.reference,
            application_received=details_summary.application_received,
            application_validated=details_summary.application_validated,
            address=details_summary.address,
            proposal=details_summary.proposal,
            appeal_status=details_summary.appeal_status,
            appeal_decision=details_summary.appeal_decision,
            application_type=details_further_information.application_type,
            expected_decision_level=details_further_information.expected_decision_level,
            case_officer=details_further_information.case_officer,
            parish=details_further_information.parish,
            ward=details_further_information.ward,
            district_reference=details_further_information.district_reference,
            applicant_name=details_further_information.applicant_name,
            applicant_address=details_further_information.applicant_address,
            environmental_assessment_requested=details_further_information.environmental_assessment_requested,
            documents=documents,
            polygon=polygon,
        )

        yield item
        self.logger.info(f"Scraped item: {item}")

    def handle_error(self, failure):
        self.logger.error(f"Error processing request {failure.request}\nError details: {failure.value}")
        raise scrapy.exceptions.CloseSpider(reason="Error processing request")

    # Comments
    # -------------------------------------------------------------------------

    # def _get_single_result_comments_public_url(self, result: Selector, response: Response):
    #     return self._get_single_result_details_summary_url(result, response).replace(
    #         "activeTab=summary", "activeTab=neighbourComments"
    #     )

    # def _get_single_result_comments_consultee_url(self, result: Selector, response: Response):
    #     return self._get_single_result_details_summary_url(result, response).replace(
    #         "activeTab=summary", "activeTab=consulteeComments"
    #     )

    # Related Cases
    # -------------------------------------------------------------------------

    # def _get_single_result_related_cases_url(self, result: Selector, response: Response):
    #     return self._get_single_result_details_summary_url(result, response).replace(
    #         "activeTab=summary", "activeTab=relatedcases"
    #     )

    # def parse_related_cases_tab(self, response: Response):
    #     pass
