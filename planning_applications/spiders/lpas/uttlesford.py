from typing import List

from planning_applications.spiders.idox import IdoxSpider


class UttlesfordSpider(IdoxSpider):
    name: str = "uttlesford"
    domain: str = "publicaccess.uttlesford.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications/search.do?action=advanced"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"
