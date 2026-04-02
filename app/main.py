from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import CompanyProfile, DemoBooking, User  # noqa: F401

app = FastAPI(title="UAE E-Invoicing Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.resolved_cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.resolved_cors_methods,
    allow_headers=settings.resolved_cors_headers,
)

Base.metadata.create_all(bind=engine)
app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
