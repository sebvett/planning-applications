from typing import List

from planning_applications.spiders.idox import IdoxSpider


class NorthTynesideSpider(IdoxSpider):
    name: str = "north_tyneside"
    domain: str = "idoxpublicaccess.northtyneside.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
