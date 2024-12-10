# Database Tables

## planning_applications

| Name                               | Type         | Nullable | Default | Extra              |
| ---------------------------------- | ------------ | -------- | ------- | ------------------ |
| uuid                               | uuid         | False    | NULL    | uuid_generate_v4() |
| lpa                                | varchar(255) | False    | NULL    | NULL               |
| idox_key_val                       | varchar(255) | False    | NULL    | NULL               |
| reference                          | varchar(255) | False    | NULL    | NULL               |
| application_received               | date         | False    | NULL    | NULL               |
| application_validated              | date         | False    | NULL    | NULL               |
| address                            | varchar(255) | False    | NULL    | NULL               |
| proposal                           | text         | False    | NULL    | NULL               |
| appeal_status                      | varchar(255) | False    | NULL    | NULL               |
| appeal_decision                    | varchar(255) | False    | NULL    | NULL               |
| application_type                   | varchar(255) | False    | NULL    | NULL               |
| expected_decision_level            | varchar(255) | False    | NULL    | NULL               |
| case_officer                       | varchar(255) | False    | NULL    | NULL               |
| parish                             | varchar(255) | False    | NULL    | NULL               |
| ward                               | varchar(255) | True     | NULL    | NULL               |
| amenity_society                    | varchar(255) | True     | NULL    | NULL               |
| district_reference                 | varchar(255) | False    | NULL    | NULL               |
| applicant_name                     | varchar(255) | False    | NULL    | NULL               |
| applicant_address                  | varchar(255) | False    | NULL    | NULL               |
| environmental_assessment_requested | bool         | False    | NULL    | NULL               |
| first_imported_at                  | timestamp    | False    | NULL    | CURRENT_TIMESTAMP  |
| last_imported_at                   | timestamp    | False    | NULL    | CURRENT_TIMESTAMP  |

## planning_application_documents

| Column                    | Type         | Nullable | Default | Extra |
| ------------------------- | ------------ | -------- | ------- | ----- |
| uuid                      | uuid         | False    | NULL    | NULL  |
| planning_application_uuid | uuid         | False    | NULL    | NULL  |
| date_published            | date         | False    | NULL    | NULL  |
| document_type             | varchar(255) | False    | NULL    | NULL  |
| drawing_number            | varchar(255) | True     | NULL    | NULL  |
| description               | text         | False    | NULL    | NULL  |
| url                       | text         | False    | NULL    | NULL  |

## planning_application_polygons

| Column                    | Type      | Nullable | Default | Extra |
| ------------------------- | --------- | -------- | ------- | ----- |
| planning_application_uuid | uuid      | False    | NULL    | NULL  |
| geometry                  | geometry  | False    | NULL    | NULL  |
| first_imported_at         | timestamp | False    | NULL    | now() |
| last_imported_at          | timestamp | False    | NULL    | now() |

## planning_application_titles

| Column                    | Type | Nullable | Default | Extra |
| ------------------------- | ---- | -------- | ------- | ----- |
| planning_application_uuid | uuid | False    | NULL    | NULL  |
| title_uuid                | uuid | False    | NULL    | NULL  |
