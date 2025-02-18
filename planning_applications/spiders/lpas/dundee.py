from typing import List

from planning_applications.spiders.idox import IdoxSpider


class DundeeSpider(IdoxSpider):
    name: str = "dundee"
    domain: str = "idoxwam.dundeecity.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/idoxpa-web"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
