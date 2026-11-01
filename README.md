# TraceForge

TraceForge is an open-source developer observability dashboard for collecting
and investigating service metrics, structured logs, traces, alerts, and
incidents.

Repository: https://github.com/0xyz-exe/traceforge

## Screenshots

### 1. Observability Overview & Service Metrics
Dashboard telemetri observabilitas sentral menyajikan status kesehatan operasional multi-layanan secara *real-time*, metrik throughput transaksi agregat (14.280 req/menit), grafik latensi P50 hingga P99 (48,2 ms), tabel direktori layanan mikro terdaftar lengkap dengan rincian versi, rasio error rate, serta kartu peringatan insiden kritis aktif yang langsung terhubung ke sistem triase penanganan masalah.

![Observability Overview & Service Metrics](docs/screenshots/01_metrics_dashboard.png)

### 2. Distributed Trace Waterfall View
Tampilan bagan air terjun (*waterfall view*) penelusuran terdistribusi memetakan dekomposisi eksekusi siklus hidup request dari gateway hingga ke dependensi terdalam, menampilkan ringkasan trace ID, durasi total perambatan (285 ms), status keberhasilan tiap span, serta hierarki visual offset waktu antar-layanan (*checkout-api*, *auth-service*, *inventory-service*, *payment-gateway*, dan *notification-worker*).

![Distributed Trace Waterfall View](docs/screenshots/02_trace_waterfall.png)

### 3. Structured Log Search & Ingestion
Antarmuka penjelajah log terstruktur memfasilitasi pencarian dan investigasi log bervolume tinggi dengan filter tingkat keparahan (DEBUG, INFO, WARN, ERROR, CRITICAL), pencarian kata kunci fleksibel, korelasi instan ke trace ID dan span ID terkait, serta panel atribut JSON mendalam untuk mendiagnosis anomali sistem secara presisi.

![Structured Log Search & Ingestion](docs/screenshots/03_log_explorer.png)

### 4. Alert Rules & Incident Management
Pusat manajemen insiden dan aturan peringatan mengotomatisasi pendeteksian degradasi performa sistem, memantau ambang batas metrik (seperti pembatasan laju 429 pada *payment-gateway*), melacak siklus hidup eskalasi dari status Open, Acknowledged, hingga Resolved, serta mencatat riwayat kronologis investigasi pada linimasa insiden.

![Alert Rules & Incident Management](docs/screenshots/04_incidents.png)

### 5. Authentication
Gerbang otentikasi berbasis token JWT mengamankan akses ke ruang kerja (*workspace isolation*), mendukung alur masuk terenkripsi dengan proteksi sesi ketat, registrasi akun pengembang baru, serta integrasi manajemen identitas pengguna berbasis standar enkripsi bcrypt.

![Authentication](docs/screenshots/05_login.png)

> **Project status:** Functional local MVP. The project is suitable for local
> development and evaluation, but it is not production-ready.

## Features

- User registration and JWT login
- Workspace-scoped service registry
- Add services from the dashboard or register them through telemetry ingestion
- Metrics ingestion with validation, seven-day in-memory retention, and a
  1,000-series cardinality limit
- Metric queries with sum, average, minimum, maximum, count, p50, p95, and p99
  aggregation
- Structured log ingestion and search
- Trace and span ingestion with trace detail and waterfall views
- Alert rules, alert events, and incident management
- Next.js dashboard with dark theme and React Query caching
- SQLite by default for local development, with PostgreSQL support available

## Requirements

- Python 3.11 or newer
- Node.js 18 or newer
- npm
- PostgreSQL 15 or newer (optional)
- Docker (optional)

## Quick start

### 1. Start the backend

From the repository root:

#### Windows PowerShell

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

#### macOS/Linux

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

The default configuration uses SQLite and creates `backend/traceforge.db`
automatically. No database server or migration command is required for the
default local setup.

The backend is available at:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

If port 8000 is already in use, start the backend on another port:

```powershell
uvicorn app.main:app --reload --port 8002
```

Then set the matching URL in `frontend/.env.local`, for example:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8002/api
```

### 2. Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

On macOS/Linux, use `cp .env.local.example .env.local` instead of
`Copy-Item`.

The dashboard is available at http://localhost:3000.

Open `/login` to create a workspace or sign in.

## Register a service

After signing in:

1. Open http://localhost:3000/services.
2. Select **+ Add service**.
3. Enter the service name, environment, and optional version.
4. Select **Register service**.

Services can also be created through the API:

```bash
curl -X POST http://127.0.0.1:8000/api/services \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "api-gateway",
    "environment": "development",
    "version": "1.0.0"
  }'
```

## Authentication API

Register a user and workspace:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "full_name": "Test User",
    "workspace_name": "My Workspace"
  }'
```

Sign in:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Use the returned `access_token` as a Bearer token for dashboard API requests.

## Telemetry ingestion

Telemetry ingestion uses an API key in the format
`workspace_id:secret` through the `X-API-Key` header. The current MVP validates
the workspace portion of the key; production deployments must replace this
with securely generated and hashed API keys.

Example metric request:

```bash
curl -X POST http://127.0.0.1:8000/api/ingest/metrics \
  -H "X-API-Key: WORKSPACE_ID:secret" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "api-gateway",
    "metrics": [{
      "name": "http.requests.total",
      "type": "counter",
      "value": 1,
      "labels": {"method": "GET"}
    }]
  }'
```

More Python and Node.js examples are available in [`examples/`](examples/).

## Testing

### Backend

```powershell
cd backend
pip install -r requirements-test.txt
pytest
```

### Frontend

```powershell
cd frontend
npm run build
```

## PostgreSQL

SQLite is recommended for local development. To use PostgreSQL:

1. Set `DATABASE_URL` in `backend/.env`.
2. Start PostgreSQL.
3. Run the migrations from the `backend` directory:

```bash
alembic upgrade head
```

Example database URL:

```env
DATABASE_URL=postgresql://traceforge:traceforge@localhost:5432/traceforge
```

## Repository structure

```text
.
├── backend/       FastAPI API, ingestion, storage, and business logic
├── frontend/      Next.js observability dashboard
├── docs/          Product, architecture, API, and security documentation
└── examples/      Python and Node.js telemetry examples
```

## Documentation

- [Product Requirements](docs/PRD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Database Design](docs/DATABASE_DESIGN.md)
- [API Specification](docs/API.md)
- [UI/UX Brief](docs/UI_UX_BRIEF.md)
- [Threat Model](docs/THREAT_MODEL.md)
- [Backend setup](backend/README.md)
- [Frontend setup](frontend/README.md)
- [Telemetry examples](examples/README.md)

## Known limitations

- Metrics are stored in memory and are lost when the backend restarts.
- The MVP is designed for a single backend instance.
- Default telemetry retention is seven days.
- API keys are not hashed yet.
- OpenTelemetry Protocol support is planned but not implemented.
- No production deployment, horizontal scaling, or managed authentication
  workflow is included yet.

## Security

This project is intended for local development and evaluation.

- Never commit `.env` or `.env.local` files.
- Set a strong, unique `SECRET_KEY` before sharing a deployment.
- Use HTTPS in production.
- Review [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) before exposing the API.

## Contributing

Issues and pull requests are welcome. Include or update tests for behavioral
changes and explain setup changes in the relevant documentation.

## License

License to be determined.

---

Built with FastAPI, SQLAlchemy, Next.js, React, TypeScript, and Tailwind CSS.
