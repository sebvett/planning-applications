# Database Tables

---

## planning_application

| Name                               | Type         | Nullable | Default            | Foreign Key |
| ---------------------------------- | ------------ | -------- | ------------------ | ----------- |
| uuid                               | uuid         | False    | uuid_generate_v4() | NULL        |
| lpa                                | varchar(255) | False    | NULL               | NULL        |
| reference                          | varchar(255) | False    | NULL               | NULL        |
| website_reference                  | varchar(255) | False    | NULL               | NULL        |
| url                                | text         | False    | NULL               | NULL        |
| submitted_date                     | date         | False    | NULL               | NULL        |
| validated_date                     | date         | False    | NULL               | NULL        |
| address                            | varchar(255) | False    | NULL               | NULL        |
| description                        | text         | False    | NULL               | NULL        |
| application_status                 | varchar(255) | False    | NULL               | NULL        |
| application_decision               | varchar(255) | False    | NULL               | NULL        |
| application_decision_date          | date         | False    | NULL               | NULL        |
| appeal_status                      | varchar(255) | False    | NULL               | NULL        |
| appeal_decision                    | varchar(255) | False    | NULL               | NULL        |
| appeal_decision_date               | date         | False    | NULL               | NULL        |
| application_type                   | varchar(255) | False    | NULL               | NULL        |
| expected_decision_level            | varchar(255) | False    | NULL               | NULL        |
| actual_decision_level              | varchar(255) | False    | NULL               | NULL        |
| case_officer                       | varchar(255) | False    | NULL               | NULL        |
| parish                             | varchar(255) | False    | NULL               | NULL        |
| ward                               | varchar(255) | True     | NULL               | NULL        |
| amenity_society                    | varchar(255) | True     | NULL               | NULL        |
| district_reference                 | varchar(255) | False    | NULL               | NULL        |
| applicant_name                     | varchar(255) | False    | NULL               | NULL        |
| applicant_address                  | varchar(255) | False    | NULL               | NULL        |
| environmental_assessment_requested | bool         | False    | NULL               | NULL        |
| first_imported_at                  | timestamp    | False    | CURRENT_TIMESTAMP  | NULL        |
| last_imported_at                   | timestamp    | False    | CURRENT_TIMESTAMP  | NULL        |

## planning_application_documents

| Column                    | Type         | Nullable | Default            | Foreign Key                |
| ------------------------- | ------------ | -------- | ------------------ | -------------------------- |
| uuid                      | uuid         | False    | uuid_generate_v4() | NULL                       |
| planning_application_uuid | uuid         | False    | NULL               | planning_applications.uuid |
| date_published            | date         | False    | NULL               | NULL                       |
| document_type             | varchar(255) | False    | NULL               | NULL                       |
| description               | text         | False    | NULL               | NULL                       |
| url                       | text         | False    | NULL               | NULL                       |
| drawing_number            | varchar(255) | True     | NULL               | NULL                       |
| first_imported_at         | timestamp    | False    | CURRENT_TIMESTAMP  | NULL                       |
| last_imported_at          | timestamp    | False    | CURRENT_TIMESTAMP  | NULL                       |

## planning_application_geometries

| Column                    | Type      | Nullable | Default            | Foreign Key                |
| ------------------------- | --------- | -------- | ------------------ | -------------------------- |
| uuid                      | uuid      | False    | uuid_generate_v4() | NULL                       |
| planning_application_uuid | uuid      | False    | NULL               | planning_applications.uuid |
| geometry                  | geometry  | False    | NULL               | NULL                       |
| first_imported_at         | timestamp | False    | CURRENT_TIMESTAMP  | NULL                       |
| last_imported_at          | timestamp | False    | CURRENT_TIMESTAMP  | NULL                       |

--- idox section

## planning_applications

| Name                               | Type         | Nullable | Default            | Foreign Key |
| ---------------------------------- | ------------ | -------- | ------------------ | ----------- |
| uuid                               | uuid         | False    | uuid_generate_v4() | NULL        |
| lpa                                | varchar(255) | False    | NULL               | NULL        |
| idox_key_val                       | varchar(255) | False    | NULL               | NULL        |
| reference                          | varchar(255) | False    | NULL               | NULL        |
| application_received               | date         | False    | NULL               | NULL        |
| application_validated              | date         | False    | NULL               | NULL        |
| address                            | varchar(255) | False    | NULL               | NULL        |
| proposal                           | text         | False    | NULL               | NULL        |
| status                             | varchar(255) | False    | NULL               | NULL        |
| appeal_status                      | varchar(255) | False    | NULL               | NULL        |
| appeal_decision                    | varchar(255) | False    | NULL               | NULL        |
| application_type                   | varchar(255) | False    | NULL               | NULL        |
| expected_decision_level            | varchar(255) | False    | NULL               | NULL        |
| case_officer                       | varchar(255) | False    | NULL               | NULL        |
| parish                             | varchar(255) | False    | NULL               | NULL        |
| ward                               | varchar(255) | True     | NULL               | NULL        |
| amenity_society                    | varchar(255) | True     | NULL               | NULL        |
| district_reference                 | varchar(255) | False    | NULL               | NULL        |
| applicant_name                     | varchar(255) | False    | NULL               | NULL        |
| applicant_address                  | varchar(255) | False    | NULL               | NULL        |
| environmental_assessment_requested | bool         | False    | NULL               | NULL        |
| first_imported_at                  | timestamp    | False    | CURRENT_TIMESTAMP  | NULL        |
| last_imported_at                   | timestamp    | False    | CURRENT_TIMESTAMP  | NULL        |

## planning_application_documents

| Column                    | Type         | Nullable | Default            | Foreign Key                |
| ------------------------- | ------------ | -------- | ------------------ | -------------------------- |
| uuid                      | uuid         | False    | uuid_generate_v4() | NULL                       |
| planning_application_uuid | uuid         | False    | NULL               | planning_applications.uuid |
| date_published            | date         | False    | NULL               | NULL                       |
| document_type             | varchar(255) | False    | NULL               | NULL                       |
| drawing_number            | varchar(255) | True     | NULL               | NULL                       |
| description               | text         | False    | NULL               | NULL                       |
| url                       | text         | False    | NULL               | NULL                       |
| first_imported_at         | timestamp    | False    | CURRENT_TIMESTAMP  | NULL                       |
| last_imported_at          | timestamp    | False    | CURRENT_TIMESTAMP  | NULL                       |
