# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import datetime
import time
from typing import List, Optional

import scrapy
from pydantic import BaseModel, Field


class LpaName(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return str(v)


class PlanningApplicationsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class BaseItem(BaseModel):
    meta_source_url: str
    meta_type: str = ""
    meta_id: str | List[str] = ""
    meta_scraped_at: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        self.meta_type = self.get_meta_type()
        self.meta_id = self.get_meta_id()
        self.meta_scraped_at = data.get("meta_scraped_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def get_meta_type(self):
        raise NotImplementedError

    def get_meta_id(self):
        raise NotImplementedError


class MediaItem(BaseItem):
    """
    A generic media item with a 'body' field for storing binary data.
    """

    body: bytes

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self):
        """Only include specific fields in the string representation."""
        # exclude the 'body' field from the string representation
        data = {k: v for k, v in self.model_dump().items() if k != "body"}
        return f"{self.__class__.__name__}({data})"


class PlanningApplication(BaseItem):
    def get_meta_type(self):
        return "planning_application"

    def get_meta_id(self):
        return [self.lpa, self.reference]

    lpa: LpaName
    reference: str

    description: Optional[str] = None
    address: Optional[str] = None
    summary_url: Optional[str] = None
    documents_url: Optional[str] = None

    # TODO: enum
    type: Optional[str] = None
    # TODO: enum
    status: Optional[str] = None
    # TODO: enum
    decision: Optional[str] = None
    # TODO: enum
    appeal_decision: Optional[str] = None

    applicant_name: Optional[str] = None
    case_officer_name: Optional[str] = None
    agent_name: Optional[str] = None
    agent_company: Optional[str] = None
    agent_address: Optional[str] = None

    parish: Optional[str] = None
    ward: Optional[str] = None
    district_reference: Optional[str] = None

    environmental_assessment_requested: Optional[bool] = None
    was_delegated: Optional[bool] = None

    received_date: Optional[datetime.date] = None
    validated_date: Optional[datetime.date] = None
    expired_date: Optional[datetime.date] = None
    committee_date: Optional[datetime.date] = None
    consultation_date: Optional[datetime.date] = None
    consultation_expired_date: Optional[datetime.date] = None
    determination_deadline_date: Optional[datetime.date] = None
    decided_date: Optional[datetime.date] = None
    permission_expired_date: Optional[datetime.date] = None
    appealed_date: Optional[datetime.date] = None


class PlanningApplicationDocument(BaseItem):
    def get_meta_type(self):
        return "planning_application_document"

    def get_meta_id(self):
        return [self.lpa, self.planning_application_reference, self.url]

    class Config:
        arbitrary_types_allowed = True

    lpa: LpaName
    planning_application_reference: str
    url: str
    # TODO: enum
    document_reference: Optional[str] = None
    metadata: str
    file_name: str
    content_hash: str
    mimetype: str
    body: bytes = Field(repr=False)


class PlanningApplicationPolygon(BaseItem):
    def get_meta_type(self):
        return "planning_application_polygon"

    def get_meta_id(self):
        return [self.lpa, self.reference]

    lpa: LpaName
    reference: str
    polygon_geojson: str = Field(repr=False)
