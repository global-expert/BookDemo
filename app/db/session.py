from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


DATABASE_URL = settings.resolved_database_url


def _engine_kwargs(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


def _ensure_postgres_database_exists(database_url: str) -> None:
    if not database_url.startswith("postgresql"):
        return

    url = make_url(database_url)
    target_db = url.database
    if not target_db:
        return

    admin_url = url.set(database="postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    try:
        with admin_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": target_db},
            ).scalar()

            if not exists:
                safe_db_name = target_db.replace('"', '""')
                connection.execute(text(f'CREATE DATABASE "{safe_db_name}"'))
    finally:
        admin_engine.dispose()


_ensure_postgres_database_exists(DATABASE_URL)
engine = create_engine(DATABASE_URL, **_engine_kwargs(DATABASE_URL))
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
