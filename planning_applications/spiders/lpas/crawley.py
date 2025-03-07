from datetime import date, datetime
from typing import Any, Callable, List

import scrapy

from planning_applications.items import PlanningApplication, PlanningApplicationDocumentsDocument
from planning_applications.settings import DEFAULT_DATE_FORMAT
from planning_applications.spiders.base import BaseSpider


class CrawleySpider(BaseSpider):
    name: str = "crawley"
    domain: str = "planningregister.crawley.gov.uk"
    allowed_domains: List[str] = [domain]
    start_url: str = f"https://{domain}/Search/Advanced"

    not_yet_working: bool = False

    start_date: date
    end_date: date

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(self.start_date, str):
            self.start_date = datetime.strptime(self.start_date, DEFAULT_DATE_FORMAT).date()

        if isinstance(self.end_date, str):
            self.end_date = datetime.strptime(self.end_date, DEFAULT_DATE_FORMAT).date()

        if self.start_date > self.end_date:
            raise ValueError(f"start_date {self.start_date} must be earlier than end_date {self.end_date}")

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_url,
            callback=self.check_disclaimer(self.prepare_search_form),
            errback=self.handle_error,
            dont_filter=True,
        )

    def has_disclaimer_form(self, response) -> bool:
        """Check if the response contains the disclaimer form."""
        return bool(response.xpath('//form[.//button[@id="agreeToDisclaimer"]]').get())

    def check_disclaimer(self, callback: Callable) -> Callable:
        """Wrap a callback to check for and handle disclaimer form if present."""

        def wrapped_callback(response):
            if self.has_disclaimer_form(response):
                self.logger.info("Disclaimer form found, accepting before proceeding")
                return scrapy.FormRequest.from_response(
                    response,
                    formxpath='//form[.//button[@id="agreeToDisclaimer"]]',
                    method="POST",
                    formdata={},
                    callback=callback,
                    errback=self.handle_error,
                    dont_filter=True,
                )
            return callback(response)

        return wrapped_callback

    def prepare_search_form(self, response):
        self.logger.info("Disclaimer accepted, now on main planning page")

        from_date = self.start_date.strftime("%d/%m/%Y")
        to_date = self.end_date.strftime("%d/%m/%Y")

        yield scrapy.FormRequest.from_response(
            response,
            formxpath='//form[@action="/Search/Results"]',
            formdata={
                "SearchPlanning": "true",
                "SearchAppeals": "false",
                "SearchEnforcement": "false",
                "DateReceivedFrom": from_date,
                "DateReceivedTo": to_date,
            },
            callback=self.check_disclaimer(self.parse_search_results),
            dont_filter=True,
        )

    def parse_search_results(self, response):
        self.logger.info(f"Search results page loaded: {response.url}")

        if "No results found" in response.text:
            self.logger.info("No results found")
            return

        for item in response.css("div.results__item"):
            application_url = item.css("div.results__application-no div.results__data a::attr(href)").get()

            if application_url and self.applications_scraped < self.limit:
                self.applications_scraped += 1

                yield scrapy.Request(
                    url=response.urljoin(application_url),
                    callback=self.check_disclaimer(self.parse_application_details),
                    errback=self.handle_error,
                    dont_filter=True,
                )

            if self.applications_scraped >= self.limit:
                self.logger.info(f"Reached limit of {self.limit} applications")
                break

        next_page = response.css('li:not(.disabled) a[aria-label="Next Page."]::attr(href)').get()
        if next_page and self.applications_scraped < self.limit:
            self.logger.info(f"Following next page: {next_page}")
            yield scrapy.Request(
                url=response.urljoin(next_page),
                callback=self.check_disclaimer(self.parse_search_results),
                errback=self.handle_error,
                dont_filter=True,
            )

    def parse_application_details(self, response):
        self.logger.info("Application details page loaded")

        # application

        details = {}
        for row in response.css(".readOnlyDetails span"):
            label = row.xpath('./ancestor::div[contains(@class, "form-group")]/label/text()').get()
            if label:
                label = label.strip()
                value = row.css("span::text").get().strip() if row.css("span::text").get() else None
                details[label] = value

        # application

        application_number = details.get("Application Number")
        application_type = details.get("Application Type")
        status = details.get("Status")
        decision_level = details.get("Decision Level")
        case_officer = details.get("Case Officer")
        case_officer_phone = details.get("Phone")
        address = details.get("Location")
        proposal = details.get("Proposal")
        submitted_date = self.parse_date(details.get("Registered Date"))
        comments_due_date = self.parse_date(details.get("Comments Due Date"))
        target_decision_date = self.parse_date(details.get("Target Decision Date"))
        committee_date = self.parse_date(details.get("Committee Date"))
        decision = details.get("Decision")
        applicant_name = details.get("Applicant")
        applicant_address = details.get("Applicant's Address")
        agent_name = details.get("Agent")
        agent_address = details.get("Agent's Address")

        if not application_number or not submitted_date or not submitted_date:
            self.logger.warn(f"Missing required fields for application at {response.url}")
            return

        yield PlanningApplication(
            lpa=self.name,
            reference=application_number,
            website_reference=application_number,
            url=response.url,
            submitted_date=submitted_date,
            validated_date=submitted_date,
            address=address,
            description=proposal,
            application_status=status,
            application_decision=decision,
            application_decision_date=target_decision_date,
            application_type=application_type,
            expected_decision_level=decision_level,
            actual_decision_level=decision_level,
            case_officer=case_officer,
            case_officer_phone=case_officer_phone,
            comments_due_date=comments_due_date,
            committee_date=committee_date,
            applicant_name=applicant_name,
            applicant_address=applicant_address,
            agent_name=agent_name,
            agent_address=agent_address,
            is_active=True,
        )

        # documents

        document_type = None

        for doc_row in response.css(".document-list table tr"):
            # if has attr .header, the th text value is the document type
            if "header" in doc_row.attrib.get("class", ""):
                document_type = doc_row.css("th::text").get()
                continue

            doc_link = doc_row.css("a::attr(href)").get()
            if not doc_link:
                continue

            doc_date_text = doc_row.css("td:nth-child(3)::text").get()
            doc_date = None
            if doc_date_text and doc_date_text.strip():
                try:
                    doc_date = datetime.strptime(doc_date_text.strip(), "%d/%m/%Y")
                except ValueError:
                    pass

            doc_description = doc_row.css("a::text").get()
            if doc_description:
                doc_description = doc_description.strip()

            yield PlanningApplicationDocumentsDocument(
                url=response.urljoin(doc_link),
                document_type=document_type,
                date_published=doc_date,
                description=doc_description,
            )

    def parse_date(self, date_str: str | None) -> datetime | None:
        if not date_str:
            return None
        return datetime.strptime(date_str.strip(), "%d/%m/%Y")
