from math import nan
from multiprocessing import Value
from requests import Response
import scrapy, json
from datetime import datetime


class WandsworthSingleSpider(scrapy.Spider):
    name = 'wandsworth_single'
    allowed_domains = ['planning.wandsworth.gov.uk']
    start_urls = ['https://planning.wandsworth.gov.uk/Northgate/PlanningExplorer/Generic/StdDetails.aspx?PT=Planning%20Applications%20On-Line&TYPE=PL/PlanningPK.xml&PARAM0=1140089&XSLT=/Northgate/PlanningExplorer/SiteFiles/Skins/Wandsworth/xslt/PL/PLDetails.xslt&FT=Planning%20Application%20Details&PUBLIC=Y&XMLSIDE=&DAURI=PLANNING']

    def __init__(self, url=None, *args, **kwargs):
        super(WandsworthSingleSpider, self).__init__(*args, **kwargs)
        # Ensure the URL is passed
        if url:
            self.start_urls = [url]
    
    def parse(self, response):
        application_details = {}
        
        try: 
            # Get the application registered date
            application_registered = response.xpath(
                '//ul[@class="list"]//li[div/span[text()="Application Registered"]]/div/text()[normalize-space()]'
            ).get().strip()
            # Parse the string to a datetime object
            application_details['date_registered'] = datetime.strptime(application_registered, '%d/%m/%Y')
        except ValueError:
            if "XPath error" in str(ValueError):
                # If the XPath error is raised, we don't have a value - NaN it
                application_details['date_registered'] = nan
                self.logger.error(f"XPath error: {ValueError}")
            elif "does not match format" in str(ValueError):
                # If we can't parse the datetime, store the raw string
                application_details['date_registered'] = application_registered
                self.logger.warning(f"Could not parse date: {ValueError}")
            else:
                # If we have no idea what happened, log it!
                self.logger.error(f"Unknown error: {ValueError}")

        # Get the application number
        application_details['application_number'] = response.xpath(
            '//ul[@class="list"]//li[div/span[text()="Application Number"]]/div/text()[normalize-space()]'
        ).get().strip()
        application_details['address'] = response.xpath(
            '//ul[@class="list"]//li[div/span[text()="Site Address"]]/div/text()[normalize-space()]'
        ).get().strip()
        application_details['proposal'] = response.xpath(
            '//ul[@class="list"]//li[div/span[text()="Proposal"]]/div/text()[normalize-space()]'
        ).get().strip()
        application_details['status']  = response.xpath(
            '//ul[@class="list"]//li[div/span[text()="Current Status"]]/div/text()[normalize-space()]'
        ).get().strip()

        print(application_details)


 




