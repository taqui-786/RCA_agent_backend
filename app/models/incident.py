from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.database import Base


class IncidentModel(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    severity = Column(String(20), nullable=False)
    service = Column(String(200), nullable=False)
    environment = Column(String(200), nullable=False)
    symptoms = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="open")
    root_cause = Column(Text, nullable=True)
    fix_applied = Column(Text, nullable=True)
    confidence = Column(Integer, nullable=True)
    recommended_fix = Column(Text, nullable=True)
    first_action = Column(Text, nullable=True)
    recalled_from = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
