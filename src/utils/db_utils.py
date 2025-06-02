import re
from datetime import datetime, timezone, date, time
from zoneinfo import ZoneInfo


def to_snake_case(name: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def current_utc_date() -> date:
    # datetime.now(timezone.utc).date()
    return datetime.now(ZoneInfo("Asia/Jakarta")).date()


def current_utc_time() -> time:
    # datetime.now(timezone.utc).time()
    return datetime.now(ZoneInfo("Asia/Jakarta")).time()


def prevent_sql_injection_safe(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9 ]", "", value)
