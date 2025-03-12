from datetime import date, datetime
from os import path

import pytest
from parsel import Selector
from scrapy.http.response.text import TextResponse

from planning_applications.items import PlanningApplicationAppeal
from planning_applications.settings import DEFAULT_DATE_FORMAT
from planning_applications.spiders.appeals import AppealsSpider


def test_spider_initialization():
    # with case IDs
    spider = AppealsSpider(from_case_id="12345", to_case_id="12346")
    assert spider.from_case_id == 12345
    assert spider.to_case_id == 12346

    # with dates
    spider = AppealsSpider(start_date="2024-01-01", end_date="2024-01-31")
    assert spider.start_date == date(2024, 1, 1)
    assert spider.end_date == date(2024, 1, 31)


def test_spider_initialization_validation():
    # case IDs must be provided together
    with pytest.raises(ValueError, match="to_case_id and from_case_id must be provided together"):
        AppealsSpider(from_case_id="12345")

    # from case ID must be less than to case ID
    with pytest.raises(ValueError, match="from_case_id .* must be less than to_case_id"):
        AppealsSpider(from_case_id="12345", to_case_id="12344")

    # dates must not be provided when case IDs are provided
    with pytest.raises(ValueError, match="start_date and end_date must not be provided when from_case_id is provided"):
        AppealsSpider(from_case_id="12345", to_case_id="12346", start_date="01/01/2024")

    # start date must not be later than end date
    with pytest.raises(ValueError, match="start_date .* must not be later than end_date"):
        AppealsSpider(start_date="2024-12-31", end_date="2024-01-01")

    # start date must be in the past
    future_date = (datetime.now().date().replace(year=datetime.now().year + 1)).strftime(DEFAULT_DATE_FORMAT)
    future_date_one_day_later = (
        datetime.now().date().replace(year=datetime.now().year + 1, day=datetime.now().day + 1)
    ).strftime(DEFAULT_DATE_FORMAT)
    with pytest.raises(ValueError, match="start_date .* must be in the past"):
        AppealsSpider(start_date=future_date, end_date=future_date_one_day_later)


def test_parse_case():
    with open(path.realpath("./tests/planning_applications/fixtures/appeals/case.html"), "r") as f:
        html = f.read()

    response = TextResponse(
        url="https://acp.planninginspectorate.gov.uk/ViewCase.aspx?CaseID=3360163&ColID=0", body=html, encoding="utf-8"
    )

    results = list(AppealsSpider(from_case_id="3360163", to_case_id="3360163").parse_case(response))

    assert len(results) == 1
    item = results[0]

    assert isinstance(item, PlanningApplicationAppeal)
    assert item.lpa == "North Yorkshire Council"
    assert item.url == "https://acp.planninginspectorate.gov.uk/ViewCase.aspx?CaseID=3360163&ColID=0"
    assert item.reference == "APP/U2750/W/25/3360163"
    assert item.case_id == 3360163
    assert item.appellant_name == "Mr D Cowton"
    assert item.agent_name == "ELG Planning"
    assert item.site_address == "Back Lane\nAlne\nYO61 1TJ"
    assert item.case_type == "Planning Appeal (W)"
    assert item.case_officer == "Nicholas Patch"
    assert item.status == "In Progress"
    assert item.decision == "Not yet decided"
    assert item.start_date == datetime(2025, 2, 10, 0, 0)
    assert item.questionnaire_due_date == datetime(2025, 2, 17, 0, 0)
    assert item.statement_due_date == datetime(2025, 3, 17, 0, 0)
    assert item.interested_party_comments_due_date == datetime(2025, 3, 17, 0, 0)
    assert item.final_comments_due_date == datetime(2025, 3, 31, 0, 0)
    assert item.inquiry_evidence_due_date is None
    assert item.event_date is None
    assert item.decision_date is None


def test_parse_case_id_from_anchor():
    spider = AppealsSpider(
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    tests = [
        {
            "html": '<a href="someurl.com?caseid=12345">Case Link</a>',
            "case_id": 12345,
        },
        {
            "html": '<a href="someurl.com?CaseID=12345">Case Link</a>',
            "case_id": 12345,
        },
        {
            "html": '<a href="someurl.com?Caseid=12345">Case Link</a>',
            "case_id": 12345,
        },
        {
            "html": '<a href="someurl.com?CASEID=67890">Case Link</a>',
            "case_id": 67890,
        },
        {
            "html": "<a>No Link</a>",
            "case_id": None,
        },
        {
            "html": '<a href="someurl.com?caseid=invalid">Invalid Case</a>',
            "case_id": None,
        },
    ]

    for test in tests:
        selector = Selector(text=test["html"])
        anchor = selector.css("a")[0]

        case_id = spider._parse_case_id_from_anchor(anchor)
        assert case_id == test["case_id"]
