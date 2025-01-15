import json
from datetime import date, datetime
from typing import Dict, Generator, List, Optional

import scrapy
import scrapy.exceptions
from parsel.selector import Selector
from scrapy.http.request import Request
from scrapy.http.response import Response
from scrapy.http.response.text import TextResponse
from scrapy.http import FormRequest

from planning_applications.items import applicationStatus
from planning_applications.settings import DEFAULT_DATE_FORMAT
from planning_applications.spiders.base import BaseSpider

DEFAULT_START_DATE = datetime(datetime.now().year, datetime.now().month, 1)
DEFAULT_END_DATE = datetime.now()


class NorthgateSpider(BaseSpider):
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

        yield from self._build_formrequest(response, formdata)

    def _build_formdata(self, response: Response) -> Dict[str, str]:
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
        return self.start_date.strftime("%d-%m-%Y")

    @property
    def formatted_end_date(self) -> str:
        return self.end_date.strftime("%d-%m-%Y")
