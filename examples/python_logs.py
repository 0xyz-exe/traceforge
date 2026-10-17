#!/usr/bin/env python3
"""
Example: Send logs to TraceForge
"""
import requests
import time
import random
from datetime import datetime, timezone

API_URL = "http://localhost:8000/api"
API_KEY = "your_workspace_id:your_api_key_secret"  # Replace with actual API key

def send_logs(service_name, logs):
    """Send logs to TraceForge ingestion endpoint"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "service": service_name,
        "logs": logs
    }
    
    response = requests.post(
        f"{API_URL}/ingest/logs",
        json=payload,
        headers=headers
    )
    
    if response.status_code == 202:
        result = response.json()
        print(f"✓ Logs ingested: {result['accepted']} accepted, {result['rejected']} rejected")
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")

def main():
    print("Sending sample logs to TraceForge...")
    
    severities = ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
    messages = [
        "User authentication successful",
        "Database query executed",
        "Cache miss for key user:123",
        "API rate limit approaching threshold",
        "Connection timeout to external service",
        "Invalid request parameters",
        "Memory usage above 80%",
    ]
    
    while True:
        logs = []
        
        for _ in range(random.randint(1, 5)):
            trace_id = f"trace{random.randint(1000, 9999)}" if random.random() > 0.7 else None
            
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "severity": random.choice(severities),
                "message": random.choice(messages),
                "attributes": {
                    "user_id": random.randint(100, 999),
                    "request_id": f"req-{random.randint(1000, 9999)}",
                }
            }
            
            if trace_id:
                log_entry["trace_id"] = trace_id
                log_entry["span_id"] = f"span{random.randint(1, 99)}"
            
            logs.append(log_entry)
        
        send_logs("api-gateway", logs)
        time.sleep(10)

if __name__ == "__main__":
    main()
