from typing import List

import scrapy
from scrapy.http.response import Response
from scrapy.http.response.text import TextResponse

from planning_applications.spiders.idox import IdoxSpider


class WestminsterSpider(IdoxSpider):
    name: str = "westminster"
    allowed_domains: List[str] = ["idoxpa.westminster.gov.uk"]
    start_url: str = "https://idoxpa.westminster.gov.uk/online-applications/search.do?action=advanced"
    arcgis_url: str = (
        "https://idoxpa.westminster.gov.uk/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
    )

    def _build_formdata(self, response: Response):
        return {
            "org.apache.struts.taglib.html.TOKEN": response.css(
                "input[name='org.apache.struts.taglib.html.TOKEN']::attr(value)"
            ).get(),
            "_csrf": response.css("input[name='_csrf']::attr(value)").get(),
            "caseAddressType": "Application",
            "date(applicationValidatedStart)": self.formatted_start_date,
            "date(applicationValidatedEnd)": self.formatted_end_date,
            "searchType": "Application",
        }

    def _build_formrequest(self, response: Response, formdata: dict):
        if not isinstance(response, TextResponse):
            raise ValueError("Response must be a TextResponse")

        yield scrapy.FormRequest.from_response(
            response, formid="advancedSearchForm", formdata=formdata, callback=self.parse_results
        )
