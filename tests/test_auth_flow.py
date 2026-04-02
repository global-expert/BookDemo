from fastapi.testclient import TestClient


def test_register_creates_user_and_returns_message() -> None:
    from tests.conftest import get_test_client

    client: TestClient = get_test_client()
    payload = {
        "full_name": "Mariam Noor",
        "email": "mariam@example.com",
        "password": "Secret123!",
        "confirm_password": "Secret123!"
    }

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "Account created. OTP sent to your email."
    assert "otp_code" not in body


def test_register_rejects_duplicate_email() -> None:
    from tests.conftest import get_test_client

    client: TestClient = get_test_client()
    payload = {
        "full_name": "Mariam Noor",
        "email": "mariam@example.com",
        "password": "Secret123!",
        "confirm_password": "Secret123!"
    }

    first = client.post("/api/v1/auth/register", json=payload)
    second = client.post("/api/v1/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "Email already registered"


def test_verify_otp_marks_user_as_verified() -> None:
    from tests.conftest import get_test_client, get_user_otp

    client: TestClient = get_test_client()
    payload = {
        "full_name": "Mariam Noor",
        "email": "mariam@example.com",
        "password": "Secret123!",
        "confirm_password": "Secret123!"
    }

    client.post("/api/v1/auth/register", json=payload)
    otp_code = get_user_otp("mariam@example.com")

    verify_response = client.post(
        "/api/v1/auth/verify-otp",
        json={"email": "mariam@example.com", "otp_code": otp_code}
    )

    assert verify_response.status_code == 200
    assert verify_response.json()["message"] == "OTP verified successfully"


def test_company_setup_requires_verified_account() -> None:
    from tests.conftest import get_test_client

    client: TestClient = get_test_client()
    payload = {
        "full_name": "Mariam Noor",
        "email": "mariam@example.com",
        "password": "Secret123!",
        "confirm_password": "Secret123!"
    }

    client.post("/api/v1/auth/register", json=payload)

    setup_payload = {
        "email": "mariam@example.com",
        "company_type": "LLC",
        "vat_number": "100256789900003",
        "trn": "123456789000003",
        "industry": "Technology",
        "address": "Dubai Media City",
        "phone_number": "+971501234567"
    }

    unverified_response = client.post("/api/v1/company/setup", json=setup_payload)

    assert unverified_response.status_code == 400
    assert unverified_response.json()["detail"] == "Account must be verified first"


def test_register_returns_503_when_smtp_not_configured_and_rolls_back_user() -> None:
    from app.core.config import settings
    from tests.conftest import get_test_client, user_exists

    client: TestClient = get_test_client()
    payload = {
        "full_name": "Noor Ali",
        "email": "noor@example.com",
        "password": "Secret123!",
        "confirm_password": "Secret123!"
    }

    original_suppress = settings.smtp_suppress_send
    original_host = settings.smtp_host
    original_from = settings.smtp_from_address
    settings.smtp_suppress_send = False
    settings.smtp_host = ""
    settings.smtp_from_address = ""

    try:
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 503
        assert response.json()["detail"] == "SMTP settings are not configured"
        assert user_exists("noor@example.com") is False
    finally:
        settings.smtp_suppress_send = original_suppress
        settings.smtp_host = original_host
        settings.smtp_from_address = original_from
