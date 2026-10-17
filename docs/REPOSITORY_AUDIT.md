# Repository Audit — TraceForge

**Date:** 2026-10-17  
**Status:** Fresh repository, no existing implementation

## Current State

### Repository Structure
- Empty Git repository initialized
- README.md and .gitignore present
- No backend implementation
- No frontend implementation
- No tests
- No dependencies

### Verified Functionality
None. This is a greenfield project.

### Reusable Modules
None.

### Missing Features
All features from the PRD need implementation:
1. Service registry and project management
2. Metrics ingestion and exploration
3. Structured log ingestion and search
4. Distributed tracing
5. Service dependency visualization
6. Error tracking
7. Alerting engine
8. Incident management
9. Telemetry correlation
10. AI-assisted investigation (optional)

## Technology Stack Selection

### Proposed Stack
**Frontend:**
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Recharts for visualization

**Backend:**
- FastAPI (Python 3.11+)
- Pydantic v2 for validation
- SQLAlchemy for metadata storage
- PostgreSQL for metadata (SQLite fallback for local MVP)

**Telemetry Storage:**
- **Metrics:** In-memory time-series store (MVP), document PostgreSQL alternative
- **Logs:** PostgreSQL JSONB with GIN indexes
- **Traces:** PostgreSQL with parent-child relationships

**Background Processing:**
- Optional: Redis for alert evaluation queue
- Fallback: In-memory with APScheduler

**Instrumentation:**
- OpenTelemetry SDK examples (Python, Node.js)
- OTLP protocol support where practical
- Direct JSON ingestion endpoints

### Rationale
- **No Prometheus/Jaeger in MVP:** Avoid external dependencies for initial version
- **PostgreSQL-native storage:** Single database, simpler operations
- **Optional Redis:** Only add if needed for alert queuing
- **Direct ingestion:** Support OTLP but also provide simple HTTP endpoints

## Security Considerations

### Authentication
- Workspace-scoped API keys for ingestion
- JWT for dashboard users
- Separate read/write credentials

### Input Validation
- Payload size limits (1MB default)
- Rate limiting per workspace
- Timestamp validation
- Metric cardinality limits
- Log field redaction

### Data Isolation
- Workspace-level data segregation
- No cross-workspace queries
- Access control on all endpoints

## Reliability and Scalability Risks

### Known Limitations (MVP)
- In-memory metrics: lost on restart
- Single-instance deployment
- No horizontal scaling
- Limited retention (7 days default)
- No distributed tracing across process boundaries

### Mitigation
- Document data loss scenarios
- Implement graceful shutdown
- Add retention cleanup jobs
- Design schema for future sharding

## Resource Constraints

### Local Development
- PostgreSQL required (Docker acceptable)
- 2GB RAM minimum for backend
- No Kubernetes requirement
- No cloud services required

### Storage Estimates
- Logs: ~100MB/day for 10k entries
- Metrics: ~50MB/day for 100 series @ 1min resolution
- Traces: ~200MB/day for 1k traces
- Total: ~350MB/day, 2.5GB/week

## Environment Limitations

### Windows Development
- Use bash (git-bash/MSYS) for scripts
- Forward-slash paths for native tools
- PostgreSQL via Docker or native Windows install
- Node.js and Python via official installers

### Testing Strategy
- pytest for backend unit/integration
- Vitest for frontend unit tests
- Playwright for E2E (deterministic fixtures)

## Recommended Implementation Order

### Milestone A: Foundation (Discovery)
1. ✅ Repository structure
2. Complete PRD
3. UI/UX brief
4. Architecture design
5. Database schema
6. API specification
7. Threat model

### Milestone B: Metrics Foundation
1. Backend skeleton (FastAPI app)
2. Database models (workspace, service, project)
3. Service registry endpoints
4. Metrics ingestion endpoint
5. In-memory time-series store
6. Metrics query endpoint
7. Basic service health dashboard

### Milestone C: Logs and Traces
1. Structured log ingestion
2. Log storage (PostgreSQL JSONB)
3. Log search and filtering
4. Trace ingestion
5. Trace storage (parent-child spans)
6. Trace waterfall visualization
7. Log-to-trace correlation

### Milestone D: Alerting and Incidents
1. Alert rule schema
2. Alert evaluation engine
3. Alert state tracking
4. Alert history
5. Incident creation
6. Incident timeline
7. Resolution workflow

### Milestone E: Operational Hardening
1. Retention policies
2. Data cleanup jobs
3. Access control enforcement
4. Resource limits and backpressure
5. Instrumentation examples (Python, Node.js)
6. End-to-end tests
7. Security audit

### Milestone F: Optional AI
1. Provider abstraction
2. Evidence-based incident summaries
3. Prompt injection defenses
4. Redaction before AI requests

## Next Steps

1. Create PRD with detailed requirements
2. Create UI/UX brief with screen definitions
3. Design architecture and telemetry pipeline
4. Define database schema
5. Begin Milestone B implementation
