from typing import List

from planning_applications.spiders.idox import IdoxSpider


class EastAyrshireSpider(IdoxSpider):
    name: str = "east_ayrshire"
    domain: str = "eplanning.east-ayrshire.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
