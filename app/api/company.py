from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.company_profile import CompanyProfile
from app.models.user import User
from app.schemas.company import CompanySetupRequest, CompanySetupResponse

router = APIRouter(prefix="/company", tags=["company"])


@router.post("/setup", response_model=CompanySetupResponse)
def setup_company(payload: CompanySetupRequest, db: Session = Depends(db_session)) -> CompanySetupResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account must be verified first",
        )

    existing_profile = db.scalar(select(CompanyProfile).where(CompanyProfile.user_id == user.id))
    if existing_profile:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Company profile already exists")

    profile = CompanyProfile(
        user_id=user.id,
        company_type=payload.company_type,
        vat_number=payload.vat_number,
        trn=payload.trn,
        industry=payload.industry,
        address=payload.address,
        phone_number=payload.phone_number,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    return CompanySetupResponse.model_validate(profile)
