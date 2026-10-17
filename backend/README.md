# TraceForge Backend

FastAPI-based observability backend.

## Setup

### 1. Install Python 3.11+

### 2. Create virtual environment

Windows:
```powershell
python -m venv venv
.\\venv\\Scripts\\Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set SECRET_KEY to a random string.

### 5. Start PostgreSQL

Using Docker:
```bash
docker run --name traceforge-db \\
  -e POSTGRES_USER=traceforge \\
  -e POSTGRES_PASSWORD=traceforge \\
  -e POSTGRES_DB=traceforge \\
  -p 5432:5432 \\
  -d postgres:15
```

### 6. Run migrations

```bash
alembic upgrade head
```

### 7. Start server

```bash
uvicorn app.main:app --reload --port 8000
```

API available at:
- http://localhost:8000
- Docs: http://localhost:8000/docs

## Testing

```bash
pytest
```

## Project Structure

```
app/
├── main.py              # FastAPI app
├── config.py            # Settings
├── database.py          # SQLAlchemy setup
├── models/              # Database models
├── schemas/             # Pydantic schemas
├── routes/              # API endpoints
└── services/            # Business logic
```
