from datetime import datetime
from enum import Enum
from typing import List, Optional

import pydantic
import scrapy


class ApplicationStatus(Enum):
    ALL = ""
    APPEAL_DECIDED = "Appeal decided"
    APPEAL_LODGED = "Appeal lodged"
    AWAITING_DECISION = "Awaiting decision"
    DECIDED = "Decided"
    REGISTERED = "Registered"
    UNKNOWN = "Unknown"
    WITHDRAWN = "Withdrawn"


# ---------------------------------------------------------------------------------------------------------------------
# Base


class PlanningApplication(pydantic.BaseModel):
    lpa: str
    reference: str
    website_reference: str
    url: str
    submitted_date: datetime
    validated_date: datetime
    address: Optional[str] = None
    description: Optional[str] = None
    application_status: ApplicationStatus
    application_decision: Optional[str] = None
    application_decision_date: Optional[datetime] = None
    appeal_status: Optional[str] = None
    appeal_decision: Optional[str] = None
    appeal_decision_date: Optional[datetime] = None
    application_type: Optional[str] = None
    expected_decision_level: Optional[str] = None
    actual_decision_level: Optional[str] = None
    case_officer: Optional[str] = None
    parish: Optional[str] = None
    ward: Optional[str] = None
    amenity_society: Optional[str] = None
    district_reference: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_address: Optional[str] = None
    environmental_assessment_requested: Optional[bool] = None
    is_active: bool


class PlanningApplicationDocumentsDocument(pydantic.BaseModel):
    url: str
    date_published: Optional[datetime] = None
    document_type: Optional[str] = None
    description: Optional[str] = None
    drawing_number: Optional[str] = None


class PlanningApplicationItem(scrapy.Item):
    lpa = scrapy.Field()
    website_reference = scrapy.Field()
    reference = scrapy.Field()
    url = scrapy.Field()
    submitted_date = scrapy.Field()
    validated_date = scrapy.Field()
    address = scrapy.Field()
    description = scrapy.Field()
    application_status = scrapy.Field()
    application_decision = scrapy.Field()
    application_decision_date = scrapy.Field()
    appeal_status = scrapy.Field()
    appeal_decision = scrapy.Field()
    appeal_decision_date = scrapy.Field()
    application_type = scrapy.Field()
    expected_decision_level = scrapy.Field()
    actual_decision_level = scrapy.Field()
    case_officer = scrapy.Field()
    parish = scrapy.Field()
    ward = scrapy.Field()
    amenity_society = scrapy.Field()
    district_reference = scrapy.Field()
    applicant_name = scrapy.Field()
    applicant_address = scrapy.Field()
    environmental_assessment_requested = scrapy.Field()
    is_active = scrapy.Field()
    documents = scrapy.Field()
    geometry = scrapy.Field()


# ---------------------------------------------------------------------------------------------------------------------
# Idox


class IdoxPlanningApplicationDetailsSummary(pydantic.BaseModel):
    reference: Optional[str] = None
    application_received: Optional[datetime] = None
    application_validated: Optional[datetime] = None
    address: Optional[str] = None
    proposal: Optional[str] = None
    status: Optional[str] = None
    decision: Optional[str] = None
    decision_issued_date: Optional[datetime] = None
    appeal_status: Optional[str] = None
    appeal_decision: Optional[str] = None


class IdoxPlanningApplicationDetailsFurtherInformation(pydantic.BaseModel):
    application_type: Optional[str] = None
    actual_decision_level: Optional[str] = None
    expected_decision_level: Optional[str] = None
    case_officer: Optional[str] = None
    parish: Optional[str] = None
    ward: Optional[str] = None
    amenity_society: Optional[str] = None
    district_reference: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_address: Optional[str] = None
    environmental_assessment_requested: Optional[str] = None


class IdoxPlanningApplicationDocuments(pydantic.BaseModel):
    documents: Optional[List[PlanningApplicationDocumentsDocument]] = None


class IdoxPlanningApplicationGeometry(pydantic.BaseModel):
    reference: str
    geometry: Optional[str] = pydantic.Field(repr=False)


class IdoxPlanningApplication(pydantic.BaseModel):
    lpa: str
    idox_key_val: str
    details_summary: Optional[IdoxPlanningApplicationDetailsSummary] = None
    details_further_information: Optional[IdoxPlanningApplicationDetailsFurtherInformation] = None
    documents: Optional[IdoxPlanningApplicationDocuments] = None
    geometry: Optional[IdoxPlanningApplicationGeometry] = None


class IdoxPlanningApplicationItem(scrapy.Item):
    lpa = scrapy.Field()
    idox_key_val = scrapy.Field()
    reference = scrapy.Field()
    url = scrapy.Field()
    application_received = scrapy.Field()
    application_validated = scrapy.Field()
    address = scrapy.Field()
    proposal = scrapy.Field()
    status = scrapy.Field()
    decision = scrapy.Field()
    decision_issued_date = scrapy.Field()
    appeal_status = scrapy.Field()
    appeal_decision = scrapy.Field()
    application_type = scrapy.Field()
    actual_decision_level = scrapy.Field()
    expected_decision_level = scrapy.Field()
    case_officer = scrapy.Field()
    parish = scrapy.Field()
    ward = scrapy.Field()
    amenity_society = scrapy.Field()
    district_reference = scrapy.Field()
    applicant_name = scrapy.Field()
    applicant_address = scrapy.Field()
    environmental_assessment_requested = scrapy.Field()
    is_active = scrapy.Field()
    documents = scrapy.Field()
    geometry = scrapy.Field()
