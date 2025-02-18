CREATE EXTENSION IF NOT EXISTS "postgis";

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DROP TABLE IF EXISTS public.scraper_runs CASCADE;

DROP TABLE IF EXISTS public.planning_application_documents CASCADE;

DROP TABLE IF EXISTS public.planning_application_geometries CASCADE;

DROP TABLE IF EXISTS public.planning_applications CASCADE;

DROP TABLE IF EXISTS public.planning_application_appeals CASCADE;

DROP TABLE IF EXISTS public.planning_application_appeals_documents CASCADE;

CREATE TABLE
    public.scraper_runs (
        name TEXT NOT NULL,
        last_finished_at TIMESTAMP,
        last_data_found_at TIMESTAMP,
        last_run_stats JSONB,
        CONSTRAINT scraper_runs_name_pkey PRIMARY KEY (name)
    );

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
        description text,
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
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
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
        description text,
        url text NOT NULL,
        drawing_number CHARACTER VARYING(255),
        first_imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT planning_application_documents_pkey PRIMARY KEY (uuid),
        CONSTRAINT planning_application_documents_url_key UNIQUE (url),
        FOREIGN KEY (planning_application_uuid) REFERENCES public.planning_applications (uuid)
    );

CREATE TABLE
    public.planning_application_geometries (
        uuid uuid NOT NULL DEFAULT uuid_generate_v4 (),
        planning_application_uuid uuid NOT NULL,
        reference CHARACTER VARYING(255) NOT NULL,
        geometry geometry,
        first_imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT planning_application_geometries_pkey PRIMARY KEY (uuid),
        CONSTRAINT planning_application_geometries_planning_application_uuid_reference_key UNIQUE (planning_application_uuid, reference),
        FOREIGN KEY (planning_application_uuid) REFERENCES public.planning_applications (uuid)
    );

CREATE TABLE
    public.planning_application_appeals (
        uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
        lpa text NOT NULL,
        reference text NOT NULL,
        case_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        appellant_name text,
        agent_name text,
        site_address text,
        case_type text,
        case_officer text,
        procedure text,
        status text,
        decision text,
        start_date DATE,
        questionnaire_due_date DATE,
        statement_due_date DATE,
        interested_party_comments_due_date DATE,
        final_comments_due_date DATE,
        inquiry_evidence_due_date DATE,
        event_date DATE,
        decision_date DATE,
        linked_case_ids INTEGER[],
        first_imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT planning_application_appeals_pkey PRIMARY KEY (uuid),
        CONSTRAINT planning_application_appeals_case_id_key UNIQUE (case_id)
    );

CREATE TABLE
    public.planning_application_appeals_documents (
        uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
        planning_application_appeal_uuid uuid NOT NULL,
        appeal_case_id INTEGER NOT NULL,
        reference text,
        name text,
        url TEXT NOT NULL,
        first_imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT planning_application_appeals_documents_pkey PRIMARY KEY (uuid),
        CONSTRAINT planning_application_appeals_documents_planning_application_appeal_uuid_key UNIQUE (planning_application_appeal_uuid),
        CONSTRAINT planning_application_appeals_documents_url_key UNIQUE (url),
        FOREIGN KEY (planning_application_appeal_uuid) REFERENCES public.planning_application_appeals (uuid)
    );
