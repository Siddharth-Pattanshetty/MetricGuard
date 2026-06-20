"""
==========================================================
MetricGuard — Knowledge Base Routes  (knowledge_routes.py)
==========================================================

Phase 17: Historical Incident Knowledge Base
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from backend.knowledge_base.schemas import (
    ArchiveRequest,
    SimilarSearchRequest,
    SimilarSearchResponse,
    IncidentHistoryResponse,
    RcaHistoryResponse,
    ResolutionHistoryResponse,
)
from backend.knowledge_base.knowledge_service import get_knowledge_service

logger = logging.getLogger("metricguard.routers.knowledge")

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])

_service = get_knowledge_service()


# ==========================================================
# POST /knowledge/archive
# ==========================================================
@router.post("/archive", status_code=200)
def archive_incident(payload: ArchiveRequest, db: Session = Depends(get_db)):
    """
    Manually archive a resolved incident and persist it in the TiDB Knowledge Base.
    """
    try:
        logger.info("[Knowledge API] Archiving incident %s", payload.incident_id)
        _service.archive_incident(db, payload.incident_id)
        return {
            "status": "success",
            "message": f"Incident '{payload.incident_id}' archived successfully."
        }
    except ValueError as ve:
        logger.warning("[Knowledge API] Archival validation error: %s", ve)
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error("[Knowledge API] Archival failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to archive incident: {str(e)}"
        )


# ==========================================================
# GET /knowledge/incidents
# ==========================================================
@router.get("/incidents", response_model=List[IncidentHistoryResponse])
def get_incident_history(db: Session = Depends(get_db)):
    """
    Retrieve all archived incident history records.
    """
    try:
        incidents = _service.get_incident_history(db)
        return incidents
    except Exception as e:
        logger.error("[Knowledge API] Failed to fetch incident history: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# GET /knowledge/rca
# ==========================================================
@router.get("/rca", response_model=List[RcaHistoryResponse])
def get_rca_history(db: Session = Depends(get_db)):
    """
    Retrieve all archived RCA history records.
    """
    try:
        rcas = _service.get_rca_history(db)
        return rcas
    except Exception as e:
        logger.error("[Knowledge API] Failed to fetch RCA history: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# GET /knowledge/resolutions
# ==========================================================
@router.get("/resolutions", response_model=List[ResolutionHistoryResponse])
def get_resolution_history(db: Session = Depends(get_db)):
    """
    Retrieve all archived resolution history records.
    """
    try:
        resolutions = _service.get_resolution_history(db)
        return resolutions
    except Exception as e:
        logger.error("[Knowledge API] Failed to fetch resolution history: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# POST /knowledge/similar
# ==========================================================
@router.post("/similar", response_model=SimilarSearchResponse)
def search_similar_incidents(payload: SimilarSearchRequest, db: Session = Depends(get_db)):
    """
    Search for similar historical incidents based on title/description comparison.
    """
    try:
        matches = _service.search_similar_incidents(db, payload.title, payload.description)
        return {"matches": matches}
    except Exception as e:
        logger.error("[Knowledge API] Similar incident search failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
