import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold mb-4">TraceForge</h1>
      <p className="text-muted mb-8">Developer observability platform</p>
      
      <div className="flex gap-4">
        <Link 
          href="/login"
          className="px-6 py-3 bg-accent text-white rounded hover:opacity-90"
        >
          Sign in
        </Link>
        <Link
          href="/services" 
          className="px-6 py-3 bg-accent text-white rounded hover:opacity-90"
        >
          View Services
        </Link>
        <Link 
          href="/logs" 
          className="px-6 py-3 bg-card border border-border rounded hover:bg-background"
        >
          View Logs
        </Link>
        <Link 
          href="/traces" 
          className="px-6 py-3 bg-card border border-border rounded hover:bg-background"
        >
          View Traces
        </Link>
        <Link 
          href="/alerts" 
          className="px-6 py-3 bg-card border border-border rounded hover:bg-background"
        >
          Alerts
        </Link>
        <Link 
          href="/incidents" 
          className="px-6 py-3 bg-card border border-border rounded hover:bg-background"
        >
          Incidents
        </Link>
      </div>
    </div>
  )
}
