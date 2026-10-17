'use client'

import { useQuery } from '@tanstack/react-query'
import { alertsApi } from '@/lib/api'
import Link from 'next/link'
import { useState } from 'react'

export default function AlertRulesPage() {
  const [showForm, setShowForm] = useState(false)

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alert-rules'],
    queryFn: () => alertsApi.listRules().then(res => res.data),
  })

  if (isLoading) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Alert Rules</h1>
          <p className="text-muted">Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Alert Rules</h1>
          <div className="bg-error/20 border border-error text-error px-4 py-3 rounded">
            Error loading alert rules. Make sure you're logged in.
          </div>
        </div>
      </div>
    )
  }

  const rules = data?.rules || []

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Alert Rules</h1>
          <div className="flex gap-4">
            <Link href="/" className="text-accent hover:underline">
              ← Home
            </Link>
            <button
              onClick={() => setShowForm(!showForm)}
              className="px-4 py-2 bg-accent text-white rounded hover:opacity-90"
            >
              {showForm ? 'Cancel' : '+ New Rule'}
            </button>
          </div>
        </div>

        {showForm && (
          <CreateRuleForm 
            onSuccess={() => {
              setShowForm(false)
              refetch()
            }}
          />
        )}

        {rules.length === 0 ? (
          <div className="bg-card border border-border rounded p-8 text-center">
            <p className="text-muted mb-4">No alert rules configured</p>
            <p className="text-sm text-muted">
              Create a rule to monitor metrics and receive alerts
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {rules.map((rule) => (
              <div 
                key={rule.id}
                className="bg-card border border-border rounded p-6"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold mb-2">{rule.name}</h3>
                    {rule.description && (
                      <p className="text-muted text-sm mb-2">{rule.description}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <SeverityBadge severity={rule.severity} />
                    <EnabledBadge enabled={rule.enabled} />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted">Condition:</span>
                    <span className="ml-2">{rule.condition_type}</span>
                  </div>
                  <div>
                    <span className="text-muted">Service:</span>
                    <span className="ml-2">{rule.service || 'All'}</span>
                  </div>
                  {rule.metric_name && (
                    <div>
                      <span className="text-muted">Metric:</span>
                      <span className="ml-2 font-mono text-xs">{rule.metric_name}</span>
                    </div>
                  )}
                  {rule.threshold !== null && (
                    <div>
                      <span className="text-muted">Threshold:</span>
                      <span className="ml-2">{rule.comparison} {rule.threshold}</span>
                    </div>
                  )}
                  <div>
                    <span className="text-muted">Window:</span>
                    <span className="ml-2">{rule.window_seconds}s</span>
                  </div>
                  <div>
                    <span className="text-muted">Cooldown:</span>
                    <span className="ml-2">{rule.cooldown_seconds}s</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8">
          <Link href="/alerts/events" className="text-accent hover:underline">
            View Alert History →
          </Link>
        </div>
      </div>
    </div>
  )
}

function CreateRuleForm({ onSuccess }: { onSuccess: () => void }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    service: '',
    condition_type: 'metric_threshold',
    metric_name: '',
    threshold: '',
    comparison: 'gt',
    aggregation: 'avg',
    window_seconds: '300',
    severity: 'warning',
    cooldown_seconds: '300',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      await alertsApi.createRule({
        name: formData.name,
        description: formData.description || undefined,
        service: formData.service || undefined,
        condition_type: formData.condition_type as any,
        metric_name: formData.metric_name || undefined,
        threshold: formData.threshold ? parseFloat(formData.threshold) : undefined,
        comparison: formData.comparison as any,
        aggregation: formData.aggregation as any,
        window_seconds: parseInt(formData.window_seconds),
        severity: formData.severity as any,
        cooldown_seconds: parseInt(formData.cooldown_seconds),
      })
      onSuccess()
    } catch (err) {
      alert('Failed to create alert rule')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-card border border-border rounded p-6 mb-6">
      <h3 className="text-xl font-semibold mb-4">Create Alert Rule</h3>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-muted mb-1">Name *</label>
          <input
            type="text"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full bg-background border border-border rounded px-3 py-2"
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

        <div className="col-span-2">
          <label className="block text-sm text-muted mb-1">Description</label>
          <input
            type="text"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full bg-background border border-border rounded px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm text-muted mb-1">Service (optional)</label>
          <input
            type="text"
            value={formData.service}
            onChange={(e) => setFormData({ ...formData, service: e.target.value })}
            className="w-full bg-background border border-border rounded px-3 py-2"
            placeholder="Leave empty for all services"
          />
        </div>

        <div>
          <label className="block text-sm text-muted mb-1">Metric Name *</label>
          <input
            type="text"
            required
            value={formData.metric_name}
            onChange={(e) => setFormData({ ...formData, metric_name: e.target.value })}
            className="w-full bg-background border border-border rounded px-3 py-2"
            placeholder="e.g. http.errors.total"
          />
        </div>

        <div>
          <label className="block text-sm text-muted mb-1">Comparison *</label>
          <select
            value={formData.comparison}
            onChange={(e) => setFormData({ ...formData, comparison: e.target.value })}
            className="w-full bg-background border border-border rounded px-3 py-2"
          >
            <option value="gt">&gt; Greater than</option>
            <option value="gte">&gt;= Greater or equal</option>
            <option value="lt">&lt; Less than</option>
            <option value="lte">&lt;= Less or equal</option>
            <option value="eq">= Equal</option>
          </select>
        </div>

        <div>
          <label className="block text-sm text-muted mb-1">Threshold *</label>
          <input
            type="number"
            step="any"
            required
            value={formData.threshold}
            onChange={(e) => setFormData({ ...formData, threshold: e.target.value })}
            className="w-full bg-background border border-border rounded px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm text-muted mb-1">Aggregation *</label>
          <select
            value={formData.aggregation}
            onChange={(e) => setFormData({ ...formData, aggregation: e.target.value })}
            className="w-full bg-background border border-border rounded px-3 py-2"
          >
            <option value="avg">Average</option>
            <option value="sum">Sum</option>
            <option value="min">Min</option>
            <option value="max">Max</option>
            <option value="count">Count</option>
            <option value="p50">P50</option>
            <option value="p95">P95</option>
            <option value="p99">P99</option>
          </select>
        </div>

        <div>
          <label className="block text-sm text-muted mb-1">Window (seconds) *</label>
          <input
            type="number"
            required
            min="60"
            max="3600"
            value={formData.window_seconds}
            onChange={(e) => setFormData({ ...formData, window_seconds: e.target.value })}
            className="w-full bg-background border border-border rounded px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm text-muted mb-1">Cooldown (seconds) *</label>
          <input
            type="number"
            required
            min="60"
            max="7200"
            value={formData.cooldown_seconds}
            onChange={(e) => setFormData({ ...formData, cooldown_seconds: e.target.value })}
            className="w-full bg-background border border-border rounded px-3 py-2"
          />
        </div>
      </div>

      <button
        type="submit"
        className="mt-4 px-6 py-2 bg-accent text-white rounded hover:opacity-90"
      >
        Create Rule
      </button>
    </form>
  )
}

function SeverityBadge({ severity }: { severity: string }) {
  const colors = {
    warning: 'bg-warning/20 text-warning border-warning',
    critical: 'bg-error/20 text-error border-error',
  }
  return (
    <span className={`px-3 py-1 rounded border text-sm ${colors[severity as keyof typeof colors]}`}>
      {severity.toUpperCase()}
    </span>
  )
}

function EnabledBadge({ enabled }: { enabled: boolean }) {
  return enabled ? (
    <span className="px-3 py-1 rounded border text-sm bg-success/20 text-success border-success">
      Enabled
    </span>
  ) : (
    <span className="px-3 py-1 rounded border text-sm bg-muted/20 text-muted border-muted">
      Disabled
    </span>
  )
}
