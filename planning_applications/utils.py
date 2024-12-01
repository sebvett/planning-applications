import os

from dotenv import load_dotenv

load_dotenv()


def getenv(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not set")
    return value
