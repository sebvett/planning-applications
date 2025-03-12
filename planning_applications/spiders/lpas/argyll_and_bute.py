from typing import List

from planning_applications.spiders.idox import IdoxSpider


class ArgyllAndButeSpider(IdoxSpider):
    name: str = "argyll_and_bute"
    domain: str = "publicaccess.argyll-bute.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications/search.do?action=advanced"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"

    not_yet_working: bool = True
