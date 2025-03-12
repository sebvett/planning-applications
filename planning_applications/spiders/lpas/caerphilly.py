from typing import List

from planning_applications.spiders.idox import IdoxSpider


class CaerphillySpider(IdoxSpider):
    name: str = "caerphilly"
    domain: str = "publicaccess.caerphilly.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/PublicAccess/search.do?action=advanced"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
