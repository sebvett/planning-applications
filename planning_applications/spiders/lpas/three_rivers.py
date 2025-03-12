from typing import List

from planning_applications.spiders.idox import IdoxSpider


class ThreeRiversSpider(IdoxSpider):
    name: str = "three_rivers"
    domain: str = "www3.threerivers.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications/search.do?action=advanced"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
