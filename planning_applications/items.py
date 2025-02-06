from datetime import datetime
from typing import List, Optional

import pydantic
import scrapy

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
    application_status: Optional[str] = None
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


# ---------------------------------------------------------------------------------------------------------------------
# Appeals


class PlanningApplicationAppeal(pydantic.BaseModel):
    lpa: str
    url: str
    reference: str
    case_id: int
    appellant_name: Optional[str] = None
    agent_name: Optional[str] = None
    site_address: Optional[str] = None
    case_type: Optional[str] = None
    case_officer: Optional[str] = None
    procedure: Optional[str] = None
    status: Optional[str] = None
    decision: Optional[str] = None
    start_date: Optional[datetime] = None
    questionnaire_due_date: Optional[datetime] = None
    statement_due_date: Optional[datetime] = None
    interested_party_comments_due_date: Optional[datetime] = None
    final_comments_due_date: Optional[datetime] = None
    inquiry_evidence_due_date: Optional[datetime] = None
    event_date: Optional[datetime] = None
    decision_date: Optional[datetime] = None
    linked_case_ids: Optional[List[int]] = None


class PlanningApplicationAppealDocument(pydantic.BaseModel):
    appeal_case_id: int
    reference: str
    name: str
    url: str


class PlanningApplicationAppealItem(scrapy.Item):
    lpa = scrapy.Field()
    url = scrapy.Field()
    reference = scrapy.Field()
    case_id = scrapy.Field()
    appellant_name = scrapy.Field()
    agent_name = scrapy.Field()
    site_address = scrapy.Field()
    case_type = scrapy.Field()
    case_officer = scrapy.Field()
    procedure = scrapy.Field()
    status = scrapy.Field()
    decision = scrapy.Field()
    start_date = scrapy.Field()
    questionnaire_due_date = scrapy.Field()
    statement_due_date = scrapy.Field()
    interested_party_comments_due_date = scrapy.Field()
    final_comments_due_date = scrapy.Field()
    inquiry_evidence_due_date = scrapy.Field()
    event_date = scrapy.Field()
    decision_date = scrapy.Field()
    linked_case_ids = scrapy.Field()


class PlanningApplicationAppealDocumentItem(scrapy.Item):
    appeal_case_id = scrapy.Field()
    reference = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
