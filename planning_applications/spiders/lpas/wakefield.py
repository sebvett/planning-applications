import random
import time
from typing import List

from scrapy import signals

from planning_applications.spiders.idox import IdoxSpider


class WakefieldSpider(IdoxSpider):
    name: str = "wakefield"
    domain: str = "planning.wakefield.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/online-applications/search.do?action=advanced"
    arcgis_url: str = f"https://{domain}/server/rest/services/PALIVE/LIVEUniformPA_Planning/FeatureServer/2/query"

    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        # More patient retry settings
        "RETRY_TIMES": 8,  # Default is 6
        "RETRY_HTTP_CODES": [400, 408, 421, 429, 500, 502, 503, 504, 520, 521, 522, 524],
        # Implement exponential backoff with jitter
        "RETRY_DELAY": 10,  # Start with 10 seconds instead of 5
        "DOWNLOAD_DELAY": 3,  # Add delay between requests
        # Register custom middleware
        "DOWNLOADER_MIDDLEWARES": {
            "planning_applications.spiders.lpas.wakefield.WakefieldRetryMiddleware": 540,
            "scrapeops_scrapy.middleware.retry.RetryMiddleware": 550,
            "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
        },
    }

    def start_requests(self):
        """Add more delay before starting to avoid immediate rate limiting"""
        self.logger.info("Starting Wakefield spider with extra patience...")
        time.sleep(5)  # Wait 5 seconds before starting
        yield from super().start_requests()


class WakefieldRetryMiddleware:
    """Custom retry middleware with exponential backoff specifically for 421 errors"""

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def spider_opened(self, spider):
        self.spider = spider

    def process_response(self, request, response, spider):
        # If not Wakefield spider or not a 421 error, continue with normal processing
        if spider.name != "wakefield" or response.status != 421:
            return response

        # Custom handling for 421 responses in Wakefield spider
        retry_times = request.meta.get("retry_times", 0)

        # Calculate exponential backoff with jitter
        delay = min(60, (2**retry_times) * 10)  # Max delay of 60 seconds
        jitter = random.uniform(0, 0.3 * delay)  # Add up to 30% jitter
        total_delay = delay + jitter

        spider.logger.info(
            f"Received 421 error from Wakefield. Retry #{retry_times + 1} scheduled with {total_delay:.2f}s delay"
        )

        time.sleep(total_delay)  # Sleep for the calculated delay

        # Create a new request object
        new_request = request.copy()
        # Add a random query parameter to avoid cache
        new_request = new_request.replace(
            url=request.url + (f"&_retry={random.random()}" if "?" in request.url else f"?_retry={random.random()}")
        )
        new_request.meta["retry_times"] = retry_times + 1
        new_request.dont_filter = True

        return new_request

    def process_exception(self, request, exception, spider):
        # Let the default retry middleware handle exceptions
        return None
