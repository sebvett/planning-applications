import enum
from typing import List, cast

import scrapy


class objectType(enum.Enum):
    APPLICATION = "application"
    DOCUMENT = "document"
    POLYGON = "polygon"
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
        objectType.POLYGON,
        objectType.COMMENT,
    ]

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
    def should_scrape_polygon(self) -> bool:
        return objectType.POLYGON in self.object_types

    @property
    def should_scrape_comment(self) -> bool:
        return objectType.COMMENT in self.object_types
