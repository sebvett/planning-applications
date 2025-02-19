from typing import List

from planning_applications.spiders.idox import IdoxSpider


class SouthendSpider(IdoxSpider):
    name: str = "southend"
    domain: str = "publicaccess.southend.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
