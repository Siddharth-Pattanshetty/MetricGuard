import os
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from backend.schemas import (
    ReportGenerateRequest,
    ReportGenerateResponse,
    ReportMetadataResponse,
)
from backend.report_generator.report_generator import get_report_generator
from backend.report_generator.report_storage import get_report_storage

logger = logging.getLogger("metricguard.routers.reports")

router = APIRouter(prefix="/reports", tags=["Reports"])

_generator = get_report_generator()
_storage = get_report_storage()


# ==========================================================
# POST /reports/generate
# ==========================================================
@router.post("/generate", response_model=ReportGenerateResponse, status_code=201)
def generate_report(payload: ReportGenerateRequest, db: Session = Depends(get_db)):
    """
    Trigger report payload aggregation and generate selected export formats (PDF/CSV).
    """
    try:
        logger.info(
            "[Reports API] Generating report for incident_id=%s, formats=%s",
            payload.incident_id,
            payload.formats,
        )
        res = _generator.generate_incident_report(
            db=db,
            incident_id=payload.incident_id,
            formats=payload.formats,
        )
        return res
    except ValueError as ve:
        logger.warning("[Reports API] Incident validation error: %s", ve)
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error("[Reports API] Report generation failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}",
        )


# ==========================================================
# GET /reports/
# ==========================================================
@router.get("/", response_model=List[ReportMetadataResponse])
def list_reports():
    """
    Retrieve history of all generated report metadata.
    """
    try:
        reports = _storage.get_all_reports()
        logger.info("[Reports API] Returning %d historical reports", len(reports))
        return reports
    except Exception as e:
        logger.error("[Reports API] Failed to retrieve report list: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve report list: {str(e)}",
        )


# ==========================================================
# GET /reports/{report_id}
# ==========================================================
@router.get("/{report_id}", response_model=ReportMetadataResponse)
def get_report_details(report_id: str):
    """
    Retrieve metadata for a specific generated report.
    """
    metadata = _storage.get_metadata(report_id)
    if metadata is None:
        logger.warning("[Reports API] Report not found: %s", report_id)
        raise HTTPException(
            status_code=404,
            detail=f"Report '{report_id}' not found.",
        )
    return metadata


# ==========================================================
# GET /reports/download/{report_id}
# ==========================================================
@router.get("/download/{report_id}")
def download_report(report_id: str, format: str = Query(..., description="Export format to download ('pdf' or 'csv')")):
    """
    Download the generated export file (PDF or CSV) for a report.
    """
    metadata = _storage.get_metadata(report_id)
    if metadata is None:
        logger.warning("[Reports API] Report not found for download: %s", report_id)
        raise HTTPException(
            status_code=404,
            detail=f"Report '{report_id}' not found.",
        )

    fmt = format.lower().strip()
    if fmt == "pdf":
        file_path = metadata.get("pdf_path")
        media_type = "application/pdf"
    elif fmt == "csv":
        file_path = metadata.get("csv_path")
        media_type = "text/csv"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format '{format}'. Supported formats are 'pdf' and 'csv'.",
        )

    if not file_path or not os.path.exists(file_path):
        logger.warning("[Reports API] File for format %s not found on disk: %s", fmt, file_path)
        raise HTTPException(
            status_code=404,
            detail=f"Requested {fmt.upper()} file for report '{report_id}' is not available.",
        )

    filename = os.path.basename(file_path)
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
