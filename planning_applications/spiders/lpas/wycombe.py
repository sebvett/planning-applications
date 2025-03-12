from typing import List

from planning_applications.spiders.idox import IdoxSpider


class WycombeSpider(IdoxSpider):
    name: str = "wycombe"
    domain: str = "publicaccess.wycombe.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/idoxpa-web/search.do?action=advanced"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
