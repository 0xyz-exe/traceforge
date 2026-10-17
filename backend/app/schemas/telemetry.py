from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List

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

# Log ingestion
class LogEntry(BaseModel):
    timestamp: datetime
    severity: str = Field(pattern="^(DEBUG|INFO|WARN|ERROR|CRITICAL)$")
    message: str = Field(max_length=10000)
    trace_id: Optional[str] = Field(None, max_length=32)
    span_id: Optional[str] = Field(None, max_length=16)
    attributes: Dict[str, Any] = {}

class LogsIngest(BaseModel):
    service: str
    logs: List[LogEntry] = Field(max_length=50)

# Log query response
class LogEntryResponse(BaseModel):
    id: str
    timestamp: datetime
    severity: str
    service: str
    message: str
    trace_id: Optional[str]
    span_id: Optional[str]
    attributes: Dict[str, Any]

class LogsSearchResponse(BaseModel):
    logs: List[LogEntryResponse]
    total: int
    limit: int
    offset: int

# Trace ingestion
class SpanData(BaseModel):
    span_id: str = Field(max_length=16)
    parent_span_id: Optional[str] = Field(None, max_length=16)
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = Field(pattern="^(ok|error)$")
    attributes: Dict[str, Any] = {}
    events: List[Dict[str, Any]] = []

class TraceData(BaseModel):
    trace_id: str = Field(max_length=32)
    spans: List[SpanData] = Field(min_length=1, max_length=100)

class TracesIngest(BaseModel):
    service: str
    traces: List[TraceData] = Field(max_length=10)

# Trace query response
class SpanResponse(BaseModel):
    span_id: str
    parent_span_id: Optional[str]
    service: str
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[int]
    status: str
    attributes: Dict[str, Any]
    events: List[Dict[str, Any]]

class TraceResponse(BaseModel):
    trace_id: str
    root_service: str
    start_time: datetime
    duration_ms: Optional[int]
    status: str
    spans: List[SpanResponse]

class TracesListResponse(BaseModel):
    traces: List[Dict[str, Any]]
    total: int
    limit: int
