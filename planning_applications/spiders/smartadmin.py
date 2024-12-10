import json
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

DEFAULT_START_DATE = datetime(datetime.now().year, datetime.now().month, 1)
DEFAULT_END_DATE = datetime.now()


class SmartAdminSpider(BaseSpider):
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
            "received_date_from": self.formatted_start_date,
            "received_date_to": self.formatted_end_date,
            "fa": "search",
            "submitted": "true",
        }

    # Helpers
    # -------------------------------------------------------------------------

    def _build_formrequest(self, response: Response, formdata: dict):
        if not isinstance(response, TextResponse):
            raise ValueError("Response must be a TextResponse")

        yield scrapy.FormRequest.from_response(response, formdata=formdata, callback=self.parse_results)

    def parse_results(self, response: Response):
        self.logger.info(f"Parsing results from {response.url}")

    @property
    def formatted_start_date(self) -> str:
        return self.start_date.strftime("%Y-%m-%d")

    @property
    def formatted_end_date(self) -> str:
        return self.end_date.strftime("%Y-%m-%d")

    def handle_error(self, failure):
        self.logger.error(f"Error processing request {failure.request}\nError details: {failure.value}")
        raise scrapy.exceptions.CloseSpider(reason="Error processing request")
