# TraceForge

Open-source developer observability platform for monitoring applications, investigating failures, analyzing performance, and managing incidents.

**Status:** Milestone B (Metrics Foundation) - In Progress

## Features (Current)

✅ **Service Registry**
- Register services with environment and version
- Track last telemetry timestamp
- Health status: healthy, stale, down

✅ **Metrics Ingestion**
- HTTP endpoint for time-series metrics
- In-memory storage (7-day retention)
- Cardinality limits (1000 series max)
- Timestamp and value validation

✅ **Metrics Query**
- Aggregation: sum, avg, min, max, p50, p95, p99
- Time-range filtering
- Label filtering

✅ **Dashboard**
- Service list with health badges
- Dark mode UI
- React Query caching

## Quick Start

## Repository Structure

```
.
├── backend/       Telemetry ingestion, storage, queries
├── frontend/      Observability dashboard
├── docs/          Architecture, PRD, security
└── examples/      Sample instrumented apps
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or SQLite for local MVP)
- Docker (optional)

## Documentation

- [Product Requirements](docs/PRD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Database Design](docs/DATABASE_DESIGN.md)
- [API Specification](docs/API.md)
- [UI/UX Brief](docs/UI_UX_BRIEF.md)
- [Threat Model](docs/THREAT_MODEL.md)

## Development Status

### Milestone A: Discovery ✅
- PRD, architecture, DB design, API spec, threat model, UI/UX brief

### Milestone B: Metrics Foundation (In Progress)
- [x] Service registry endpoints
- [x] Metrics ingestion
- [x] In-memory time-series store
- [x] Metrics query with aggregation
- [x] Service health dashboard
- [ ] End-to-end test
- [ ] Instrumentation examples

### Milestone C: Logs and Traces
- Structured log ingestion
- Log search
- Trace ingestion and waterfall
- Cross-telemetry correlation

### Milestone D: Alerting and Incidents
- Alert rules and evaluation
- Alert history
- Incident management
- Timeline and resolution

### Milestone E: Operational Hardening
- Retention policies
- Access control
- Resource limits
- E2E tests with Playwright

### Milestone F: Optional AI
- Provider abstraction
- Evidence-based incident summaries
- Prompt injection defenses

## Known Limitations (MVP)

- In-memory metrics (lost on restart)
- Single-instance deployment
- No horizontal scaling
- 7-day retention default
- API key format not hashed (MVP)

## Security

⚠️ **This is early development. Not production-ready.**

- Change SECRET_KEY in `.env` before any use
- Use HTTPS in production
- Never commit `.env` files
- Review [THREAT_MODEL.md](docs/THREAT_MODEL.md)

## License

TBD

## Contributing

Issues and PRs welcome. Include tests for behavioral changes.

---

**Built with:** FastAPI, Next.js, PostgreSQL, TypeScript, Tailwind CSS
