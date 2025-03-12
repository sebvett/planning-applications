from typing import Dict, List

from scrapy.http.response import Response

from planning_applications.spiders.idox import IdoxSpider


class CarlisleSpider(IdoxSpider):
    name: str = "carlisle"
    domain: str = "publicaccess.carlisle.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications/search.do?action=advanced"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"

    not_yet_working: bool = True

    def _build_formdata(self, response: Response) -> Dict[str, str | None]:
        csrf = response.css("input[name='_csrf']::attr(value)").get()
        if not csrf:
            raise ValueError("Failed to find _csrf in response")

        recaptcha_token = self.get_recaptcha_token(response)
        if not recaptcha_token:
            raise ValueError("Failed to find reCAPTCHA token")

        return {
            "_csrf": csrf,
            "caseAddressType": "Application",
            "date(applicationValidatedStart)": self.start_date.strftime("%d/%m/%Y"),
            "date(applicationValidatedEnd)": self.end_date.strftime("%d/%m/%Y"),
            "searchType": "Application",
            "recaptchaToken": recaptcha_token,
        }

    def get_recaptcha_token(self, response: Response) -> str | None:
        recaptcha_token = response.xpath("//script[contains(text(), '_grecaptcha')]/text()").re_first(
            r'"_grecaptcha":"([^"]+)"'
        )

        if not recaptcha_token:
            self.logger.error("Failed to find reCAPTCHA token")
            return None
