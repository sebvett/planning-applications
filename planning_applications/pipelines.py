import os
import tempfile
from typing import Any
from urllib.parse import urlparse

import boto3
import requests
from botocore.exceptions import ClientError

from planning_applications.db import (
    get_connection,
    get_cursor,
    upsert_planning_application,
    upsert_planning_application_appeal,
    upsert_planning_application_appeal_document,
    upsert_planning_application_document,
    upsert_planning_application_geometry,
)
from planning_applications.items import (
    IdoxPlanningApplicationGeometry,
    IdoxPlanningApplicationItem,
    PlanningApplicationAppeal,
    PlanningApplicationAppealDocument,
    PlanningApplicationItem,
)
from planning_applications.utils import getenv, hasenv


class IdoxPlanningApplicationPipeline:
    def process_item(self, idox_item: IdoxPlanningApplicationItem | Any, spider) -> PlanningApplicationItem:
        if not isinstance(idox_item, IdoxPlanningApplicationItem):
            return idox_item

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
            application_decision=idox_item["decision"],
            application_decision_date=idox_item["decision_issued_date"],
            appeal_status=idox_item["appeal_status"],
            appeal_decision=idox_item["appeal_decision"],
            appeal_decision_date=None,  # TODO: Add this
            application_type=idox_item["application_type"],
            expected_decision_level=idox_item["expected_decision_level"],
            actual_decision_level=idox_item["actual_decision_level"],
            case_officer=idox_item["case_officer"],
            parish=idox_item["parish"],
            ward=idox_item["ward"],
            amenity_society=idox_item["amenity_society"],
            district_reference=idox_item["district_reference"],
            applicant_name=idox_item["applicant_name"],
            applicant_address=idox_item["applicant_address"],
            environmental_assessment_requested=idox_item["environmental_assessment_requested"]
            if idox_item["environmental_assessment_requested"]
            else None,
            is_active=idox_item["is_active"],
            documents=idox_item["documents"],
            geometry=idox_item["geometry"],
        )

        return item


class PostgresPipeline:
    def __init__(self):
        self.connection = get_connection()
        self.cur = get_cursor(self.connection)

    def process_item(self, item: PlanningApplicationItem | PlanningApplicationAppeal, spider):
        if isinstance(item, PlanningApplicationAppealDocument):
            return self.process_appeal_case_document_item(item, spider)

        if isinstance(item, PlanningApplicationAppeal):
            return self.process_appeal_case_item(item, spider)

        if isinstance(item, PlanningApplicationItem):
            return self.process_planning_application_item(item, spider)

    def process_appeal_case_item(self, item: PlanningApplicationAppeal, spider):
        spider.logger.info(f"Inserting planning application appeal {item.reference}")
        try:
            _ = upsert_planning_application_appeal(self.cur, item)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            spider.logger.error(f"Error inserting appeal case into the database: {e}")
            raise

    def process_appeal_case_document_item(self, item: PlanningApplicationAppealDocument, spider):
        spider.logger.info(f"Inserting planning application appeal document {item.reference}")
        try:
            _ = upsert_planning_application_appeal_document(self.cur, item)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            spider.logger.error(f"Error inserting appeal case document into the database: {e}")
            raise

    def process_planning_application_item(self, item: PlanningApplicationItem, spider):
        spider.logger.info(f"Inserting planning application {item['reference']}")

        try:
            uuid = upsert_planning_application(self.cur, item)

            for document in item["documents"]:
                _ = upsert_planning_application_document(self.cur, uuid, document)

            geometry: IdoxPlanningApplicationGeometry = item["geometry"]
            _ = upsert_planning_application_geometry(self.cur, uuid, geometry)

            self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            spider.logger.error(f"Error inserting item into the database: {e}")
            raise

        return item

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()


class S3FileDownloadPipeline:
    download_files: bool = False
    s3_bucket: str
    s3_client: Any

    def __init__(self):
        self.download_files = getenv("DOWNLOAD_FILES").lower() == "true" if hasenv("DOWNLOAD_FILES") else False
        if not self.download_files:
            return

        self.s3_bucket = getenv("PLANNING_APPLICATIONS_BUCKET_NAME")

        if hasenv("AWS_ACCESS_KEY_ID") and hasenv("AWS_SECRET_ACCESS_KEY") and hasenv("AWS_REGION"):
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=getenv("AWS_REGION"),
            )
            return

        try:
            self.s3_client = boto3.client("s3")
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
        except Exception as e:
            raise Exception("AWS credentials not found") from e

    def process_item(self, item, spider):
        if not self.download_files:
            return item

        if isinstance(item, PlanningApplicationAppealDocument):
            self._download_and_upload_appeal_document(item, spider)

        return item

    def _download_and_upload_appeal_document(self, document, spider):
        url = self._get_attribute_or_key(document, "url")
        if not url:
            return

        appeal_case_id = self._get_attribute_or_key(document, "appeal_case_id")
        reference = self._get_attribute_or_key(document, "reference")
        filename = self._get_attribute_or_key(document, "name")

        s3_key = f"appeals/{appeal_case_id}/{reference}/{filename}"
        if self._object_exists(s3_key):
            spider.logger.info(f"Appeal document already exists in S3: {s3_key}")
            return

        spider.logger.info(f"Downloading appeal document: {url}")

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()

                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)

                temp_file.flush()

                self._upload_file_to_s3(temp_file.name, s3_key, spider)

                spider.logger.info(f"Successfully uploaded appeal document {s3_key} to S3")

                document.s3_path = f"s3://{self.s3_bucket}/{s3_key}"

            except requests.RequestException as e:
                spider.logger.error(f"Error downloading appeal document {url}: {e}")
            finally:
                os.unlink(temp_file.name)

    def _upload_file_to_s3(self, file_path, s3_key, spider):
        try:
            content_type = self._get_content_type(s3_key)

            self.s3_client.upload_file(file_path, self.s3_bucket, s3_key, ExtraArgs={"ContentType": content_type})
        except ClientError as e:
            spider.logger.error(f"S3 upload error for {s3_key}: {e}")
            raise

    def _get_content_type(self, filename):
        ext = os.path.splitext(filename)[1].lower()

        content_types = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".tif": "image/tiff",
            ".tiff": "image/tiff",
            ".txt": "text/plain",
            ".html": "text/html",
        }

        return content_types.get(ext, "application/octet-stream")

    def _object_exists(self, s3_key):
        try:
            self.s3_client.head_object(Bucket=self.s3_bucket, Key=s3_key)
            return True
        except ClientError as e:
            # Object does not exist
            if e.response["Error"]["Code"] == "404":
                return False
            # Some other error
            raise

    def _get_attribute_or_key(self, obj, name, default=None):
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

    def _set_attribute_or_key(self, obj, name, value):
        if isinstance(obj, dict):
            obj[name] = value
        else:
            setattr(obj, name, value)
