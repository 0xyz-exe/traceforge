from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

# Metric ingestion
class MetricPoint(BaseModel):
    name: str = Field(min_length=1)
    type: str = Field(pattern="^(counter|gauge|histogram)$")
    value: float
    timestamp: datetime
    labels: Dict[str, str] = {}

class MetricsIngest(BaseModel):
    service: str
    metrics: list[MetricPoint] = Field(max_length=100)

class IngestResponse(BaseModel):
    accepted: int
    rejected: int

# Metric query
class MetricDataPoint(BaseModel):
    timestamp: datetime
    value: float

class MetricQueryResponse(BaseModel):
    metric: str
    aggregation: str
    data_points: list[MetricDataPoint]
    unit: Optional[str] = None
