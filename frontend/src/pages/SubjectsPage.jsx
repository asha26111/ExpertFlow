import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../utils/api'
import toast from 'react-hot-toast'

export default function SubjectsPage() {
  const navigate = useNavigate()
  const [subjects, setSubjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [toggling, setToggling] = useState({})

  useEffect(() => {
    api.get('/subjects')
      .then(res => setSubjects(res.data))
      .catch(() => toast.error('Failed to load subjects'))
      .finally(() => setLoading(false))
  }, [])

  const toggleEnroll = async (subject) => {
    if (toggling[subject.id]) return
    setToggling(t => ({ ...t, [subject.id]: true }))
    try {
      if (subject.enrolled) {
        await api.delete(`/subjects/${subject.id}/enroll`)
        toast('Unenrolled', { icon: '👋' })
      } else {
        await api.post(`/subjects/${subject.id}/enroll`)
        toast.success('Enrolled!')
      }
      setSubjects(s => s.map(sub =>
        sub.id === subject.id ? { ...sub, enrolled: !sub.enrolled } : sub
      ))
    } catch { toast.error('Failed') }
    finally { setToggling(t => ({ ...t, [subject.id]: false })) }
  }

  const enrolled = subjects.filter(s => s.enrolled)
  const available = subjects.filter(s => !s.enrolled)

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6 animate-slide-up">
        <h1 className="text-2xl font-display font-700">
          <span className="gradient-text">Subjects</span>
        </h1>
        <p className="text-sm mt-1" style={{color:'var(--text-muted)'}}>
          Enroll in subjects to personalize your AI learning experience
        </p>
      </div>

      {/* Enrolled */}
      {enrolled.length > 0 && (
        <div className="mb-8">
          <h2 className="font-display font-600 mb-4 flex items-center gap-2">
            <span>✅</span> Enrolled ({enrolled.length})
          </h2>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
            {enrolled.map(s => (
              <SubjectCard key={s.id} subject={s} onToggle={toggleEnroll}
                loading={toggling[s.id]} onChat={() => navigate('/chat')} />
            ))}
          </div>
        </div>
      )}

      {/* All subjects */}
      <div>
        <h2 className="font-display font-600 mb-4">
          {enrolled.length > 0 ? `Available (${available.length})` : `All Subjects (${subjects.length})`}
        </h2>
        {loading ? (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {[1,2,3,4,5,6,7,8].map(i => (
              <div key={i} className="glass rounded-2xl p-5 animate-pulse" style={{height:'140px'}} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
            {(enrolled.length > 0 ? available : subjects).map(s => (
              <SubjectCard key={s.id} subject={s} onToggle={toggleEnroll}
                loading={toggling[s.id]} onChat={() => navigate('/chat')} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function SubjectCard({ subject, onToggle, loading, onChat }) {
  return (
    <div className="glass rounded-2xl p-5 transition-all hover:border-indigo-500/30 group animate-fade-in"
      style={{borderColor: subject.enrolled ? `${subject.color}30` : undefined}}>
      <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-3"
        style={{background:`${subject.color}20`,border:`1px solid ${subject.color}30`}}>
        {subject.icon}
      </div>
      <h3 className="font-display font-600 text-sm mb-1">{subject.name}</h3>
      <p className="text-xs mb-4 leading-relaxed" style={{color:'var(--text-muted)'}}>
        {subject.description}
      </p>
      <div className="flex gap-2">
        <button onClick={() => onToggle(subject)} disabled={loading}
          className="flex-1 py-1.5 rounded-lg text-xs font-500 transition-all"
          style={subject.enrolled
            ? {background:'rgba(239,68,68,0.1)',color:'#fca5a5',border:'1px solid rgba(239,68,68,0.2)'}
            : {background:`${subject.color}20`,color:subject.color,border:`1px solid ${subject.color}30`}}>
          {loading ? '...' : subject.enrolled ? 'Unenroll' : '+ Enroll'}
        </button>
        {subject.enrolled && (
          <button onClick={onChat}
            className="px-3 py-1.5 rounded-lg text-xs transition-all"
            style={{background:'rgba(99,102,241,0.15)',color:'#a5b4fc',border:'1px solid rgba(99,102,241,0.2)'}}>
            Chat
          </button>
        )}
      </div>
    </div>
  )
}
