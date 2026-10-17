'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { servicesApi } from '@/lib/api'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { FormEvent, useState } from 'react'

export default function ServicesPage() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [environment, setEnvironment] = useState('production')
  const [version, setVersion] = useState('')
  const [formError, setFormError] = useState('')

  const { data, isLoading, error } = useQuery({
    queryKey: ['services'],
    queryFn: () => servicesApi.list().then(res => res.data),
  })

  const createService = useMutation({
    mutationFn: () => servicesApi.create({
      name: name.trim(),
      environment,
      version: version.trim() || undefined,
    }),
    onSuccess: () => {
      setName('')
      setEnvironment('production')
      setVersion('')
      setFormError('')
      setShowForm(false)
      queryClient.invalidateQueries({ queryKey: ['services'] })
    },
    onError: (requestError: any) => {
      const detail = requestError.response?.data?.detail
      setFormError(typeof detail === 'string' ? detail : 'Unable to register the service.')
    },
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError('')
    if (!name.trim()) {
      setFormError('Service name is required.')
      return
    }
    createService.mutate()
  }

  if (isLoading) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Services</h1>
          <p className="text-muted">Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Services</h1>
          <div className="bg-error/20 border border-error text-error px-4 py-3 rounded">
            Error loading services. Make sure the backend is running.
          </div>
        </div>
      </div>
    )
  }

  const services = data?.services || []

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Services</h1>
          <div className="flex items-center gap-4">
            <button
              onClick={() => {
                setShowForm(!showForm)
                setFormError('')
              }}
              className="px-4 py-2 bg-accent text-white rounded hover:opacity-90"
            >
              {showForm ? 'Cancel' : '+ Add service'}
            </button>
            <Link href="/" className="text-accent hover:underline">
              ← Home
            </Link>
          </div>
        </div>

        {showForm && (
          <form onSubmit={handleSubmit} className="bg-card border border-border rounded p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Register a service</h2>
            {formError && (
              <div className="bg-error/20 border border-error text-error px-4 py-3 rounded mb-4">
                {formError}
              </div>
            )}
            <div className="grid gap-4 md:grid-cols-3">
              <label className="block">
                <span className="text-sm text-muted">Service name</span>
                <input
                  required
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="api-gateway"
                  className="mt-1 w-full bg-background border border-border rounded px-3 py-2"
                />
              </label>
              <label className="block">
                <span className="text-sm text-muted">Environment</span>
                <select
                  value={environment}
                  onChange={(event) => setEnvironment(event.target.value)}
                  className="mt-1 w-full bg-background border border-border rounded px-3 py-2"
                >
                  <option value="production">Production</option>
                  <option value="staging">Staging</option>
                  <option value="development">Development</option>
                </select>
              </label>
              <label className="block">
                <span className="text-sm text-muted">Version (optional)</span>
                <input
                  value={version}
                  onChange={(event) => setVersion(event.target.value)}
                  placeholder="1.0.0"
                  className="mt-1 w-full bg-background border border-border rounded px-3 py-2"
                />
              </label>
            </div>
            <button
              type="submit"
              disabled={createService.isPending}
              className="mt-4 px-4 py-2 bg-accent text-white rounded hover:opacity-90 disabled:opacity-50"
            >
              {createService.isPending ? 'Registering...' : 'Register service'}
            </button>
          </form>
        )}

        {services.length === 0 ? (
          <div className="bg-card border border-border rounded p-8 text-center">
            <p className="text-muted mb-4">No services registered yet</p>
            <p className="text-sm text-muted">
              Add a service here, or register one automatically by sending telemetry to the ingestion endpoint.
            </p>
          </div>
        ) : (
          <div className="bg-card border border-border rounded overflow-hidden">
            <table className="w-full">
              <thead className="bg-background border-b border-border">
                <tr>
                  <th className="text-left p-4">Name</th>
                  <th className="text-left p-4">Environment</th>
                  <th className="text-left p-4">Status</th>
                  <th className="text-left p-4">Last Telemetry</th>
                </tr>
              </thead>
              <tbody>
                {services.map((service) => (
                  <tr 
                    key={service.id}
                    className="border-b border-border last:border-b-0 hover:bg-background/50"
                  >
                    <td className="p-4">
                      <Link 
                        href={`/services/${service.id}`}
                        className="text-accent hover:underline font-medium"
                      >
                        {service.name}
                      </Link>
                    </td>
                    <td className="p-4 text-muted">{service.environment}</td>
                    <td className="p-4">
                      <StatusBadge status={service.health_status} />
                    </td>
                    <td className="p-4 text-muted text-sm">
                      {service.last_telemetry_at 
                        ? formatDistanceToNow(new Date(service.last_telemetry_at), { addSuffix: true })
                        : 'Never'
                      }
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <p className="text-muted text-sm mt-4">
          Total: {data?.total || 0} services
        </p>
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const colors = {
    healthy: 'bg-success/20 text-success border-success',
    stale: 'bg-warning/20 text-warning border-warning',
    down: 'bg-error/20 text-error border-error',
    unknown: 'bg-muted/20 text-muted border-muted',
  }

  const labels = {
    healthy: '● Healthy',
    stale: '● Stale',
    down: '● Down',
    unknown: '● Unknown',
  }

  const colorClass = colors[status as keyof typeof colors] || colors.unknown
  const label = labels[status as keyof typeof labels] || '● Unknown'

  return (
    <span className={`inline-block px-3 py-1 rounded border text-sm ${colorClass}`}>
      {label}
    </span>
  )
}
