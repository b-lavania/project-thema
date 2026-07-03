"""SQLAlchemy ORM models for the Tempus job-hunt OS."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def _uuid() -> str:
    return uuid.uuid4().hex[:12]


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def _today_iso() -> str:
    return date.today().isoformat()


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Company
# ---------------------------------------------------------------------------
class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    url = Column(String)
    linkedin_url = Column(String)
    careers_url = Column(String)
    industry = Column(String)
    segment = Column(String, nullable=False, default="realistic")  # dream | realistic | consulting
    stage = Column(String, nullable=False, default="sourced")
    hypothesis = Column(Text)
    notes = Column(Text)
    key_people = Column(Text)  # JSON array
    date_added = Column(String, nullable=False, default=_today_iso)
    date_updated = Column(String, nullable=False, default=_today_iso)
    date_stage_changed = Column(String)

    memos = relationship("Memo", back_populates="company", cascade="all, delete-orphan")
    outreach_actions = relationship("Outreach", back_populates="company", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Outreach
# ---------------------------------------------------------------------------
class Outreach(Base):
    __tablename__ = "outreach"

    id = Column(String, primary_key=True, default=_uuid)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    channel = Column(String, nullable=False)       # email | linkedin | warm_intro | application
    action = Column(String, nullable=False)         # sent | replied | booked | follow_up
    subject = Column(String)
    body = Column(Text)
    contact_name = Column(String)
    contact_role = Column(String)
    date = Column(String, nullable=False, default=_today_iso)
    response = Column(Text)
    response_date = Column(String)
    notes = Column(Text)

    company = relationship("Company", back_populates="outreach_actions")


# ---------------------------------------------------------------------------
# Memo
# ---------------------------------------------------------------------------
class Memo(Base):
    __tablename__ = "memos"

    id = Column(String, primary_key=True, default=_uuid)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    stated_problem = Column(Text)
    real_bottleneck = Column(Text)
    wrong_solution = Column(Text)
    metric_to_move = Column(Text)
    full_memo = Column(Text)
    date_created = Column(String, nullable=False, default=_today_iso)
    version = Column(Integer, nullable=False, default=1)

    company = relationship("Company", back_populates="memos")


# ---------------------------------------------------------------------------
# Artifact (weekly proof content)
# ---------------------------------------------------------------------------
class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(String, primary_key=True, default=_uuid)
    title = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    file_path = Column(String)
    date_created = Column(String, nullable=False, default=_today_iso)
    published = Column(Integer, nullable=False, default=0)
    published_to = Column(String)


# ---------------------------------------------------------------------------
# Evidence (positioning claims)
# ---------------------------------------------------------------------------
class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String, primary_key=True, default=_uuid)
    claim = Column(String, nullable=False)
    evidence = Column(Text, nullable=False)
    source = Column(String)
    date_added = Column(String, nullable=False, default=_today_iso)


# ---------------------------------------------------------------------------
# Metric (daily snapshots)
# ---------------------------------------------------------------------------
class Metric(Base):
    __tablename__ = "metrics"

    id = Column(String, primary_key=True, default=_uuid)
    date = Column(String, nullable=False)
    outbound_touches = Column(Integer, default=0)
    warm_intro_requests = Column(Integer, default=0)
    conversations = Column(Integer, default=0)
    applications = Column(Integer, default=0)
    replies_received = Column(Integer, default=0)
    interviews_booked = Column(Integer, default=0)
    onsites = Column(Integer, default=0)
    artifacts_published = Column(Integer, default=0)
    wip_count = Column(Integer, default=0)
    notes = Column(Text)


# Pipeline stage ordering (for SLA + sorting)
PIPELINE_STAGES = [
    "sourced",
    "researching",
    "contacted",
    "conversation",
    "applied",
    "interview",
    "onsite",
    "offer",
]

TERMINAL_STAGES = {"rejected", "ghosted"}

SEGMENTS = ["dream", "realistic", "consulting"]

CHANNELS = ["email", "linkedin", "warm_intro", "application"]

ACTIONS = ["sent", "replied", "booked", "follow_up"]
