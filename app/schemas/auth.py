from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, value: str, info):
        password = info.data.get("password")
        if password and value != password:
            raise ValueError("Passwords do not match")
        return value


class RegisterResponse(BaseModel):
    message: str


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp_code: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class MessageResponse(BaseModel):
    message: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    is_verified: bool


class CompanyProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_type: str
    vat_number: str
    trn: str
    industry: str
    address: str
    phone_number: str


class ProfileMeResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_verified: bool
    company_profile: CompanyProfileOut | None
