from typing import Dict, List

import scrapy
from scrapy.http.response import Response
from scrapy.http.response.text import TextResponse

from planning_applications.spiders.idox import IdoxSpider


class WestminsterSpider(IdoxSpider):
    name: str = "westminster"
    domain: str = "idoxpa.westminster.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications/search.do?action=advanced"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"

    def _build_formdata(self, response: Response) -> Dict[str, str | None]:
        return {
            "org.apache.struts.taglib.html.TOKEN": response.css(
                "input[name='org.apache.struts.taglib.html.TOKEN']::attr(value)"
            ).get(),
            "_csrf": response.css("input[name='_csrf']::attr(value)").get(),
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
            formid="advancedSearchForm",
        )
