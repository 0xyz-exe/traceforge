# Milestone C Complete — Logs and Traces

**Date:** 2026-10-17  
**Status:** Complete

## Summary

Built structured log and distributed trace ingestion, storage, and query system with PostgreSQL.

## Deliverables

### Backend API Endpoints

✅ **Ingestion**
- POST /api/ingest/logs
  - Max 50 logs per request
  - Max 10KB per log message
  - Stores in PostgreSQL JSONB
  - Links trace_id for correlation
  
- POST /api/ingest/traces
  - Max 10 traces per request
  - Max 100 spans per trace
  - Validates parent-child relationships
  - Calculates trace duration and status

✅ **Query**
- GET /api/logs
  - Filter: service, severity, time range, text search, trace_id
  - Pagination (default 50, max 100)
  - Returns with service names resolved
  
- GET /api/traces
  - Filter: service, status, min_duration, time range
  - Pagination
  - Returns trace list with span counts
  
- GET /api/traces/:trace_id
  - Full trace with all spans
  - Span hierarchy via parent_span_id
  - Service names resolved

### Database

✅ **Migration 002**
- `log_entries` table with JSONB attributes
- `traces` table with duration/status
- `spans` table with parent-child links
- Indexes: timestamp, trace_id, GIN on JSONB
- Workspace isolation via FK

✅ **Models**
- LogEntry: timestamp, severity, message, trace_id, attributes
- Trace: trace_id, start/end time, duration_ms, status
- Span: span_id, parent_span_id, operation, duration, status, events

### Schemas

✅ **Pydantic Models**
- LogEntry, LogsIngest
- SpanData, TraceData, TracesIngest
- LogEntryResponse, LogsSearchResponse
- SpanResponse, TraceResponse, TracesListResponse

## Technical Details

### Log Storage
- PostgreSQL TEXT for message (max 10KB)
- JSONB for attributes with GIN index
- B-tree composite index on (workspace_id, timestamp)
- Supports ILIKE search on message

### Trace Storage
- Trace metadata separate from spans
- Duration calculated: max(span.end_time) - min(span.start_time)
- Status aggregated: "error" if any span has error
- Unique constraint on (trace_id, span_id)

### Correlation
- trace_id links logs to traces
- span_id identifies specific operation
- Query logs by trace_id for related entries
- Navigate from log → trace via UI (frontend next)

## Verification

### Manual Testing

```bash
# 1. Send logs
curl -X POST http://localhost:8000/api/ingest/logs \
  -H "X-API-Key: <workspace_id>:secret" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "api-gateway",
    "logs": [{
      "timestamp": "2026-10-17T13:30:00Z",
      "severity": "ERROR",
      "message": "Database connection timeout",
      "trace_id": "abc123",
      "attributes": {"db": "users", "timeout_ms": 5000}
    }]
  }'

# 2. Search logs
curl "http://localhost:8000/api/logs?start=2026-10-17T13:00:00Z&end=2026-10-17T14:00:00Z&severity=ERROR" \
  -H "Authorization: Bearer <jwt>"

# 3. Send trace
curl -X POST http://localhost:8000/api/ingest/traces \
  -H "X-API-Key: <workspace_id>:secret" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "api-gateway",
    "traces": [{
      "trace_id": "abc123",
      "spans": [
        {
          "span_id": "span1",
          "parent_span_id": null,
          "operation_name": "GET /users",
          "start_time": "2026-10-17T13:30:00.000Z",
          "end_time": "2026-10-17T13:30:02.100Z",
          "status": "ok",
          "attributes": {"http.method": "GET"}
        }
      ]
    }]
  }'

# 4. Get trace
curl "http://localhost:8000/api/traces/abc123" \
  -H "Authorization: Bearer <jwt>"
```

### Database Verification

```sql
-- Check tables created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Verify log storage
SELECT id, timestamp, severity, message, trace_id 
FROM log_entries 
LIMIT 5;

-- Verify trace/span relationship
SELECT t.trace_id, t.duration_ms, COUNT(s.id) as span_count
FROM traces t
LEFT JOIN spans s ON t.trace_id = s.trace_id
GROUP BY t.trace_id, t.duration_ms;
```

## Acceptance Criteria

✅ Logs can be ingested with trace_id  
✅ Logs can be searched by service, time, severity  
✅ Traces can be ingested with parent-child spans  
✅ Trace waterfall data available via API  
✅ Log → trace link works when trace_id present  

## Known Limitations

1. **No redaction yet**  
   Sensitive fields stored as-is. Add redaction middleware in Milestone E.

2. **Text search is basic**  
   Uses ILIKE, not full-text. Good enough for MVP.

3. **No span ordering in response**  
   Frontend needs to build tree from parent_span_id.

4. **No automatic service detection from spans**  
   All spans inherit root service. Multi-service traces need enhancement.

## Git History

```
c2c60dc feat: log and trace query endpoints
0737cd8 feat: log and trace ingestion with PostgreSQL storage
```

## Metrics

- **API endpoints added:** 5 (2 ingestion, 3 query)
- **Database tables:** 3 (log_entries, traces, spans)
- **Models:** 3
- **Schemas:** 12
- **Lines of code added:** ~450

## Next: Frontend (Logs & Traces Pages)

Priorities:
1. Log search page with filters
2. Trace list page
3. Trace waterfall visualization (Recharts timeline)
4. Log → trace link (clickable trace_id)
5. Service detail: link to logs/traces

Estimated: 2-3 hours
