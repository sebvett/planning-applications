from typing import List

from planning_applications.spiders.idox import IdoxSpider


class HullSpider(IdoxSpider):
    name: str = "hull"
    domain: str = "hullcc.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/padcbc/publicaccess-live"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
