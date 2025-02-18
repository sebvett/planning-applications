import enum
from typing import List, cast

import scrapy
from scrapy import signals
from twisted.python.failure import Failure


class objectType(enum.Enum):
    APPLICATION = "application"
    DOCUMENT = "document"
    GEOMETRY = "geometry"
    COMMENT = "comment"


class BaseSpider(scrapy.Spider):
    name: str
    applications_scraped: int = 0

    # How many applications to scrape before stopping
    limit: int = 999_999_999_999

    # Which objects should be scraped
    object_types: List[objectType] = [
        objectType.APPLICATION,
        objectType.DOCUMENT,
        objectType.GEOMETRY,
        objectType.COMMENT,
    ]

    # Whether the spider is not yet working (will be skipped when running all in production)
    not_yet_working: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit = int(self.limit)
        if isinstance(self.object_types, str):
            ot = cast(str, self.object_types).split(",")
            self.object_types = [objectType(o) for o in ot]

    @property
    def should_scrape_application(self) -> bool:
        return objectType.APPLICATION in self.object_types

    @property
    def should_scrape_document(self) -> bool:
        return objectType.DOCUMENT in self.object_types

    @property
    def should_scrape_geometry(self) -> bool:
        return objectType.GEOMETRY in self.object_types

    @property
    def should_scrape_comment(self) -> bool:
        return objectType.COMMENT in self.object_types

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        self.logger.info(f"Spider closed: {reason}")

        if reason == "finished":
            self.logger.info(f"Spider {self.name} finished successfully")
            self.logger.info(f"Total applications scraped: {self.applications_scraped}")
        elif reason == "shutdown":
            self.logger.warning(f"Spider {self.name} was shut down")
        elif reason == "cancelled":
            self.logger.warning(f"Spider {self.name} was cancelled")
        else:
            self.logger.error(f"Spider {self.name} closed due to: {reason}")

    def handle_error(self, failure: Failure):
        self.logger.error(f"Error occurred in spider {self.name}:")
        self.logger.error(f"Error type: {failure.type}")
        self.logger.error(f"Error value: {failure.value}")
        self.logger.error(f"Error traceback: {failure.getTraceback()}")
        # Avoid raising the error — passing keeps the spider alive
        pass
