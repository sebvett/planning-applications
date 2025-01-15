import scrapy



class WandsworthSingleSpider(scrapy.Spider):
    name = 'wandsworth_single'
    allowed_domains = ['planning.wandsworth.gov.uk']
    start_urls = ['https://planning.wandsworth.gov.uk/Northgate/PlanningExplorer/Generic/StdDetails.aspx?PT=Planning%20Applications%20On-Line&TYPE=PL/PlanningPK.xml&PARAM0=1140089&XSLT=/Northgate/PlanningExplorer/SiteFiles/Skins/Wandsworth/xslt/PL/PLDetails.xslt&FT=Planning%20Application%20Details&PUBLIC=Y&XMLSIDE=&DAURI=PLANNING']

    def __init__(self, url=None, *args, **kwargs):
        super(WandsworthSingleSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []  # Ensure the URL is passed
    
    def parse(self, response):
        # Your parsing code here
        print(response.text)  # Just as an example to print the HTML content


 




