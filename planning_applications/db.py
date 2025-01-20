from typing import Optional

import psycopg

from planning_applications.items import (
    IdoxPlanningApplicationGeometry,
    PlanningApplication,
    PlanningApplicationDocumentsDocument,
    PlanningApplicationItem,
)
from planning_applications.utils import getenv, to_datetime_or_none

database_url = getenv("DATABASE_URL")
print(f"DATABASE_URL: {database_url}")


def get_connection():
    return psycopg.connect(database_url)


def get_cursor(connection):
    return connection.cursor()


# Selects
# -------------------------------------------------------------------------------------------------


def select_planning_application_by_url(url: str) -> Optional[PlanningApplication]:
    cursor = get_cursor(get_connection())

    cursor.execute("SELECT * FROM planning_applications WHERE URL = %s", (url,))
    row = cursor.fetchone()
    if not row:
        return None

    lpa = row[1]
    reference = row[2]
    website_reference = row[3]
    url = row[4]
    submitted_date = row[5]
    validated_date = row[6]
    address = row[7]
    description = row[8]
    application_status = row[9]
    application_decision = row[10]
    application_decision_date = to_datetime_or_none(row[11])
    appeal_status = row[12]
    appeal_decision = row[13]
    appeal_decision_date = to_datetime_or_none(row[14])
    application_type = row[15]
    expected_decision_level = row[16]
    actual_decision_level = row[17]
    case_officer = row[18]
    parish = row[19]
    ward = row[20]
    amenity_society = row[21]
    district_reference = row[22]
    applicant_name = row[23]
    applicant_address = row[24]
    environmental_assessment_requested = row[25]
    is_active = row[26]

    cursor.close()

    return PlanningApplication(
        lpa=lpa,
        reference=reference,
        website_reference=website_reference,
        url=url,
        submitted_date=submitted_date,
        validated_date=validated_date,
        address=address,
        description=description,
        application_status=application_status,
        application_decision=application_decision,
        application_decision_date=application_decision_date,
        appeal_status=appeal_status,
        appeal_decision=appeal_decision,
        appeal_decision_date=appeal_decision_date,
        application_type=application_type,
        expected_decision_level=expected_decision_level,
        actual_decision_level=actual_decision_level,
        case_officer=case_officer,
        parish=parish,
        ward=ward,
        amenity_society=amenity_society,
        district_reference=district_reference,
        applicant_name=applicant_name,
        applicant_address=applicant_address,
        environmental_assessment_requested=environmental_assessment_requested,
        is_active=is_active,
    )


# Upserts
# -------------------------------------------------------------------------------------------------


def upsert_planning_application(cursor: psycopg.Cursor, item: PlanningApplicationItem) -> str:
    cursor.execute(
        """ INSERT INTO planning_applications (
                lpa,
                reference,
                website_reference,
                url,
                submitted_date,
                validated_date,
                address,
                description,
                application_status,
                application_decision,
                application_decision_date,
                appeal_status,
                appeal_decision,
                appeal_decision_date,
                application_type,
                expected_decision_level,
                actual_decision_level,
                case_officer,
                parish,
                ward,
                amenity_society,
                district_reference,
                applicant_name,
                applicant_address,
                environmental_assessment_requested,
                is_active
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (lpa, reference)
            DO UPDATE SET
                website_reference = EXCLUDED.website_reference,
                url = EXCLUDED.url,
                submitted_date = EXCLUDED.submitted_date,
                validated_date = EXCLUDED.validated_date,
                address = EXCLUDED.address,
                description = EXCLUDED.description,
                application_status = EXCLUDED.application_status,
                application_decision = EXCLUDED.application_decision,
                application_decision_date = EXCLUDED.application_decision_date,
                appeal_status = EXCLUDED.appeal_status,
                appeal_decision = EXCLUDED.appeal_decision,
                appeal_decision_date = EXCLUDED.appeal_decision_date,
                application_type = EXCLUDED.application_type,
                expected_decision_level = EXCLUDED.expected_decision_level,
                actual_decision_level = EXCLUDED.actual_decision_level,
                case_officer = EXCLUDED.case_officer,
                parish = EXCLUDED.parish,
                ward = EXCLUDED.ward,
                amenity_society = EXCLUDED.amenity_society,
                district_reference = EXCLUDED.district_reference,
                applicant_name = EXCLUDED.applicant_name,
                applicant_address = EXCLUDED.applicant_address,
                environmental_assessment_requested = EXCLUDED.environmental_assessment_requested,
                is_active = EXCLUDED.is_active,
                last_imported_at = NOW()
            RETURNING uuid;
            """,
        (
            item["lpa"],
            item["reference"],
            item["website_reference"],
            item["url"],
            item["submitted_date"],
            item["validated_date"],
            item["address"],
            item["description"],
            item["application_status"],
            item["application_decision"],
            item["application_decision_date"],
            item["appeal_status"],
            item["appeal_decision"],
            item["appeal_decision_date"],
            item["application_type"],
            item["expected_decision_level"],
            item["actual_decision_level"],
            item["case_officer"],
            item["parish"],
            item["ward"],
            item["amenity_society"],
            item["district_reference"],
            item["applicant_name"],
            item["applicant_address"],
            item["environmental_assessment_requested"],
            item["is_active"],
        ),
    )

    row = cursor.fetchone()
    if not row:
        raise ValueError("No row returned from the upsert query!")
    return row[0]


def upsert_planning_application_document(
    cursor: psycopg.Cursor, uuid: str, document: PlanningApplicationDocumentsDocument
) -> str:
    cursor.execute(
        """ INSERT INTO planning_application_documents (
                planning_application_uuid,
                date_published,
                document_type,
                description,
                url,
                drawing_number
            ) VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT (url)
            DO UPDATE SET
                date_published = EXCLUDED.date_published,
                document_type = EXCLUDED.document_type,
                description = EXCLUDED.description,
                drawing_number = EXCLUDED.drawing_number,
                last_imported_at = NOW()
            RETURNING uuid;
            """,
        (
            uuid,
            document.date_published,
            document.document_type,
            document.description,
            document.url,
            document.drawing_number,
        ),
    )

    row = cursor.fetchone()
    if not row:
        raise ValueError("No row returned from the upsert query!")
    return row[0]


def upsert_planning_application_geometry(
    cursor: psycopg.Cursor, uuid: str, geometry: IdoxPlanningApplicationGeometry
) -> str:
    cursor.execute(
        """ INSERT INTO planning_application_geometries (
                planning_application_uuid,
                reference,
                geometry
            ) VALUES (%s,%s,%s)
            ON CONFLICT (planning_application_uuid, reference)
            DO UPDATE SET
                geometry = EXCLUDED.geometry,
                last_imported_at = NOW()
            RETURNING uuid;
""",
        (uuid, geometry.reference, geometry.geometry),
    )

    row = cursor.fetchone()
    if not row:
        raise ValueError("No row returned from the upsert query!")
    return row[0]
