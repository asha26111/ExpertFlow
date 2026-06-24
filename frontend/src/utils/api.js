import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 300000,   // 5 minutes — Gemini may take time on complex queries
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    // Only auto-logout on 401 for non-auth routes
    if (err.response?.status === 401) {
      const url = err.config?.url || ''
      const isAuthRoute = url.includes('/auth/login') || url.includes('/auth/register')
      if (!isAuthRoute) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export default api
