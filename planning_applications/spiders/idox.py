import json
from datetime import date, datetime, timedelta
from typing import Dict, Generator, List, Optional

import scrapy
import scrapy.exceptions
from parsel.selector import Selector
from scrapy.http.request import Request
from scrapy.http.response import Response
from scrapy.http.response.text import TextResponse

from planning_applications.db import select_planning_application_by_url
from planning_applications.items import (
    ApplicationStatus,
    IdoxPlanningApplicationDetailsFurtherInformation,
    IdoxPlanningApplicationDetailsSummary,
    IdoxPlanningApplicationGeometry,
    IdoxPlanningApplicationItem,
    PlanningApplicationDocumentsDocument,
)
from planning_applications.settings import DEFAULT_DATE_FORMAT
from planning_applications.spiders.base import BaseSpider
from planning_applications.utils import previous_month

DEFAULT_START_DATE = datetime(datetime.now().year, datetime.now().month, 1).date()
DEFAULT_END_DATE = datetime.now().date()


class IdoxSpider(BaseSpider):
    start_url: str
    allowed_domains: List[str] = []
    arcgis_url: Optional[str] = None

    start_date: date = DEFAULT_START_DATE
    end_date: date = DEFAULT_END_DATE
    filter_status: ApplicationStatus = ApplicationStatus.ALL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(self.start_date, str):
            self.start_date = datetime.strptime(self.start_date, DEFAULT_DATE_FORMAT).date()

        if isinstance(self.end_date, str):
            self.end_date = datetime.strptime(self.end_date, DEFAULT_DATE_FORMAT).date()

        if isinstance(self.filter_status, str):
            self.filter_status = ApplicationStatus(self.filter_status)

        if self.start_date > self.end_date:
            raise ValueError(f"start_date {self.start_date} must be earlier than to_date {self.end_date}")

    def start_requests(self) -> Generator[Request, None, None]:
        """
        First entry point: load the advanced search page so we can get the form/CSRF token.
        """
        yield Request(
            self.start_url,
            callback=self._start_new_month,
            errback=self.handle_error,
            dont_filter=True,
        )

    def _start_new_month(self, response: Response):
        """
        We are on the advanced search page.
        Now we can 'submit_form' using the date range in response.meta (start_date, end_date).
        """
        self.logger.info(f"Scheduling new month {self.start_date} to {self.end_date}")
        yield from self.submit_form(response)

    def submit_form(self, response: Response) -> Generator[Request, None, None]:
        self.logger.info(f"Submitting search form on {response.url}")
        formdata = self._build_formdata(response)

        if self.filter_status != ApplicationStatus.ALL:
            formdata["caseStatus"] = self.filter_status.value

        yield from self._build_formrequest(response, formdata)

    def _build_formdata(self, response: Response) -> Dict[str, str]:
        csrf = response.css("input[name='_csrf']::attr(value)").get()
        if not csrf:
            raise ValueError("Failed to find _csrf in response")

        return {
            "_csrf": csrf,
            "caseAddressType": "Application",
            "date(applicationValidatedStart)": self.start_date.strftime("%d/%m/%Y"),
            "date(applicationValidatedEnd)": self.end_date.strftime("%d/%m/%Y"),
            "searchType": "Application",
        }

    def _build_formrequest(self, response: Response, formdata: dict):
        if not isinstance(response, TextResponse):
            raise ValueError("Response must be a TextResponse")

        yield scrapy.FormRequest.from_response(
            response,
            formdata=formdata,
            callback=self.parse_results,
            meta=response.meta,
            dont_filter=True,
        )

    def parse_results(self, response: Response):
        self.logger.info(f"Parsing results from {response.url}")

        message_box = response.css(".messagebox")
        if message_box:
            msg_text = message_box[0].extract()
            if "No results found" in msg_text:
                self.logger.info(f"No applications found on {response.url}")
                # Do not return here; let it fall through to check search_results
            elif "Too many results found" in msg_text:
                self.logger.error(f"Too many results found on {response.url}. Make the search more specific.")
                # If you still want to proceed, remove this return OR schedule previous month here, too.
                return

        application_tools = response.css("#applicationTools")
        if application_tools:
            self.logger.info(f"Only one application found on {response.url}")
            yield from self.parse_details_summary_tab(response)
            yield from self._maybe_schedule_previous_month(response)
            return

        # If #searchresults doesn’t exist or is empty => no apps => schedule previous month
        search_results = response.css("#searchresults")
        if not search_results:
            self.logger.info(f"No #searchresults found on {response.url}")
            yield from self._maybe_schedule_previous_month(response)
            return

        # If #searchresults exists but is empty => no apps => schedule previous month
        search_results = search_results[0].css(".searchresult")
        if len(search_results) == 0:
            self.logger.info(f"No applications found on {response.url}")
            yield from self._maybe_schedule_previous_month(response)
            return

        self.logger.info(f"Found {len(search_results)} applications on {response.url}")
        for result in search_results:
            description = result.css(".summaryLinkTextClamp::text").get()
            self.logger.info(f"Found application: {description}")

            if self.applications_scraped >= self.limit:
                self.logger.info(f"Reached the limit of {self.limit} applications")
                return

            url = result.css("a::attr(href)").get()
            if not url:
                self.logger.error(f"Failed to parse url from {result}")
                continue

            url = response.urljoin(url)

            existing_application = select_planning_application_by_url(url)
            if existing_application and not existing_application.is_active:
                self.logger.info(f"Application already exists: {existing_application.url}")
                continue

            yield from self._parse_single_result(result, response)

        # If no next page (or if no results, etc.), schedule previous month:
        next_page = response.css(".next::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            self.logger.info(f"Found next page at {next_page_url}")
            yield Request(
                url=next_page_url,
                callback=self.parse_results,
                meta=response.meta,
                dont_filter=True,
            )
        else:
            yield from self._maybe_schedule_previous_month(response)

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
                details_summary_url, callback=self.parse_details_summary_tab, meta=meta, errback=self.handle_error
            )

    # Details
    # -------------------------------------------------------------------------

    def parse_details_summary_tab(self, response: Response) -> Generator[Request, None, None]:
        self.logger.info(f"Parsing results on {response.url} (parse_details_summary_tab)")

        item = IdoxPlanningApplicationDetailsSummary()

        summary_table = response.css("#simpleDetailsTable")[0]

        item.reference = self._get_horizontal_table_value(summary_table, "Reference")
        application_received = self._get_horizontal_table_value(summary_table, "Application Received")
        if application_received:
            item.application_received = datetime.strptime(application_received, "%a %d %b %Y")
        application_validated = self._get_horizontal_table_value(summary_table, "Application Validated")
        if application_validated:
            item.application_validated = datetime.strptime(application_validated, "%a %d %b %Y")
        item.address = self._get_horizontal_table_value(summary_table, "Address")
        item.proposal = self._get_horizontal_table_value(summary_table, "Proposal")
        item.status = self._get_horizontal_table_value(summary_table, "Status")
        item.decision = self._get_horizontal_table_value(summary_table, "Decision")
        decision_issued_date = self._get_horizontal_table_value(summary_table, "Decision Issued Date")
        if decision_issued_date:
            item.decision_issued_date = datetime.strptime(decision_issued_date, "%a %d %b %Y")
        item.appeal_status = self._get_horizontal_table_value(summary_table, "Appeal Status")
        item.appeal_decision = self._get_horizontal_table_value(summary_table, "Appeal Decision")

        meta = response.meta
        meta["url"] = response.url
        meta["details_summary"] = item

        yield Request(
            response.url.replace("activeTab=summary", "activeTab=details"),
            callback=self.parse_details_further_information_tab,
            meta=meta,
            errback=self.handle_error,
        )

    def parse_details_further_information_tab(self, response: Response) -> Generator[Request, None, None]:
        self.logger.info(f"Parsing results on {response.url} (parse_details_further_information_tab)")

        item = IdoxPlanningApplicationDetailsFurtherInformation()

        details_table = response.css("#applicationDetails")[0]

        item.application_type = self._get_horizontal_table_value(details_table, "Application Type")
        item.expected_decision_level = self._get_horizontal_table_value(details_table, "Expected Decision Level")
        item.case_officer = self._get_horizontal_table_value(details_table, "Case Officer")
        item.parish = self._get_horizontal_table_value(details_table, "Parish")
        item.ward = self._get_horizontal_table_value(details_table, "Ward")
        item.amenity_society = self._get_horizontal_table_value(details_table, "Amenity Society")
        item.applicant_name = self._get_horizontal_table_value(details_table, "Applicant Name")
        item.district_reference = self._get_horizontal_table_value(details_table, "District Reference")
        item.applicant_name = self._get_horizontal_table_value(details_table, "Applicant Name")
        item.applicant_address = self._get_horizontal_table_value(details_table, "Applicant Address")
        item.environmental_assessment_requested = self._get_horizontal_table_value(
            details_table, "Environmental Assessment Requested"
        )

        meta = response.meta
        meta["details_further_information"] = item

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
        date_published = datetime.strptime(datestr, "%d %b %Y") if datestr else None

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

    def parse_idox_arcgis(self, response: Response) -> Generator[IdoxPlanningApplicationItem, None, None]:
        self.logger.info(f"Parsing ArcGIS for application at {response.meta['url']}")

        parsed_response = json.loads(response.text)

        item = IdoxPlanningApplicationGeometry(reference=response.meta["details_summary"].reference, geometry=None)

        if not parsed_response["features"]:
            self.logger.error(f"No features found in response from {response.url}")

        if parsed_response["features"][0]["geometry"] is None:
            self.logger.error(f"No geometry found in response from {response.url}")
        elif parsed_response["features"][0]["properties"] is None:
            self.logger.error(f"No geometry found in response from {response.url}")
        elif parsed_response["features"][0]["properties"]["KEYVAL"] is None:
            self.logger.error(f"No KEYVAL found in response from {response.url}")
        elif parsed_response["features"][0]["properties"]["KEYVAL"] != response.meta["keyval"]:
            self.logger.error(f"KEYVAL mismatch in response from {response.url}")
        else:
            item.geometry = json.dumps(parsed_response["features"][0]["geometry"])

        meta = response.meta
        meta["geometry"] = item

        yield from self.create_planning_application_item(meta)

    # Helpers
    # -------------------------------------------------------------------------

    def _maybe_schedule_previous_month(self, response: Response):
        """
        Revisit the advanced search page, passing the *previous month* date range via meta.
        Because some sites require a fresh form load and new tokens for each search.
        """

        if self.start_date >= date(2000, 1, 1):
            prev_month_start, prev_month_end = previous_month(self.start_date)
            if prev_month_start >= date(2000, 1, 1):
                self.start_date = prev_month_start
                self.end_date = prev_month_end
                self.logger.info(f"Scheduling previous month {self.start_date} to {self.end_date}")
                yield Request(
                    self.start_url,
                    callback=self._start_new_month,
                    errback=self.handle_error,
                    dont_filter=True,
                )

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

    def _is_active(self, status: Optional[str], decision_issued_date: Optional[datetime]) -> bool:
        # if application is decided and the decision was more than 6 months ago, it is no longer active
        if (
            status == "Decided"
            and decision_issued_date
            and decision_issued_date < datetime.now() - timedelta(days=185)
        ):
            return False
        return True

    def create_planning_application_item(self, meta) -> Generator[IdoxPlanningApplicationItem, None, None]:
        url: str = meta["url"]
        idox_key_val: str = meta["keyval"]
        details_summary: IdoxPlanningApplicationDetailsSummary = meta["details_summary"]
        details_further_information: IdoxPlanningApplicationDetailsFurtherInformation = meta[
            "details_further_information"
        ]
        is_active = self._is_active(details_summary.decision, details_summary.decision_issued_date)
        documents: List[PlanningApplicationDocumentsDocument] = meta["documents"]
        geometry: IdoxPlanningApplicationGeometry = meta["geometry"]

        item = IdoxPlanningApplicationItem(
            lpa=self.name,
            idox_key_val=idox_key_val,
            reference=details_summary.reference,
            url=url,
            application_received=details_summary.application_received,
            application_validated=details_summary.application_validated,
            address=details_summary.address,
            proposal=details_summary.proposal,
            status=details_summary.status,
            appeal_status=details_summary.appeal_status,
            appeal_decision=details_summary.appeal_decision,
            application_type=details_further_information.application_type,
            expected_decision_level=details_further_information.expected_decision_level,
            case_officer=details_further_information.case_officer,
            parish=details_further_information.parish,
            ward=details_further_information.ward,
            amenity_society=details_further_information.amenity_society,
            district_reference=details_further_information.district_reference,
            applicant_name=details_further_information.applicant_name,
            applicant_address=details_further_information.applicant_address,
            environmental_assessment_requested=details_further_information.environmental_assessment_requested,
            is_active=is_active,
            documents=documents,
            geometry=geometry,
        )

        yield item
        self.logger.info(f"Scraped item: {item}")

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
