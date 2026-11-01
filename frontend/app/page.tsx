import Link from 'next/link'

export default function Home() {
  const services = [
    { name: 'checkout-api', env: 'production', version: 'v1.8.0', status: 'healthy', latency: '28ms', p99: '68ms', reqs: '5.2k req/m', errorRate: '0.02%' },
    { name: 'auth-service', env: 'production', version: 'v2.4.1', status: 'healthy', latency: '12ms', p99: '24ms', reqs: '4.8k req/m', errorRate: '0.00%' },
    { name: 'inventory-service', env: 'production', version: 'v3.1.2', status: 'healthy', latency: '19ms', p99: '48ms', reqs: '2.4k req/m', errorRate: '0.01%' },
    { name: 'payment-gateway', env: 'production', version: 'v2.0.4', status: 'degraded', latency: '114ms', p99: '142ms', reqs: '1.6k req/m', errorRate: '1.85%' },
    { name: 'notification-worker', env: 'production', version: 'v1.2.0', status: 'healthy', latency: '15ms', p99: '18ms', reqs: '280 req/m', errorRate: '0.00%' },
  ]

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Top Navigation Bar */}
      <header className="border-b border-border bg-card/80 backdrop-blur px-6 py-3.5 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link href="/" className="flex items-center space-x-3 group">
              <div className="w-8 h-8 rounded-lg bg-accent/20 border border-accent/40 flex items-center justify-center text-accent font-black text-sm">
                ⚡
              </div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight text-white group-hover:text-accent transition-colors">
                  TraceForge
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                  OBSERVABILITY LAB
                </span>
              </div>
            </Link>

            <nav className="hidden md:flex items-center space-x-1">
              <Link href="/" className="px-3 py-1.5 rounded-md text-sm font-semibold bg-border text-white">
                Overview
              </Link>
              <Link href="/services" className="px-3 py-1.5 rounded-md text-sm text-muted hover:text-white hover:bg-card transition-colors">
                Services
              </Link>
              <Link href="/traces" className="px-3 py-1.5 rounded-md text-sm text-muted hover:text-white hover:bg-card transition-colors">
                Traces
              </Link>
              <Link href="/logs" className="px-3 py-1.5 rounded-md text-sm text-muted hover:text-white hover:bg-card transition-colors">
                Logs
              </Link>
              <Link href="/alerts" className="px-3 py-1.5 rounded-md text-sm text-muted hover:text-white hover:bg-card transition-colors">
                Alerts
              </Link>
              <Link href="/incidents" className="px-3 py-1.5 rounded-md text-sm text-muted hover:text-white hover:bg-card transition-colors">
                Incidents
              </Link>
            </nav>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 px-2.5 py-1 rounded-full bg-success/10 border border-success/30 text-success text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse"></span>
              <span>INGESTION ACTIVE • 7D RETENTION</span>
            </div>
            <Link href="/login" className="text-xs text-muted hover:text-white font-mono">
              Workspace: Production
            </Link>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
        {/* Header with quick filters */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-6">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-extrabold tracking-tight text-white">Observability Overview & Service Metrics</h1>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-accent/10 text-accent border border-accent/30">
                Live Metrics
              </span>
            </div>
            <p className="text-muted mt-1">
              Multi-service telemetry, distributed trace latency, error budget status, and incident triage.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link href="/traces/4bf92f3577b34da6a3ce929d0e0e4736" className="px-3.5 py-2 bg-card hover:bg-border text-foreground border border-border rounded-lg text-xs font-semibold">
              Trace Waterfall View &rarr;
            </Link>
            <Link href="/incidents" className="px-3.5 py-2 bg-accent hover:opacity-90 text-white rounded-lg text-xs font-bold shadow-lg shadow-accent/20">
              Active Incidents (1)
            </Link>
          </div>
        </div>

        {/* Top 4 KPI Metrics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <div className="bg-card border border-border rounded-xl p-5 relative overflow-hidden">
            <div className="flex items-center justify-between text-muted text-xs font-medium uppercase font-mono">
              <span>Monitored Services</span>
              <span>⚡</span>
            </div>
            <div className="mt-3 text-3xl font-bold text-white tracking-tight font-mono">5 Active</div>
            <div className="mt-2 text-xs text-success flex items-center gap-1.5 font-mono">
              <span>✓ 4 Healthy</span>
              <span className="text-muted">•</span>
              <span className="text-warning">1 Degraded</span>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-5 relative overflow-hidden">
            <div className="flex items-center justify-between text-muted text-xs font-medium uppercase font-mono">
              <span>Throughput Velocity</span>
              <span>📈</span>
            </div>
            <div className="mt-3 text-3xl font-bold text-white tracking-tight font-mono">14,280 req/m</div>
            <div className="mt-2 text-xs text-accent flex items-center gap-1.5 font-mono">
              <span>↑ +8.5% peak load</span>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-5 relative overflow-hidden">
            <div className="flex items-center justify-between text-muted text-xs font-medium uppercase font-mono">
              <span>P99 Trace Latency</span>
              <span>⏱️</span>
            </div>
            <div className="mt-3 text-3xl font-bold text-foreground tracking-tight font-mono">48.2 ms</div>
            <div className="mt-2 text-xs text-muted flex items-center gap-1.5 font-mono">
              <span>P50: 12ms • P95: 35ms</span>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-5 relative overflow-hidden">
            <div className="flex items-center justify-between text-muted text-xs font-medium uppercase font-mono">
              <span>Incident Posture</span>
              <span>🛡️</span>
            </div>
            <div className="mt-3 text-3xl font-bold text-error tracking-tight font-mono">1 Active</div>
            <div className="mt-2 text-xs text-error flex items-center gap-1.5 font-mono">
              <span>INC-4021: Acquirer 429</span>
            </div>
          </div>
        </div>

        {/* Service Metrics & Health Grid */}
        <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-xl">
          <div className="p-6 border-b border-border flex items-center justify-between flex-wrap gap-4">
            <div>
              <h2 className="text-lg font-bold text-white">Registered Services & Telemetry Health</h2>
              <p className="text-xs text-muted mt-0.5">Real-time latency aggregation, error rate, and throughput per service</p>
            </div>
            <div className="flex items-center gap-2">
              <Link href="/services" className="px-3 py-1.5 bg-background hover:bg-border text-foreground border border-border rounded text-xs font-semibold">
                + Register Service
              </Link>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-background text-muted text-xs font-semibold uppercase tracking-wider border-b border-border">
                <tr>
                  <th className="px-6 py-3.5">Service Name</th>
                  <th className="px-6 py-3.5">Environment</th>
                  <th className="px-6 py-3.5">Health Status</th>
                  <th className="px-6 py-3.5">P50 Latency</th>
                  <th className="px-6 py-3.5">P99 Latency</th>
                  <th className="px-6 py-3.5">Throughput</th>
                  <th className="px-6 py-3.5">Error Rate</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border text-foreground">
                {services.map((svc) => (
                  <tr key={svc.name} className="hover:bg-background/40 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-bold text-white flex items-center gap-2">
                        <span>{svc.name}</span>
                        <span className="text-[10px] font-mono text-muted">{svc.version}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded text-[11px] font-mono uppercase bg-blue-950 text-blue-300 border border-blue-800">
                        {svc.env}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded text-xs font-bold uppercase tracking-wider border flex items-center gap-1.5 w-fit ${
                        svc.status === 'healthy' 
                          ? 'bg-success/10 text-success border-success/30' 
                          : 'bg-warning/10 text-warning border-warning/30'
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${svc.status === 'healthy' ? 'bg-success' : 'bg-warning'}`}></span>
                        {svc.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs">{svc.latency}</td>
                    <td className="px-6 py-4 font-mono text-xs font-bold text-white">{svc.p99}</td>
                    <td className="px-6 py-4 font-mono text-xs">{svc.reqs}</td>
                    <td className="px-6 py-4 font-mono text-xs">
                      <span className={svc.errorRate === '0.00%' ? 'text-muted' : svc.status === 'degraded' ? 'text-error font-bold' : 'text-foreground'}>
                        {svc.errorRate}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link href="/traces" className="text-xs text-accent hover:underline font-semibold">
                        View Traces &rarr;
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Active Incident Alert Banner */}
        <div className="bg-gradient-to-r from-error/20 via-card to-card border border-error/50 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase bg-error/30 text-error border border-error/50 font-mono">
                CRITICAL INCIDENT ACTIVE
              </span>
              <span className="text-xs font-mono text-muted">INC-4021 • Started 24m ago</span>
            </div>
            <h3 className="text-lg font-bold text-white">Payment Gateway Upstream Acquirer 429 Rate Limiting</h3>
            <p className="text-xs text-muted max-w-3xl">
              Automated settlement calls to Stripe acquirer experienced transient 429 rate limiting, triggering circuit breaker isolation. Impact: Refund retries delayed.
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <Link href="/incidents" className="px-4 py-2 bg-error hover:opacity-90 text-white rounded-lg text-xs font-bold shadow-md shadow-error/20">
              Triage Incident &rarr;
            </Link>
          </div>
        </div>
      </main>
    </div>
  )
}
