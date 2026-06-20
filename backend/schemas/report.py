from pydantic import BaseModel, Field
from typing import List

class ReportGenerateRequest(BaseModel):
    """Payload schema for generating a new incident report."""
    incident_id: str = Field(..., description="The ID of the incident, e.g. INC-000001")
    formats: List[str] = Field(default=["pdf", "csv"], description="The export formats desired")

class ReportGenerateResponse(BaseModel):
    """Response returned after report generation finishes."""
    status: str = Field(..., description="Generation status (e.g. 'success')")
    report_id: str = Field(..., description="The unique report ID, e.g. REP-000001")
    files: List[str] = Field(..., description="List of generated file basenames")

class ReportMetadataResponse(BaseModel):
    """Metadata schema representing a generated report."""
    report_id: str = Field(..., description="The unique report ID")
    incident_id: str = Field(..., description="The associated incident ID")
    created_at: str = Field(..., description="ISO timestamp of report creation")
    available_formats: List[str] = Field(..., description="Export formats available (e.g. ['pdf', 'csv'])")
    pdf_path: str = Field(..., description="Absolute path to the PDF export file")
    csv_path: str = Field(..., description="Absolute path to the CSV export file")
