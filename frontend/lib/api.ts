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
  }) => api.get('/metrics/query', { params }),
}
