from typing import List

from planning_applications.spiders.idox import IdoxSpider


class IsleOfManSpider(IdoxSpider):
    name: str = "isle_of_man"
    domain: str = "pbc.gov.im"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
