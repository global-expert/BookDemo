import secrets
from datetime import datetime, timedelta, timezone


def generate_otp_code() -> str:
    return str(secrets.randbelow(900000) + 100000)


def otp_expiry(minutes: int = 10) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)
