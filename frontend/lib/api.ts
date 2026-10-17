import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export const api = axios.create({
  baseURL: API_URL,
})

// Add auth token interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

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
