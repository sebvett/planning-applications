from typing import List

from planning_applications.spiders.idox import IdoxSpider


class StockportSpider(IdoxSpider):
    name: str = "stockport"
    domain: str = "planning.stockport.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/PlanningData-live"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
