from typing import List

from planning_applications.spiders.idox import IdoxSpider


class TorbaySpider(IdoxSpider):
    name: str = "torbay"
    domain: str = "publicaccess.torbay.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/view"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
