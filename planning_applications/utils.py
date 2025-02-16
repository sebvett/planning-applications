import os
import subprocess
import tempfile
from datetime import date, datetime
from typing import Optional

import scrapy.http.response
from dotenv import load_dotenv

load_dotenv()


def getenv(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not set")
    return value


def to_datetime_or_none(value: Optional[str | datetime | date]) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    return datetime.fromisoformat(value)


def open_in_browser(response: scrapy.http.response.Response):
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp:
        temp.write(response.text.encode("utf-8"))
        temp.seek(0)
        subprocess.run(["open", temp.name])


def multiline_css(response: scrapy.http.response.Response, selector: str, join_with: str = "\n") -> str | None:
    return join_with.join(response.css(selector).getall()) or None
