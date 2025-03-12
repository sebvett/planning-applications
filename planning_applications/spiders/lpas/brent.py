from typing import List

from planning_applications.spiders.idox import IdoxSpider


class BreconBeaconsSpider(IdoxSpider):
    name: str = "brecon_beacons"
    domain: str = "planning.beacons-npa.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications/search.do?action=advanced"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
