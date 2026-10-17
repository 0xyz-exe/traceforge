'use client'

import { useQuery } from '@tanstack/react-query'
import { alertsApi } from '@/lib/api'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { useState } from 'react'

export default function AlertEventsPage() {
  const [stateFilter, setStateFilter] = useState('')

  const { data, isLoading, error } = useQuery({
    queryKey: ['alert-events', stateFilter],
    queryFn: () => alertsApi.listEvents({
      state: stateFilter || undefined,
    }).then(res => res.data),
  })

  if (isLoading) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Alert History</h1>
          <p className="text-muted">Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Alert History</h1>
          <div className="bg-error/20 border border-error text-error px-4 py-3 rounded">
            Error loading alert events. Make sure you're logged in.
          </div>
        </div>
      </div>
    )
  }

  const events = data?.events || []

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Alert History</h1>
          <Link href="/alerts" className="text-accent hover:underline">
            ← Back to Rules
          </Link>
        </div>

        {/* Filters */}
        <div className="bg-card border border-border rounded p-4 mb-4">
          <select 
            value={stateFilter}
            onChange={(e) => setStateFilter(e.target.value)}
            className="bg-background border border-border rounded px-3 py-2"
          >
            <option value="">All States</option>
            <option value="firing">Firing</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>

        {events.length === 0 ? (
          <div className="bg-card border border-border rounded p-8 text-center">
            <p className="text-muted mb-4">No alert events found</p>
            <p className="text-sm text-muted">
              Alert events appear when rules are triggered
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {events.map((event) => (
              <div 
                key={event.id}
                className="bg-card border border-border rounded p-6"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <div className="flex gap-2 items-center mb-2">
                      <h3 className="text-lg font-semibold">{event.rule_name}</h3>
                      <StateBadge state={event.state} />
                      <SeverityBadge severity={event.severity} />
                    </div>
                    <p className="text-foreground mb-2">{event.message}</p>
                  </div>
                  <span className="text-sm text-muted">
                    {formatDistanceToNow(new Date(event.fired_at), { addSuffix: true })}
                  </span>
                </div>

                {Object.keys(event.details).length > 0 && (
                  <details className="mt-2">
                    <summary className="text-sm text-muted cursor-pointer">
                      Details
                    </summary>
                    <pre className="text-xs mt-2 text-muted bg-background p-2 rounded">
                      {JSON.stringify(event.details, null, 2)}
                    </pre>
                  </details>
                )}

                {event.resolved_at && (
                  <p className="text-sm text-muted mt-2">
                    Resolved {formatDistanceToNow(new Date(event.resolved_at), { addSuffix: true })}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}

        <p className="text-muted text-sm mt-4">
          Total: {data?.total || 0} events
        </p>

        <div className="mt-8">
          <Link href="/incidents" className="text-accent hover:underline">
            View Incidents →
          </Link>
        </div>
      </div>
    </div>
  )
}

function StateBadge({ state }: { state: string }) {
  const colors = {
    firing: 'bg-error/20 text-error border-error',
    resolved: 'bg-success/20 text-success border-success',
  }
  return (
    <span className={`px-2 py-1 rounded border text-xs ${colors[state as keyof typeof colors]}`}>
      {state.toUpperCase()}
    </span>
  )
}

function SeverityBadge({ severity }: { severity: string }) {
  const colors = {
    warning: 'bg-warning/20 text-warning border-warning',
    critical: 'bg-error/20 text-error border-error',
  }
  return (
    <span className={`px-2 py-1 rounded border text-xs ${colors[severity as keyof typeof colors]}`}>
      {severity.toUpperCase()}
    </span>
  )
}
