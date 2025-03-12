from typing import List

from planning_applications.spiders.idox import IdoxSpider


class FenlandSpider(IdoxSpider):
    name: str = "fenland"
    domain: str = "publicaccess.fenland.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/publicaccess"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
