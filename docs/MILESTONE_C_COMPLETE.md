# Milestone C Complete — Logs and Traces (Full Stack)

**Date:** 2026-10-17  
**Status:** Complete ✅

## Summary

Built complete structured logging and distributed tracing system with PostgreSQL storage, REST API, and React frontend with waterfall visualization.

## Deliverables

### Backend (5 endpoints)

✅ **POST /api/ingest/logs**
- Accepts 50 logs per request
- Max 10KB message length
- JSONB attributes storage
- trace_id/span_id for correlation

✅ **POST /api/ingest/traces**
- Accepts 10 traces per request
- Max 100 spans per trace
- Parent-child span relationships
- Auto-calculates trace duration and status

✅ **GET /api/logs**
- Filter: service, severity, time, text search, trace_id
- Pagination (50 default, 100 max)
- ILIKE text search on message
- Service name resolution

✅ **GET /api/traces**
- Filter: service, status, min_duration, time
- Pagination
- Returns trace list with span counts

✅ **GET /api/traces/:trace_id**
- Full trace with all spans
- Span hierarchy preserved
- Service names resolved

### Database (Migration 002)

✅ **Tables**
- `log_entries`: timestamp, severity, message, trace_id, span_id, JSONB attributes
- `traces`: trace_id (unique), duration_ms, status, root_service_id
- `spans`: span_id, parent_span_id, operation_name, duration_ms, status, events

✅ **Indexes**
- B-tree composite: (workspace_id, timestamp)
- B-tree: trace_id, span_id, service_id
- GIN: JSONB attributes for log search
- Unique constraint: (trace_id, span_id)

✅ **Models**
- LogEntry with JSONB
- Trace with calculated fields
- Span with parent-child FK

### Frontend (3 pages)

✅ **/logs**
- Severity filter (DEBUG/INFO/WARN/ERROR/CRITICAL)
- Text search on messages
- Color-coded severity badges
- Clickable trace_id → trace detail
- Expandable attributes viewer
- Last 1 hour default range

✅ **/traces**
- Status filter (OK/Error)
- Trace list table
- Shows: trace_id, service, duration, span count
- Click trace_id → detail page

✅ **/traces/:id**
- Trace metadata card
- Span waterfall visualization
- Hierarchical rendering (indentation)
- Timeline bars positioned by start/duration
- Color-coded status (blue=ok, red=error)
- Parent-child relationships preserved

### Example Scripts

✅ **python_logs.py**
- Sends structured logs every 10s
- Random severity and messages
- 30% of logs include trace_id
- Sample attributes

✅ **python_traces.py**
- Sends distributed traces every 15s
- 3-span hierarchy (API → DB → Cache)
- Realistic durations
- Parent-child relationships

## Technical Implementation

### Correlation Strategy

**Log → Trace:**
```
Log.trace_id = Trace.trace_id
→ Click trace_id in log viewer
→ Navigate to /traces/:trace_id
→ See full waterfall
```

**Trace → Logs:**
```
Query logs WHERE trace_id = :trace_id
→ Filter logs by trace_id
→ See all logs for that request
```

### Waterfall Algorithm

1. Build span map: `Map<span_id, Span & { children }>`
2. Link children to parents via `parent_span_id`
3. Collect root spans (parent_span_id = null)
4. Recursive render with depth tracking
5. Calculate bar position: `(span_start - trace_start) / trace_duration * 100%`
6. Calculate bar width: `span_duration / trace_duration * 100%`

### Storage Characteristics

- **Log message**: TEXT, truncated to 10KB
- **Attributes**: JSONB with GIN index for fast search
- **Timestamps**: timestamptz for correct timezone handling
- **Workspace isolation**: All queries filtered by workspace_id
- **Cascade deletes**: Spans/logs deleted when workspace deleted

## Verification

### Backend Tests (Manual)

```bash
# 1. Ingest logs
curl -X POST http://localhost:8000/api/ingest/logs \
  -H "X-API-Key: <workspace_id>:secret" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "api-gateway",
    "logs": [{
      "timestamp": "2026-10-17T13:30:00Z",
      "severity": "ERROR",
      "message": "Database timeout",
      "trace_id": "abc123",
      "span_id": "span1",
      "attributes": {"db": "users"}
    }]
  }'

# Expected: {"accepted": 1, "rejected": 0}

# 2. Search logs
curl "http://localhost:8000/api/logs?start=2026-10-17T13:00:00Z&end=2026-10-17T14:00:00Z&severity=ERROR" \
  -H "Authorization: Bearer <jwt>"

# Expected: {"logs": [...], "total": N, "limit": 50, "offset": 0}

# 3. Ingest trace
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
          "end_time": "2026-10-17T13:30:00.250Z",
          "status": "ok",
          "attributes": {"http.method": "GET"}
        }
      ]
    }]
  }'

# Expected: {"accepted": 1, "rejected": 0}

# 4. Get trace
curl "http://localhost:8000/api/traces/abc123" \
  -H "Authorization: Bearer <jwt>"

# Expected: {"trace_id": "abc123", "spans": [...], ...}
```

### Frontend Tests (Manual)

1. **Log Search**
   - Open http://localhost:3000/logs
   - Select severity "ERROR"
   - Verify filtered results
   - Type "timeout" in search
   - Verify text search works
   - Click trace_id link
   - Verify redirects to trace detail

2. **Trace List**
   - Open http://localhost:3000/traces
   - Select status "error"
   - Verify filtered traces
   - Click trace_id
   - Verify trace detail loads

3. **Trace Detail**
   - Open http://localhost:3000/traces/abc123
   - Verify trace metadata shown
   - Verify span waterfall renders
   - Verify timeline bars positioned correctly
   - Verify child spans indented
   - Verify error spans shown in red

### Database Tests

```sql
-- Verify tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('log_entries', 'traces', 'spans');

-- Check log storage
SELECT id, severity, message, trace_id 
FROM log_entries 
ORDER BY timestamp DESC 
LIMIT 5;

-- Check trace-span join
SELECT 
  t.trace_id, 
  t.duration_ms, 
  COUNT(s.id) as span_count,
  string_agg(s.operation_name, ', ') as operations
FROM traces t
LEFT JOIN spans s ON t.trace_id = s.trace_id
GROUP BY t.trace_id, t.duration_ms;

-- Verify correlation
SELECT 
  l.severity,
  l.message,
  l.trace_id,
  t.duration_ms as trace_duration
FROM log_entries l
JOIN traces t ON l.trace_id = t.trace_id
WHERE l.trace_id IS NOT NULL
LIMIT 10;
```

## Acceptance Criteria

✅ Logs ingested with trace_id for correlation  
✅ Logs searchable by service, time, severity, text  
✅ Traces ingested with parent-child spans  
✅ Trace waterfall shows hierarchy and timing  
✅ Log → trace navigation works via trace_id link  
✅ Trace → log correlation query works  
✅ Workspace isolation enforced on all queries  
✅ Frontend renders severity badges correctly  
✅ Frontend renders status badges correctly  
✅ Timeline bars positioned accurately  

## Git History

```
64e1c69 feat: trace detail waterfall visualization
efc50d7 feat: frontend log and trace list pages
48deabf docs: Milestone C backend completion report
c2c60dc feat: log and trace query endpoints
0737cd8 feat: log and trace ingestion with PostgreSQL storage
```

## Metrics

- **Commits:** 6 (5 implementation + 1 doc)
- **API endpoints:** 5 new (12 total)
- **Database tables:** 3 new (6 total)
- **Frontend pages:** 3 new (4 total)
- **Models:** 3 (LogEntry, Trace, Span)
- **Schemas:** 12 (request/response types)
- **Example scripts:** 2 (logs, traces)
- **Lines of code:** ~750 backend + ~550 frontend = ~1300 LOC

## Known Limitations

1. **No log redaction**  
   Sensitive fields stored as-is. Add in Milestone E.

2. **Basic text search**  
   ILIKE is good for MVP. Full-text search upgrade later.

3. **Single service per trace**  
   All spans inherit root service. Multi-service traces need enhancement.

4. **No automatic span ordering in API**  
   Frontend builds tree from parent_span_id. Backend could pre-sort.

5. **Fixed time range (1 hour)**  
   Frontend hardcoded. Add time picker in next iteration.

6. **No pagination UI**  
   Backend supports it, frontend shows first page only.

## Next Steps: Milestone D (Alerting & Incidents)

Priorities:
1. Alert rules table (metric thresholds, conditions)
2. Alert evaluation engine (background worker)
3. Alert history and state transitions
4. Incident creation from alerts
5. Incident timeline and evidence links
6. Frontend: alert rules page, incident management

Estimated: 4-6 hours

## Production Readiness Gaps

Before production:
- [ ] Add retention cleanup job
- [ ] Add rate limiting on ingestion
- [ ] Add field redaction middleware
- [ ] Add telemetry payload validation
- [ ] Add integration tests (pytest)
- [ ] Add E2E tests (Playwright)
- [ ] Add monitoring for the platform itself
- [ ] Add backup/restore procedures
- [ ] Add runbook for common failures

## Architecture Decisions

**Why PostgreSQL for logs instead of Elasticsearch?**
- Simpler MVP deployment
- No additional infrastructure
- JSONB + GIN index sufficient for search
- Easy workspace isolation via FK
- Can migrate to ES later if needed

**Why calculate trace duration in backend?**
- Single source of truth
- Consistent across all views
- Handles incomplete traces gracefully
- Frontend just renders, no logic

**Why in-memory metrics but PostgreSQL logs/traces?**
- Metrics: high volume, stateless, loss acceptable
- Logs/traces: lower volume, need persistence, correlation requires joins
- Can migrate metrics to TimescaleDB later

**Why hierarchical span rendering in frontend?**
- Timeline position shows concurrency
- Indentation shows causality
- Both dimensions needed for understanding
- Simple recursive component

## Conclusion

Milestone C complete. TraceForge now has:
- ✅ Service registry (Milestone B)
- ✅ Metrics ingestion and query (Milestone B)
- ✅ Structured logs with search (Milestone C)
- ✅ Distributed traces with waterfall (Milestone C)
- ✅ Cross-telemetry correlation (Milestone C)
- ⏳ Alerting (Milestone D - next)
- ⏳ Incidents (Milestone D - next)

Total implementation: ~2500 LOC across 15 commits over Phase 1 + Milestones B + C.
