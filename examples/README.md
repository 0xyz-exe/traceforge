# TraceForge Instrumentation Examples

Example scripts for sending telemetry to TraceForge.

## Setup

1. Register a user and get workspace ID:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "yourpassword",
    "full_name": "Your Name",
    "workspace_name": "Your Workspace"
  }'
```

2. Note the `workspace_id` from response.

3. Set API key in example files:
```python
API_KEY = "YOUR_WORKSPACE_ID:secret"
```

## Python Example

```bash
pip install requests
python python_metrics.py
```

Sends metrics every 10 seconds:
- `http.requests.total` (counter)
- `app.memory.used_mb` (gauge)
- `http.request.duration` (histogram)

## Node.js Example

```bash
npm install axios
node nodejs_metrics.js
```

Sends metrics every 10 seconds:
- `http.requests.total` (counter)
- `app.cpu.percent` (gauge)
- `http.response.time` (histogram)

## Query Metrics

After sending metrics, query them via API:

```bash
curl "http://localhost:8000/api/metrics/query?service=example-python-app&metric=http.request.duration&aggregation=p95&start=2026-10-17T12:00:00Z&end=2026-10-17T13:00:00Z" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Query Logs

```bash
# Search all logs
curl "http://localhost:8000/api/logs?start=2026-10-17T12:00:00Z&end=2026-10-17T14:00:00Z" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Filter by severity
curl "http://localhost:8000/api/logs?start=2026-10-17T12:00:00Z&end=2026-10-17T14:00:00Z&severity=ERROR" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Search text
curl "http://localhost:8000/api/logs?start=2026-10-17T12:00:00Z&end=2026-10-17T14:00:00Z&search=timeout" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Query Traces

```bash
# List traces
curl "http://localhost:8000/api/traces?start=2026-10-17T12:00:00Z&end=2026-10-17T14:00:00Z" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Filter by status
curl "http://localhost:8000/api/traces?start=2026-10-17T12:00:00Z&end=2026-10-17T14:00:00Z&status=error" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get trace detail
curl "http://localhost:8000/api/traces/trace12345" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Or view in dashboard: http://localhost:3000

## OpenTelemetry Integration (Future)

TraceForge will support OpenTelemetry Protocol (OTLP) endpoints for standard instrumentation:

```python
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

exporter = OTLPMetricExporter(endpoint="http://localhost:8000/v1/metrics")
reader = PeriodicExportingMetricReader(exporter)
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

meter = metrics.get_meter("my-app")
counter = meter.create_counter("requests")
counter.add(1)
```

(OTLP support planned for Milestone C)
