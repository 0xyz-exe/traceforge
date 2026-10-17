import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export const api = axios.create({
  baseURL: API_URL,
})

// Add auth token interceptor
api.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (
      typeof window !== 'undefined' &&
      error.response?.status === 401 &&
      window.location.pathname !== '/login'
    ) {
      window.location.assign(`/login?returnTo=${encodeURIComponent(window.location.pathname)}`)
    }
    return Promise.reject(error)
  },
)

// Types
export interface Service {
  id: string
  name: string
  environment: string
  version: string | null
  last_telemetry_at: string | null
  health_status: 'healthy' | 'stale' | 'down' | 'unknown'
  created_at: string
}

export interface ServiceListResponse {
  services: Service[]
  total: number
  limit: number
  offset: number
}

export interface MetricDataPoint {
  timestamp: string
  value: number
}

export interface MetricQueryResponse {
  metric: string
  aggregation: string
  data_points: MetricDataPoint[]
  unit: string | null
}

// API functions
export const authApi = {
  register: (data: { email: string; password: string; full_name: string; workspace_name: string }) =>
    api.post('/auth/register', data),
  
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
}

export const servicesApi = {
  list: (params?: { environment?: string; limit?: number; offset?: number }) =>
    api.get<ServiceListResponse>('/services', { params }),
  
  get: (id: string) =>
    api.get<Service>(`/services/${id}`),
  
  create: (data: { name: string; environment: string; version?: string }) =>
    api.post<Service>('/services', data),
}

export const metricsApi = {
  query: (params: {
    service: string
    metric: string
    aggregation: string
    start: string
    end: string
    interval?: number
  }) => api.get<MetricQueryResponse>('/metrics/query', { params }),
}

export interface LogEntry {
  id: string
  timestamp: string
  severity: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL'
  service: string
  message: string
  trace_id: string | null
  span_id: string | null
  attributes: Record<string, any>
}

export interface LogsSearchResponse {
  logs: LogEntry[]
  total: number
  limit: number
  offset: number
}

export interface Trace {
  trace_id: string
  root_service: string
  start_time: string
  duration_ms: number | null
  status: 'ok' | 'error'
  span_count: number
}

export interface Span {
  span_id: string
  parent_span_id: string | null
  service: string
  operation_name: string
  start_time: string
  end_time: string | null
  duration_ms: number | null
  status: 'ok' | 'error'
  attributes: Record<string, any>
  events: Array<Record<string, any>>
}

export interface TraceDetail {
  trace_id: string
  root_service: string
  start_time: string
  duration_ms: number | null
  status: 'ok' | 'error'
  spans: Span[]
}

export interface TracesListResponse {
  traces: Trace[]
  total: number
  limit: number
}

export const logsApi = {
  search: (params: {
    start: string
    end: string
    service?: string
    severity?: string
    search?: string
    trace_id?: string
    limit?: number
    offset?: number
  }) => api.get<LogsSearchResponse>('/logs', { params }),
}

export const tracesApi = {
  list: (params: {
    start: string
    end: string
    service?: string
    status?: string
    min_duration_ms?: number
    limit?: number
    offset?: number
  }) => api.get<TracesListResponse>('/traces', { params }),
  
  get: (trace_id: string) => api.get<TraceDetail>(`/traces/${trace_id}`),
}

// Alert Rules
export interface AlertRule {
  id: string
  name: string
  description: string | null
  service: string | null
  condition_type: string
  metric_name: string | null
  threshold: number | null
  comparison: string | null
  aggregation: string | null
  window_seconds: number
  severity: 'warning' | 'critical'
  enabled: boolean
  cooldown_seconds: number
  created_at: string
}

export interface AlertRulesListResponse {
  rules: AlertRule[]
  total: number
}

export interface AlertRuleCreate {
  name: string
  description?: string
  service?: string
  condition_type: 'metric_threshold' | 'error_rate' | 'missing_telemetry'
  metric_name?: string
  threshold?: number
  comparison?: 'gt' | 'lt' | 'gte' | 'lte' | 'eq'
  aggregation?: 'avg' | 'sum' | 'min' | 'max' | 'count' | 'p50' | 'p95' | 'p99'
  window_seconds?: number
  severity: 'warning' | 'critical'
  cooldown_seconds?: number
}

export interface AlertEvent {
  id: string
  alert_rule_id: string
  rule_name: string
  state: 'firing' | 'resolved'
  severity: 'warning' | 'critical'
  message: string
  details: Record<string, any>
  fired_at: string
  resolved_at: string | null
}

export interface AlertEventsListResponse {
  events: AlertEvent[]
  total: number
  limit: number
}

export interface Incident {
  id: string
  title: string
  description: string | null
  severity: 'warning' | 'critical'
  status: 'open' | 'acknowledged' | 'resolved'
  assigned_to: string | null
  created_by: string | null
  started_at: string
  acknowledged_at: string | null
  resolved_at: string | null
  resolution_notes: string | null
  metadata: Record<string, any>
  timeline: IncidentTimelineEntry[]
}

export interface IncidentTimelineEntry {
  id: string
  event_type: string
  message: string
  created_by: string | null
  created_at: string
}

export interface IncidentsListResponse {
  incidents: Incident[]
  total: number
  limit: number
}

export const alertsApi = {
  listRules: () => api.get<AlertRulesListResponse>('/alerts/rules'),
  
  createRule: (data: AlertRuleCreate) => api.post<AlertRule>('/alerts/rules', data),
  
  updateRule: (id: string, data: Partial<AlertRuleCreate>) => 
    api.patch<AlertRule>(`/alerts/rules/${id}`, data),
  
  deleteRule: (id: string) => api.delete(`/alerts/rules/${id}`),
  
  listEvents: (params?: { state?: string; limit?: number; offset?: number }) =>
    api.get<AlertEventsListResponse>('/alerts/events', { params }),
  
  listIncidents: (params?: { status?: string; limit?: number; offset?: number }) =>
    api.get<IncidentsListResponse>('/alerts/incidents', { params }),
  
  createIncident: (data: { title: string; description?: string; severity: string; alert_event_id?: string }) =>
    api.post<Incident>('/alerts/incidents', data),
  
  updateIncident: (id: string, data: { status?: string; assigned_to?: string; resolution_notes?: string }) =>
    api.patch<Incident>(`/alerts/incidents/${id}`, data),
}
