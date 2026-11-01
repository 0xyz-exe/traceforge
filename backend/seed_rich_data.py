import uuid
import json
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('backend/traceforge.db')
cur = conn.cursor()

print("Seeding rich telemetry data for TraceForge...")

# Find workspace
workspaces = cur.execute("SELECT id FROM workspaces").fetchall()
if not workspaces:
    ws_id = str(uuid.uuid4())
    cur.execute("INSERT INTO workspaces (id, name, slug) VALUES (?, 'Production Workspace', 'production-workspace')", (ws_id,))
else:
    ws_id = workspaces[0][0]

users = cur.execute("SELECT id FROM users").fetchall()
user_id = users[0][0] if users else None

now = datetime.utcnow()

# Clean previous telemetry
cur.execute("DELETE FROM incident_timeline")
cur.execute("DELETE FROM incidents")
cur.execute("DELETE FROM alert_events")
cur.execute("DELETE FROM alert_rules")
cur.execute("DELETE FROM log_entries")
cur.execute("DELETE FROM spans")
cur.execute("DELETE FROM traces")
cur.execute("DELETE FROM services")

for ws_row in workspaces:
    ws_id = ws_row[0]
    
    # 1. Services
    services_data = [
        (str(uuid.uuid4()), ws_id, 'checkout-api', 'production', 'v1.8.0', now),
        (str(uuid.uuid4()), ws_id, 'auth-service', 'production', 'v2.4.1', now),
        (str(uuid.uuid4()), ws_id, 'inventory-service', 'production', 'v3.1.2', now),
        (str(uuid.uuid4()), ws_id, 'payment-gateway', 'production', 'v2.0.4', now),
        (str(uuid.uuid4()), ws_id, 'notification-worker', 'production', 'v1.2.0', now),
    ]

    for s in services_data:
        cur.execute("""
        INSERT INTO services (id, workspace_id, name, environment, version, last_telemetry_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (s[0], s[1], s[2], s[3], s[4], s[5], s[5], s[5]))

    checkout_svc_id = services_data[0][0]
    auth_svc_id = services_data[1][0]
    inv_svc_id = services_data[2][0]
    pay_svc_id = services_data[3][0]
    notif_svc_id = services_data[4][0]

    # 2. Traces
    trace1_id = "4bf92f3577b34da6a3ce929d0e0e4736" if ws_id == workspaces[0][0] else str(uuid.uuid4()).replace('-', '')[:32]
    cur.execute("""
    INSERT INTO traces (id, workspace_id, trace_id, root_service_id, start_time, end_time, duration_ms, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (str(uuid.uuid4()), ws_id, trace1_id, checkout_svc_id, now - timedelta(minutes=5), now - timedelta(minutes=5) + timedelta(milliseconds=285), 285, 'ok', now))

    trace2_id = str(uuid.uuid4()).replace('-', '')[:32]
    cur.execute("""
    INSERT INTO traces (id, workspace_id, trace_id, root_service_id, start_time, end_time, duration_ms, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (str(uuid.uuid4()), ws_id, trace2_id, pay_svc_id, now - timedelta(minutes=12), now - timedelta(minutes=12) + timedelta(milliseconds=520), 520, 'error', now))

    # 3. Spans for Trace 1 (Waterfall)
    root_span_id = "00f067aa0ba902b7"
    t1_start = now - timedelta(minutes=5)

    spans_data = [
        # Root span
        (str(uuid.uuid4()), ws_id, trace1_id, root_span_id, None, checkout_svc_id, 'HTTP POST /api/v1/checkout/process',
         t1_start, t1_start + timedelta(milliseconds=285), 285, 'ok',
         json.dumps({"http.method": "POST", "http.status_code": 200, "user.id": "usr_99812", "cart.total": 249.50}),
         json.dumps([{"name": "checkout_started", "timestamp": t1_start.isoformat()}])),

        # Span 1: auth
        (str(uuid.uuid4()), ws_id, trace1_id, "5fb397be34d23b0f", root_span_id, auth_svc_id, 'auth.verify_jwt_token',
         t1_start + timedelta(milliseconds=5), t1_start + timedelta(milliseconds=29), 24, 'ok',
         json.dumps({"auth.type": "Bearer", "jwt.algo": "RS256"}), json.dumps([])),

        # Span 2: inventory
        (str(uuid.uuid4()), ws_id, trace1_id, "6db482ef21a47c12", root_span_id, inv_svc_id, 'inventory.reserve_stock',
         t1_start + timedelta(milliseconds=32), t1_start + timedelta(milliseconds=80), 48, 'ok',
         json.dumps({"sku": "SKU-HEADPHONE-MBL", "quantity": 1, "warehouse": "us-east-1"}), json.dumps([])),

        # Span 3: payment
        (str(uuid.uuid4()), ws_id, trace1_id, "7ac591ea10f58d34", root_span_id, pay_svc_id, 'payment.charge_credit_card',
         t1_start + timedelta(milliseconds=82), t1_start + timedelta(milliseconds=224), 142, 'ok',
         json.dumps({"gateway": "stripe", "currency": "USD", "amount": 249.50, "card.brand": "Visa"}), json.dumps([])),

        # Span 4: db transaction
        (str(uuid.uuid4()), ws_id, trace1_id, "8be602fb09c69e45", root_span_id, checkout_svc_id, 'db.commit_order_record',
         t1_start + timedelta(milliseconds=226), t1_start + timedelta(milliseconds=261), 35, 'ok',
         json.dumps({"db.system": "postgresql", "db.table": "orders", "sql.query": "INSERT INTO orders..."}), json.dumps([])),

        # Span 5: async notification
        (str(uuid.uuid4()), ws_id, trace1_id, "9cf713ac98b70f56", root_span_id, notif_svc_id, 'event.emit_order_confirmation',
         t1_start + timedelta(milliseconds=263), t1_start + timedelta(milliseconds=281), 18, 'ok',
         json.dumps({"queue": "notifications.email", "template": "order_receipt_v2"}), json.dumps([])),

        # Trace 2 Spans
        (str(uuid.uuid4()), ws_id, trace2_id, "1122334455667788", None, pay_svc_id, 'HTTP POST /api/v1/payment/refund',
         now - timedelta(minutes=12), now - timedelta(minutes=12) + timedelta(milliseconds=520), 520, 'error',
         json.dumps({"http.method": "POST", "http.status_code": 502, "error": "UpstreamGatewayTimeout"}), json.dumps([])),

        (str(uuid.uuid4()), ws_id, trace2_id, "9988776655443322", "1122334455667788", pay_svc_id, 'stripe.refund_api_call',
         now - timedelta(minutes=12) + timedelta(milliseconds=15), now - timedelta(minutes=12) + timedelta(milliseconds=510), 495, 'error',
         json.dumps({"error.type": "StripeRateLimitError", "status": 429, "retry_after": 2}), json.dumps([]))
    ]

    for sp in spans_data:
        cur.execute("""
        INSERT INTO spans (id, workspace_id, trace_id, span_id, parent_span_id, service_id, operation_name, start_time, end_time, duration_ms, status, attributes, events, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sp[0], sp[1], sp[2], sp[3], sp[4], sp[5], sp[6], sp[7], sp[8], sp[9], sp[10], sp[11], sp[12], sp[7]))

    # 4. Logs
    logs_data = [
        (str(uuid.uuid4()), ws_id, checkout_svc_id, now - timedelta(minutes=5), 'INFO', 'Checkout initiated for cart crt_881923 with 1 items', trace1_id, root_span_id, json.dumps({"user_id": "usr_99812", "amount": 249.50})),
        (str(uuid.uuid4()), ws_id, auth_svc_id, now - timedelta(minutes=5, seconds=2), 'INFO', 'JWT session token validated successfully for user usr_99812', trace1_id, "5fb397be34d23b0f", json.dumps({"auth_scope": "customer:write"})),
        (str(uuid.uuid4()), ws_id, inv_svc_id, now - timedelta(minutes=4, seconds=58), 'INFO', 'Stock reservation held for SKU-HEADPHONE-MBL (1 qty)', trace1_id, "6db482ef21a47c12", json.dumps({"held_until": (now + timedelta(minutes=15)).isoformat()})),
        (str(uuid.uuid4()), ws_id, pay_svc_id, now - timedelta(minutes=4, seconds=55), 'INFO', 'Stripe payment intent pi_99214 confirmed (charged $249.50)', trace1_id, "7ac591ea10f58d34", json.dumps({"card_last4": "4242", "receipt_url": "https://pay.stripe.com/rcpt_99214"})),
        (str(uuid.uuid4()), ws_id, checkout_svc_id, now - timedelta(minutes=4, seconds=52), 'INFO', 'Order ord_552109 successfully persisted to primary relational cluster', trace1_id, "8be602fb09c69e45", json.dumps({"order_id": "ord_552109", "latency_ms": 35})),
        (str(uuid.uuid4()), ws_id, notif_svc_id, now - timedelta(minutes=4, seconds=50), 'INFO', 'Order receipt dispatched to queue notifications.email', trace1_id, "9cf713ac98b70f56", json.dumps({"recipient": "customer@storefront.internal"})),
        (str(uuid.uuid4()), ws_id, pay_svc_id, now - timedelta(minutes=12), 'ERROR', 'Payment refund failed: StripeRateLimitError 429 Too Many Requests received from acquirer', trace2_id, "9988776655443322", json.dumps({"gateway": "stripe", "status_code": 429, "circuit_breaker": "half-open"})),
        (str(uuid.uuid4()), ws_id, pay_svc_id, now - timedelta(minutes=15), 'WARN', 'Upstream payment gateway response latency exceeded P95 threshold (142ms > 100ms)', None, None, json.dumps({"metric": "http_request_duration_ms", "threshold": 100})),
    ]

    for lg in logs_data:
        cur.execute("""
        INSERT INTO log_entries (id, workspace_id, service_id, timestamp, severity, message, trace_id, span_id, attributes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (lg[0], lg[1], lg[2], lg[3], lg[4], lg[5], lg[6], lg[7], lg[8], lg[3]))

    # 5. Alert Rules
    alert_rules_data = [
        (str(uuid.uuid4()), ws_id, 'High P99 Latency on Payment Gateway', 'Alerts when payment gateway latency exceeds 500ms over a 5m window', 'payment-gateway', 'metric_threshold', 'http_request_duration_ms', 500.0, 'gt', 'p99', 300, 'critical', 1, 300),
        (str(uuid.uuid4()), ws_id, 'Elevated Checkout 5xx Error Rate', 'Triggers when 5xx response ratio exceeds 2% across checkout API endpoints', 'checkout-api', 'error_rate', 'http_requests_total', 2.0, 'gt', 'avg', 300, 'critical', 1, 300),
        (str(uuid.uuid4()), ws_id, 'Auth Token Renewal Failure Spike', 'Detects sudden increases in failed token exchange attempts', 'auth-service', 'metric_threshold', 'auth_token_refresh_failures', 10.0, 'gt', 'sum', 300, 'warning', 1, 600),
    ]

    for ar in alert_rules_data:
        cur.execute("""
        INSERT INTO alert_rules (id, workspace_id, name, description, service, condition_type, metric_name, threshold, comparison, aggregation, window_seconds, severity, enabled, cooldown_seconds, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ar[0], ar[1], ar[2], ar[3], ar[4], ar[5], ar[6], ar[7], ar[8], ar[9], ar[10], ar[11], ar[12], ar[13], now, now))

    # 6. Incidents
    incidents_data = [
        (str(uuid.uuid4()), ws_id, 'INC-4021: Payment Gateway Upstream Acquirer 429 Rate Limiting',
         'Automated refund and settlement requests to Stripe acquirer experienced transient 429 rate limiting, triggering circuit breaker isolation.',
         'critical', 'acknowledged', user_id, user_id, now - timedelta(minutes=24), now - timedelta(minutes=18), None, None,
         json.dumps({"affected_service": "payment-gateway", "impact": "Refund retries delayed by up to 2m", "traces": [trace2_id]})),
        (str(uuid.uuid4()), ws_id, 'INC-4019: Inventory Sync Redis Memory Pressure',
         'Redis eviction count spiked during high volume warehouse replenishment synchronization. Cache memory increased from 75% to 92%.',
         'warning', 'resolved', user_id, user_id, now - timedelta(hours=3), now - timedelta(hours=2, minutes=50), now - timedelta(hours=2, minutes=10),
         'Eviction policy tuned to volatile-lru and node memory scaled by 2GB.',
         json.dumps({"affected_service": "inventory-service", "impact": "Cache misses temporarily increased latency by 12ms"}))
    ]

    for inc in incidents_data:
        cur.execute("""
        INSERT INTO incidents (id, workspace_id, title, description, severity, status, assigned_to, created_by, started_at, acknowledged_at, resolved_at, resolution_notes, metadata, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (inc[0], inc[1], inc[2], inc[3], inc[4], inc[5], inc[6], inc[7], inc[8], inc[9], inc[10], inc[11], inc[12], inc[8], now))

conn.commit()
conn.close()
print("TraceForge telemetry database successfully populated!")
