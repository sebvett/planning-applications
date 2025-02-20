from typing import List

from planning_applications.spiders.idox import IdoxSpider


class StocktonOnTeesSpider(IdoxSpider):
    name: str = "stockton_on_tees"
    domain: str = "www.developmentmanagement.stockton.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
