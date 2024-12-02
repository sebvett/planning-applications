# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from datetime import datetime
from typing import Optional

import pydantic
import scrapy


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
    district_reference: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_address: Optional[str] = None
    environmental_assessment_requested: Optional[bool] = None


class PlanningApplicationCommentsPublicComments(pydantic.BaseModel):
    pass


class PlanningApplicationCommentsConsulteeComments(pydantic.BaseModel):
    pass


class PlanningApplicationDocuments(pydantic.BaseModel):
    pass


class PlanningApplicationRelatedCases(pydantic.BaseModel):
    pass


class PlanningApplicationMap(pydantic.BaseModel):
    pass


class PlanningApplication(pydantic.BaseModel):
    details_summary: Optional[PlanningApplicationDetailsSummary] = None
    details_further_information: Optional[PlanningApplicationDetailsFurtherInformation] = None
    comments_public_comments: Optional[PlanningApplicationCommentsPublicComments] = None
    comments_consultee_comments: Optional[PlanningApplicationCommentsConsulteeComments] = None
    documents: Optional[PlanningApplicationDocuments] = None
    related_cases: Optional[PlanningApplicationRelatedCases] = None
    map: Optional[PlanningApplicationMap] = None


# ---------------------------------------------------------------------------------------------------------------------


class MediaItem(scrapy.Item):
    """
    A generic media item with a 'body' field for storing binary data.
    """

    body = scrapy.Field()


class PlanningApplicationItem(scrapy.Item):
    lpa = scrapy.Field()
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
    district_reference = scrapy.Field()
    applicant_name = scrapy.Field()
    applicant_address = scrapy.Field()
    environmental_assessment_requested = scrapy.Field()


class PlanningApplicationDocument(scrapy.Item):
    lpa = scrapy.Field()
    planning_application_reference = scrapy.Field()
    url = scrapy.Field()
    # TODO: enum
    document_reference = scrapy.Field()
    metadata = scrapy.Field()
    file_name = scrapy.Field()
    content_hash = scrapy.Field()
    mimetype = scrapy.Field()
    body = scrapy.Field()


class PlanningApplicationPolygon(scrapy.Item):
    lpa = scrapy.Field()
    reference = scrapy.Field()
    polygon_geojson = scrapy.Field()
