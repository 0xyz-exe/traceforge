# Database Design — TraceForge

**Version:** 0.1.0  
**Date:** 2026-10-17

## Schema Overview

PostgreSQL 15+ with JSONB for flexible telemetry storage.

### Entity Relationships
```
workspaces (1) ──< (N) users
workspaces (1) ──< (N) services
workspaces (1) ──< (N) log_entries
workspaces (1) ──< (N) traces
traces (1) ──< (N) spans
workspaces (1) ──< (N) alert_rules
alert_rules (1) ──< (N) alert_events
workspaces (1) ──< (N) incidents
incidents (1) ──< (N) incident_events
```

## Tables

### `workspaces`
Tenant isolation.

```sql
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_workspaces_slug ON workspaces(slug);
```

### `users`
Dashboard authentication.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_workspace ON users(workspace_id);
CREATE INDEX idx_users_email ON users(email);
```

### `api_keys`
Ingestion authentication.

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_api_keys_workspace ON api_keys(workspace_id);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
```

**Note:** Store bcrypt hash of key, not plaintext.

### `services`
Registered services.

```sql
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    environment VARCHAR(100) DEFAULT 'production',
    version VARCHAR(100),
    last_telemetry_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(workspace_id, name, environment)
);

CREATE INDEX idx_services_workspace ON services(workspace_id);
CREATE INDEX idx_services_last_telemetry ON services(last_telemetry_at);
```

**Health Logic:**
- Stale: `last_telemetry_at < NOW() - INTERVAL '5 minutes'`
- Down: `last_telemetry_at < NOW() - INTERVAL '1 hour'`

### `log_entries`
Structured logs.

```sql
CREATE TABLE log_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id) ON DELETE SET NULL,
    timestamp TIMESTAMP NOT NULL,
    severity VARCHAR(20) NOT NULL, -- DEBUG, INFO, WARN, ERROR, CRITICAL
    message TEXT NOT NULL,
    trace_id VARCHAR(32), -- Hex trace ID for correlation
    span_id VARCHAR(16),  -- Hex span ID
    attributes JSONB,     -- Flexible structured data
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_logs_workspace_time ON log_entries(workspace_id, timestamp DESC);
CREATE INDEX idx_logs_service ON log_entries(service_id);
CREATE INDEX idx_logs_severity ON log_entries(severity);
CREATE INDEX idx_logs_trace ON log_entries(trace_id) WHERE trace_id IS NOT NULL;
CREATE INDEX idx_logs_attributes_gin ON log_entries USING GIN(attributes);
```

**Attributes Example:**
```json
{
  "user_id": "12345",
  "request_id": "abc-def",
  "db_query_ms": 250,
  "error_code": "CONN_TIMEOUT"
}
```

### `traces`
Trace metadata.

```sql
CREATE TABLE traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    trace_id VARCHAR(32) UNIQUE NOT NULL, -- Hex trace ID
    root_service_id UUID REFERENCES services(id) ON DELETE SET NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_ms INTEGER, -- Calculated: end_time - start_time
    status VARCHAR(20),  -- ok, error
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_traces_workspace_time ON traces(workspace_id, start_time DESC);
CREATE INDEX idx_traces_trace_id ON traces(trace_id);
CREATE INDEX idx_traces_status ON traces(status);
CREATE INDEX idx_traces_duration ON traces(duration_ms);
```

### `spans`
Individual operations within traces.

```sql
CREATE TABLE spans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    trace_id VARCHAR(32) NOT NULL,
    span_id VARCHAR(16) NOT NULL,
    parent_span_id VARCHAR(16), -- NULL for root span
    service_id UUID REFERENCES services(id) ON DELETE SET NULL,
    operation_name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_ms INTEGER,
    status VARCHAR(20), -- ok, error
    attributes JSONB,
    events JSONB, -- Array of span events (e.g., exceptions)
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(trace_id, span_id)
);

CREATE INDEX idx_spans_trace ON spans(trace_id);
CREATE INDEX idx_spans_parent ON spans(parent_span_id) WHERE parent_span_id IS NOT NULL;
CREATE INDEX idx_spans_workspace_time ON spans(workspace_id, start_time DESC);
CREATE INDEX idx_spans_service ON spans(service_id);
CREATE INDEX idx_spans_duration ON spans(duration_ms);
```

**Attributes Example:**
```json
{
  "http.method": "GET",
  "http.url": "/api/users/123",
  "http.status_code": 200,
  "db.system": "postgresql",
  "db.statement": "SELECT * FROM users WHERE id = $1"
}
```

**Events Example:**
```json
[
  {
    "timestamp": "2026-10-17T12:45:32Z",
    "name": "exception",
    "attributes": {
      "exception.type": "QueryTimeout",
      "exception.message": "Query exceeded 5s timeout"
    }
  }
]
```

### `alert_rules`
Alert definitions.

```sql
CREATE TABLE alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    service_id UUID REFERENCES services(id) ON DELETE CASCADE,
    condition_type VARCHAR(50) NOT NULL, -- metric_threshold, error_rate, missing_data
    metric_name VARCHAR(255),
    threshold_value FLOAT,
    threshold_operator VARCHAR(10), -- >, <, >=, <=, ==
    evaluation_interval_seconds INTEGER DEFAULT 60,
    pending_period_seconds INTEGER DEFAULT 120,
    severity VARCHAR(20) NOT NULL, -- WARNING, CRITICAL
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alert_rules_workspace ON alert_rules(workspace_id);
CREATE INDEX idx_alert_rules_active ON alert_rules(is_active) WHERE is_active = TRUE;
```

### `alert_events`
Alert state transitions.

```sql
CREATE TABLE alert_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    alert_rule_id UUID NOT NULL REFERENCES alert_rules(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL, -- normal, pending, firing, resolved
    evaluated_value FLOAT,
    message TEXT,
    started_at TIMESTAMP,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alert_events_workspace ON alert_events(workspace_id);
CREATE INDEX idx_alert_events_rule ON alert_events(alert_rule_id);
CREATE INDEX idx_alert_events_status ON alert_events(status);
CREATE INDEX idx_alert_events_created ON alert_events(created_at DESC);
```

**State Machine:**
```
normal → pending → firing → resolved
         ↑                  ↓
         └──────────────────┘
```

### `incidents`
Tracked issues.

```sql
CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    incident_number INTEGER NOT NULL, -- Auto-increment per workspace
    title VARCHAR(255) NOT NULL,
    severity VARCHAR(20) NOT NULL, -- WARNING, CRITICAL
    status VARCHAR(20) DEFAULT 'open', -- open, resolved
    owner_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    resolution_notes TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(workspace_id, incident_number)
);

CREATE INDEX idx_incidents_workspace ON incidents(workspace_id);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_owner ON incidents(owner_user_id);
```

**Incident Number:** Auto-increment within workspace (e.g., #1, #2, #3).

### `incident_events`
Incident timeline.

```sql
CREATE TABLE incident_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- created, note, linked_trace, linked_alert, resolved
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    content TEXT,
    metadata JSONB, -- Flexible: trace_id, alert_id, etc.
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_incident_events_incident ON incident_events(incident_id);
CREATE INDEX idx_incident_events_created ON incident_events(created_at);
```

**Metadata Examples:**
```json
{"trace_id": "abc123"}
{"alert_id": "uuid-here"}
{"log_entry_id": "uuid-here"}
```

## Indexes Strategy

### Query Patterns
1. **Service health:** `SELECT * FROM services WHERE workspace_id = ? ORDER BY last_telemetry_at DESC`
2. **Log search:** `SELECT * FROM log_entries WHERE workspace_id = ? AND timestamp BETWEEN ? AND ? AND severity = ? ORDER BY timestamp DESC LIMIT 50`
3. **Trace lookup:** `SELECT * FROM spans WHERE trace_id = ? ORDER BY start_time`
4. **Alert history:** `SELECT * FROM alert_events WHERE workspace_id = ? ORDER BY created_at DESC LIMIT 50`
5. **Incident timeline:** `SELECT * FROM incident_events WHERE incident_id = ? ORDER BY created_at`

### Index Coverage
- All workspace filters: composite index starting with `workspace_id`
- Time-series queries: composite index `(workspace_id, timestamp DESC)`
- Trace correlation: unique index on `trace_id`, index on `span_id`
- JSONB attributes: GIN index for flexible queries

## Retention Policy

### Cleanup Query (Daily Job)
```sql
-- Delete old logs
DELETE FROM log_entries 
WHERE workspace_id = ? 
  AND timestamp < NOW() - INTERVAL '7 days';

-- Delete old traces and spans
DELETE FROM traces 
WHERE workspace_id = ? 
  AND start_time < NOW() - INTERVAL '7 days';
-- Spans cascade via foreign key

-- Delete old alert events (keep last 30 days)
DELETE FROM alert_events 
WHERE workspace_id = ? 
  AND created_at < NOW() - INTERVAL '30 days';
```

### Workspace-Level Configuration (Future)
```sql
ALTER TABLE workspaces 
ADD COLUMN retention_days_logs INTEGER DEFAULT 7,
ADD COLUMN retention_days_traces INTEGER DEFAULT 7,
ADD COLUMN retention_days_metrics INTEGER DEFAULT 7;
```

## Data Volume Estimates

### Per Day (10 Services)
- Log entries: 100,000 × ~1KB = 100MB
- Spans: 100,000 × ~500B = 50MB
- Traces: 10,000 × ~200B = 2MB
- Alert events: ~100 × ~500B = 50KB
- Total: ~150MB/day

### 7-Day Retention
- Logs: 700MB
- Spans: 350MB
- Traces: 14MB
- Total: ~1GB

### 1-Year Projection (with retention)
- Storage remains ~1GB (old data deleted)
- Write throughput: ~150MB/day
- Read patterns: Recent data (last 24h) 90% of queries

## Migrations

### Alembic Setup
```python
# alembic/env.py
from app.models import Base
target_metadata = Base.metadata
```

### Migration Example
```python
# alembic/versions/001_initial_schema.py
def upgrade():
    op.create_table('workspaces', ...)
    op.create_table('users', ...)
    # ... all tables

def downgrade():
    op.drop_table('users')
    op.drop_table('workspaces')
```

## Schema Evolution

### Backward-Compatible Changes
- Add nullable columns
- Add indexes
- Add tables (no foreign key dependencies)

### Breaking Changes (Require Migration)
- Rename columns
- Change column types
- Add NOT NULL constraints
- Change foreign key relationships

## Performance Considerations

### Query Optimization
- Limit result sets (default 50, max 1000)
- Use covering indexes where possible
- Avoid `SELECT *` in hot paths
- Paginate with cursor-based pagination (timestamp + id)

### Write Optimization
- Batch inserts for spans (insert trace + all spans in transaction)
- Use prepared statements
- Connection pooling (SQLAlchemy default: 5-20 connections)

### JSONB Queries
```sql
-- Fast (uses GIN index)
SELECT * FROM log_entries WHERE attributes @> '{"error_code": "TIMEOUT"}';

-- Slow (no index, full scan)
SELECT * FROM log_entries WHERE attributes->>'user_id' = '12345';
```

**Recommendation:** Index frequently queried JSONB paths with expression indexes:
```sql
CREATE INDEX idx_logs_user_id ON log_entries((attributes->>'user_id'));
```

## Backup and Recovery

### Backup Strategy (Production)
1. Daily full backup: `pg_dump traceforge > backup.sql`
2. WAL archiving for point-in-time recovery
3. Store backups off-site (S3 or equivalent)

### Restore
```bash
psql traceforge < backup.sql
```

### MVP (Development)
- Manual backups only
- Document backup commands in README

## Security Considerations

### Row-Level Security (Future)
```sql
ALTER TABLE log_entries ENABLE ROW LEVEL SECURITY;

CREATE POLICY workspace_isolation ON log_entries
    USING (workspace_id = current_setting('app.current_workspace_id')::uuid);
```

**MVP:** Application-level filtering (all queries include `WHERE workspace_id = ?`)

### Sensitive Data
- Passwords: bcrypt hash
- API keys: bcrypt hash
- Redaction: Applied before storage

### SQL Injection
- Use parameterized queries (SQLAlchemy ORM)
- Never interpolate user input into raw SQL

## Testing Data

### Seed Script
```python
# scripts/seed.py
def seed_demo_data():
    workspace = Workspace(name="Demo", slug="demo")
    service = Service(name="api-gateway", environment="production")
    log = LogEntry(
        service_id=service.id,
        timestamp=datetime.utcnow(),
        severity="INFO",
        message="Request handled",
        attributes={"status": 200}
    )
    db.add_all([workspace, service, log])
    db.commit()
```

### Fixture Data (Tests)
- Use SQLAlchemy factories (factory_boy)
- Separate test database
- Rollback after each test

## Appendix: SQL Scripts

### Create Database
```sql
CREATE DATABASE traceforge;
CREATE USER traceforge WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE traceforge TO traceforge;
```

### Enable Extensions
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search
```

### Check Table Sizes
```sql
SELECT 
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

### Vacuum and Analyze
```sql
VACUUM ANALYZE log_entries;
VACUUM ANALYZE spans;
```

Run weekly to reclaim space and update statistics.
