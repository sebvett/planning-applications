from typing import List

import scrapy

from planning_applications.items import applicationStatus
from planning_applications.spiders.idox import IdoxSpider


class WestminsterSpider(IdoxSpider):
    name: str = "westminster"
    allowed_domains: List[str] = ["idoxpa.westminster.gov.uk"]
    start_url: str = "https://idoxpa.westminster.gov.uk/online-applications/search.do?action=advanced"
    arcgis_url: str = (
        "https://idoxpa.westminster.gov.uk/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
    )

    def submit_form(self, response):
        self.logger.info(f"Submitting search form on {response.url}")

        formdata = {
            "org.apache.struts.taglib.html.TOKEN": response.css(
                "input[name='org.apache.struts.taglib.html.TOKEN']::attr(value)"
            ).get(),  # TODO needs Playwright
            "_csrf": response.css("input[name='_csrf']::attr(value)").get(),
            "caseAddressType": "Application",
            "date(applicationReceivedStart)": self.formatted_start_date,
            "date(applicationReceivedEnd)": self.formatted_end_date,
            "searchType": "Application",
        }

        if self.filter_status != applicationStatus.ALL:
            formdata["caseStatus"] = self.filter_status.value

        return [scrapy.FormRequest.from_response(response, formdata=formdata, callback=self.parse_results)]
