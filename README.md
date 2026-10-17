# TraceForge

Open-source developer observability platform for monitoring applications, investigating failures, analyzing performance, and managing incidents.

**Status:** In development

## Vision

Help developers answer:
- Is the application healthy?
- Which services have errors?
- How have latency and throughput changed?
- Which requests are slow?
- What happened before a failure?
- Which trace, log, or metric supports a diagnosis?

## Core Capabilities (Planned)

1. Service health dashboards
2. Time-series metrics and custom charts
3. Structured log ingestion and search
4. Distributed tracing
5. Service dependency visualization
6. Error tracking
7. Alert rules and history
8. Incident management
9. OpenTelemetry integration
10. Optional AI-assisted investigation

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

## Development Status

Phase 1 (Discovery): In progress
- Repository audit
- Product requirements
- Architecture design
- UI/UX brief

## License

TBD

## Security

This is early development. Do not use in production.
Never commit credentials or sensitive telemetry.
