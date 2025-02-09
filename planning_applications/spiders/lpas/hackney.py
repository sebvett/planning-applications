from typing import List

from planning_applications.spiders.smartadmin import SmartAdminSpider


class HackneySpider(SmartAdminSpider):
    name: str = "hackney"
    domain: str = "developmentandhousing.hackney.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/planning/index.html?fa=search"
