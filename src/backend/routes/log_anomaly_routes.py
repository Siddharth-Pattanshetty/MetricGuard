"""
==========================================================
MetricGuard — Log Anomaly Routes  (log_anomaly_routes.py)
==========================================================

Phase 15: Unified AIOps Dashboard

REST API endpoint for retrieving detected log anomalies:
    GET /log-anomalies  — Fetch recent logs, run ML inference,
                          return anomalous entries with scores.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import Log
from backend.services.log_anomaly_service import get_log_anomaly_service

logger = logging.getLogger("metricguard.routers.log_anomalies")

router = APIRouter(tags=["Log Anomalies"])


# ==========================================================
# RESPONSE SCHEMA
# ==========================================================

class LogAnomalyResponse(BaseModel):
    """Output schema for a single detected log anomaly."""
    id: int
    timestamp: datetime
    level: str
    service_name: str
    message: str
    anomaly_score: float
    template: str

    model_config = ConfigDict(from_attributes=True)


# ==========================================================
# GET /log-anomalies
# ==========================================================

@router.get("/log-anomalies", response_model=list[LogAnomalyResponse])
def get_log_anomalies(
    minutes: int = Query(default=60, ge=1, le=1440, description="Time window in minutes to scan for log anomalies"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum number of anomalous logs to return"),
    db: Session = Depends(get_db),
):
    """
    Fetch recent logs from the database, run the Isolation Forest
    log anomaly model on each, and return entries classified as
    anomalous along with their anomaly scores.
    """
    try:
        log_service = get_log_anomaly_service()

        if log_service.model is None or log_service.vectorizer is None:
            logger.warning("[Log Anomaly API] Model not loaded, returning empty list.")
            return []

        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        logs = (
            db.query(Log)
            .filter(Log.timestamp >= cutoff)
            .order_by(desc(Log.timestamp))
            .limit(500)  # Cap raw fetch to avoid overload
            .all()
        )

        anomalous_logs = []
        for log in logs:
            if log_service.predict_log_anomaly(log.message):
                # Compute anomaly score from the model's decision function
                try:
                    X = log_service.vectorizer.transform([log.message])
                    import pandas as pd
                    df = pd.DataFrame(X.toarray(), columns=[f"E{i}" for i in range(1, 30)])
                    score = float(-log_service.model.decision_function(df)[0])
                    # Normalize to 0-1 range (higher = more anomalous)
                    score = max(0.0, min(1.0, (score + 0.5) / 1.0))
                except Exception:
                    score = 0.85  # Fallback score for confirmed anomalies

                # Generate a simplified template from the message
                template = _extract_template(log.message)

                anomalous_logs.append(LogAnomalyResponse(
                    id=log.id,
                    timestamp=log.timestamp,
                    level=log.level,
                    service_name=log.service_name,
                    message=log.message,
                    anomaly_score=round(score, 4),
                    template=template,
                ))

                if len(anomalous_logs) >= limit:
                    break

        logger.info(
            "[Log Anomaly API] Returning %d anomalies from %d logs (last %d min)",
            len(anomalous_logs), len(logs), minutes,
        )
        return anomalous_logs

    except Exception as e:
        logger.error("[Log Anomaly API] Failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve log anomalies: {str(e)}")


def _extract_template(message: str) -> str:
    """
    Extract a simplified template from a log message by replacing
    numeric values and IPs with placeholders.
    """
    import re
    # Replace IP addresses
    result = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '<IP>', message)
    # Replace numbers
    result = re.sub(r'\b\d+\b', '<N>', result)
    # Truncate long templates
    if len(result) > 120:
        result = result[:117] + "..."
    return result
