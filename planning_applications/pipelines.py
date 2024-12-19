# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os

import psycopg

from planning_applications.items import (
    IdoxPlanningApplicationGeometry,
    IdoxPlanningApplicationItem,
    PlanningApplicationDocumentsDocument,
    PlanningApplicationItem,
)
from planning_applications.utils import getenv


class IdoxPlanningApplicationPipeline:
    def process_item(self, idox_item: IdoxPlanningApplicationItem, spider) -> PlanningApplicationItem:
        spider.logger.info("Mapping item")

        item = PlanningApplicationItem(
            lpa=idox_item["lpa"],
            website_reference=idox_item["idox_key_val"],
            reference=idox_item["reference"],
            url=idox_item["url"],
            submitted_date=idox_item["application_received"],
            validated_date=idox_item["application_validated"],
            address=idox_item["address"],
            description=idox_item["proposal"],
            application_status=idox_item["status"],
            application_decision=idox_item["appeal_decision"],
            application_decision_date=None,
            appeal_status=idox_item["appeal_status"],
            appeal_decision=idox_item["appeal_decision"],
            appeal_decision_date=None,
            application_type=idox_item["application_type"],
            expected_decision_level=idox_item["expected_decision_level"],
            actual_decision_level=None,
            case_officer=idox_item["case_officer"],
            parish=idox_item["parish"],
            ward=idox_item["ward"],
            amenity_society=idox_item["amenity_society"],
            district_reference=idox_item["district_reference"],
            applicant_name=idox_item["applicant_name"],
            applicant_address=idox_item["applicant_address"],
            environmental_assessment_requested=idox_item["environmental_assessment_requested"],
            documents=idox_item["documents"],
            geometry=idox_item["geometry"],
        )

        return item


class PostgresPipeline:
    def __init__(self):
        hostname = getenv("POSTGRES_HOST")
        username = getenv("POSTGRES_USER")
        password = getenv("POSTGRES_PASSWORD")
        database = getenv("POSTGRES_DB")

        self.connection = psycopg.connect(host=hostname, dbname=database, user=username, password=password)

        self.cur = self.connection.cursor()

    def process_item(self, item: PlanningApplicationItem, spider):
        spider.logger.info("Inserting item")

        try:
            self.cur.execute(
                """ insert into planning_applications (
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
                environmental_assessment_requested
            ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                returning uuid;
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
                ),
            )

            row = self.cur.fetchone()
            if not row:
                raise ValueError("No row returned from the insert query!")
            uuid = row[0]

            for document in item["documents"]:
                document: PlanningApplicationDocumentsDocument = document

            self.cur.execute(
                """ insert into planning_application_documents (
                    planning_application_uuid,
                    date_published,
                    document_type,
                    description,
                    url,
                    drawing_number
                ) values (%s,%s,%s,%s,%s,%s)""",
                (
                    uuid,
                    document.date_published,
                    document.document_type,
                    document.description,
                    document.url,
                    document.drawing_number,
                ),
            )

            geometry: IdoxPlanningApplicationGeometry = item["geometry"]

            self.cur.execute(
                """ insert into planning_application_geometries (
                planning_application_uuid,
                reference,
                geometry
            ) values (%s,%s,%s)""",
                (uuid, geometry.reference, geometry.geometry),
            )

            self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            spider.logger.error(f"Error inserting item into the database: {e}")
            raise

        return item

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
