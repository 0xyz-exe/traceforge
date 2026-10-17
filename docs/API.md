# API Specification — TraceForge

**Version:** 0.1.0  
**Date:** 2026-10-17

## Base URLs

- Local development: `http://localhost:8000/api`
- Production: `https://api.traceforge.example.com/api`

## Authentication

### Dashboard (JWT)
```http
Authorization: Bearer <jwt_token>
```

### Ingestion (API Key)
```http
X-API-Key: <workspace_id>:<secret>
```

## Common Response Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `202 Accepted`: Async operation accepted
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing/invalid auth
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Schema validation failed
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid timestamp: future timestamp not allowed",
    "details": {
      "field": "timestamp",
      "value": "2027-01-01T00:00:00Z"
    }
  }
}
```

---

## Authentication Endpoints

### POST /auth/register
Create new user account.

**Request:**
```json
{
  "email": "alice@example.com",
  "password": "SecurePass123!",
  "full_name": "Alice Developer",
  "workspace_name": "My Team"
}
```

**Response: 201**
```json
{
  "user_id": "uuid",
  "workspace_id": "uuid",
  "email": "alice@example.com"
}
```

### POST /auth/login
Authenticate and get JWT.

**Request:**
```json
{
  "email": "alice@example.com",
  "password": "SecurePass123!"
}
```

**Response: 200**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### POST /auth/refresh
Refresh JWT token.

**Headers:** `Authorization: Bearer <token>`

**Response: 200**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

## Workspace Endpoints

### GET /workspaces/current
Get current workspace details.

**Headers:** `Authorization: Bearer <token>`

**Response: 200**
```json
{
  "id": "uuid",
  "name": "My Team",
  "slug": "my-team",
  "created_at": "2026-10-17T12:00:00Z"
}
```

### PATCH /workspaces/current
Update workspace settings.

**Request:**
```json
{
  "name": "New Team Name",
  "retention_days_logs": 14
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "name": "New Team Name",
  "retention_days_logs": 14
}
```

---

## Service Registry Endpoints

### GET /services
List registered services.

**Query Parameters:**
- `environment`: Filter by environment (optional)
- `limit`: Max results (default 50, max 100)
- `offset`: Pagination offset (default 0)

**Response: 200**
```json
{
  "services": [
    {
      "id": "uuid",
      "name": "api-gateway",
      "environment": "production",
      "version": "v1.2.3",
      "last_telemetry_at": "2026-10-17T13:25:00Z",
      "health_status": "healthy",
      "created_at": "2026-10-15T10:00:00Z"
    }
  ],
  "total": 10,
  "limit": 50,
  "offset": 0
}
```

### POST /services
Register new service.

**Request:**
```json
{
  "name": "user-service",
  "environment": "production",
  "version": "v2.0.0"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "name": "user-service",
  "environment": "production",
  "version": "v2.0.0"
}
```

### GET /services/:id
Get service details.

**Response: 200**
```json
{
  "id": "uuid",
  "name": "api-gateway",
  "environment": "production",
  "version": "v1.2.3",
  "last_telemetry_at": "2026-10-17T13:25:00Z",
  "health_status": "healthy",
  "metrics_summary": {
    "error_rate": 0.012,
    "request_rate": 120.5,
    "p95_latency_ms": 450
  }
}
```

---

## Telemetry Ingestion Endpoints

### POST /ingest/metrics
Ingest time-series metrics.

**Auth:** API Key

**Request:**
```json
{
  "service": "api-gateway",
  "metrics": [
    {
      "name": "http.request.duration",
      "type": "histogram",
      "value": 250,
      "timestamp": "2026-10-17T13:26:00Z",
      "labels": {
        "method": "GET",
        "status": "200"
      }
    }
  ]
}
```

**Response: 202**
```json
{
  "accepted": 1,
  "rejected": 0
}
```

**Validation:**
- Max 100 metrics per request
- Timestamp not in future
- Timestamp not > 1 year old
- Value must be finite number

### POST /ingest/logs
Ingest structured logs.

**Auth:** API Key

**Request:**
```json
{
  "service": "api-gateway",
  "logs": [
    {
      "timestamp": "2026-10-17T13:26:00Z",
      "severity": "ERROR",
      "message": "Database connection timeout",
      "trace_id": "abc123",
      "span_id": "def456",
      "attributes": {
        "db": "users",
        "timeout_ms": 5000
      }
    }
  ]
}
```

**Response: 202**
```json
{
  "accepted": 1,
  "rejected": 0
}
```

**Validation:**
- Max 50 logs per request
- Max 10KB per log entry
- Severity: DEBUG, INFO, WARN, ERROR, CRITICAL
- Sensitive fields redacted before storage

### POST /ingest/traces
Ingest distributed traces.

**Auth:** API Key

**Request:**
```json
{
  "service": "api-gateway",
  "traces": [
    {
      "trace_id": "abc123",
      "spans": [
        {
          "span_id": "span1",
          "parent_span_id": null,
          "operation_name": "GET /users",
          "start_time": "2026-10-17T13:26:00.000Z",
          "end_time": "2026-10-17T13:26:02.100Z",
          "status": "ok",
          "attributes": {
            "http.method": "GET",
            "http.url": "/users"
          }
        }
      ]
    }
  ]
}
```

**Response: 202**
```json
{
  "accepted": 1,
  "rejected": 0
}
```

**Validation:**
- Max 10 traces per request
- Max 100 spans per trace
- Valid parent-child relationships

---

## Metrics Query Endpoints

### GET /metrics/query
Query time-series metrics.

**Query Parameters:**
- `service`: Service name (required)
- `metric`: Metric name (required)
- `aggregation`: sum, avg, min, max, p50, p95, p99 (required)
- `start`: ISO timestamp (required)
- `end`: ISO timestamp (required)
- `interval`: Bucket size in seconds (optional, auto-calculated)
- `labels`: JSON filter `{"status": "200"}` (optional)

**Response: 200**
```json
{
  "metric": "http.request.duration",
  "aggregation": "p95",
  "data_points": [
    {
      "timestamp": "2026-10-17T13:20:00Z",
      "value": 450
    },
    {
      "timestamp": "2026-10-17T13:25:00Z",
      "value": 520
    }
  ],
  "unit": "ms"
}
```

### GET /metrics/services/:service_id/summary
Get service health metrics.

**Response: 200**
```json
{
  "service_id": "uuid",
  "time_range": "1h",
  "error_rate": 0.052,
  "request_rate": 120.5,
  "p50_latency_ms": 250,
  "p95_latency_ms": 450,
  "p99_latency_ms": 1200
}
```

---

## Log Query Endpoints

### GET /logs
Search logs.

**Query Parameters:**
- `service`: Service name (optional)
- `severity`: Severity level (optional)
- `start`: ISO timestamp (required)
- `end`: ISO timestamp (required)
- `search`: Text search (optional)
- `trace_id`: Filter by trace (optional)
- `limit`: Max results (default 50, max 100)
- `offset`: Pagination offset (default 0)

**Response: 200**
```json
{
  "logs": [
    {
      "id": "uuid",
      "timestamp": "2026-10-17T13:26:00Z",
      "severity": "ERROR",
      "service": "api-gateway",
      "message": "Database connection timeout",
      "trace_id": "abc123",
      "span_id": "def456",
      "attributes": {
        "db": "users"
      }
    }
  ],
  "total": 123,
  "limit": 50,
  "offset": 0
}
```

---

## Trace Query Endpoints

### GET /traces
List traces.

**Query Parameters:**
- `service`: Service name (optional)
- `status`: ok, error (optional)
- `min_duration_ms`: Minimum duration (optional)
- `start`: ISO timestamp (required)
- `end`: ISO timestamp (required)
- `limit`: Max results (default 50, max 100)

**Response: 200**
```json
{
  "traces": [
    {
      "trace_id": "abc123",
      "root_service": "api-gateway",
      "start_time": "2026-10-17T13:26:00Z",
      "duration_ms": 2100,
      "status": "ok",
      "span_count": 5
    }
  ],
  "total": 50,
  "limit": 50
}
```

### GET /traces/:trace_id
Get trace details with all spans.

**Response: 200**
```json
{
  "trace_id": "abc123",
  "root_service": "api-gateway",
  "start_time": "2026-10-17T13:26:00Z",
  "duration_ms": 2100,
  "status": "ok",
  "spans": [
    {
      "span_id": "span1",
      "parent_span_id": null,
      "service": "api-gateway",
      "operation_name": "GET /users",
      "start_time": "2026-10-17T13:26:00.000Z",
      "end_time": "2026-10-17T13:26:02.100Z",
      "duration_ms": 2100,
      "status": "ok",
      "attributes": {},
      "events": []
    }
  ]
}
```

---

## Alert Endpoints

### GET /alerts/rules
List alert rules.

**Response: 200**
```json
{
  "rules": [
    {
      "id": "uuid",
      "name": "High latency",
      "service": "api-gateway",
      "condition_type": "metric_threshold",
      "metric_name": "http.request.duration.p95",
      "threshold_value": 2000,
      "threshold_operator": ">",
      "severity": "CRITICAL",
      "is_active": true,
      "current_status": "firing"
    }
  ]
}
```

### POST /alerts/rules
Create alert rule.

**Request:**
```json
{
  "name": "High error rate",
  "service_id": "uuid",
  "condition_type": "metric_threshold",
  "metric_name": "http.error.rate",
  "threshold_value": 0.05,
  "threshold_operator": ">",
  "evaluation_interval_seconds": 60,
  "pending_period_seconds": 120,
  "severity": "WARNING"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "name": "High error rate",
  "created_at": "2026-10-17T13:26:00Z"
}
```

### GET /alerts/events
Get alert history.

**Query Parameters:**
- `status`: normal, pending, firing, resolved (optional)
- `severity`: WARNING, CRITICAL (optional)
- `limit`: Max results (default 50)

**Response: 200**
```json
{
  "events": [
    {
      "id": "uuid",
      "alert_rule_name": "High latency",
      "status": "firing",
      "severity": "CRITICAL",
      "evaluated_value": 2500,
      "started_at": "2026-10-17T13:20:00Z",
      "message": "p95 latency 2500ms exceeds threshold 2000ms"
    }
  ]
}
```

---

## Incident Endpoints

### GET /incidents
List incidents.

**Query Parameters:**
- `status`: open, resolved (optional)
- `severity`: WARNING, CRITICAL (optional)

**Response: 200**
```json
{
  "incidents": [
    {
      "id": "uuid",
      "incident_number": 42,
      "title": "Database timeout in user-service",
      "severity": "CRITICAL",
      "status": "open",
      "owner": "alice@example.com",
      "started_at": "2026-10-17T12:45:00Z"
    }
  ]
}
```

### POST /incidents
Create incident.

**Request:**
```json
{
  "title": "Database timeout in user-service",
  "severity": "CRITICAL",
  "alert_event_id": "uuid"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "incident_number": 42,
  "title": "Database timeout in user-service"
}
```

### GET /incidents/:id
Get incident details.

**Response: 200**
```json
{
  "id": "uuid",
  "incident_number": 42,
  "title": "Database timeout",
  "severity": "CRITICAL",
  "status": "open",
  "owner": "alice@example.com",
  "started_at": "2026-10-17T12:45:00Z",
  "events": [
    {
      "id": "uuid",
      "event_type": "created",
      "user": "alice@example.com",
      "content": "Incident created from alert",
      "created_at": "2026-10-17T12:45:00Z"
    }
  ],
  "linked_telemetry": {
    "traces": ["abc123"],
    "alert_events": ["uuid"]
  }
}
```

### POST /incidents/:id/events
Add timeline event.

**Request:**
```json
{
  "event_type": "note",
  "content": "Investigated DB connections, found slow query"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "event_type": "note",
  "created_at": "2026-10-17T13:00:00Z"
}
```

### POST /incidents/:id/resolve
Resolve incident.

**Request:**
```json
{
  "resolution_notes": "Fixed by optimizing query in PR #123"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "status": "resolved",
  "resolved_at": "2026-10-17T13:30:00Z"
}
```

---

## Correlation Endpoints

### GET /correlation/logs-from-metric
Get logs related to metric spike.

**Query Parameters:**
- `service`: Service name (required)
- `start`: ISO timestamp (required)
- `end`: ISO timestamp (required)

**Response:** Same as GET /logs

### GET /correlation/traces-from-log
Get trace from log entry.

**Query Parameters:**
- `log_id`: Log entry ID (required)

**Response:** Same as GET /traces/:trace_id

---

## Rate Limits

- **Ingestion:** 100 req/s per API key
- **Queries:** 60 req/min per user

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1634567890
```

**Rate Limit Exceeded:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Retry after 60 seconds.",
    "retry_after": 60
  }
}
```

---

## OpenAPI

Interactive docs available at:
- Development: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`

## SDK Support (Future)

- Python SDK: `pip install traceforge-sdk`
- Node.js SDK: `npm install @traceforge/sdk`
- Go SDK: `go get github.com/traceforge/go-sdk`
