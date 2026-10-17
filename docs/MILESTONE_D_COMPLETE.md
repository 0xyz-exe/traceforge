# Milestone D Complete — Alerting & Incidents

**Date:** 2026-10-17  
**Status:** Complete ✅

## Summary

Built alerting engine and incident management system with rule evaluation, alert history, and incident lifecycle tracking.

## Deliverables

### Backend API (9 endpoints)

✅ **Alert Rules**
- GET /api/alerts/rules (list with enabled filter)
- POST /api/alerts/rules (create with validation)
- GET /api/alerts/rules/:id
- PATCH /api/alerts/rules/:id (update)
- DELETE /api/alerts/rules/:id

✅ **Alert Events**
- GET /api/alerts/events (list with state filter)
- Alert evaluator engine (background)

✅ **Incidents**
- GET /api/alerts/incidents (list with status filter)
- POST /api/alerts/incidents (create from alert)
- PATCH /api/alerts/incidents/:id (acknowledge, resolve, assign)

### Database (Migration 003)

✅ **Tables**
- `alert_rules`: condition_type, metric_name, threshold, comparison, aggregation, window_seconds, cooldown_seconds
- `alert_events`: state (firing/resolved), severity, message, details JSONB, fired_at, resolved_at
- `incidents`: status (open/acknowledged/resolved), severity, assigned_to, started_at, acknowledged_at, resolved_at
- `incident_timeline`: event_type, message, created_by, audit trail

✅ **Models**
- AlertRule with metric threshold conditions
- AlertEvent with state transitions
- Incident with lifecycle timestamps
- IncidentTimeline for audit log

### Alert Evaluator Engine

✅ **Features**
- Evaluates enabled rules against metrics
- Metric threshold comparison (gt, gte, lt, lte, eq)
- Aggregation support (avg, sum, min, max, count, p50, p95, p99)
- Configurable evaluation window (60-3600s)
- Cooldown prevents alert spam
- Creates AlertEvent on trigger
- Tracks last_fired_at per rule

✅ **Condition Types**
- `metric_threshold`: value vs threshold with comparison operator
- (extensible for `error_rate`, `missing_telemetry` in future)

### Incident Lifecycle

✅ **States**
- `open` → `acknowledged` → `resolved`
- Timestamps tracked for each transition
- Timeline entry created on every change

✅ **Timeline Events**
- `created`: incident opened
- `updated`: status change, assignment, notes
- Message describes what changed
- Created_by tracks actor

✅ **Metadata**
- Links to alert_event_id that triggered it
- JSONB for extensibility (future: linked traces, logs)

## Technical Implementation

### Alert Rule Validation

```python
# metric_threshold requires all fields
if condition_type == "metric_threshold":
    assert metric_name and threshold and comparison and aggregation
```

### Evaluation Flow

1. Query enabled AlertRules
2. For each rule:
   - Check cooldown (skip if < cooldown_seconds since last fire)
   - Query metrics for window (start = now - window_seconds, end = now)
   - Aggregate data using rule.aggregation
   - Compare aggregated value against threshold
   - If triggered: create AlertEvent, update cooldown tracker
3. Runs periodically (cron/background worker)

### Cooldown Mechanism

```python
last_alert_times = {}  # rule_id -> last_fired_at
if (now - last_alert_times[rule_id]) < cooldown_seconds:
    return  # Skip evaluation
```

Prevents alert spam when metric stays above threshold.

### Incident Timeline

Every incident mutation adds timeline entry:
- Status change: "Status changed from open to acknowledged"
- Assignment: "Assigned to user {user_id}"
- Resolution: "Resolution notes added"

Provides audit trail and context for post-incident review.

## Verification

### Manual Tests

```bash
# 1. Create alert rule
curl -X POST http://localhost:8000/api/alerts/rules \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High error rate",
    "condition_type": "metric_threshold",
    "service": "api-gateway",
    "metric_name": "http.errors.total",
    "threshold": 10,
    "comparison": "gt",
    "aggregation": "sum",
    "window_seconds": 300,
    "severity": "critical",
    "cooldown_seconds": 600
  }'

# Expected: {"id": "...", "name": "High error rate", "enabled": true, ...}

# 2. List alert rules
curl "http://localhost:8000/api/alerts/rules" \
  -H "Authorization: Bearer <jwt>"

# Expected: {"rules": [...], "total": N}

# 3. Update rule (disable)
curl -X PATCH http://localhost:8000/api/alerts/rules/<rule_id> \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Expected: {"id": "...", "enabled": false, ...}

# 4. List alert events
curl "http://localhost:8000/api/alerts/events?state=firing" \
  -H "Authorization: Bearer <jwt>"

# Expected: {"events": [...], "total": N, "limit": 50}

# 5. Create incident
curl -X POST http://localhost:8000/api/alerts/incidents \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "API gateway errors",
    "description": "High error rate detected",
    "severity": "critical",
    "alert_event_id": "<event_id>"
  }'

# Expected: {"id": "...", "status": "open", "timeline": [{"event_type": "created", ...}]}

# 6. Acknowledge incident
curl -X PATCH http://localhost:8000/api/alerts/incidents/<incident_id> \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"status": "acknowledged"}'

# Expected: {"status": "acknowledged", "acknowledged_at": "...", "timeline": [...]}

# 7. Resolve incident
curl -X PATCH http://localhost:8000/api/alerts/incidents/<incident_id> \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved",
    "resolution_notes": "Restarted service, errors cleared"
  }'

# Expected: {"status": "resolved", "resolved_at": "...", "resolution_notes": "...", ...}
```

### Database Tests

```sql
-- Check tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'alert%' OR table_name LIKE 'incident%';

-- Verify alert rule
SELECT id, name, condition_type, metric_name, threshold, enabled 
FROM alert_rules;

-- Check alert events
SELECT ae.state, ae.severity, ae.message, ar.name as rule_name
FROM alert_events ae
JOIN alert_rules ar ON ae.alert_rule_id = ar.id
ORDER BY ae.fired_at DESC;

-- Incident with timeline
SELECT 
  i.title,
  i.status,
  i.severity,
  COUNT(it.id) as timeline_entries
FROM incidents i
LEFT JOIN incident_timeline it ON i.id = it.incident_id
GROUP BY i.id, i.title, i.status, i.severity;

-- Timeline detail
SELECT 
  it.event_type,
  it.message,
  it.created_at,
  i.title as incident
FROM incident_timeline it
JOIN incidents i ON it.incident_id = i.id
ORDER BY it.created_at;
```

## Acceptance Criteria

✅ Alert rules can be created with metric thresholds  
✅ Alert rules can be enabled/disabled  
✅ Alert evaluator checks rules against metrics  
✅ AlertEvent created when threshold crossed  
✅ Cooldown prevents duplicate alerts  
✅ Alert events listed with state filter  
✅ Incidents can be created from alerts  
✅ Incidents track status transitions  
✅ Incident timeline provides audit trail  
✅ Workspace isolation enforced  

## Git History

```
b127c67 feat: alert events and incident management API
755090d feat: alert rule CRUD API
d7f735d feat: alerting and incident database models
```

## Metrics

- **Commits:** 3
- **API endpoints:** 9 new (21 total)
- **Database tables:** 4 new (10 total)
- **Models:** 4 (AlertRule, AlertEvent, Incident, IncidentTimeline)
- **Schemas:** 10 (request/response types)
- **Services:** 1 (AlertEvaluator)
- **Lines of code:** ~700 backend

## Known Limitations

1. **Evaluator runs manually**  
   No background worker yet. Need cron or celery integration.

2. **Single condition type**  
   Only metric_threshold implemented. error_rate, missing_telemetry planned.

3. **No notification channels**  
   AlertEvents stored only. Email/Slack/webhook planned.

4. **No auto-incident creation**  
   Incidents created manually. Auto-create from critical alerts planned.

5. **No incident comments**  
   Timeline tracks system events only. User comments planned.

6. **No alert grouping**  
   Each rule fires independently. Correlation/grouping planned.

## Architecture Decisions

**Why cooldown instead of state-based alerting?**
- Simpler MVP implementation
- Prevents spam when metric oscillates
- State-based (pending → firing → resolved) adds complexity
- Can migrate to stateful later

**Why JSONB for alert details?**
- Flexible schema for different condition types
- Can store metric values, thresholds, labels
- Easy to extend without migration

**Why separate alert_events from alert_rules?**
- Rules are configuration (template)
- Events are instances (history)
- Enables alert history analysis
- Rule can be deleted without losing events

**Why timeline table instead of JSONB array?**
- Easier queries and filtering
- Can join with users table for actor names
- Supports pagination
- Better indexing

## Integration Points

**Alert → Incident:**
```
1. AlertEvent fired with severity=critical
2. User reviews event in UI
3. Click "Create Incident"
4. Incident.metadata.alert_event_id = event.id
5. Incident created with link back to alert
```

**Incident → Evidence:**
```
Future: Incident.metadata can store:
- trace_ids: linked traces showing failures
- log_query: filter params that show related logs
- metric_snapshot: values at incident time
```

## Next Steps: Frontend (Alerts & Incidents Pages)

Priorities:
1. Alert rules list page
2. Create alert rule form
3. Alert events history page
4. Incidents list page
5. Incident detail with timeline
6. Create incident from alert button

Estimated: 3-4 hours

## Production Gaps

Before production:
- [ ] Background worker for alert evaluation (celery/apscheduler)
- [ ] Notification channels (email, Slack, webhook)
- [ ] Auto-incident creation from critical alerts
- [ ] Alert grouping and correlation
- [ ] Incident comments
- [ ] Alert silencing/muting
- [ ] Alert rule testing (dry-run)
- [ ] Incident response runbooks

## Conclusion

Milestone D complete. TraceForge now has:
- ✅ Service registry (Milestone B)
- ✅ Metrics ingestion and query (Milestone B)
- ✅ Structured logs with search (Milestone C)
- ✅ Distributed traces with waterfall (Milestone C)
- ✅ Cross-telemetry correlation (Milestone C)
- ✅ Alert rules with evaluation (Milestone D)
- ✅ Incident management with timeline (Milestone D)
- ⏳ Frontend for alerts/incidents (next)
- ⏳ E2E tests (Milestone E)

Total: ~3500 LOC, 21 API endpoints, 10 database tables, 19 commits.
