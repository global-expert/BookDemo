from pydantic import BaseModel, ConfigDict, EmailStr


class CompanySetupRequest(BaseModel):
    email: EmailStr
    company_type: str
    vat_number: str
    trn: str
    industry: str
    address: str
    phone_number: str


class CompanySetupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_type: str
    vat_number: str
    trn: str
    industry: str
    address: str
    phone_number: str
