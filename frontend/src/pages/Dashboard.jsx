import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../utils/api'

const StatCard = ({ icon, label, value, color }) => (
  <div className="glass rounded-2xl p-5 animate-fade-in" style={{border:`1px solid ${color}30`}}>
    <div className="flex items-center gap-3 mb-2">
      <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl" style={{background:`${color}20`}}>{icon}</div>
      <span className="text-sm font-500" style={{color:'var(--text-secondary)'}}>{label}</span>
    </div>
    <div className="text-3xl font-display font-700" style={{color}}>{value}</div>
  </div>
)

const EXPERT_DOMAINS = [
  { icon: '📐', label: 'Mathematics',  color: '#6366f1' },
  { icon: '⚛️', label: 'Physics',      color: '#0ea5e9' },
  { icon: '💻', label: 'CS & Coding',  color: '#10b981' },
  { icon: '🧪', label: 'Chemistry',    color: '#f59e0b' },
  { icon: '🧬', label: 'Biology',      color: '#ec4899' },
  { icon: '📜', label: 'History',      color: '#8b5cf6' },
  { icon: '🌍', label: 'Geography',    color: '#06b6d4' },
  { icon: '📊', label: 'Economics',    color: '#84cc16' },
  { icon: '📚', label: 'Literature',   color: '#f97316' },
  { icon: '🧠', label: 'Psychology',   color: '#a855f7' },
  { icon: '🤔', label: 'Philosophy',   color: '#14b8a6' },
  { icon: '∑',  label: 'Adv. Math',   color: '#e11d48' },
]

const TIPS = [
  { icon: '🎯', text: 'Be specific — "solve x²+3x-4=0" beats "help with math"', color: '#6366f1' },
  { icon: '🔍', text: 'Ask follow-ups to dive deeper into any concept', color: '#10b981' },
  { icon: '📝', text: 'Ask "why" not just "how" — understanding > memorisation', color: '#f59e0b' },
  { icon: '💡', text: 'Try "compare X and Y" for exam-style analysis answers', color: '#8b5cf6' },
]

const SUBJECT_ICONS = {
  mathematics:'📐', physics:'⚛️', computer_science:'💻', chemistry:'🧪',
  biology:'🧬', history:'📜', geography:'🌍', economics:'📊',
  literature_english:'📚', psychology:'🧠', philosophy:'🤔',
  mathematics_advanced:'∑', general:'🎓',
}

export default function Dashboard() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [stats, setStats] = useState({ chats: 0, messages: 0, subjects: 0 })
  const [recentChats, setRecentChats] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/chats').catch(() => ({ data: [] })),
      api.get('/subjects').catch(() => ({ data: [] })),
    ]).then(([chatsRes, subjectsRes]) => {
      const chats = chatsRes.data || []
      const subjects = subjectsRes.data || []
      const enrolled = subjects.filter(s => s.enrolled).length
      const messages = chats.reduce((acc, c) => acc + (c.message_count || 0), 0)
      setStats({ chats: chats.length, messages, subjects: enrolled })
      setRecentChats(chats.slice(0, 5))
    }).finally(() => setLoading(false))
  }, [])

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good Morning' : hour < 17 ? 'Good Afternoon' : 'Good Evening'
  const name = user?.full_name?.split(' ')[0] || user?.username || 'Learner'

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8 animate-slide-up flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-display font-700">
            {greeting}, <span className="gradient-text">{name}</span> 👋
          </h1>
          <p className="mt-1 text-sm" style={{color:'var(--text-muted)'}}>
            {new Date().toLocaleDateString('en-US', { weekday:'long', month:'long', day:'numeric' })}
          </p>
        </div>
        <button onClick={() => navigate('/chat')} className="btn-primary flex items-center gap-2">
          <span>✨</span> New Chat
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <StatCard icon="💬" label="Total Chats"       value={loading ? '…' : stats.chats}    color="#6366f1" />
        <StatCard icon="📨" label="Messages Sent"     value={loading ? '…' : stats.messages}  color="#10b981" />
        <StatCard icon="📚" label="Enrolled Subjects" value={loading ? '…' : stats.subjects}  color="#f59e0b" />
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Recent Chats */}
        <div className="col-span-2">
          <h2 className="font-display font-600 mb-4 flex items-center gap-2"><span>📋</span> Recent Chats</h2>
          <div className="space-y-2">
            {loading ? (
              [1,2,3].map(i => <div key={i} className="glass rounded-xl p-4 animate-pulse" style={{height:'60px'}} />)
            ) : recentChats.length === 0 ? (
              <div className="glass rounded-2xl p-8 text-center">
                <div className="text-4xl mb-3">💬</div>
                <p className="font-display font-500">No chats yet</p>
                <p className="text-sm mt-1 mb-4" style={{color:'var(--text-muted)'}}>Ask anything across 13 expert domains!</p>
                <button onClick={() => navigate('/chat')} className="btn-primary px-6">Start Chatting</button>
              </div>
            ) : (
              recentChats.map(chat => (
                <div key={chat.id} onClick={() => navigate(`/chat/${chat.id}`)}
                  className="glass rounded-xl p-4 cursor-pointer hover:border-indigo-500/30 transition-all flex items-center gap-3 group">
                  <div className="w-9 h-9 rounded-lg flex items-center justify-center text-sm flex-shrink-0"
                    style={{background:'rgba(99,102,241,0.15)'}}>
                    {SUBJECT_ICONS[chat.subject] || '💬'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-500 truncate">{chat.title}</div>
                    <div className="text-xs mt-0.5" style={{color:'var(--text-muted)'}}>{chat.message_count} messages</div>
                  </div>
                  <span className="text-xs opacity-0 group-hover:opacity-100 transition-opacity" style={{color:'var(--accent-light)'}}>Open →</span>
                </div>
              ))
            )}
          </div>
          {recentChats.length > 0 && (
            <button onClick={() => navigate('/history')} className="btn-secondary w-full mt-3 text-sm">View All History</button>
          )}
        </div>

        {/* Sidebar */}
        <div>
          {/* Expert domains */}
          <h2 className="font-display font-600 mb-3 flex items-center gap-2"><span>🔬</span> Expert Domains</h2>
          <div className="grid grid-cols-3 gap-1.5 mb-5">
            {EXPERT_DOMAINS.map(d => (
              <button key={d.label} onClick={() => navigate('/chat')}
                className="flex flex-col items-center gap-1 px-1 py-2 rounded-xl text-center glass transition-all hover:scale-105"
                style={{borderColor:`${d.color}20`}}>
                <span className="text-base">{d.icon}</span>
                <span style={{color:d.color,fontSize:'0.65rem',fontWeight:500,lineHeight:1.2}}>{d.label}</span>
              </button>
            ))}
          </div>

          {/* Tips */}
          <h2 className="font-display font-600 mb-3 flex items-center gap-2"><span>💡</span> Tips</h2>
          <div className="space-y-2">
            {TIPS.map((tip, i) => (
              <div key={i} className="glass rounded-xl p-3 flex items-start gap-2.5 animate-fade-in"
                style={{animationDelay:`${i*0.07}s`,borderColor:`${tip.color}20`}}>
                <span className="flex-shrink-0 text-base">{tip.icon}</span>
                <p className="text-xs leading-relaxed" style={{color:'var(--text-secondary)'}}>{tip.text}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
