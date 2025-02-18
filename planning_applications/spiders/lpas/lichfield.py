from typing import List

from planning_applications.spiders.idox import IdoxSpider


class LichfieldSpider(IdoxSpider):
    name: str = "lichfield"
    domain: str = "planning.lichfielddc.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
