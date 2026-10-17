# Architecture — TraceForge

**Version:** 0.1.0  
**Date:** 2026-10-17

## System Overview

TraceForge is a three-tier observability platform:
1. **Frontend:** Next.js dashboard (React, TypeScript)
2. **Backend:** FastAPI ingestion and query API (Python)
3. **Storage:** PostgreSQL (metadata + telemetry)

```
┌─────────────────────────────────────────────────────┐
│                   Instrumented Apps                 │
│         (OpenTelemetry SDKs or Direct HTTP)         │
└──────────────┬──────────────────────────────────────┘
               │ Logs, Metrics, Traces
               ▼
┌─────────────────────────────────────────────────────┐
│              Ingestion API (FastAPI)                │
│  • Validation  • Rate Limiting  • Auth              │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│                   Storage Layer                     │
│  • PostgreSQL (metadata, logs, traces)              │
│  • In-memory (metrics time-series, MVP)             │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│               Query API (FastAPI)                   │
│  • Metrics aggregation  • Log search  • Traces      │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│              Dashboard (Next.js)                    │
│  • Service health  • Charts  • Correlation          │
└─────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend (Next.js 14)

**Framework:** Next.js 14 App Router, React 18, TypeScript

**Structure:**
```
frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Overview dashboard
│   ├── services/
│   │   ├── page.tsx            # Service inventory
│   │   └── [id]/page.tsx       # Service detail
│   ├── metrics/page.tsx        # Metrics explorer
│   ├── logs/page.tsx           # Log search
│   ├── traces/
│   │   ├── page.tsx            # Trace list
│   │   └── [id]/page.tsx       # Trace waterfall
│   ├── alerts/
│   │   ├── rules/page.tsx      # Alert rules
│   │   └── history/page.tsx    # Alert history
│   └── incidents/
│       ├── page.tsx            # Incident list
│       └── [id]/page.tsx       # Incident timeline
├── components/
│   ├── ui/                     # shadcn/ui base components
│   ├── charts/                 # Recharts wrappers
│   ├── layout/                 # Header, Sidebar, TimeRangePicker
│   └── telemetry/              # LogEntry, TraceWaterfall, MetricChart
├── lib/
│   ├── api.ts                  # API client (axios + React Query)
│   ├── types.ts                # TypeScript types
│   └── utils.ts                # Formatters, validators
└── public/
```

**Data Fetching:**
- React Query for caching and automatic refetching
- SSR for initial page loads (metadata)
- Client-side for live telemetry updates

**State Management:**
- React Query cache for server state
- URL search params for filters (shareable links)
- Local state for UI (modals, expanded rows)

### Backend (FastAPI)

**Framework:** FastAPI, Python 3.11+, Pydantic v2

**Structure:**
```
backend/
├── app/
│   ├── main.py                 # FastAPI app, middleware, CORS
│   ├── config.py               # Environment config
│   ├── database.py             # SQLAlchemy session
│   ├── dependencies.py         # Auth, workspace injection
│   ├── models/                 # SQLAlchemy models
│   │   ├── workspace.py
│   │   ├── service.py
│   │   ├── log_entry.py
│   │   ├── trace.py
│   │   ├── span.py
│   │   ├── alert_rule.py
│   │   ├── alert_event.py
│   │   └── incident.py
│   ├── schemas/                # Pydantic request/response models
│   │   ├── telemetry.py        # Ingestion schemas
│   │   ├── query.py            # Query filters
│   │   └── alert.py            # Alert models
│   ├── routes/
│   │   ├── auth.py             # Login, register, token
│   │   ├── workspaces.py       # Workspace CRUD
│   │   ├── services.py         # Service registry
│   │   ├── ingest.py           # Telemetry ingestion
│   │   ├── metrics.py          # Metrics queries
│   │   ├── logs.py             # Log search
│   │   ├── traces.py           # Trace queries
│   │   ├── alerts.py           # Alert rules and history
│   │   └── incidents.py        # Incident management
│   ├── services/               # Business logic
│   │   ├── metrics_store.py    # In-memory time-series
│   │   ├── log_service.py      # Log filtering
│   │   ├── trace_service.py    # Trace assembly
│   │   ├── alert_engine.py     # Alert evaluation
│   │   └── correlation.py      # Cross-telemetry links
│   └── utils/
│       ├── validation.py       # Input validators
│       ├── redaction.py        # Sensitive field masking
│       └── retention.py        # Cleanup jobs
├── alembic/                    # Database migrations
│   └── versions/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── requirements.txt
```

**Middleware:**
- CORS (configurable origins)
- Request logging (excluding sensitive headers)
- Exception handlers (never leak internal errors)
- Rate limiting (per workspace API key)

**Authentication:**
- JWT for dashboard users (HS256, 24h expiry)
- API keys for telemetry ingestion (workspace-scoped)
- No cross-workspace access

### Storage Layer

#### PostgreSQL Schema

**Metadata Tables:**
- `workspaces`: Tenant isolation
- `users`: Dashboard accounts
- `services`: Registered services
- `api_keys`: Ingestion credentials

**Telemetry Tables:**
- `log_entries`: Structured logs (JSONB)
- `traces`: Trace metadata
- `spans`: Individual spans (parent-child via `parent_span_id`)
- `alert_rules`: Alert definitions
- `alert_events`: Fired alerts
- `incidents`: Tracked incidents
- `incident_events`: Timeline entries

**Indexes:**
- `log_entries`: GIN on JSONB, B-tree on (workspace_id, timestamp)
- `spans`: B-tree on (trace_id, parent_span_id, timestamp)
- `alert_events`: B-tree on (workspace_id, created_at, status)

#### In-Memory Metrics Store (MVP)

**Structure:**
```python
{
    "workspace_id:service_name:metric_name:label_hash": [
        (timestamp, value),
        (timestamp, value),
        ...
    ]
}
```

**Retention:** 7 days in-memory (circular buffer)

**Limitations:**
- Lost on restart (document this clearly)
- Single-instance only
- No persistence

**Future:** Replace with Prometheus remote-write or PostgreSQL time-series extension

### Telemetry Pipeline

#### Ingestion Flow
```
1. HTTP POST /api/ingest/logs
2. Validate API key → workspace_id
3. Validate payload schema (Pydantic)
4. Check rate limits
5. Redact sensitive fields
6. Insert into PostgreSQL (logs) or memory (metrics)
7. Return 202 Accepted
```

#### Query Flow
```
1. HTTP GET /api/metrics?service=X&metric=Y&range=1h
2. Validate JWT → user → workspace_id
3. Query metrics store (filtered by workspace)
4. Aggregate (p95, sum, avg)
5. Return time-series JSON
```

#### Correlation Flow
```
1. User clicks "View Related Logs" from metric spike
2. Frontend sends GET /api/logs?service=X&start=T1&end=T2
3. Backend queries log_entries with time window
4. Returns logs with trace_id links
5. User clicks trace_id
6. Frontend fetches GET /api/traces/{trace_id}
7. Backend queries spans, assembles hierarchy
8. Returns waterfall data
```

## Data Flow Diagrams

### Metric Ingestion
```
App → [POST /ingest/metrics] → Validate → Rate Limit → Store in-memory → 202 Accepted
```

### Log Ingestion
```
App → [POST /ingest/logs] → Validate → Redact → Insert PostgreSQL → 202 Accepted
                                                    └─ Extract trace_id for correlation
```

### Trace Ingestion
```
App → [POST /ingest/traces] → Validate → Parse spans → Insert PostgreSQL → 202 Accepted
                                            └─ Build parent-child links
```

### Alert Evaluation
```
Background Job (every 1 minute):
  1. Fetch active alert_rules
  2. For each rule:
     - Query metrics or logs
     - Evaluate condition
     - Update alert_event state (normal → pending → firing → resolved)
     - Store transition in alert_events table
  3. Sleep until next interval
```

## Security Architecture

### Authentication Layers
1. **Dashboard:** JWT (HTTP-only cookie or Bearer token)
2. **Ingestion:** API key (Header: `X-API-Key: workspace_id:secret`)
3. **Admin:** Superuser flag (workspace management)

### Authorization Model
- All queries filtered by `workspace_id`
- API keys scoped to workspace
- Users belong to one workspace
- No cross-workspace reads

### Input Validation
- Payload size: 1MB max
- Rate limits: 100 req/s per API key
- Timestamp validation: not in future, not > 1 year old
- Metric cardinality: max 1000 unique series per workspace

### Redaction
Default patterns (case-insensitive):
- `password`, `passwd`, `pwd`
- `token`, `api_key`, `apikey`
- `secret`, `auth`, `authorization`
- `credit_card`, `ssn`

Applied:
- Before storage
- Before AI requests
- In query responses

### Threat Mitigations
- SQL injection: Parameterized queries (SQLAlchemy)
- XSS: React auto-escapes, JSONB display sanitized
- CSRF: SameSite cookies + CORS
- SSRF: Webhook URLs validated (no localhost, private IPs)
- DoS: Rate limiting, payload limits, query timeouts
- Prompt injection: Treat logs as untrusted, validate AI responses

## Scalability Considerations

### MVP Scale Targets
- Services: 10
- Requests: 100 req/s ingestion
- Logs: 100k/day
- Metrics: 100 series @ 1/min
- Traces: 10k/day
- Users: 10

### Single-Instance Limitations
- In-memory metrics: ~500MB RAM for 7d @ 100 series
- PostgreSQL: ~1GB for 7d telemetry
- No horizontal scaling
- No load balancing

### Future Scaling Paths
1. **Metrics:** Prometheus remote storage or TimescaleDB
2. **Logs:** Elasticsearch or ClickHouse
3. **Traces:** Jaeger or Tempo
4. **Read replicas:** PostgreSQL replication
5. **Ingestion queue:** Redis Streams or Kafka

## Operational Architecture

### Health Endpoints
- `GET /health` → `{"status": "ok"}`
- `GET /health/db` → Database connectivity
- `GET /health/metrics` → In-memory store status

### Observability (Self-Monitoring)
- Backend logs to stdout (JSON)
- Request duration metrics (logged)
- Error rate tracking
- No external telemetry for MVP

### Deployment (MVP)

**Docker Compose:**
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: traceforge
      POSTGRES_USER: traceforge
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pg_data:/var/lib/postgresql/data
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://traceforge:${DB_PASSWORD}@postgres/traceforge
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - postgres
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api
```

**Native:**
1. Install PostgreSQL
2. Run Alembic migrations
3. Start backend: `uvicorn app.main:app --reload`
4. Start frontend: `npm run dev`

### Background Jobs

**Alert Evaluation:**
- Scheduler: APScheduler
- Interval: 1 minute
- Idempotency: Track last evaluation timestamp

**Retention Cleanup:**
- Scheduler: APScheduler
- Interval: Daily at 2 AM UTC
- Delete: `WHERE timestamp < NOW() - INTERVAL '7 days'`

**Stale Service Detection:**
- On-demand (query time)
- Logic: `last_telemetry_at < NOW() - INTERVAL '5 minutes'`

## Technology Choices Rationale

### Why FastAPI?
- Automatic OpenAPI docs
- Pydantic validation
- Async support (future streaming)
- Type hints
- Fast iteration

### Why Next.js?
- SSR for SEO and initial load
- App Router for modern patterns
- TypeScript first-class
- React ecosystem

### Why PostgreSQL for Everything?
- JSONB for flexible log storage
- GIN indexes for fast JSONB queries
- Recursive CTEs for span hierarchy
- Simplicity (one database)
- Acceptable performance for MVP scale

### Why In-Memory Metrics?
- Fast queries (no disk I/O)
- Simple implementation
- Acceptable data loss for MVP
- Easy to replace later

## Future Enhancements

### Phase 2 (Post-MVP)
- Persistent metrics (Prometheus or TimescaleDB)
- Service dependency map from traces
- Custom dashboards
- Deployment annotations
- Error grouping

### Phase 3
- Horizontal scaling (read replicas)
- Streaming ingestion (Kafka)
- Long-term storage (S3 + Parquet)
- Multi-workspace RBAC
- SSO (OAuth2)

## Open Questions

1. **Metrics storage:** Stick with in-memory or add PostgreSQL fallback for MVP?
   - **Decision:** In-memory for MVP, document clearly
2. **Alert notifications:** Local only or add webhook support in MVP?
   - **Decision:** Alert history only, webhooks in P1
3. **Trace sampling:** Store all traces or add sampling in MVP?
   - **Decision:** Store all for MVP, add sampling in P1

## References

- OpenTelemetry Protocol: https://opentelemetry.io/docs/specs/otlp/
- PostgreSQL JSONB: https://www.postgresql.org/docs/current/datatype-json.html
- FastAPI: https://fastapi.tiangolo.com/
- Next.js: https://nextjs.org/docs
