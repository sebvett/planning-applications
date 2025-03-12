from typing import List

from planning_applications.spiders.idox import IdoxSpider


class LochLomondSpider(IdoxSpider):
    name: str = "loch_lomond"
    domain: str = "eplanning.lochlomond-trossachs.org"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/OnlinePlanning"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
