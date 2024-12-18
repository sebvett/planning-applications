# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os

import psycopg

from planning_applications.items import IdoxPlanningApplicationItem, PlanningApplicationItem
from planning_applications.utils import getenv


class IdoxPlanningApplicationPipeline:
    def process_item(self, idox_item: IdoxPlanningApplicationItem, spider) -> PlanningApplicationItem:
        spider.logger.info(f"Mapping item: {idox_item}")

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
            polygon=idox_item["polygon"],
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
        spider.logger.info(f"Inserting item: {item}")

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
            ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
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

        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
