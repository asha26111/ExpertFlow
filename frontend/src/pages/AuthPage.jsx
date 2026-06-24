import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'
import api from '../utils/api'

export default function AuthPage({ mode = 'login' }) {
  const navigate = useNavigate()
  const { login, register, loading, error, clearError, user } = useAuthStore()
  const [isLogin, setIsLogin] = useState(mode === 'login')
  const [showPass, setShowPass] = useState(false)
  const [backendStatus, setBackendStatus] = useState('checking') // 'checking' | 'ok' | 'error'
  const [form, setForm] = useState({ email: '', password: '', username: '', full_name: '' })
  const [fieldErrors, setFieldErrors] = useState({})

  // Redirect if already logged in
  useEffect(() => { if (user) navigate('/dashboard') }, [user])

  // Check backend health on mount
  useEffect(() => {
    api.get('/health', { timeout: 35000 })
      .then(() => setBackendStatus('ok'))
      .catch(() => setBackendStatus('error'))
  }, [])

  useEffect(() => {
    clearError()
    setFieldErrors({})
    setForm({ email: '', password: '', username: '', full_name: '' })
  }, [isLogin])

  const validate = () => {
    const errs = {}
    if (!form.email.trim()) {
      errs.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
      errs.email = 'Enter a valid email address'
    }
    if (!form.password) {
      errs.password = 'Password is required'
    } else if (form.password.length < 6) {
      errs.password = 'Password must be at least 6 characters'
    }
    if (!isLogin) {
      if (!form.username.trim()) {
        errs.username = 'Username is required'
      } else if (form.username.trim().length < 3) {
        errs.username = 'Username must be at least 3 characters'
      } else if (!/^[a-zA-Z0-9_]+$/.test(form.username.trim())) {
        errs.username = 'Only letters, numbers, underscores allowed'
      }
    }
    setFieldErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    clearError()
    if (!validate()) return

    const payload = isLogin
      ? { email: form.email.trim(), password: form.password }
      : {
          email: form.email.trim(),
          password: form.password,
          username: form.username.trim(),
          full_name: form.full_name.trim() || undefined,
        }

    const result = isLogin ? await login(payload) : await register(payload)

    if (result.success) {
      toast.success(isLogin ? '👋 Welcome back!' : '🎉 Account created!')
      navigate('/dashboard')
    }
    // error is shown in UI from store
  }

  const setField = (k, v) => {
    setForm(f => ({ ...f, [k]: v }))
    if (fieldErrors[k]) setFieldErrors(e => ({ ...e, [k]: null }))
    clearError()
  }

  return (
    <div className="mesh-bg min-h-screen flex items-center justify-center p-4">
      {/* Animated background orbs */}
      <div className="fixed top-1/4 left-1/4 w-96 h-96 rounded-full bg-indigo-600/10 blur-3xl pointer-events-none animate-pulse-slow" />
      <div className="fixed bottom-1/4 right-1/4 w-64 h-64 rounded-full bg-violet-600/10 blur-3xl pointer-events-none animate-pulse-slow" style={{animationDelay:'1.2s'}} />

      <div className="relative z-10 w-full max-w-md animate-slide-up">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 glow-indigo"
            style={{background:'linear-gradient(135deg,#6366f1,#8b5cf6)'}}>
            <span className="text-2xl">🧠</span>
          </div>
          <h1 className="text-3xl font-display font-700 gradient-text">ExpertFlow</h1>
          <p className="text-sm mt-1" style={{color:'var(--text-muted)'}}>AI-Powered Learning Platform</p>
        </div>

        {/* Backend status indicator */}
        <div className="flex justify-center mb-4">
          {backendStatus === 'checking' && (
            <div className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-full"
              style={{background:'rgba(99,102,241,0.1)',color:'#a5b4fc',border:'1px solid rgba(99,102,241,0.2)'}}>
              <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
              Connecting to server…
            </div>
          )}
          {backendStatus === 'ok' && (
            <div className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-full"
              style={{background:'rgba(16,185,129,0.1)',color:'#10b981',border:'1px solid rgba(16,185,129,0.2)'}}>
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Server connected
            </div>
          )}
          {backendStatus === 'error' && (
            <div className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-full"
              style={{background:'rgba(239,68,68,0.1)',color:'#fca5a5',border:'1px solid rgba(239,68,68,0.3)'}}>
              <div className="w-1.5 h-1.5 rounded-full bg-red-400" />
              Backend offline — start it with <code className="ml-1 font-mono">python run.py</code>
            </div>
          )}
        </div>

        {/* Card */}
        <div className="glass rounded-2xl p-8" style={{boxShadow:'0 25px 50px rgba(0,0,0,0.5)'}}>
          {/* Tab switcher */}
          <div className="flex mb-6 p-1 rounded-xl" style={{background:'var(--bg-secondary)'}}>
            {['Sign In', 'Create Account'].map((label, i) => (
              <button key={label} onClick={() => setIsLogin(i === 0)}
                className="flex-1 py-2.5 rounded-lg text-sm font-display font-500 transition-all"
                style={isLogin === (i === 0)
                  ? {background:'linear-gradient(135deg,#6366f1,#8b5cf6)',color:'#fff',boxShadow:'0 4px 15px rgba(99,102,241,0.3)'}
                  : {color:'var(--text-muted)'}}>
                {label}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} noValidate>
            {/* Register-only fields */}
            {!isLogin && (
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div>
                  <label className="block text-xs mb-1.5 font-500" style={{color:'var(--text-secondary)'}}>
                    Username <span style={{color:'var(--danger)'}}>*</span>
                  </label>
                  <input
                    className="input-field"
                    placeholder="john_doe"
                    autoComplete="username"
                    value={form.username}
                    onChange={e => setField('username', e.target.value)}
                    style={fieldErrors.username ? {borderColor:'var(--danger)'} : {}}
                  />
                  {fieldErrors.username && (
                    <p className="text-xs mt-1" style={{color:'var(--danger)'}}>⚠ {fieldErrors.username}</p>
                  )}
                </div>
                <div>
                  <label className="block text-xs mb-1.5 font-500" style={{color:'var(--text-secondary)'}}>Full Name</label>
                  <input
                    className="input-field"
                    placeholder="John Doe"
                    autoComplete="name"
                    value={form.full_name}
                    onChange={e => setField('full_name', e.target.value)}
                  />
                </div>
              </div>
            )}

            {/* Email */}
            <div className="mb-4">
              <label className="block text-xs mb-1.5 font-500" style={{color:'var(--text-secondary)'}}>
                Email Address <span style={{color:'var(--danger)'}}>*</span>
              </label>
              <input
                className="input-field"
                type="email"
                placeholder="you@example.com"
                autoComplete="email"
                value={form.email}
                onChange={e => setField('email', e.target.value)}
                style={fieldErrors.email ? {borderColor:'var(--danger)'} : {}}
              />
              {fieldErrors.email && (
                <p className="text-xs mt-1" style={{color:'var(--danger)'}}>⚠ {fieldErrors.email}</p>
              )}
            </div>

            {/* Password */}
            <div className="mb-6">
              <label className="block text-xs mb-1.5 font-500" style={{color:'var(--text-secondary)'}}>
                Password <span style={{color:'var(--danger)'}}>*</span>
              </label>
              <div className="relative">
                <input
                  className="input-field pr-10"
                  type={showPass ? 'text' : 'password'}
                  placeholder="Minimum 6 characters"
                  autoComplete={isLogin ? 'current-password' : 'new-password'}
                  value={form.password}
                  onChange={e => setField('password', e.target.value)}
                  style={fieldErrors.password ? {borderColor:'var(--danger)'} : {}}
                />
                <button type="button" onClick={() => setShowPass(p => !p)}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                  style={{color:'var(--text-muted)', background:'none', border:'none', cursor:'pointer'}}>
                  {showPass ? '🙈' : '👁'}
                </button>
              </div>
              {fieldErrors.password && (
                <p className="text-xs mt-1" style={{color:'var(--danger)'}}>⚠ {fieldErrors.password}</p>
              )}
            </div>

            {/* Server/API error */}
            {error && (
              <div className="mb-5 p-3.5 rounded-xl text-sm whitespace-pre-wrap"
                style={{background:'rgba(239,68,68,0.08)',border:'1px solid rgba(239,68,68,0.3)',color:'#fca5a5'}}>
                ❌ {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2 text-base"
              style={{height:'48px'}}>
              {loading
                ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                : (isLogin ? '→ Sign In' : '✓ Create Account')
              }
            </button>
          </form>

          <p className="text-center text-sm mt-5" style={{color:'var(--text-muted)'}}>
            {isLogin ? "Don't have an account? " : 'Already have an account? '}
            <button onClick={() => setIsLogin(!isLogin)}
              className="font-500 transition-colors hover:underline"
              style={{color:'var(--accent-light)', background:'none', border:'none', cursor:'pointer'}}>
              {isLogin ? 'Sign up free' : 'Sign in'}
            </button>
          </p>
        </div>

        {/* Setup reminder */}
        <div className="mt-4 p-4 rounded-xl text-xs" style={{background:'rgba(17,24,39,0.6)',border:'1px solid rgba(99,102,241,0.15)',color:'var(--text-muted)'}}>
          <p className="font-500 mb-1" style={{color:'var(--text-secondary)'}}>🚀 Quick Setup (2 steps)</p>
          <ol className="space-y-0.5 list-decimal list-inside">
            <li>Terminal 1 — Backend: <code className="font-mono" style={{color:'#a5b4fc'}}>cd backend &amp;&amp; python run.py</code></li>
            <li>Terminal 2 — Frontend: <code className="font-mono" style={{color:'#a5b4fc'}}>cd frontend &amp;&amp; npm run dev</code></li>
          </ol>
          <p className="mt-1.5" style={{color:'#6ee7b7'}}>✅ Uses SQLite by default — no PostgreSQL needed!</p>
        </div>
      </div>
    </div>
  )
}
