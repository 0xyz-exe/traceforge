# Product Requirements Document — TraceForge

**Version:** 0.1.0  
**Date:** 2026-10-17  
**Status:** Draft

## Executive Summary

TraceForge is an open-source developer observability platform that helps engineering teams monitor applications, investigate failures, analyze performance, and manage incidents through correlated telemetry (logs, metrics, traces).

**Primary differentiator:** Evidence-based troubleshooting through cross-telemetry correlation, not just pretty charts.

## Problem Statement

Developers struggle to diagnose production issues because:
1. Telemetry is siloed (logs in one tool, metrics in another, traces elsewhere)
2. Correlation requires manual work across multiple systems
3. Commercial observability platforms are expensive
4. Existing open-source solutions require complex infrastructure
5. Teams waste hours searching for the right evidence

## User Personas

### Primary: Backend Developer
- Builds and maintains services
- Needs to diagnose errors and performance issues
- Wants fast time-to-evidence
- Familiar with logs, metrics, HTTP status codes
- Limited ops/infrastructure expertise

### Secondary: SRE/Platform Engineer
- Operates services in production
- Configures alerting and incident response
- Needs reliable, low-overhead observability
- Comfortable with infrastructure
- Values operational simplicity

### Tertiary: Engineering Manager
- Tracks service health and incident trends
- Reviews incident timelines
- Needs high-level summaries

## Product Vision

A single platform where developers can:
1. See which services are healthy and which have errors
2. Explore metric anomalies and drill into related logs
3. Open a trace from a slow request and see the full call path
4. Jump from an error log to its trace
5. Configure alerts and track incident timelines
6. Correlate telemetry without manual timestamp matching

## Goals and Non-Goals

### Goals
- Collect logs, metrics, and traces in one platform
- Provide cross-telemetry navigation (metric → logs → trace)
- Support OpenTelemetry instrumentation
- Run locally without paid services
- Simple setup (Docker Compose or native)
- Workspace isolation for multi-team use

### Non-Goals
- Replace Kubernetes-native monitoring (Prometheus/Grafana)
- Support every possible backend (focus on PostgreSQL)
- Build a full APM suite (profiling, RUM, synthetic monitoring)
- Compete on scale (focus on small-to-medium workloads)

## Success Metrics

### Product Metrics
- Time-to-first-telemetry < 10 minutes
- Evidence correlation success rate > 80%
- Alert false-positive rate < 20%
- Incident MTTR reduction vs. manual investigation

### Technical Metrics
- Query latency (logs/traces): p95 < 2s
- Ingestion latency: p95 < 500ms
- Storage efficiency: < 1GB per 10k log entries
- Resource overhead: < 1GB RAM for backend

## Functional Requirements

### P0: MVP Must-Have

#### FR-1: Service Registry
- Create workspaces
- Register services with name, environment, version
- Track last telemetry timestamp
- Mark services stale when no recent data
- Display service inventory

#### FR-2: Metrics Ingestion
- HTTP endpoint accepting JSON metrics
- Support counters, gauges, histograms
- Validate timestamps, names, labels
- Reject non-finite values
- Store time-series data
- Return ingestion errors

#### FR-3: Metrics Querying
- Query by service, metric name, time range
- Support aggregation (sum, avg, p50, p95, p99)
- Return time-series data for charts
- Handle missing data gracefully

#### FR-4: Service Health Dashboard
- Display list of services
- Show health status (healthy, degraded, down, stale)
- Display error rate, request rate, latency
- Link to metric explorer
- Filter by environment

#### FR-5: Log Ingestion
- HTTP endpoint accepting JSON logs
- Parse structured log fields (timestamp, severity, message, service, trace_id)
- Validate and store in PostgreSQL JSONB
- Reject oversized payloads (> 10KB per entry)
- Return ingestion errors

#### FR-6: Log Search
- Search by time range, service, severity, text
- Paginate results
- Link to trace when trace_id present
- Highlight search terms
- Display empty states

#### FR-7: Trace Ingestion
- HTTP endpoint accepting JSON traces
- Parse trace_id, span_id, parent_span_id
- Validate relationships
- Store spans with start/end timestamps
- Calculate duration
- Track span status (ok, error)

#### FR-8: Trace Visualization
- Display trace waterfall
- Show span hierarchy (parent-child)
- Highlight slow spans (> p95 duration)
- Highlight error spans
- Show span attributes (redact sensitive fields)
- Link to related logs

#### FR-9: Cross-Telemetry Correlation
- From metric anomaly → logs in time window
- From log entry → trace via trace_id
- From trace span → logs in time window
- From service dashboard → all telemetry for service

#### FR-10: Alert Rules
- Define rules: metric threshold, error rate, missing data
- Set evaluation interval, pending period
- Support warning and critical severity
- Track alert state (normal, pending, firing, resolved)
- Store alert events

#### FR-11: Alert History
- Display recent alerts
- Filter by service, severity, status
- Show evaluation results
- Link to related telemetry

#### FR-12: Incident Management
- Create incident from alert
- Assign owner
- Set severity
- Add timeline events
- Link telemetry (logs, traces, metrics)
- Track resolution
- Export incident report

### P1: Important but Not MVP

#### FR-13: Service Dependency Map
- Visualize service-to-service calls from traces
- Show error rates on edges
- Detect circular dependencies
- Filter by time range

#### FR-14: Error Tracking
- Group similar errors by message/stack trace
- Track error frequency
- Show first/last seen timestamps
- Link to affected traces

#### FR-15: Custom Dashboards
- Create dashboard with multiple charts
- Pin metrics to dashboard
- Share dashboard URL
- Export dashboard config

#### FR-16: Deployment Annotations
- Mark deployment events on timelines
- Correlate metric changes with deployments
- Display deployment version

#### FR-17: Retention Configuration
- Set retention per telemetry type
- Auto-delete old data
- Display storage usage

### P2: Future Enhancements

#### FR-18: AI-Assisted Investigation
- Optional LLM-based incident summaries
- Evidence citations required
- Local inference option
- Prompt injection defenses

#### FR-19: Webhooks and Integrations
- Send alerts to Slack, PagerDuty, email
- SSRF protection on webhook URLs

#### FR-20: Multi-Workspace Access Control
- Role-based permissions (admin, editor, viewer)
- Workspace invitation workflow

## Primary User Journey (MVP)

### Setup
1. Developer installs TraceForge locally (Docker Compose or native)
2. Creates a workspace
3. Registers a service (e.g., "api-gateway", "production")
4. Configures instrumentation or gets API key

### Instrumentation
5. Adds OpenTelemetry SDK to application
6. Configures exporter to TraceForge endpoints
7. Deploys instrumented service

### Monitoring
8. Opens TraceForge dashboard
9. Views service health overview
10. Sees "api-gateway" with green status, current metrics

### Investigation (Error)
11. Service experiences elevated error rate
12. Developer notices red indicator on dashboard
13. Clicks service → sees error rate spike in chart
14. Clicks "View Related Logs" → filters to errors in time window
15. Sees error: "Database connection timeout"
16. Clicks trace_id → opens waterfall
17. Sees span "database.query" with 5s duration, status=error
18. Identifies root cause: slow query

### Investigation (Latency)
19. Dashboard shows p95 latency increase
20. Developer opens metrics explorer
21. Selects p95 latency chart
22. Clicks spike → "View Related Traces"
23. Sees list of slow traces
24. Opens slowest trace
25. Identifies service "user-service" is slow
26. Drills into that service's metrics

### Alerting
27. Developer creates alert rule: "api-gateway error rate > 5%"
28. Sets evaluation interval: 1 minute
29. Sets pending period: 2 minutes (reduce noise)
30. Alert fires when condition met
31. Alert appears in alert history
32. Developer creates incident from alert
33. Adds investigation notes to timeline
34. Links relevant traces
35. Resolves incident
36. Reviews incident report

## Non-Functional Requirements

### NFR-1: Performance
- Log query: p95 < 2s for 10k entries
- Trace query: p95 < 2s for 1k spans
- Metric query: p95 < 1s for 1 day range
- Ingestion: handle 100 req/s per endpoint

### NFR-2: Reliability
- Graceful handling of storage failures
- Bounded queues (no OOM)
- Data loss scenarios documented
- Health endpoints for monitoring

### NFR-3: Security
- Workspace data isolation
- API key authentication for ingestion
- JWT authentication for dashboard
- Input validation and size limits
- Rate limiting per workspace
- Sensitive field redaction (configurable)

### NFR-4: Scalability
- Support 10 services initially
- Store 7 days telemetry by default
- Handle 1M log entries, 100k traces, 10k metrics
- Document scale ceiling

### NFR-5: Usability
- Time-to-first-telemetry < 10 minutes
- Empty states and loading indicators
- Clear error messages
- Responsive dashboard (desktop + tablet)

### NFR-6: Maintainability
- Unit tests for business logic
- Integration tests for ingestion/query paths
- E2E tests for critical workflows
- Clear architecture documentation

## Data Volume Assumptions

### Per Day (MVP Scale)
- Services: 10
- Log entries: 100,000 (10k per service)
- Metrics: 100 series × 1440 samples (1/min) = 144k data points
- Traces: 10,000 traces × 10 spans avg = 100k spans

### Storage Estimates
- Logs: 100k × ~1KB = 100MB/day
- Metrics: 144k × ~50 bytes = 7MB/day
- Traces: 100k × ~500 bytes = 50MB/day
- Total: ~160MB/day, ~1.1GB/week

### Retention
- Default: 7 days
- Configurable: 1-30 days
- Auto-cleanup job runs daily

## Acceptance Criteria

### Milestone B: Metrics Foundation
- [ ] Service can be registered via API
- [ ] Metrics can be ingested via POST
- [ ] Metrics can be queried by service and time range
- [ ] Service health dashboard displays metrics
- [ ] Stale services marked when no data for 5 minutes

### Milestone C: Logs and Traces
- [ ] Logs can be ingested with trace_id
- [ ] Logs can be searched by service, time, severity
- [ ] Traces can be ingested with parent-child relationships
- [ ] Trace waterfall renders correctly
- [ ] Log → trace link works when trace_id present
- [ ] Trace → logs link shows logs in time window

### Milestone D: Alerting and Incidents
- [ ] Alert rule can be created with threshold
- [ ] Alert evaluates and transitions to firing
- [ ] Alert appears in history
- [ ] Incident can be created from alert
- [ ] Incident timeline stores events
- [ ] Incident can be resolved with notes

### Milestone E: Operational Hardening
- [ ] Retention cleanup runs and deletes old data
- [ ] Oversized payloads rejected with clear error
- [ ] Unauthorized requests blocked
- [ ] Instrumentation example sends real telemetry
- [ ] E2E test covers full investigation flow

### Milestone F: Optional AI
- [ ] AI provider configured (optional)
- [ ] Incident summary generated with evidence citations
- [ ] Sensitive fields redacted before AI request
- [ ] System works fully without AI

## Known Limitations (MVP)

1. **Single-instance deployment:** No horizontal scaling
2. **In-memory metrics:** Lost on restart (document or add persistence)
3. **Limited query capabilities:** No full-text search, no regex
4. **No distributed tracing coordination:** Trace must be sent as complete payload
5. **No automatic service discovery:** Services must be registered
6. **No built-in notifications:** Alert history only, no email/Slack (P1)

## Security Requirements

### Authentication
- API keys for telemetry ingestion
- JWT for dashboard users
- Workspace-scoped credentials

### Input Validation
- Reject payloads > 1MB
- Validate timestamps (not in future, not > 1 year old)
- Sanitize log messages for display
- Limit metric cardinality per workspace (max 1000 series)

### Data Isolation
- All queries filtered by workspace_id
- No cross-workspace API calls
- Separate ingestion keys per workspace

### Redaction
- Configurable sensitive field patterns
- Default: password, token, secret, apikey, authorization
- Apply before storage and before AI requests

## Privacy Considerations

1. **Telemetry ownership:** Workspace owns all telemetry
2. **Retention:** Auto-delete after configured period
3. **Deletion:** Support manual deletion requests
4. **Third-party AI:** Require explicit consent before sending telemetry to external LLM
5. **No tracking:** No usage analytics sent to external services

## Deployment Options

### Local Development
- Docker Compose (backend + frontend + PostgreSQL)
- Native (manual backend + frontend + PostgreSQL)

### Self-Hosted (Future)
- Docker images for backend and frontend
- Kubernetes manifests (optional)
- Environment variables for configuration

### Managed (Out of Scope)
- SaaS offering not planned for MVP

## Technical Debt and Trade-offs

### Accepted Trade-offs
1. **In-memory metrics:** Fast but ephemeral (acceptable for MVP)
2. **PostgreSQL for everything:** Not optimal for time-series but simpler
3. **No streaming:** Request/response ingestion only
4. **No sampling:** Store all traces (acceptable at MVP scale)

### Future Improvements
1. Add persistent time-series storage (Prometheus, VictoriaMetrics)
2. Add streaming ingestion (Kafka, Redis Streams)
3. Add trace sampling configuration
4. Add query result caching

## Appendix: Glossary

- **Workspace:** Isolated tenant with its own services and telemetry
- **Service:** Logical application component (e.g., "api-gateway", "user-service")
- **Environment:** Deployment context (e.g., "production", "staging")
- **Metric:** Numeric time-series data point (counter, gauge, histogram)
- **Log:** Structured event with timestamp, severity, message
- **Trace:** Distributed request path across services
- **Span:** Single operation within a trace
- **Alert Rule:** Condition that triggers an alert when met
- **Incident:** Tracked issue with timeline and resolution
- **Telemetry:** Collective term for logs, metrics, and traces
- **Correlation:** Linking related telemetry using IDs or timestamps
