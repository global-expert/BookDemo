from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.demo_booking import DemoBooking
from app.schemas.demo import DemoBookingRequest, DemoBookingResponse

router = APIRouter(prefix="/demo", tags=["demo"])


def _normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@router.post("/book", response_model=DemoBookingResponse, status_code=status.HTTP_201_CREATED)
def book_demo(payload: DemoBookingRequest, db: Session = Depends(db_session)) -> DemoBookingResponse:
    meeting_time = _normalize_datetime(payload.meeting_time)
    if meeting_time <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Meeting time must be in the future")

    booking = DemoBooking(
        full_name=payload.full_name.strip(),
        email=payload.email.lower(),
        industry=payload.industry.strip(),
        meeting_time=meeting_time,
        status="pending",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return DemoBookingResponse(
        id=booking.id,
        full_name=booking.full_name,
        email=booking.email,
        industry=booking.industry,
        meeting_time=booking.meeting_time,
        status=booking.status,
        message="Demo booked successfully. We will contact you shortly to confirm your demo.",
    )