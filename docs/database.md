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
| description                        | text         | True     | NULL               | NULL        |
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
| is_active                          | bool         | False    | TRUE               | NULL        |
| first_imported_at                  | timestamp    | False    | CURRENT_TIMESTAMP  | NULL        |
| last_imported_at                   | timestamp    | False    | CURRENT_TIMESTAMP  | NULL        |

## planning_application_documents

| Column                    | Type         | Nullable | Default            | Foreign Key                |
| ------------------------- | ------------ | -------- | ------------------ | -------------------------- |
| uuid                      | uuid         | False    | uuid_generate_v4() | NULL                       |
| planning_application_uuid | uuid         | False    | NULL               | planning_applications.uuid |
| date_published            | date         | False    | NULL               | NULL                       |
| document_type             | varchar(255) | False    | NULL               | NULL                       |
| description               | text         | True     | NULL               | NULL                       |
| url                       | text         | False    | NULL               | NULL                       |
| drawing_number            | varchar(255) | True     | NULL               | NULL                       |
| first_imported_at         | timestamp    | False    | CURRENT_TIMESTAMP  | NULL                       |
| last_imported_at          | timestamp    | False    | CURRENT_TIMESTAMP  | NULL                       |

## planning_application_geometries

| Column                    | Type         | Nullable | Default            | Foreign Key                |
| ------------------------- | ------------ | -------- | ------------------ | -------------------------- |
| uuid                      | uuid         | False    | uuid_generate_v4() | NULL                       |
| planning_application_uuid | uuid         | False    | NULL               | planning_applications.uuid |
| reference                 | varchar(255) | False    | NULL               | NULL                       |
| geometry                  | geometry     | False    | NULL               | NULL                       |
| first_imported_at         | timestamp    | False    | CURRENT_TIMESTAMP  | NULL                       |
| last_imported_at          | timestamp    | False    | CURRENT_TIMESTAMP  | NULL                       |

## planning_application_appeals

| Column                             | Type         | Nullable | Default            | Foreign Key |
| ---------------------------------- | ------------ | -------- | ------------------ | ----------- |
| uuid                               | uuid         | False    | uuid_generate_v4() | NULL        |
| lpa                                | varchar(255) | False    | NULL               | NULL        |
| reference                          | varchar(255) | False    | NULL               | NULL        |
| case_id                            | int          | False    | NULL               | NULL        |
| url                                | text         | False    | NULL               | NULL        |
| appellant_name                     | varchar(255) | True     | NULL               | NULL        |
| agent_name                         | varchar(255) | True     | NULL               | NULL        |
| site_address                       | varchar(255) | True     | NULL               | NULL        |
| case_type                          | varchar(255) | True     | NULL               | NULL        |
| case_officer                       | varchar(255) | True     | NULL               | NULL        |
| procedure                          | varchar(255) | True     | NULL               | NULL        |
| status                             | varchar(255) | True     | NULL               | NULL        |
| decision                           | varchar(255) | True     | NULL               | NULL        |
| start_date                         | date         | True     | NULL               | NULL        |
| questionnaire_due_date             | date         | True     | NULL               | NULL        |
| statement_due_date                 | date         | True     | NULL               | NULL        |
| interested_party_comments_due_date | date         | True     | NULL               | NULL        |
| final_comments_due_date            | date         | True     | NULL               | NULL        |
| inquiry_evidence_due_date          | date         | True     | NULL               | NULL        |
| event_date                         | date         | True     | NULL               | NULL        |
| decision_date                      | date         | True     | NULL               | NULL        |
| linked_case_ids                    | int[]        | True     | NULL               | NULL        |
| first_imported_at                  | timestamp    | False    | CURRENT_TIMESTAMP  | NULL        |
| last_imported_at                   | timestamp    | False    | CURRENT_TIMESTAMP  | NULL        |

## planning_application_appeals_documents

| Column                           | Type         | Nullable | Default            | Foreign Key                       |
| -------------------------------- | ------------ | -------- | ------------------ | --------------------------------- |
| uuid                             | uuid         | False    | uuid_generate_v4() | NULL                              |
| planning_application_appeal_uuid | uuid         | False    | NULL               | planning_application_appeals.uuid |
| appeal_case_id                   | int          | False    | NULL               | NULL                              |
| reference                        | varchar(255) | True     | NULL               | NULL                              |
| name                             | varchar(255) | True     | NULL               | NULL                              |
| url                              | text         | False    | NULL               | NULL                              |
| first_imported_at                | timestamp    | False    | CURRENT_TIMESTAMP  | NULL                              |
| last_imported_at                 | timestamp    | False    | CURRENT_TIMESTAMP  | NULL                              |
