from typing import List

from planning_applications.spiders.idox import IdoxSpider


class HorshamSpider(IdoxSpider):
    name: str = "horsham"
    domain: str = "public-access.horsham.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/public-access"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
