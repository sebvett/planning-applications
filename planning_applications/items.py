# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from datetime import datetime
from enum import Enum
from typing import List, Optional

import pydantic
import scrapy


class applicationStatus(Enum):
    ALL = ""
    APPEAL_DECIDED = "Appeal decided"
    APPEAL_LODGED = "Appeal lodged"
    AWAITING_DECISION = "Awaiting decision"
    DECIDED = "Decided"
    REGISTERED = "Registered"
    UNKNOWN = "Unknown"
    WITHDRAWN = "Withdrawn"


class PlanningApplicationDetailsSummary(pydantic.BaseModel):
    reference: Optional[str] = None
    application_received: Optional[datetime] = None
    application_validated: Optional[datetime] = None
    address: Optional[str] = None
    proposal: Optional[str] = None
    appeal_status: Optional[str] = None
    appeal_decision: Optional[str] = None


class PlanningApplicationDetailsFurtherInformation(pydantic.BaseModel):
    application_type: Optional[str] = None
    expected_decision_level: Optional[str] = None
    case_officer: Optional[str] = None
    parish: Optional[str] = None
    ward: Optional[str] = None
    amenity_society: Optional[str] = None
    district_reference: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_address: Optional[str] = None
    environmental_assessment_requested: Optional[str] = None


class PlanningApplicationCommentsPublicComments(pydantic.BaseModel):
    pass


class PlanningApplicationCommentsConsulteeComments(pydantic.BaseModel):
    pass


class PlanningApplicationDocumentsDocument(pydantic.BaseModel):
    date_published: Optional[str] = None
    document_type: Optional[str] = None
    drawing_number: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None


class PlanningApplicationDocuments(pydantic.BaseModel):
    documents: Optional[List[PlanningApplicationDocumentsDocument]] = None


class PlanningApplicationRelatedCases(pydantic.BaseModel):
    pass


class PlanningApplicationPolygon(pydantic.BaseModel):
    reference: str
    polygon_geojson: str = pydantic.Field(repr=False)


class PlanningApplication(pydantic.BaseModel):
    lpa: str
    idox_key_val: str
    details_summary: Optional[PlanningApplicationDetailsSummary] = None
    details_further_information: Optional[PlanningApplicationDetailsFurtherInformation] = None
    comments_public_comments: Optional[PlanningApplicationCommentsPublicComments] = None
    comments_consultee_comments: Optional[PlanningApplicationCommentsConsulteeComments] = None
    documents: Optional[PlanningApplicationDocuments] = None
    related_cases: Optional[PlanningApplicationRelatedCases] = None
    polygon: Optional[PlanningApplicationPolygon] = None


# ---------------------------------------------------------------------------------------------------------------------


class PlanningApplicationItem(scrapy.Item):
    lpa = scrapy.Field()
    idox_key_val = scrapy.Field()
    reference = scrapy.Field()
    application_received = scrapy.Field()
    application_validated = scrapy.Field()
    address = scrapy.Field()
    proposal = scrapy.Field()
    appeal_status = scrapy.Field()
    appeal_decision = scrapy.Field()
    application_type = scrapy.Field()
    expected_decision_level = scrapy.Field()
    case_officer = scrapy.Field()
    parish = scrapy.Field()
    ward = scrapy.Field()
    amenity_society = scrapy.Field()
    district_reference = scrapy.Field()
    applicant_name = scrapy.Field()
    applicant_address = scrapy.Field()
    environmental_assessment_requested = scrapy.Field()
    documents = scrapy.Field()
    polygon = scrapy.Field()
