from typing import List

from planning_applications.spiders.idox import IdoxSpider


class SunderlandSpider(IdoxSpider):
    name: str = "sunderland"
    domain: str = "online-applications.sunderland.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
