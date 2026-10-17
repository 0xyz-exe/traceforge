# UI/UX Design Brief — TraceForge

**Version:** 0.1.0  
**Date:** 2026-10-17  
**Status:** Draft

## Design Philosophy

TraceForge is a **developer-first observability workspace** focused on evidence-based troubleshooting, not marketing dashboards.

### Core Principles
1. **Evidence over decoration:** Show data, not empty charts
2. **Correlation first:** Every view enables drill-down to related telemetry
3. **Honest state:** Clear labels for LIVE, HISTORICAL, DEMO, STALE, EMPTY
4. **Fast time-to-evidence:** Minimize clicks between symptom and root cause
5. **Dark-mode native:** Developers work at night

### Visual Language
- **Typography:** System fonts, monospace for IDs/timestamps
- **Color:** Semantic (green=healthy, red=error, yellow=warning, gray=stale)
- **Density:** Information-dense but scannable
- **Charts:** Recharts with time on X-axis, clear units, no fake data

## Layout Structure

### Global Layout
```
┌─────────────────────────────────────────────┐
│ [Logo] TraceForge    [Workspace ▼] [User ▼]│ ← Header
├────────┬────────────────────────────────────┤
│        │                                    │
│ Nav    │          Main Content              │
│        │                                    │
│ • Over │                                    │
│ • Svcs │                                    │
│ • Metr │                                    │
│ • Logs │                                    │
│ • Trac │                                    │
│ • Alrt │                                    │
│ • Incd │                                    │
│        │                                    │
└────────┴────────────────────────────────────┘
```

### Responsive Behavior
- Desktop (≥1024px): Sidebar visible
- Tablet (768-1023px): Collapsible sidebar
- Mobile (<768px): Hamburger menu

### Time Range Control
Every metrics/logs/traces view has unified time picker:
- Last 15 minutes
- Last 1 hour
- Last 6 hours
- Last 24 hours
- Last 7 days
- Custom range
- Auto-refresh toggle (off, 10s, 30s, 1m)

### Filter Bar
Persistent across views:
- Workspace selector
- Environment filter (production, staging, dev, all)
- Service filter (multi-select)
- Search box (context-aware)

## Screen Definitions

### 1. Overview Dashboard

**Route:** `/`

**Purpose:** At-a-glance system health

**Layout:**
```
┌─────────────────────────────────────────────┐
│ System Health               [Last 1 hour ▼] │
├─────────────────────────────────────────────┤
│ [⚪ 8 Healthy] [🔴 2 Error] [⚠️ 0 Warn]      │
├─────────────────────────────────────────────┤
│ Services with Errors                        │
│ • api-gateway (5.2% error rate) [View →]   │
│ • user-service (12 errors/min)  [View →]   │
├─────────────────────────────────────────────┤
│ Recent Alerts (Last 24h)                    │
│ [🔴 CRITICAL] api-gateway latency > 2s      │
│   Fired: 2026-10-17 12:45 UTC               │
│   [View Alert] [Create Incident]            │
├─────────────────────────────────────────────┤
│ Active Incidents                            │
│ [🔴 #42] Database timeout in user-service   │
│   Owner: alice  Started: 45m ago            │
│   [View Timeline]                           │
└─────────────────────────────────────────────┘
```

**Empty State:**
- No services registered: "Get started by registering your first service"
- No errors: "All services healthy ✓"
- No alerts: "No recent alerts"

**Data Labels:**
- "LIVE" badge when auto-refresh enabled
- "STALE" badge if no telemetry in last 5 minutes

---

### 2. Service Inventory

**Route:** `/services`

**Purpose:** Browse all registered services

**Layout:**
```
┌─────────────────────────────────────────────┐
│ Services                       [+ Register] │
│ [Search...] [Environment: All ▼]            │
├────────┬────────┬────────┬─────────┬────────┤
│ Name   │ Env    │ Status │ Errors  │ Last ⚡│
├────────┼────────┼────────┼─────────┼────────┤
│ api-gw │ prod   │ 🟢 OK  │ 0.1%    │ 2s ago │
│ user-  │ prod   │ 🔴 ERR │ 5.2%    │ 5s ago │
│ auth   │ prod   │ ⚪ STAL│ -       │ 1h ago │
│ jobs   │ stage  │ 🟢 OK  │ 0%      │ 10s    │
└────────┴────────┴────────┴─────────┴────────┘
                                    [1-10 of 42]
```

**Status Logic:**
- 🟢 OK: Error rate < 1%, telemetry fresh (<5m)
- 🟡 WARN: Error rate 1-5%
- 🔴 ERROR: Error rate > 5%
- ⚪ STALE: No telemetry for >5 minutes
- ⚫ DOWN: No telemetry for >1 hour

**Interactions:**
- Click row → Service Detail
- Hover → Tooltip with version, last deployment

---

### 3. Service Detail

**Route:** `/services/:service_id`

**Purpose:** Deep-dive into one service

**Layout:**
```
┌─────────────────────────────────────────────┐
│ ← Back to Services                          │
│ api-gateway (production)           [🟢 OK]  │
│ Version: v1.2.3  Last Deploy: 2h ago        │
├─────────────────────────────────────────────┤
│ Key Metrics                  [Last 1h ▼]    │
│ ┌─────────────────┐ ┌─────────────────┐    │
│ │ Request Rate    │ │ Error Rate      │    │
│ │ [Line Chart]    │ │ [Line Chart]    │    │
│ │ 120 req/min     │ │ 5.2%            │    │
│ └─────────────────┘ └─────────────────┘    │
│ ┌─────────────────┐ ┌─────────────────┐    │
│ │ P95 Latency     │ │ P99 Latency     │    │
│ │ [Line Chart]    │ │ [Line Chart]    │    │
│ │ 450ms           │ │ 1.2s            │    │
│ └─────────────────┘ └─────────────────┘    │
├─────────────────────────────────────────────┤
│ Quick Links                                 │
│ [View Logs] [View Traces] [View Alerts]     │
├─────────────────────────────────────────────┤
│ Recent Errors (Last 1h)                     │
│ • "Database connection timeout" (45 times)  │
│   [View Logs] [View Traces]                 │
└─────────────────────────────────────────────┘
```

**Chart Behavior:**
- Hover: Show exact value and timestamp
- Click spike: "View Related Logs/Traces in this time window"
- Empty data: "No data in selected range"

---

### 4. Metrics Explorer

**Route:** `/metrics`

**Purpose:** Query and visualize any metric

**Layout:**
```
┌─────────────────────────────────────────────┐
│ Metrics Explorer                            │
├─────────────────────────────────────────────┤
│ [Service: api-gateway ▼]  [Last 6h ▼]      │
│ [Metric: http.request.duration ▼]          │
│ [Aggregation: p95 ▼]                        │
│ [Group by: status_code ▼]                   │
├─────────────────────────────────────────────┤
│                                             │
│         [Time Series Chart]                 │
│                                             │
│  Legend:                                    │
│  ─── 200 OK (p95: 250ms)                   │
│  ─── 500 Error (p95: 1.2s)                 │
│                                             │
├─────────────────────────────────────────────┤
│ [+ Add to Dashboard] [Export CSV]           │
└─────────────────────────────────────────────┘
```

**Metric Selection:**
- Typeahead search
- Recent metrics
- Available metrics per service

**Aggregations:**
- Count, Sum, Average
- Min, Max
- P50, P95, P99 (when histogram data available)

**Empty State:**
- "No data for selected metric and time range"
- "Select a metric to begin"

---

### 5. Log Explorer

**Route:** `/logs`

**Purpose:** Search and filter structured logs

**Layout:**
```
┌─────────────────────────────────────────────┐
│ Log Explorer                 [Last 1h ▼]    │
├─────────────────────────────────────────────┤
│ [Search: "timeout"] [Service: all ▼]        │
│ [Severity: ERROR ▼] [Has Trace ID: any ▼]  │
│                            [50 results]      │
├─────────────────────────────────────────────┤
│ 2026-10-17 12:45:32 [ERROR] api-gateway     │
│ Database connection timeout                 │
│ trace_id: abc123  [View Trace →]            │
│ { "db": "users", "timeout_ms": 5000 }       │
├─────────────────────────────────────────────┤
│ 2026-10-17 12:45:28 [ERROR] user-service    │
│ Failed to process request                   │
│ trace_id: def456  [View Trace →]            │
│ { "error": "QueryTimeout", "query": "..." } │
├─────────────────────────────────────────────┤
│                 [Load More (50)]            │
└─────────────────────────────────────────────┘
```

**Interactions:**
- Click log entry: Expand full details
- Click trace_id: Open trace view
- Click timestamp: Set time filter to ±5 minutes

**Severity Colors:**
- DEBUG: gray
- INFO: blue
- WARN: yellow
- ERROR: red
- CRITICAL: dark red

**Redaction:**
- Fields matching "password", "token", "secret" → `***REDACTED***`

---

### 6. Trace Explorer

**Route:** `/traces`

**Purpose:** Find slow or failed traces

**Layout:**
```
┌─────────────────────────────────────────────┐
│ Trace Explorer               [Last 1h ▼]    │
├─────────────────────────────────────────────┤
│ [Service: all ▼] [Status: all ▼]            │
│ [Min Duration: 1000ms]                      │
│                            [25 traces]       │
├─────────┬────────┬────────┬────────┬────────┤
│ Trace   │ Root   │ Status │ Dur    │ Start  │
├─────────┼────────┼────────┼────────┼────────┤
│ abc123  │api-gw  │ ❌ ERR │ 5.2s   │ 12:45  │
│ def456  │api-gw  │ ✅ OK  │ 2.1s   │ 12:44  │
│ ghi789  │user-sv │ ❌ ERR │ 1.8s   │ 12:43  │
└─────────┴────────┴────────┴────────┴────────┘
                            [Load More (25)]
```

**Click Row → Trace Detail (Waterfall)**

---

### 7. Trace Waterfall

**Route:** `/traces/:trace_id`

**Purpose:** Visualize distributed request path

**Layout:**
```
┌─────────────────────────────────────────────┐
│ ← Back to Traces                            │
│ Trace abc123                         ❌ ERR │
│ Started: 2026-10-17 12:45:32  Duration: 5.2s│
├─────────────────────────────────────────────┤
│ Waterfall                                   │
│                                             │
│ ▼ api-gateway GET /users           2.1s    │
│   ├─ user-service getUser()        5.1s ⚠️ │
│   │  ├─ database.query()           5.0s ❌ │
│   │  │   { error: "timeout" }              │
│   │  └─ cache.get()                0.05s   │
│   └─ auth-service verify()         0.1s    │
│                                             │
├─────────────────────────────────────────────┤
│ Span Details: database.query()              │
│ Duration: 5.0s  Status: error               │
│ Attributes:                                 │
│   db.system: postgresql                     │
│   db.statement: SELECT * FROM users WHERE...│
│   db.timeout_ms: 5000                       │
│ Events:                                     │
│   exception: QueryTimeout                   │
├─────────────────────────────────────────────┤
│ Related Logs [View All →]                   │
│ 2026-10-17 12:45:37 [ERROR] Database timeout│
└─────────────────────────────────────────────┘
```

**Visual Cues:**
- Span background color: green (fast), yellow (slow), red (error)
- Indentation: parent-child hierarchy
- Duration bar: proportional to trace total

---

### 8. Alert Rules

**Route:** `/alerts/rules`

**Purpose:** Configure alert conditions

**Layout:**
```
┌─────────────────────────────────────────────┐
│ Alert Rules                  [+ Create Rule]│
├─────────┬────────┬────────┬────────┬────────┤
│ Name    │ Service│ Condit │ Sever  │ Status │
├─────────┼────────┼────────┼────────┼────────┤
│ High    │ api-gw │ p95>2s │ CRIT   │ 🟢 OK  │
│ latency │        │        │        │        │
│ Error   │ user-  │ err>5% │ WARN   │ 🔴 FIRE│
│ spike   │ svc    │        │        │        │
└─────────┴────────┴────────┴────────┴────────┘
```

**Create Rule Form:**
```
Rule Name: [________________]
Service: [api-gateway ▼]
Condition Type: [Metric Threshold ▼]
Metric: [http.request.duration.p95 ▼]
Threshold: [___] ms  Operator: [> ▼]
Evaluation Interval: [1 minute ▼]
Pending Period: [2 minutes ▼]
Severity: [● CRITICAL ○ WARNING]
[Cancel] [Create]
```

---

### 9. Alert History

**Route:** `/alerts/history`

**Purpose:** Review fired alerts

**Layout:**
```
┌─────────────────────────────────────────────┐
│ Alert History                [Last 24h ▼]   │
│ [Severity: all ▼] [Status: all ▼]           │
├────────┬────────┬────────┬────────┬────────┤
│ Alert  │ Sever  │ Status │ Fired  │ Resolv │
├────────┼────────┼────────┼────────┼────────┤
│ High   │ CRIT   │ RESOLV │ 12:45  │ 13:10  │
│ latency│        │        │        │        │
│ Error  │ WARN   │ FIRING │ 12:30  │ -      │
│ spike  │        │        │ (15m)  │        │
└────────┴────────┴────────┴────────┴────────┘
```

**Click Row → Alert Event Detail:**
- Evaluation results
- Link to service
- Link to relevant telemetry
- [Create Incident] button

---

### 10. Incident Management

**Route:** `/incidents`

**Purpose:** Track ongoing and resolved incidents

**Layout:**
```
┌─────────────────────────────────────────────┐
│ Incidents                  [+ Create]        │
│ [Status: active ▼] [Severity: all ▼]        │
├────┬────────┬────────┬────────┬─────────────┤
│ ID │ Title  │ Sever  │ Owner  │ Age         │
├────┼────────┼────────┼────────┼─────────────┤
│ #42│ DB slow│ CRIT   │ alice  │ 45m (OPEN)  │
│ #41│ API err│ WARN   │ bob    │ 2h (RESOLV) │
└────┴────────┴────────┴────────┴─────────────┘
```

---

### 11. Incident Timeline

**Route:** `/incidents/:id`

**Purpose:** Investigation workspace

**Layout:**
```
┌─────────────────────────────────────────────┐
│ ← Back to Incidents                         │
│ #42 Database timeout in user-service        │
│ 🔴 CRITICAL   Owner: alice   OPEN (45m)     │
│ [Resolve] [Add Note] [Link Telemetry]       │
├─────────────────────────────────────────────┤
│ Timeline                                    │
│ ● 12:45  Incident created from alert        │
│ ● 12:48  alice: Investigating DB connection │
│ ● 12:50  Linked trace abc123               │
│ ● 12:52  alice: Found slow query           │
│                                             │
│ [Add Event: _______________] [Add]          │
├─────────────────────────────────────────────┤
│ Linked Telemetry                            │
│ • Alert: High latency (api-gateway)         │
│ • Trace: abc123 (5.2s, error)               │
│ • Log: "Database timeout" (45 entries)      │
├─────────────────────────────────────────────┤
│ Resolution Notes                            │
│ [Write summary...                         ] │
│ [Cancel] [Resolve Incident]                 │
└─────────────────────────────────────────────┘
```

---

### 12. Instrumentation Guide

**Route:** `/settings/instrumentation`

**Purpose:** Help developers send telemetry

**Content:**
- Workspace ingestion endpoints
- API keys (with copy button)
- Code examples (Python, Node.js, cURL)
- OpenTelemetry configuration snippets

---

### 13. Workspace Settings

**Route:** `/settings/workspace`

**Purpose:** Configure retention, limits, redaction

**Sections:**
- Retention: logs (7d), metrics (7d), traces (7d)
- Storage usage meter
- Sensitive field patterns (comma-separated)
- Rate limits per API key

---

## Common UI Patterns

### Empty States
- Illustration or icon
- Helpful message: "No X found" or "Get started by..."
- Primary action button when applicable

### Loading States
- Spinner with "Loading metrics..."
- Skeleton loaders for tables/charts

### Error States
- Red alert box
- Error message with context
- Retry button when transient
- "Report Issue" link

### Time Formatting
- Absolute: `2026-10-17 12:45:32 UTC`
- Relative: `45m ago`, `2h ago`, `3d ago`
- Tooltip: Show both on hover

### Toast Notifications
- Success: Green, auto-dismiss 3s
- Error: Red, manual dismiss
- Info: Blue, auto-dismiss 5s

### Buttons
- Primary: Filled, high-contrast
- Secondary: Outline
- Danger: Red (for destructive actions)

### Tables
- Sortable columns (default: most recent first)
- Sticky header on scroll
- Pagination: [Previous] [1 2 3 ... 10] [Next]
- "No results" row when empty

## Accessibility

### Keyboard Navigation
- Tab order follows visual hierarchy
- Focus indicators visible
- Escape closes modals/dropdowns
- Enter submits forms

### Screen Readers
- Semantic HTML (nav, main, article)
- ARIA labels for icon-only buttons
- Alt text for illustrations
- Status announcements for async updates

### Color Contrast
- WCAG AA minimum (4.5:1 for text)
- Don't rely on color alone (use icons + color)

## Theme

### Colors (Dark Mode Primary)
```css
--background: #0a0a0a
--foreground: #fafafa
--card: #1a1a1a
--border: #2a2a2a
--accent: #3b82f6
--success: #22c55e
--warning: #eab308
--error: #ef4444
--muted: #737373
```

### Typography
```css
--font-sans: system-ui, -apple-system, sans-serif
--font-mono: 'Menlo', 'Consolas', monospace
```

## Implementation Notes

### Component Library
- Use shadcn/ui for base components (Button, Dialog, Select, etc.)
- Recharts for all charts
- Lucide icons

### Data Fetching
- React Query for caching and refetching
- Optimistic updates where safe
- Error boundaries for chart failures

### Performance
- Virtualize long log/trace lists (>100 items)
- Debounce search inputs (300ms)
- Lazy-load chart library on metrics pages

### Responsive Breakpoints
```css
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Wide desktop */
```

## Design Deliverables Checklist

- [ ] Figma/wireframes (out of scope for MVP)
- [x] Screen definitions and layouts
- [x] Interaction patterns
- [x] Empty/loading/error states
- [x] Color palette
- [x] Typography scale
- [x] Accessibility guidelines
- [x] Component inventory

## Next Steps

1. Implement base layout (header, sidebar, content)
2. Build service inventory and detail pages
3. Implement metrics explorer with Recharts
4. Build log search with pagination
5. Implement trace waterfall visualization
6. Wire up alert rules and history
7. Build incident timeline
8. Playwright E2E tests for critical paths
