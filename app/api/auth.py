from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.user import User
from app.schemas.auth import MessageResponse, RegisterRequest, RegisterResponse, VerifyOtpRequest
from app.services.email_sender import EmailConfigurationError, EmailDeliveryError, send_otp_email
from app.services.otp import generate_otp_code, otp_expiry
from app.services.security import get_password_hash

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(db_session)) -> RegisterResponse:
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    code = generate_otp_code()
    user = User(
        full_name=payload.full_name,
        email=payload.email.lower(),
        hashed_password=get_password_hash(payload.password),
        otp_code=code,
        otp_expires_at=otp_expiry(),
    )
    db.add(user)
    try:
        send_otp_email(payload.email.lower(), code)
        db.commit()
    except EmailConfigurationError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except EmailDeliveryError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.message,
        ) from exc

    return RegisterResponse(message="Account created. OTP sent to your email.")


@router.post("/verify-otp", response_model=MessageResponse)
def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(db_session)) -> MessageResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.otp_code or user.otp_code != payload.otp_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code")

    if user.otp_expires_at:
        expires_at = user.otp_expires_at
        if expires_at.tzinfo is None or expires_at.tzinfo.utcoffset(expires_at) is None:
            # SQLite returns naive datetime, treat as UTC
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP code expired")

    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None
    db.add(user)
    db.commit()

    return MessageResponse(message="OTP verified successfully")
