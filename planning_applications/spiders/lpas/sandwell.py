from typing import List

from planning_applications.spiders.idox import IdoxSpider


class SandwellSpider(IdoxSpider):
    name: str = "sandwell"
    domain: str = "webcaps.sandwell.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/publicaccess"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
