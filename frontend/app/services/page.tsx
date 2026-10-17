'use client'

import { useQuery } from '@tanstack/react-query'
import { servicesApi } from '@/lib/api'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'

export default function ServicesPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['services'],
    queryFn: () => servicesApi.list().then(res => res.data),
  })

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
          <Link 
            href="/"
            className="text-accent hover:underline"
          >
            ← Home
          </Link>
        </div>

        {services.length === 0 ? (
          <div className="bg-card border border-border rounded p-8 text-center">
            <p className="text-muted mb-4">No services registered yet</p>
            <p className="text-sm text-muted">
              Register a service by sending telemetry to the ingestion endpoint
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
