"""
==========================================================
MetricGuard — Knowledge Base Schemas  (schemas.py)
==========================================================

Phase 17: Historical Incident Knowledge Base
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ArchiveRequest(BaseModel):
    """Payload schema to manually archive a resolved incident."""
    incident_id: str = Field(..., description="The ID of the incident to archive, e.g. INC-000001")


class SimilarSearchRequest(BaseModel):
    """Payload schema to search for similar historical incidents."""
    title: str = Field(..., description="Title or summary of the incident")
    description: str = Field(..., description="Description details of the incident")


class SimilarIncidentMatch(BaseModel):
    """Schema representing a single historical similarity match."""
    incident_id: str = Field(..., description="The ID of the matching past incident")
    similarity_score: float = Field(..., description="The similarity score (0.0 to 1.0)")
    root_cause: Optional[str] = Field(None, description="The root cause of the past incident")
    resolution: Optional[str] = Field(None, description="The resolution of the past incident")


class SimilarSearchResponse(BaseModel):
    """Response returned for similarity search queries."""
    matches: List[SimilarIncidentMatch] = Field(..., description="List of similar historical matches")


class IncidentHistoryResponse(BaseModel):
    """Schema representing archived incident history."""
    incident_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    service_name: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    recommendation: Optional[str] = None
    impact_summary: Optional[str] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RcaHistoryResponse(BaseModel):
    """Schema representing archived RCA history."""
    id: int
    incident_id: str
    root_cause: Optional[str] = None
    confidence: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResolutionHistoryResponse(BaseModel):
    """Schema representing archived Resolution history."""
    id: int
    incident_id: str
    resolution: Optional[str] = None
    action_taken: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
