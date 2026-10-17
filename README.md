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

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+ (or SQLite for development)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env and set:
#   DATABASE_URL=postgresql://user:pass@localhost:5432/traceforge
#   SECRET_KEY=<generate-random-secret>

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local
# Edit .env.local:
#   NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

### Testing

```bash
# Backend tests
cd backend
pip install -r requirements-test.txt
pytest

# Frontend tests (when added)
cd frontend
npm test
```

### Example Usage

1. **Register a user:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "full_name": "Test User",
    "workspace_name": "My Workspace"
  }'
```

2. **Login and get JWT:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

3. **Send metrics (use workspace_id from register response):**
```bash
cd examples
export API_KEY="<workspace_id>:secret"
python python_metrics.py
```

4. **Open dashboard:**
Visit http://localhost:3000 and explore services, logs, traces, alerts, and incidents.

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
