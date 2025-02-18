from typing import List

from planning_applications.spiders.idox import IdoxSpider


class FalkirkSpider(IdoxSpider):
    name: str = "falkirk"
    domain: str = "edevelopment.falkirk.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
