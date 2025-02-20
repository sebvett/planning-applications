from typing import List

from planning_applications.spiders.idox import IdoxSpider


class AdurAndWorthingSpider(IdoxSpider):
    name: str = "adur_and_worthing"
    domain: str = "planning.adur-worthing.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications/search.do?action=advanced"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"

    not_yet_working: bool = True
