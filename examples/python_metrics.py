#!/usr/bin/env python3
"""
Example: Send metrics to TraceForge from a Python application
"""

import requests
import time
from datetime import datetime

# Configuration
TRACEFORGE_API = "http://localhost:8000/api"
API_KEY = "YOUR_WORKSPACE_ID:secret"  # Replace with your API key
SERVICE_NAME = "example-python-app"

def send_metric(metric_name: str, value: float, metric_type: str = "gauge", labels: dict = None):
    """Send a single metric to TraceForge"""
    payload = {
        "service": SERVICE_NAME,
        "metrics": [
            {
                "name": metric_name,
                "type": metric_type,
                "value": value,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "labels": labels or {}
            }
        ]
    }
    
    response = requests.post(
        f"{TRACEFORGE_API}/ingest/metrics",
        json=payload,
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"}
    )
    
    if response.status_code == 202:
        print(f"✓ Sent {metric_name}={value}")
    else:
        print(f"✗ Failed: {response.status_code} {response.text}")

def main():
    """Send example metrics every 10 seconds"""
    print(f"Sending metrics for service: {SERVICE_NAME}")
    print("Press Ctrl+C to stop\n")
    
    request_count = 0
    
    try:
        while True:
            # Counter: total requests
            request_count += 1
            send_metric("http.requests.total", request_count, "counter", {"endpoint": "/api/users"})
            
            # Gauge: simulated memory usage
            import random
            memory_mb = 512 + random.randint(-50, 50)
            send_metric("app.memory.used_mb", memory_mb, "gauge")
            
            # Histogram: simulated request duration
            duration_ms = 100 + random.randint(0, 400)
            send_metric("http.request.duration", duration_ms, "histogram", {"method": "GET", "status": "200"})
            
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nStopped")

if __name__ == "__main__":
    main()
