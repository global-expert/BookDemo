from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class DemoBookingRequest(BaseModel):
    full_name: str
    email: EmailStr
    industry: str
    meeting_time: datetime

    @field_validator("full_name", "industry")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value


class DemoBookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    industry: str
    meeting_time: datetime
    status: str
    message: str