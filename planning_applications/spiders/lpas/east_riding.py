from typing import List

from planning_applications.spiders.idox import IdoxSpider


class EastRidingSpider(IdoxSpider):
    name: str = "east_riding"
    domain: str = "newplanningaccess.eastriding.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/newplanningaccess"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
