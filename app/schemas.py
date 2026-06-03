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
