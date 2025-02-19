from typing import List

from planning_applications.spiders.idox import IdoxSpider


class StevenageSpider(IdoxSpider):
    name: str = "stevenage"
    domain: str = "publicaccess.stevenage.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
