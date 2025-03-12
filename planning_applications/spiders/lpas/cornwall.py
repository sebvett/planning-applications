from typing import List

from planning_applications.spiders.idox import IdoxSpider


class CornwallSpider(IdoxSpider):
    name: str = "cornwall"
    domain: str = "planning.cornwall.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications/search.do?action=advanced"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
