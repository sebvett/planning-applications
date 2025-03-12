from typing import List

from planning_applications.spiders.idox import IdoxSpider


class StokeOnTrentSpider(IdoxSpider):
    name: str = "stoke_on_trent"
    domain: str = "planning.stoke.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications/search.do?action=advanced"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
