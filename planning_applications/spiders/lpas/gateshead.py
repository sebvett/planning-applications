from typing import List

from planning_applications.spiders.idox import IdoxSpider


class GatesheadSpider(IdoxSpider):
    name: str = "gateshead"
    domain: str = "public.gateshead.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications/search.do?action=advanced"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
