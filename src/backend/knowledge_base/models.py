"""
==========================================================
MetricGuard — Knowledge Base Database Models  (models.py)
==========================================================

Phase 17: Historical Incident Knowledge Base
"""

from sqlalchemy import Column, String, Text, DateTime, Float, BigInteger, func
from app.database import Base


class IncidentHistory(Base):
    """
    ORM model representing the archived state of resolved incidents.
    """
    __tablename__ = "incident_history"

    incident_id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    service_name = Column(String(255), nullable=True)
    severity = Column(String(32), nullable=True)
    status = Column(String(32), nullable=True)
    root_cause = Column(Text, nullable=True)
    resolution = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    impact_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<IncidentHistory(incident_id='{self.incident_id}', title='{self.title}', status='{self.status}')>"


class RcaHistory(Base):
    """
    ORM model representing the historical RCA findings.
    """
    __tablename__ = "rca_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    incident_id = Column(String(64), index=True)
    root_cause = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<RcaHistory(id={self.id}, incident_id='{self.incident_id}', root_cause='{self.root_cause[:30]}')>"


class ResolutionHistory(Base):
    """
    ORM model representing the resolutions applied to past incidents.
    """
    __tablename__ = "resolution_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    incident_id = Column(String(64), index=True)
    resolution = Column(Text, nullable=True)
    action_taken = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<ResolutionHistory(id={self.id}, incident_id='{self.incident_id}', resolution='{self.resolution[:30]}')>"
