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
    IdoxPlanningApplicationDetailsFurtherInformation,
    IdoxPlanningApplicationDetailsSummary,
    IdoxPlanningApplicationGeometry,
    IdoxPlanningApplicationItem,
    PlanningApplicationDocumentsDocument,
    applicationStatus,
)
from planning_applications.settings import DEFAULT_DATE_FORMAT
from planning_applications.spiders.base import BaseSpider
from planning_applications.utils import previous_month

DEFAULT_START_DATE = datetime(datetime.now().year, datetime.now().month, 1).date()
DEFAULT_END_DATE = datetime.now().date()

class NorthgateSpider (BaseSpider):
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
        self.logger.info(f"Building formdata for {response.url}")
        formdata = self._build_formdata(response)

        if self.filter_status != applicationStatus.ALL:
            formdata["caseStatus"] = self.filter_status.value

        yield from self._build_formrequest(response, formdata)

    def _build_formdata(self, response: Response) -> Dict[str, str]:
        # Typing requires I check the calls (of type str|None) to make sure they're str in returned formdata
        viewstate = response.css("#__VIEWSTATE").get()
        if not viewstate:
            raise ValueError("Failed to find viewstate in response")
        viewstategenerator = response.css("#__VIEWSTATEGENERATOR").get()
        if not viewstategenerator:
            raise ValueError("Failed to find viewstagegenerator in response")
        eventvalidation = response.css("#__EVENTVALIDATION").get()
        if not eventvalidation:
            raise ValueError("Failed to find eventvalidation in response")
        
        # Having rbGroup == rbRange means cboMonths/cboDays isn't used - they need to be set, so use default "1". 
        return {
            "__VIEWSTATE": viewstate, 
            "__VIEWSTATEGENERATOR": viewstategenerator,
            "__EVENTVALIDATION": eventvalidation,
            "txtApplicationNumber": "", 
            "txtApplicantName": "", 
            "txtAgentName": "", 
            "cboStreetReferenceNumber": "", 
            "txtProposal": "", 
            "cboWardCode": "", 
            "cboParishCode": "", 
            "cboApplicationTypeCode": "", 
            "cboDevelopmentTypeCode": "", 
            "cboStatusCode": "", 
            "cboSelectDateValue": "DATE_RECEIVED", 
            "cboMonths": "1", 
            "cboDays": "1", 
            "rbGroup": "rbRange", 
            "dateStart": self.start_date.strftime("%Y-%m-%d"), 
            "dateEnd": self.end_date.strftime("%Y-%m-%d"), 
            "edrDateSelection": "", 
            "csbtnSearch": "Search",
        }
    
    def _build_formrequest(self, response: Response, formdata: dict):
        if not isinstance(response, TextResponse):
            raise ValueError("Response must be a TextResponse")

        self.logger.info(f"Building querying {response.url} with our new formdata")
        # meta=response.meta should cover meta={"cookiejar": response.meta["cookiejar"]}, so the cookies get sent back
        yield scrapy.FormRequest.from_response(
            response,
            formdata=formdata,
            callback=self.parse_results,
            meta=response.meta,
            dont_filter=True,
        )

    def parse_results(self, response: Response):
        self.logger.info(f"Parsing results from {response.url}")
        from scrapy.shell import inspect_response
        inspect_response(response, self)
        print(response.body)