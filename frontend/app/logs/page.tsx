'use client'

import { useQuery } from '@tanstack/react-query'
import { logsApi } from '@/lib/api'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { useState } from 'react'

export default function LogsPage() {
  const [startTime] = useState(() => {
    const d = new Date()
    d.setHours(d.getHours() - 1)
    return d.toISOString()
  })
  const [endTime] = useState(() => new Date().toISOString())
  const [severity, setSeverity] = useState('')
  const [search, setSearch] = useState('')

  const { data, isLoading, error } = useQuery({
    queryKey: ['logs', startTime, endTime, severity, search],
    queryFn: () => logsApi.search({
      start: startTime,
      end: endTime,
      severity: severity || undefined,
      search: search || undefined,
    }).then(res => res.data),
  })

  if (isLoading) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Logs</h1>
          <p className="text-muted">Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Logs</h1>
          <div className="bg-error/20 border border-error text-error px-4 py-3 rounded">
            Error loading logs. Make sure the backend is running.
          </div>
        </div>
      </div>
    )
  }

  const logs = data?.logs || []

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Logs</h1>
          <Link href="/" className="text-accent hover:underline">
            ← Home
          </Link>
        </div>

        {/* Filters */}
        <div className="bg-card border border-border rounded p-4 mb-4 flex gap-4">
          <select 
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            className="bg-background border border-border rounded px-3 py-2"
          >
            <option value="">All Severities</option>
            <option value="DEBUG">DEBUG</option>
            <option value="INFO">INFO</option>
            <option value="WARN">WARN</option>
            <option value="ERROR">ERROR</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>
          
          <input
            type="text"
            placeholder="Search messages..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-background border border-border rounded px-3 py-2 flex-1"
          />
        </div>

        {logs.length === 0 ? (
          <div className="bg-card border border-border rounded p-8 text-center">
            <p className="text-muted mb-4">No logs found</p>
            <p className="text-sm text-muted">
              Send logs to /api/ingest/logs or adjust filters
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {logs.map((log) => (
              <div 
                key={log.id}
                className="bg-card border border-border rounded p-4 hover:bg-background/50"
              >
                <div className="flex gap-4 items-start">
                  <SeverityBadge severity={log.severity} />
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-sm text-muted">
                        {formatDistanceToNow(new Date(log.timestamp), { addSuffix: true })}
                      </span>
                      <span className="text-sm text-muted">{log.service}</span>
                    </div>
                    <p className="text-foreground mb-2">{log.message}</p>
                    {log.trace_id && (
                      <Link 
                        href={`/traces/${log.trace_id}`}
                        className="text-accent text-sm hover:underline"
                      >
                        trace_id: {log.trace_id} →
                      </Link>
                    )}
                    {Object.keys(log.attributes).length > 0 && (
                      <details className="mt-2">
                        <summary className="text-sm text-muted cursor-pointer">
                          Attributes
                        </summary>
                        <pre className="text-xs mt-2 text-muted">
                          {JSON.stringify(log.attributes, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <p className="text-muted text-sm mt-4">
          Showing {logs.length} of {data?.total || 0} logs (last 1 hour)
        </p>
      </div>
    </div>
  )
}

function SeverityBadge({ severity }: { severity: string }) {
  const colors = {
    DEBUG: 'bg-muted/20 text-muted border-muted',
    INFO: 'bg-blue-500/20 text-blue-400 border-blue-500',
    WARN: 'bg-warning/20 text-warning border-warning',
    ERROR: 'bg-error/20 text-error border-error',
    CRITICAL: 'bg-red-900/40 text-red-400 border-red-600',
  }

  const colorClass = colors[severity as keyof typeof colors] || colors.INFO

  return (
    <span className={`inline-block px-3 py-1 rounded border text-xs font-mono ${colorClass}`}>
      {severity}
    </span>
  )
}
