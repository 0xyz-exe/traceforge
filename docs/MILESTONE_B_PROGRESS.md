# Milestone B Progress

**Date:** 2026-10-17  
**Status:** In Progress

## Completed

### Backend Foundation
- [x] FastAPI app with CORS
- [x] SQLAlchemy models (Workspace, User, Service)
- [x] Alembic migration 001 (initial schema)
- [x] Environment config with SECRET_KEY validation
- [x] Database session management

### Authentication
- [x] User registration endpoint
- [x] Login with JWT
- [x] Password hashing (bcrypt)
- [x] JWT dependencies for protected routes
- [x] API key auth stub (workspace_id:secret format)

### Service Registry
- [x] POST /api/services - Create service
- [x] GET /api/services - List services with pagination
- [x] GET /api/services/:id - Get service detail
- [x] Health status calculation (healthy/stale/down based on last_telemetry_at)
- [x] Workspace isolation enforcement

### Schemas
- [x] Pydantic models for request/response
- [x] Metric ingestion schemas
- [x] Service schemas with health status

## In Progress

### Metrics Ingestion
- [ ] POST /api/ingest/metrics endpoint
- [ ] In-memory time-series store
- [ ] Metric validation (finite values, timestamp checks)
- [ ] Rate limiting

### Metrics Query
- [ ] GET /api/metrics/query endpoint
- [ ] Aggregation (p95, avg, sum)
- [ ] Time-range filtering

### Service Health Dashboard (Frontend)
- [ ] Next.js setup
- [ ] Service list page
- [ ] Service detail with charts

## Blocked
None

## Next Steps
1. Implement in-memory metrics store
2. Add metrics ingestion endpoint
3. Add metrics query endpoint
4. Test with curl
5. Start frontend
