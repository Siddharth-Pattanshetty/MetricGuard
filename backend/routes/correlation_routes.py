"""
==========================================================
MetricGuard — Correlation Routes  (correlation_routes.py)
==========================================================

Phase 10: Metric-Log Correlation Engine

REST API endpoints for the correlation engine:

    GET  /correlations/         — All stored correlations
    GET  /correlations/latest   — Latest 20 correlations
    POST /correlations/run      — Trigger correlation engine manually
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from backend.schemas import CorrelationResponse, CorrelationRunResponse
from backend.services.correlation_service import CorrelationService

logger = logging.getLogger("metricguard.routers.correlations")

router = APIRouter(prefix="/correlations", tags=["Correlations"])

# Singleton service instance
_service = CorrelationService()


# ==========================================================
# GET /correlations/
# ==========================================================

@router.get("/", response_model=list[CorrelationResponse])
def get_correlations(db: Session = Depends(get_db)):
    """
    Retrieve all stored metric-log correlations.

    Returns a list of correlation records ordered by
    creation time (newest first).
    """
    try:
        correlations = _service.get_all_correlations(db)
        logger.info(
            "Returning %d correlation records", len(correlations),
        )
        return correlations
    except Exception as e:
        logger.error("Failed to retrieve correlations: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve correlations: {str(e)}",
        )


# ==========================================================
# GET /correlations/latest
# ==========================================================

@router.get("/latest", response_model=list[CorrelationResponse])
def get_latest_correlations(db: Session = Depends(get_db)):
    """
    Retrieve the latest 20 metric-log correlations.

    Returns a compact view of the most recent correlation
    events for dashboard consumption.
    """
    try:
        correlations = _service.get_latest_correlations(db, limit=20)
        logger.info(
            "Returning %d latest correlations", len(correlations),
        )
        return correlations
    except Exception as e:
        logger.error(
            "Failed to retrieve latest correlations: %s", e, exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve latest correlations: {str(e)}",
        )


# ==========================================================
# POST /correlations/run
# ==========================================================

@router.post("/run", response_model=CorrelationRunResponse)
def run_correlation_engine(db: Session = Depends(get_db)):
    """
    Manually trigger the correlation engine.

    Fetches recent metric anomalies and log anomalies,
    correlates them using the multi-factor scoring algorithm,
    and persists the results.

    Returns the number of new correlations created.
    """
    try:
        logger.info("Manual correlation engine trigger received.")
        count = _service.run_correlation_engine(db)

        return CorrelationRunResponse(
            status="success",
            correlations_created=count,
        )

    except Exception as e:
        logger.error(
            "Correlation engine run failed: %s", e, exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Correlation engine run failed: {str(e)}",
        )
