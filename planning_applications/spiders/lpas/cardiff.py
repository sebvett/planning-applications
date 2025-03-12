from typing import List

from planning_applications.spiders.idox import IdoxSpider


class CardiffSpider(IdoxSpider):
    name: str = "cardiff"
    domain: str = "cardiffidoxcloud.wales"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/publicaccess/search.do?action=advanced"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
