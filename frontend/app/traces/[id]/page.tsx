'use client'

import { useQuery } from '@tanstack/react-query'
import { tracesApi, Span } from '@/lib/api'
import Link from 'next/link'
import { use } from 'react'

export default function TraceDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  
  const { data: trace, isLoading, error } = useQuery({
    queryKey: ['trace', id],
    queryFn: () => tracesApi.get(id).then(res => res.data),
  })

  if (isLoading) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Trace Detail</h1>
          <p className="text-muted">Loading...</p>
        </div>
      </div>
    )
  }

  if (error || !trace) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Trace Detail</h1>
          <div className="bg-error/20 border border-error text-error px-4 py-3 rounded">
            Trace not found or error loading.
          </div>
          <Link href="/traces" className="text-accent hover:underline mt-4 inline-block">
            ← Back to traces
          </Link>
        </div>
      </div>
    )
  }

  // Build span hierarchy
  const spanMap = new Map<string, Span & { children: Span[] }>()
  trace.spans.forEach(span => {
    spanMap.set(span.span_id, { ...span, children: [] })
  })
  
  const rootSpans: (Span & { children: Span[] })[] = []
  trace.spans.forEach(span => {
    const spanNode = spanMap.get(span.span_id)!
    if (span.parent_span_id) {
      const parent = spanMap.get(span.parent_span_id)
      if (parent) {
        parent.children.push(spanNode)
      } else {
        rootSpans.push(spanNode)
      }
    } else {
      rootSpans.push(spanNode)
    }
  })

  const traceStartMs = new Date(trace.start_time).getTime()
  const traceDurationMs = trace.duration_ms || 1

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <Link href="/traces" className="text-accent hover:underline mb-4 inline-block">
          ← Back to traces
        </Link>
        
        <div className="bg-card border border-border rounded p-6 mb-6">
          <h1 className="text-2xl font-bold mb-4">Trace {trace.trace_id}</h1>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted">Service:</span>
              <span className="ml-2">{trace.root_service}</span>
            </div>
            <div>
              <span className="text-muted">Duration:</span>
              <span className="ml-2">{trace.duration_ms}ms</span>
            </div>
            <div>
              <span className="text-muted">Status:</span>
              <span className={`ml-2 ${trace.status === 'ok' ? 'text-success' : 'text-error'}`}>
                {trace.status === 'ok' ? '✓ OK' : '✗ Error'}
              </span>
            </div>
            <div>
              <span className="text-muted">Spans:</span>
              <span className="ml-2">{trace.spans.length}</span>
            </div>
          </div>
        </div>

        <h2 className="text-xl font-bold mb-4">Span Waterfall</h2>
        <div className="bg-card border border-border rounded p-4">
          {rootSpans.map(span => (
            <SpanRow 
              key={span.span_id}
              span={span}
              traceStartMs={traceStartMs}
              traceDurationMs={traceDurationMs}
              depth={0}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

function SpanRow({ 
  span, 
  traceStartMs, 
  traceDurationMs, 
  depth 
}: { 
  span: Span & { children: Span[] }
  traceStartMs: number
  traceDurationMs: number
  depth: number
}) {
  const spanStartMs = new Date(span.start_time).getTime()
  const spanDurationMs = span.duration_ms || 0
  
  const offsetPct = ((spanStartMs - traceStartMs) / traceDurationMs) * 100
  const widthPct = (spanDurationMs / traceDurationMs) * 100

  return (
    <div className="mb-2">
      <div className="flex items-center gap-2 text-sm mb-1" style={{ paddingLeft: `${depth * 20}px` }}>
        <span className="text-muted w-32 truncate">{span.service}</span>
        <span className="flex-1 truncate">{span.operation_name}</span>
        <span className="text-muted">{spanDurationMs}ms</span>
        <span className={span.status === 'ok' ? 'text-success' : 'text-error'}>
          {span.status === 'ok' ? '✓' : '✗'}
        </span>
      </div>
      
      <div className="relative h-6 bg-background rounded mb-1" style={{ paddingLeft: `${depth * 20}px` }}>
        <div 
          className={`absolute h-full rounded ${span.status === 'ok' ? 'bg-accent' : 'bg-error'}`}
          style={{ 
            left: `${offsetPct}%`, 
            width: `${Math.max(widthPct, 0.5)}%` 
          }}
        />
      </div>

      {span.children.map(child => (
        <SpanRow 
          key={child.span_id}
          span={child}
          traceStartMs={traceStartMs}
          traceDurationMs={traceDurationMs}
          depth={depth + 1}
        />
      ))}
    </div>
  )
}
