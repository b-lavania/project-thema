"""SQLite engine + session factory."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base

CRM_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = CRM_ROOT / "crm.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db() -> None:
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Return a new session (caller must close)."""
    return SessionLocal()


def reset_db() -> None:
    """Drop all tables and recreate."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
