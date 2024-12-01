from typing import List

from planning_applications.items import LpaName
from planning_applications.spiders.idox import IdoxSpider


class CambridgeSpider(IdoxSpider):
    name: LpaName = "cambridge"
    allowed_domains: List[str] = ["applications.greatercambridgeplanning.org"]
    base_url: str = "https://applications.greatercambridgeplanning.org"
    start_url: str = f"{base_url}/online-applications/search.do?action=advanced"
    arcgis_url: str = "https://applications.greatercambridgeplanning.org/server/rest/services/LIVEUniformPA_Planning/FeatureServer/2/query"
