CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DROP TABLE IF EXISTS public.planning_application_documents CASCADE;

DROP TABLE IF EXISTS public.planning_application_geometries CASCADE;

DROP TABLE IF EXISTS public.planning_applications CASCADE;

CREATE TABLE
    public.planning_applications (
        uuid uuid DEFAULT uuid_generate_v4 () NOT NULL,
        lpa CHARACTER VARYING(255) NOT NULL,
        reference CHARACTER VARYING(255) NOT NULL,
        website_reference CHARACTER VARYING(255) NOT NULL,
        url text NOT NULL,
        submitted_date DATE NOT NULL,
        validated_date DATE,
        address text NOT NULL,
        description text NOT NULL,
        application_status CHARACTER VARYING(255) NOT NULL,
        application_decision CHARACTER VARYING(255),
        application_decision_date DATE,
        appeal_status CHARACTER VARYING(255),
        appeal_decision CHARACTER VARYING(255),
        appeal_decision_date DATE,
        application_type CHARACTER VARYING(255) NOT NULL,
        expected_decision_level CHARACTER VARYING(255),
        actual_decision_level CHARACTER VARYING(255),
        case_officer CHARACTER VARYING(255),
        parish CHARACTER VARYING(255),
        ward CHARACTER VARYING(255),
        amenity_society CHARACTER VARYING(255),
        district_reference CHARACTER VARYING(255),
        applicant_name CHARACTER VARYING(255) NOT NULL,
        applicant_address CHARACTER VARYING(255),
        environmental_assessment_requested BOOLEAN,
        first_imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT planning_applications_pkey PRIMARY KEY (uuid),
        CONSTRAINT planning_applications_lpa_reference_key UNIQUE (lpa, reference),
        CONSTRAINT planning_applications_submitted_date_validated_date_check CHECK (submitted_date <= validated_date),
        CONSTRAINT planning_applications_validated_date_application_decision_date_check CHECK (validated_date <= application_decision_date),
        CONSTRAINT planning_applications_application_decision_date_appeal_decision_date_check CHECK (application_decision_date <= appeal_decision_date)
    );

CREATE TABLE
    public.planning_application_documents (
        uuid uuid NOT NULL DEFAULT uuid_generate_v4 (),
        planning_application_uuid uuid NOT NULL,
        date_published DATE NOT NULL,
        document_type CHARACTER VARYING(255) NOT NULL,
        description text NOT NULL,
        url text NOT NULL,
        drawing_number CHARACTER VARYING(255),
        first_imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (planning_application_uuid) REFERENCES public.planning_applications (uuid)
    );

CREATE TABLE
    public.planning_application_geometries (
        uuid uuid NOT NULL DEFAULT uuid_generate_v4 (),
        planning_application_uuid uuid NOT NULL,
        geometry geometry NOT NULL,
        first_imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (planning_application_uuid) REFERENCES public.planning_applications (uuid)
    );