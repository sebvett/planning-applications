from typing import List

from planning_applications.spiders.idox import IdoxSpider


class NorthSomersetSpider(IdoxSpider):
    name: str = "north_somerset"
    domain: str = "planning.n-somerset.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
