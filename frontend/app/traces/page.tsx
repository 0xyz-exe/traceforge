'use client'

import { useQuery } from '@tanstack/react-query'
import { tracesApi } from '@/lib/api'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { useState } from 'react'

export default function TracesPage() {
  const [startTime] = useState(() => {
    const d = new Date()
    d.setHours(d.getHours() - 1)
    return d.toISOString()
  })
  const [endTime] = useState(() => new Date().toISOString())
  const [statusFilter, setStatusFilter] = useState('')

  const { data, isLoading, error } = useQuery({
    queryKey: ['traces', startTime, endTime, statusFilter],
    queryFn: () => tracesApi.list({
      start: startTime,
      end: endTime,
      status: statusFilter || undefined,
    }).then(res => res.data),
  })

  if (isLoading) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Traces</h1>
          <p className="text-muted">Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Traces</h1>
          <div className="bg-error/20 border border-error text-error px-4 py-3 rounded">
            Error loading traces. Make sure the backend is running.
          </div>
        </div>
      </div>
    )
  }

  const traces = data?.traces || []

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Traces</h1>
          <Link href="/" className="text-accent hover:underline">
            ← Home
          </Link>
        </div>

        {/* Filters */}
        <div className="bg-card border border-border rounded p-4 mb-4 flex gap-4">
          <select 
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-background border border-border rounded px-3 py-2"
          >
            <option value="">All Status</option>
            <option value="ok">OK</option>
            <option value="error">Error</option>
          </select>
        </div>

        {traces.length === 0 ? (
          <div className="bg-card border border-border rounded p-8 text-center">
            <p className="text-muted mb-4">No traces found</p>
            <p className="text-sm text-muted">
              Send traces to /api/ingest/traces or adjust filters
            </p>
          </div>
        ) : (
          <div className="bg-card border border-border rounded overflow-hidden">
            <table className="w-full">
              <thead className="bg-background border-b border-border">
                <tr>
                  <th className="text-left p-4">Trace ID</th>
                  <th className="text-left p-4">Service</th>
                  <th className="text-left p-4">Status</th>
                  <th className="text-left p-4">Duration</th>
                  <th className="text-left p-4">Spans</th>
                  <th className="text-left p-4">Started</th>
                </tr>
              </thead>
              <tbody>
                {traces.map((trace) => (
                  <tr 
                    key={trace.trace_id}
                    className="border-b border-border last:border-b-0 hover:bg-background/50"
                  >
                    <td className="p-4">
                      <Link 
                        href={`/traces/${trace.trace_id}`}
                        className="text-accent hover:underline font-mono text-sm"
                      >
                        {trace.trace_id.slice(0, 8)}...
                      </Link>
                    </td>
                    <td className="p-4 text-muted">{trace.root_service}</td>
                    <td className="p-4">
                      <StatusBadge status={trace.status} />
                    </td>
                    <td className="p-4 text-muted">
                      {trace.duration_ms ? `${trace.duration_ms}ms` : '-'}
                    </td>
                    <td className="p-4 text-muted">{trace.span_count}</td>
                    <td className="p-4 text-muted text-sm">
                      {formatDistanceToNow(new Date(trace.start_time), { addSuffix: true })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <p className="text-muted text-sm mt-4">
          Total: {data?.total || 0} traces (last 1 hour)
        </p>
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const colors = {
    ok: 'bg-success/20 text-success border-success',
    error: 'bg-error/20 text-error border-error',
  }

  const labels = {
    ok: '✓ OK',
    error: '✗ Error',
  }

  const colorClass = colors[status as keyof typeof colors] || colors.ok
  const label = labels[status as keyof typeof labels] || status

  return (
    <span className={`inline-block px-3 py-1 rounded border text-sm ${colorClass}`}>
      {label}
    </span>
  )
}
