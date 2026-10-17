#!/usr/bin/env python3
"""
Example: Send traces to TraceForge
"""
import requests
import time
import random
from datetime import datetime, timezone, timedelta

API_URL = "http://localhost:8000/api"
API_KEY = "your_workspace_id:your_api_key_secret"  # Replace with actual API key

def send_traces(service_name, traces):
    """Send traces to TraceForge ingestion endpoint"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "service": service_name,
        "traces": traces
    }
    
    response = requests.post(
        f"{API_URL}/ingest/traces",
        json=payload,
        headers=headers
    )
    
    if response.status_code == 202:
        result = response.json()
        print(f"✓ Traces ingested: {result['accepted']} accepted, {result['rejected']} rejected")
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")

def generate_trace():
    """Generate a sample distributed trace"""
    trace_id = f"trace{random.randint(10000, 99999)}"
    start_time = datetime.now(timezone.utc)
    
    # Root span
    root_duration = random.randint(50, 500)
    root_end = start_time + timedelta(milliseconds=root_duration)
    
    spans = [
        {
            "span_id": "span1",
            "parent_span_id": None,
            "operation_name": "GET /api/users",
            "start_time": start_time.isoformat(),
            "end_time": root_end.isoformat(),
            "status": "ok",
            "attributes": {
                "http.method": "GET",
                "http.url": "/api/users",
                "http.status_code": 200,
            },
            "events": []
        }
    ]
    
    # Child spans
    db_start = start_time + timedelta(milliseconds=10)
    db_duration = random.randint(20, 100)
    db_end = db_start + timedelta(milliseconds=db_duration)
    
    spans.append({
        "span_id": "span2",
        "parent_span_id": "span1",
        "operation_name": "SELECT users",
        "start_time": db_start.isoformat(),
        "end_time": db_end.isoformat(),
        "status": "ok" if random.random() > 0.2 else "error",
        "attributes": {
            "db.system": "postgresql",
            "db.statement": "SELECT * FROM users WHERE id = $1",
        },
        "events": []
    })
    
    # Cache span
    cache_start = db_end + timedelta(milliseconds=5)
    cache_duration = random.randint(5, 30)
    cache_end = cache_start + timedelta(milliseconds=cache_duration)
    
    spans.append({
        "span_id": "span3",
        "parent_span_id": "span1",
        "operation_name": "REDIS GET",
        "start_time": cache_start.isoformat(),
        "end_time": cache_end.isoformat(),
        "status": "ok",
        "attributes": {
            "cache.key": "user:profile:123",
            "cache.hit": random.choice([True, False]),
        },
        "events": []
    })
    
    return {
        "trace_id": trace_id,
        "spans": spans
    }

def main():
    print("Sending sample traces to TraceForge...")
    
    while True:
        traces = [generate_trace() for _ in range(random.randint(1, 3))]
        send_traces("api-gateway", traces)
        time.sleep(15)

if __name__ == "__main__":
    main()
