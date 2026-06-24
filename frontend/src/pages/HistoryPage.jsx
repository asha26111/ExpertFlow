import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../utils/api'
import toast from 'react-hot-toast'
import { formatDistanceToNow } from 'date-fns'

const SUBJECT_META = {
  mathematics: { icon: '📐', color: '#6366f1', label: 'Mathematics' },
  physics: { icon: '⚛️', color: '#0ea5e9', label: 'Physics' },
  computer_science: { icon: '💻', color: '#10b981', label: 'Computer Science' },
  chemistry: { icon: '🧪', color: '#f59e0b', label: 'Chemistry' },
  biology: { icon: '🧬', color: '#ec4899', label: 'Biology' },
  general: { icon: '🧠', color: '#8b5cf6', label: 'General' },
}

export default function HistoryPage() {
  const navigate = useNavigate()
  const [chats, setChats] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    api.get('/chats')
      .then(res => setChats(res.data))
      .catch(() => toast.error('Failed to load history'))
      .finally(() => setLoading(false))
  }, [])

  const deleteChat = async (e, id) => {
    e.stopPropagation()
    try {
      await api.delete(`/chats/${id}`)
      setChats(c => c.filter(ch => ch.id !== id))
      toast.success('Deleted')
    } catch { toast.error('Failed') }
  }

  const subjects = [...new Set(chats.map(c => c.subject).filter(Boolean))]

  const filtered = chats.filter(c => {
    const matchSearch = c.title?.toLowerCase().includes(search.toLowerCase())
    const matchFilter = filter === 'all' || c.subject === filter
    return matchSearch && matchFilter
  })

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6 animate-slide-up">
        <h1 className="text-2xl font-display font-700">Chat <span className="gradient-text">History</span></h1>
        <p className="text-sm mt-1" style={{color:'var(--text-muted)'}}>All your previous conversations</p>
      </div>

      {/* Controls */}
      <div className="flex gap-3 mb-6 flex-wrap">
        <input className="input-field flex-1 min-w-48" placeholder="🔍 Search chats..."
          value={search} onChange={e => setSearch(e.target.value)} />
        
        <div className="flex gap-2 flex-wrap">
          <button onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-xl text-sm font-500 transition-all border ${filter === 'all' ? 'nav-active' : 'border-transparent hover:bg-white/5'}`}
            style={{color: filter === 'all' ? '#a5b4fc' : 'var(--text-secondary)'}}>
            All
          </button>
          {subjects.map(s => {
            const meta = SUBJECT_META[s] || SUBJECT_META.general
            return (
              <button key={s} onClick={() => setFilter(s)}
                className={`px-4 py-2 rounded-xl text-sm font-500 transition-all border ${filter === s ? 'nav-active' : 'border-transparent hover:bg-white/5'}`}
                style={{color: filter === s ? '#a5b4fc' : 'var(--text-secondary)'}}>
                {meta.icon} {meta.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Count */}
      <div className="mb-4 text-sm" style={{color:'var(--text-muted)'}}>
        {filtered.length} conversation{filtered.length !== 1 ? 's' : ''}
      </div>

      {/* Chat list */}
      {loading ? (
        <div className="space-y-3">
          {[1,2,3,4,5].map(i => (
            <div key={i} className="glass rounded-2xl p-4 animate-pulse" style={{height:'80px'}} />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">📭</div>
          <h3 className="font-display font-600 mb-2">No chats found</h3>
          <p className="text-sm mb-6" style={{color:'var(--text-muted)'}}>
            {search ? 'Try a different search term' : 'Start your first conversation!'}
          </p>
          <button onClick={() => navigate('/chat')} className="btn-primary">New Chat</button>
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map(chat => {
            const meta = SUBJECT_META[chat.subject] || SUBJECT_META.general
            return (
              <div key={chat.id} onClick={() => navigate(`/chat/${chat.id}`)}
                className="glass rounded-2xl p-4 cursor-pointer hover:border-indigo-500/30 transition-all group flex items-center gap-4"
                style={{animationDelay:'0.05s'}}>
                <div className="w-11 h-11 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
                  style={{background:`${meta.color}20`,border:`1px solid ${meta.color}30`}}>
                  {meta.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-500 text-sm truncate">{chat.title || 'Untitled Chat'}</h3>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs px-2 py-0.5 rounded-full"
                      style={{background:`${meta.color}15`,color:meta.color}}>
                      {meta.label}
                    </span>
                    <span className="text-xs" style={{color:'var(--text-muted)'}}>
                      {chat.message_count} messages
                    </span>
                    {chat.created_at && (
                      <span className="text-xs" style={{color:'var(--text-muted)'}}>
                        {formatDistanceToNow(new Date(chat.created_at), { addSuffix: true })}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={(e) => deleteChat(e, chat.id)}
                    className="p-2 rounded-lg hover:bg-red-500/20 transition-colors text-sm"
                    style={{color:'var(--text-muted)'}}>
                    🗑
                  </button>
                  <span className="text-xs" style={{color:'var(--accent-light)'}}>Open →</span>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
