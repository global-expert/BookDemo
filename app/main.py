from fastapi import FastAPI

from app.api.router import api_router
from app.db.base import Base
from app.db.session import engine
from app.models import CompanyProfile, DemoBooking, User  # noqa: F401

app = FastAPI(title="UAE E-Invoicing Backend")

Base.metadata.create_all(bind=engine)
app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
