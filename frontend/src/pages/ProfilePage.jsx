import { useState } from 'react'
import { useAuthStore } from '../store/authStore'
import api from '../utils/api'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const { user, updateUser, logout } = useAuthStore()
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({
    full_name: user?.full_name || '',
    bio: user?.bio || '',
    avatar_url: user?.avatar_url || '',
  })
  const [saving, setSaving] = useState(false)

  const save = async () => {
    setSaving(true)
    try {
      const res = await api.put('/auth/me', form)
      updateUser(res.data)
      setEditing(false)
      toast.success('Profile updated!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update')
    } finally { setSaving(false) }
  }

  const initials = user?.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : user?.username?.[0]?.toUpperCase() || 'U'

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="mb-6 animate-slide-up">
        <h1 className="text-2xl font-display font-700"><span className="gradient-text">Profile</span></h1>
        <p className="text-sm mt-1" style={{color:'var(--text-muted)'}}>Manage your account</p>
      </div>

      {/* Avatar & Name */}
      <div className="glass rounded-2xl p-6 mb-4 animate-fade-in">
        <div className="flex items-center gap-5">
          <div className="relative">
            {user?.avatar_url ? (
              <img src={user.avatar_url} className="w-20 h-20 rounded-2xl object-cover" alt="avatar" />
            ) : (
              <div className="w-20 h-20 rounded-2xl flex items-center justify-center text-2xl font-display font-700"
                style={{background:'linear-gradient(135deg,#6366f1,#8b5cf6)',color:'#fff'}}>
                {initials}
              </div>
            )}
          </div>
          <div>
            <h2 className="text-xl font-display font-700">{user?.full_name || user?.username}</h2>
            <p className="text-sm" style={{color:'var(--text-muted)'}}>@{user?.username}</p>
            <p className="text-sm" style={{color:'var(--text-muted)'}}>{user?.email}</p>
          </div>
          <button onClick={() => setEditing(e => !e)} className="ml-auto btn-secondary text-sm">
            {editing ? 'Cancel' : '✏️ Edit'}
          </button>
        </div>

        {user?.bio && !editing && (
          <p className="mt-4 text-sm p-3 rounded-xl" style={{background:'var(--bg-elevated)',color:'var(--text-secondary)'}}>
            {user.bio}
          </p>
        )}
      </div>

      {/* Edit form */}
      {editing && (
        <div className="glass rounded-2xl p-6 mb-4 animate-slide-up">
          <h3 className="font-display font-600 mb-4">Edit Profile</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-xs mb-1.5 font-500" style={{color:'var(--text-secondary)'}}>Full Name</label>
              <input className="input-field" value={form.full_name}
                onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))}
                placeholder="Your full name" />
            </div>
            <div>
              <label className="block text-xs mb-1.5 font-500" style={{color:'var(--text-secondary)'}}>Bio</label>
              <textarea className="input-field" rows={3} value={form.bio}
                onChange={e => setForm(f => ({ ...f, bio: e.target.value }))}
                placeholder="Tell us about yourself..." />
            </div>
            <div>
              <label className="block text-xs mb-1.5 font-500" style={{color:'var(--text-secondary)'}}>Avatar URL</label>
              <input className="input-field" value={form.avatar_url}
                onChange={e => setForm(f => ({ ...f, avatar_url: e.target.value }))}
                placeholder="https://..." />
            </div>
            <button onClick={save} disabled={saving} className="btn-primary w-full">
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      )}

      {/* Account info */}
      <div className="glass rounded-2xl p-6 mb-4 animate-fade-in">
        <h3 className="font-display font-600 mb-4">Account Info</h3>
        <div className="space-y-3">
          {[
            { label: 'Username', value: `@${user?.username}` },
            { label: 'Email', value: user?.email },
            { label: 'Member since', value: user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) : '—' },
          ].map(({ label, value }) => (
            <div key={label} className="flex justify-between items-center py-2 border-b"
              style={{borderColor:'var(--border)'}}>
              <span className="text-sm" style={{color:'var(--text-muted)'}}>{label}</span>
              <span className="text-sm font-500">{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Tech stack badge */}
      <div className="rounded-2xl p-5 animate-fade-in"
        style={{background:'linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.08))',border:'1px solid rgba(99,102,241,0.2)'}}>
        <h3 className="font-display font-600 text-sm mb-3" style={{color:'#a5b4fc'}}>⚙️ Platform Stack</h3>
        <div className="flex flex-wrap gap-2">
          {['Gemini 2.5 Flash', 'RAG Pipeline', 'MoE Routing', 'ChromaDB', 'SQLite', 'FastAPI', 'SentenceTransformers', 'React'].map(t => (
            <span key={t} className="text-xs px-2.5 py-1 rounded-full font-mono"
              style={{background:'rgba(99,102,241,0.15)',color:'#a5b4fc',border:'1px solid rgba(99,102,241,0.2)'}}>
              {t}
            </span>
          ))}
        </div>
      </div>

      {/* Danger zone */}
      <div className="glass rounded-2xl p-5 mt-4 animate-fade-in"
        style={{borderColor:'rgba(239,68,68,0.15)'}}>
        <h3 className="font-display font-600 text-sm mb-3" style={{color:'#fca5a5'}}>⚠️ Danger Zone</h3>
        <button onClick={logout} className="py-2 px-4 rounded-xl text-sm transition-all"
          style={{background:'rgba(239,68,68,0.1)',color:'#fca5a5',border:'1px solid rgba(239,68,68,0.2)'}}>
          Sign Out
        </button>
      </div>
    </div>
  )
}
