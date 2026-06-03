import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MetricCreate, MetricResponse, MetricCollectorInput
from app.crud import insert_metric, get_metrics, parse_speed_string

logger = logging.getLogger("metricguard.routers.metrics")

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.post("/", response_model=MetricResponse, status_code=201)
def create_metric(payload: MetricCollectorInput, db: Session = Depends(get_db)):
    """
    Store incoming metrics in TiDB.

    Accepts the raw payload from metric_collector.py, parses
    formatted speed strings into numeric KB values, and persists
    the record.
    """
    try:
        # Parse the collector timestamp string into a datetime object
        try:
            ts = datetime.strptime(payload.timestamp, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            ts = datetime.now()

        # Build the cleaned MetricCreate object
        metric_in = MetricCreate(
            timestamp=ts,
            cpu_usage=payload.cpu_usage,
            memory_usage=payload.ram_usage,
            disk_read=parse_speed_string(payload.disk_read_speed),
            disk_write=parse_speed_string(payload.disk_write_speed),
            network_rx=parse_speed_string(payload.network_download_speed),
            network_tx=parse_speed_string(payload.network_upload_speed),
        )

        db_metric = insert_metric(db, metric_in)
        logger.info("Metric stored (ID: %d)", db_metric.id)
        return db_metric

    except Exception as e:
        logger.error("Failed to store metric: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to store metric: {str(e)}")


@router.get("/", response_model=list[MetricResponse])
def read_metrics(
    limit: int = Query(default=100, ge=1, le=1000, description="Number of records to retrieve"),
    db: Session = Depends(get_db),
):
    """
    Retrieve stored metrics from TiDB, ordered by timestamp descending.
    """
    try:
        metrics = get_metrics(db, limit=limit)
        return metrics
    except Exception as e:
        logger.error("Failed to retrieve metrics: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")
