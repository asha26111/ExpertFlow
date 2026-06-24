import { create } from 'zustand'
import api from '../utils/api'

// Helper to extract the clearest error message from any axios error
function extractError(err) {
  // Network error (backend not running)
  if (!err.response) {
    return `Cannot connect to server. Make sure the backend is running on port 8000.\n(${err.message})`
  }
  const data = err.response.data
  // FastAPI validation errors come as { detail: [ {loc, msg, type} ] }
  if (Array.isArray(data?.detail)) {
    return data.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ')
  }
  // FastAPI HTTPException: { detail: "string" }
  if (typeof data?.detail === 'string') {
    return data.detail
  }
  // Fallback
  return `Error ${err.response.status}: ${err.response.statusText || 'Request failed'}`
}

export const useAuthStore = create((set) => ({
  user: (() => {
    try { return JSON.parse(localStorage.getItem('user') || 'null') } catch { return null }
  })(),
  token: localStorage.getItem('token') || null,
  loading: false,
  error: null,

  register: async (data) => {
    set({ loading: true, error: null })
    try {
      const res = await api.post('/auth/register', data)
      const { access_token, user } = res.data
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(user))
      set({ token: access_token, user, loading: false, error: null })
      return { success: true }
    } catch (err) {
      const msg = extractError(err)
      set({ error: msg, loading: false })
      return { success: false, error: msg }
    }
  },

  login: async (data) => {
    set({ loading: true, error: null })
    try {
      const res = await api.post('/auth/login', data)
      const { access_token, user } = res.data
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(user))
      set({ token: access_token, user, loading: false, error: null })
      return { success: true }
    } catch (err) {
      const msg = extractError(err)
      set({ error: msg, loading: false })
      return { success: false, error: msg }
    }
  },

  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    set({ user: null, token: null, error: null })
  },

  updateUser: (user) => {
    localStorage.setItem('user', JSON.stringify(user))
    set({ user })
  },

  clearError: () => set({ error: null }),
}))
