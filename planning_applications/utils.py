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


def to_datetime_or_none(value: Optional[str | datetime | date]) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    return datetime.fromisoformat(value)
