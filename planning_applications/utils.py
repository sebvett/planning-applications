import os
from calendar import monthrange
from datetime import date, datetime
from typing import Optional, Tuple

from dotenv import load_dotenv

load_dotenv()


def getenv(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not set")
    return value


def previous_month(some_date: date) -> Tuple[date, date]:
    year = some_date.year
    month = some_date.month
    if month == 1:
        new_year = year - 1
        new_month = 12
    else:
        new_year = year
        new_month = month - 1
    last_day = monthrange(new_year, new_month)[1]
    return date(new_year, new_month, 1), date(new_year, new_month, last_day)


def to_datetime_or_none(value: Optional[str | datetime | date]) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    return datetime.fromisoformat(value)
