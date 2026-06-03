from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# ==========================================
# METRICS SCHEMAS
# ==========================================

class MetricBase(BaseModel):
    timestamp: datetime
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_read: Optional[float] = None
    disk_write: Optional[float] = None
    network_rx: Optional[float] = None
    network_tx: Optional[float] = None

class MetricCreate(MetricBase):
    pass

class MetricCollectorInput(BaseModel):
    """
    Accepts the raw payload from metric_collector.py.
    Speed fields arrive as formatted strings (e.g. '4.39 MB').
    The router will parse these into float KB before storing.
    """
    timestamp: str
    cpu_usage: Optional[float] = None
    ram_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    disk_read_speed: Optional[str] = None
    disk_write_speed: Optional[str] = None
    network_upload_speed: Optional[str] = None
    network_download_speed: Optional[str] = None
    process_count: Optional[int] = None
    system_load: Optional[float] = None
    system_uptime: Optional[str] = None

class MetricResponse(MetricBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ANOMALY SCHEMAS
# ==========================================

class AnomalyBase(BaseModel):
    timestamp: datetime
    anomaly_score: float
    root_cause: Optional[str] = None
    severity: str
    detected_by: str

class AnomalyCreate(AnomalyBase):
    pass

class AnomalyResponse(AnomalyBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
