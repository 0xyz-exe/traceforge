'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { alertsApi } from '@/lib/api'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { useState } from 'react'

export default function IncidentsPage() {
  const [statusFilter, setStatusFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['incidents', statusFilter],
    queryFn: () => alertsApi.listIncidents({
      status: statusFilter || undefined,
    }).then(res => res.data),
  })

  if (isLoading) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Incidents</h1>
          <p className="text-muted">Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Incidents</h1>
          <div className="bg-error/20 border border-error text-error px-4 py-3 rounded">
            Error loading incidents. Make sure you're logged in.
          </div>
        </div>
      </div>
    )
  }

  const incidents = data?.incidents || []

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Incidents</h1>
          <div className="flex gap-4">
            <Link href="/" className="text-accent hover:underline">
              ← Home
            </Link>
            <button
              onClick={() => setShowForm(!showForm)}
              className="px-4 py-2 bg-accent text-white rounded hover:opacity-90"
            >
              {showForm ? 'Cancel' : '+ New Incident'}
            </button>
          </div>
        </div>

        {showForm && (
          <CreateIncidentForm 
            onSuccess={() => {
              setShowForm(false)
              queryClient.invalidateQueries({ queryKey: ['incidents'] })
            }}
          />
        )}

        {/* Filters */}
        <div className="bg-card border border-border rounded p-4 mb-4">
          <select 
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-background border border-border rounded px-3 py-2"
          >
            <option value="">All Status</option>
            <option value="open">Open</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>

        {incidents.length === 0 ? (
          <div className="bg-card border border-border rounded p-8 text-center">
            <p className="text-muted mb-4">No incidents found</p>
            <p className="text-sm text-muted">
              Create an incident to track issues
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {incidents.map((incident) => (
              <IncidentCard 
                key={incident.id} 
                incident={incident}
                onUpdate={() => queryClient.invalidateQueries({ queryKey: ['incidents'] })}
              />
            ))}
          </div>
        )}

        <p className="text-muted text-sm mt-4">
          Total: {data?.total || 0} incidents
        </p>
      </div>
    </div>
  )
}

function IncidentCard({ incident, onUpdate }: { incident: any; onUpdate: () => void }) {
  const [expanded, setExpanded] = useState(false)
  
  const acknowledgeMutation = useMutation({
    mutationFn: () => alertsApi.updateIncident(incident.id, { status: 'acknowledged' }),
    onSuccess: onUpdate,
  })

  const resolveMutation = useMutation({
    mutationFn: (notes: string) => alertsApi.updateIncident(incident.id, { 
      status: 'resolved',
      resolution_notes: notes 
    }),
    onSuccess: onUpdate,
  })

  return (
    <div className="bg-card border border-border rounded p-6">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex gap-2 items-center mb-2">
            <h3 className="text-lg font-semibold">{incident.title}</h3>
            <StatusBadge status={incident.status} />
            <SeverityBadge severity={incident.severity} />
          </div>
          {incident.description && (
            <p className="text-muted text-sm mb-2">{incident.description}</p>
          )}
          <p className="text-sm text-muted">
            Started {formatDistanceToNow(new Date(incident.started_at), { addSuffix: true })}
          </p>
        </div>
        <div className="flex gap-2">
          {incident.status === 'open' && (
            <button
              onClick={() => acknowledgeMutation.mutate()}
              disabled={acknowledgeMutation.isPending}
              className="px-3 py-1 text-sm bg-warning/20 text-warning border border-warning rounded hover:opacity-80"
            >
              Acknowledge
            </button>
          )}
          {incident.status !== 'resolved' && (
            <button
              onClick={() => {
                const notes = prompt('Resolution notes:')
                if (notes) resolveMutation.mutate(notes)
              }}
              disabled={resolveMutation.isPending}
              className="px-3 py-1 text-sm bg-success/20 text-success border border-success rounded hover:opacity-80"
            >
              Resolve
            </button>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="px-3 py-1 text-sm bg-card border border-border rounded hover:bg-background"
          >
            {expanded ? 'Hide' : 'Show'} Timeline
          </button>
        </div>
      </div>

      {expanded && (
        <div className="mt-4 pt-4 border-t border-border">
          <h4 className="text-sm font-semibold mb-2">Timeline</h4>
          <div className="space-y-2">
            {incident.timeline.map((entry: any) => (
              <div key={entry.id} className="text-sm">
                <span className="text-muted">
                  {formatDistanceToNow(new Date(entry.created_at), { addSuffix: true })}
                </span>
                {' — '}
                <span className="text-foreground">{entry.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {incident.resolution_notes && (
        <div className="mt-4 pt-4 border-t border-border">
          <p className="text-sm text-muted">
            <strong>Resolution:</strong> {incident.resolution_notes}
          </p>
        </div>
      )}
    </div>
  )
}

function CreateIncidentForm({ onSuccess }: { onSuccess: () => void }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    severity: 'warning',
  })

  const mutation = useMutation({
    mutationFn: () => alertsApi.createIncident(formData),
    onSuccess,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate()
  }

  return (
    <form onSubmit={handleSubmit} className="bg-card border border-border rounded p-6 mb-6">
      <h3 className="text-xl font-semibold mb-4">Create Incident</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm text-muted mb-1">Title *</label>
          <input
            type="text"
            required
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="w-full bg-background border border-border rounded px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm text-muted mb-1">Description</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full bg-background border border-border rounded px-3 py-2"
            rows={3}
          />
        </div>

        <div>
          <label className="block text-sm text-muted mb-1">Severity *</label>
          <select
            value={formData.severity}
            onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
            className="w-full bg-background border border-border rounded px-3 py-2"
          >
            <option value="warning">Warning</option>
            <option value="critical">Critical</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={mutation.isPending}
          className="px-6 py-2 bg-accent text-white rounded hover:opacity-90 disabled:opacity-50"
        >
          {mutation.isPending ? 'Creating...' : 'Create Incident'}
        </button>
      </div>
    </form>
  )
}

function StatusBadge({ status }: { status: string }) {
  const colors = {
    open: 'bg-error/20 text-error border-error',
    acknowledged: 'bg-warning/20 text-warning border-warning',
    resolved: 'bg-success/20 text-success border-success',
  }
  return (
    <span className={`px-2 py-1 rounded border text-xs ${colors[status as keyof typeof colors]}`}>
      {status.toUpperCase()}
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
