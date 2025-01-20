from math import nan
from multiprocessing import Value
from parsel import Selector
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

        for dataview in response.xpath('//div[@class="dataview"]'):
            # Get the table heading (h1)
            heading = dataview.xpath('h1/text()').get().split('\xa0')[0]
            # Split the string on the non-breaking space character - everything before spaces is consistent
            application_details[heading] = self._parse_dataview(dataview)


        # try: 
        #     # Get the application registered date
        #     application_registered = response.xpath(
        #         '//ul[@class="list"]//li[div/span[text()="Application Registered"]]/div/text()[normalize-space()]'
        #     ).get().strip()
        #     # Parse the string to a datetime object
        #     application_details['date_registered'] = datetime.strptime(application_registered, '%d/%m/%Y')
        # except ValueError:
        #     if "XPath error" in str(ValueError):
        #         # If the XPath error is raised, we don't have a value - NaN it
        #         application_details['date_registered'] = nan
        #         self.logger.error(f"XPath error: {ValueError}")
        #     elif "does not match format" in str(ValueError):
        #         # If we can't parse the datetime, store the raw string
        #         application_details['date_registered'] = application_registered
        #         self.logger.warning(f"Could not parse date: {ValueError}")
        #     else:
        #         # If we have no idea what happened, log it!
        #         self.logger.error(f"Unknown error: {ValueError}")

        # # Get the application number
        # application_details['application_number'] = response.xpath(
        #     '//ul[@class="list"]//li[div/span[text()="Application Number"]]/div/text()[normalize-space()]'
        # ).get().strip()
        # application_details['address'] = response.xpath(
        #     '//ul[@class="list"]//li[div/span[text()="Site Address"]]/div/text()[normalize-space()]'
        # ).get().strip()
        # application_details['proposal'] = response.xpath(
        #     '//ul[@class="list"]//li[div/span[text()="Proposal"]]/div/text()[normalize-space()]'
        # ).get().strip()
        # application_details['status']  = response.xpath(
        #     '//ul[@class="list"]//li[div/span[text()="Current Status"]]/div/text()[normalize-space()]'
        # ).get().strip()

        print(application_details)

    def _parse_dataview(self, dataview) -> dict:
        dataview_parsed = {}
        table_title = dataview.xpath('h1/text()').get().split('\xa0')[0]
        
        # Work through every row in the table
        for row in dataview.xpath('ul/li'):
            # The text in the span is the table row name
            row_name = row.xpath('div/span/text()').get()
            # If we need to do something special about this row, do it
            if row_name in self.special_rows:
                handler = self.special_handlers.get(self.special_rows[row_name])
                if handler:
                    row_value = handler(row)
                else:
                    self.logger.error(f"No handler for {row_name}")
                    return {}
            else: 
                # The text in the div and outside of the span is the row value, plus some unprinted stuff
                #    - we only want the div text
                row_value = row.xpath('div/text()')[1].get().split('\xa0')[0]
            # When we've finished parsing, or if we haven't parsed, store
                dataview_parsed[row_name] = row_value
        
        return dataview_parsed

        # handler = self.handlers.get(dataview.xpath('h1/text()').get().split('\xa0')[0])
        if handler:
            return handler(self, dataview)
        

    def _handle_date(self, row:Selector) -> datetime:
        ### Handle DATE-ONLY rows - not status+date
        date_string = row.xpath('div/text()')[1].get().split('\xa0')[0]
        return datetime.strptime(date_string, '%d/%m/%Y')
    
    def _handle_status_plus_date(self, row:Selector) -> dict:
        ### Handle STATUS+DATE rows
        [status, date_string] = row.xpath('div/text()')[1].get().split('\xa0')
        return {'status': status, 'date': datetime.strptime(date_string.strip(), '%d/%m/%Y')}

    # Define our special rows, and which handler needs to be used
    special_rows = {
        "Application Registered": "date", 
        "Comments Until": "date",
        "Date of Committee": "date",
        "Decision": "status_plus_date",
        "Appeal Lodged": "date",
    }

    # Define our special handlers
    special_handlers = {
        "date": _handle_date,
        "status_plus_date": _handle_status_plus_date,
    }

    # def _parse_heading(self, dataview) -> dict:

    # def _parse_application_progress_summary(self, dataview) -> dict:

    # def _parse_application_details(self, dataview) -> dict:

    # def _parse_other_information(self, dataview) -> dict:
        

 #to do: parse comments as well (separate page)




