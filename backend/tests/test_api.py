import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Workspace, User, Service
from app.utils.auth import hash_password
import uuid

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def test_workspace(db_session):
    workspace = Workspace(
        id=uuid.uuid4(),
        name="Test Workspace",
        slug="test-workspace"
    )
    db_session.add(workspace)
    db_session.commit()
    return workspace

@pytest.fixture
def test_user(db_session, test_workspace):
    user = User(
        id=uuid.uuid4(),
        workspace_id=test_workspace.id,
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def auth_token(client, test_user):
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def api_key(test_workspace):
    return f"{test_workspace.id}:secret"

@pytest.fixture
def api_key_headers(api_key):
    return {"X-API-Key": api_key}


class TestAuth:
    def test_register_user(self, client):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "full_name": "New User",
                "workspace_name": "New Workspace"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "workspace" in data

    def test_login(self, client, test_user):
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, test_user):
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401


class TestServices:
    def test_create_service(self, client, auth_headers):
        response = client.post(
            "/api/services",
            headers=auth_headers,
            json={
                "name": "test-service",
                "environment": "production",
                "version": "1.0.0"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-service"
        assert data["environment"] == "production"
        assert data["health_status"] == "unknown"

    def test_list_services(self, client, auth_headers, db_session, test_workspace):
        # Create a service
        service = Service(
            workspace_id=test_workspace.id,
            name="api-gateway",
            environment="production"
        )
        db_session.add(service)
        db_session.commit()

        response = client.get("/api/services", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(s["name"] == "api-gateway" for s in data["services"])


class TestMetricsIngestion:
    def test_ingest_metrics(self, client, api_key_headers):
        response = client.post(
            "/api/ingest/metrics",
            headers=api_key_headers,
            json={
                "service": "test-service",
                "metrics": [
                    {
                        "name": "http.requests.total",
                        "type": "counter",
                        "value": 100.0,
                        "timestamp": "2026-10-17T12:00:00Z",
                        "labels": {"method": "GET"}
                    }
                ]
            }
        )
        assert response.status_code == 202
        data = response.json()
        assert data["accepted"] == 1
        assert data["rejected"] == 0

    def test_ingest_metrics_invalid_payload(self, client, api_key_headers):
        response = client.post(
            "/api/ingest/metrics",
            headers=api_key_headers,
            json={
                "service": "test-service",
                "metrics": []  # Empty metrics
            }
        )
        # Should still accept but with 0 accepted
        assert response.status_code in [202, 422]


class TestLogsIngestion:
    def test_ingest_logs(self, client, api_key_headers):
        response = client.post(
            "/api/ingest/logs",
            headers=api_key_headers,
            json={
                "service": "test-service",
                "logs": [
                    {
                        "timestamp": "2026-10-17T12:00:00Z",
                        "severity": "ERROR",
                        "message": "Database connection failed",
                        "trace_id": "abc123",
                        "attributes": {"db": "users"}
                    }
                ]
            }
        )
        assert response.status_code == 202
        data = response.json()
        assert data["accepted"] == 1

    def test_search_logs(self, client, auth_headers, api_key_headers):
        # Ingest a log first
        client.post(
            "/api/ingest/logs",
            headers=api_key_headers,
            json={
                "service": "test-service",
                "logs": [
                    {
                        "timestamp": "2026-10-17T12:00:00Z",
                        "severity": "ERROR",
                        "message": "Test error message",
                        "attributes": {}
                    }
                ]
            }
        )

        # Search logs
        response = client.get(
            "/api/logs?start=2026-10-17T11:00:00Z&end=2026-10-17T13:00:00Z",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data


class TestTracesIngestion:
    def test_ingest_traces(self, client, api_key_headers):
        response = client.post(
            "/api/ingest/traces",
            headers=api_key_headers,
            json={
                "service": "test-service",
                "traces": [
                    {
                        "trace_id": "trace123",
                        "spans": [
                            {
                                "span_id": "span1",
                                "parent_span_id": None,
                                "operation_name": "GET /users",
                                "start_time": "2026-10-17T12:00:00.000Z",
                                "end_time": "2026-10-17T12:00:00.500Z",
                                "status": "ok",
                                "attributes": {},
                                "events": []
                            }
                        ]
                    }
                ]
            }
        )
        assert response.status_code == 202
        data = response.json()
        assert data["accepted"] == 1

    def test_get_trace(self, client, auth_headers, api_key_headers):
        # Ingest a trace first
        client.post(
            "/api/ingest/traces",
            headers=api_key_headers,
            json={
                "service": "test-service",
                "traces": [
                    {
                        "trace_id": "trace456",
                        "spans": [
                            {
                                "span_id": "span1",
                                "parent_span_id": None,
                                "operation_name": "GET /api",
                                "start_time": "2026-10-17T12:00:00Z",
                                "end_time": "2026-10-17T12:00:01Z",
                                "status": "ok",
                                "attributes": {},
                                "events": []
                            }
                        ]
                    }
                ]
            }
        )

        # Get trace
        response = client.get("/api/traces/trace456", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["trace_id"] == "trace456"
        assert len(data["spans"]) == 1


class TestAlertRules:
    def test_create_alert_rule(self, client, auth_headers):
        response = client.post(
            "/api/alerts/rules",
            headers=auth_headers,
            json={
                "name": "High error rate",
                "condition_type": "metric_threshold",
                "metric_name": "http.errors.total",
                "threshold": 10.0,
                "comparison": "gt",
                "aggregation": "sum",
                "window_seconds": 300,
                "severity": "critical",
                "cooldown_seconds": 600
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "High error rate"
        assert data["enabled"] == True

    def test_list_alert_rules(self, client, auth_headers):
        response = client.get("/api/alerts/rules", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "rules" in data
        assert "total" in data


class TestIncidents:
    def test_create_incident(self, client, auth_headers):
        response = client.post(
            "/api/alerts/incidents",
            headers=auth_headers,
            json={
                "title": "API gateway down",
                "description": "Service not responding",
                "severity": "critical"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "API gateway down"
        assert data["status"] == "open"
        assert len(data["timeline"]) == 1

    def test_list_incidents(self, client, auth_headers):
        response = client.get("/api/alerts/incidents", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "incidents" in data
        assert "total" in data
