import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SMTP_SUPPRESS_SEND"] = "true"

from app.api.deps import db_session
from app.db.base import Base
from app.main import app
from app.models.user import User

test_engine = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


def override_db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=test_engine)
app.dependency_overrides[db_session] = override_db_session


def get_test_client() -> TestClient:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    return TestClient(app)


def get_user_otp(email: str) -> str:
    with TestingSessionLocal() as db:
        user = db.query(User).filter(User.email == email.lower()).first()
        if not user or not user.otp_code:
            raise AssertionError("OTP code was not generated for user")
        return user.otp_code


def user_exists(email: str) -> bool:
    with TestingSessionLocal() as db:
        user = db.query(User).filter(User.email == email.lower()).first()
        return user is not None
