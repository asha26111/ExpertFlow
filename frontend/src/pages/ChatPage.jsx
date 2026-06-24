import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import api from '../utils/api'
import toast from 'react-hot-toast'

const EXPERT_META = {
  '📐 Math Expert':          '#6366f1',
  '⚛️ Physics Expert':       '#0ea5e9',
  '💻 CS Expert':            '#10b981',
  '🧪 Chemistry Expert':     '#f59e0b',
  '🧬 Biology Expert':       '#ec4899',
  '📜 History Expert':       '#8b5cf6',
  '🌍 Geography Expert':     '#06b6d4',
  '📊 Economics Expert':     '#84cc16',
  '📚 Literature & English Expert': '#f97316',
  '🧠 Psychology Expert':    '#a855f7',
  '🤔 Philosophy Expert':    '#14b8a6',
  '∑ Advanced Math Expert':  '#e11d48',
  '🎓 General Expert':       '#94a3b8',
}

const SUBJECT_ICONS = {
  mathematics:'📐', physics:'⚛️', computer_science:'💻',
  chemistry:'🧪', biology:'🧬', history:'📜',
  geography:'🌍', economics:'📊', literature_english:'📚',
  psychology:'🧠', philosophy:'🤔', mathematics_advanced:'∑',
  general:'🎓',
}

const SUGGESTIONS = [
  { icon:'📐', text:'Explain integration by parts with a worked example' },
  { icon:'💻', text:'Write a Python binary search function' },
  { icon:'⚛️', text:"Explain Newton's three laws of motion" },
  { icon:'📜', text:'What were the main causes of World War I?' },
  { icon:'🧬', text:'How does DNA replication work step by step?' },
  { icon:'📊', text:'Explain supply and demand with an example' },
  { icon:'🌍', text:'What causes earthquakes and volcanoes?' },
  { icon:'🧪', text:"What is Le Chatelier's principle?" },
  { icon:'📚', text:'How do I write a strong essay introduction?' },
  { icon:'🧠', text:"Explain Pavlov's classical conditioning" },
  { icon:'🤔', text:'What is the difference between deontology and utilitarianism?' },
  { icon:'🎓', text:'How does the immune system fight infections?' },
]

function getErrorMessage(err) {
  if (!err.response) return `Cannot reach backend server.\n\nMake sure it's running:\n  cd backend\n  python run.py`
  const detail = err.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map(d => d.msg || JSON.stringify(d)).join(', ')
  return `Server error ${err.response.status}: ${err.response.statusText}`
}

/* ── Copy button ── */
function CopyBtn({ text }) {
  const [copied, setCopied] = useState(false)
  const copy = (e) => {
    e.stopPropagation()
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }
  return (
    <button onClick={copy}
      title="Copy message"
      className="opacity-0 group-hover:opacity-100 transition-all text-xs px-1.5 py-1 rounded-lg flex items-center gap-1 flex-shrink-0"
      style={{ color: copied ? '#10b981' : 'var(--text-muted)', background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
      {copied ? '✓' : '⎘'}
    </button>
  )
}

/* ── Single message ── */
function Message({ msg }) {
  const isUser = msg.role === 'user'
  const expertColor = EXPERT_META[msg.expert_used] || '#6366f1'

  return (
    <div className={`flex gap-3 animate-slide-up group ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-sm"
        style={{
          background: isUser ? 'linear-gradient(135deg,#6366f1,#8b5cf6)' : `${expertColor}25`,
          border: isUser ? 'none' : `1px solid ${expertColor}40`,
        }}>
        {isUser ? '👤' : (msg.expert_used?.split(' ')[0] || '🎓')}
      </div>

      <div className={`flex-1 max-w-2xl ${isUser ? 'flex flex-col items-end' : ''}`}>
        {!isUser && msg.expert_used && (
          <span className="inline-block text-xs px-2 py-0.5 rounded-full font-mono mb-1.5"
            style={{ background:`${expertColor}20`, color:expertColor, border:`1px solid ${expertColor}30` }}>
            {msg.expert_used}
          </span>
        )}

        <div className={`flex items-start gap-2 ${isUser ? 'flex-row-reverse' : ''}`}>
          <div className={`rounded-2xl px-4 py-3 text-sm ${isUser ? 'rounded-tr-sm' : 'rounded-tl-sm'}`}
            style={isUser
              ? { background:'linear-gradient(135deg,#6366f1,#8b5cf6)', color:'#fff' }
              : { background:'var(--bg-elevated)', border:'1px solid var(--border)', color:'var(--text-primary)' }}>
            {isUser
              ? <p style={{ lineHeight:1.7 }}>{msg.content}</p>
              : <div className="prose-chat"><ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown></div>
            }
          </div>
          <CopyBtn text={msg.content} />
        </div>

        {!isUser && msg.sources?.length > 0 && (
          <details className="mt-1.5 text-xs" style={{ color:'var(--text-muted)' }}>
            <summary className="cursor-pointer hover:text-indigo-400 select-none">
              📎 {msg.sources.length} source{msg.sources.length > 1 ? 's' : ''} retrieved
            </summary>
            <div className="mt-1 space-y-1 pl-2">
              {msg.sources.map((s, i) => (
                <div key={i} className="flex items-start gap-2 p-2 rounded-lg"
                  style={{ background:'rgba(99,102,241,0.08)', border:'1px solid rgba(99,102,241,0.1)' }}>
                  <span className="opacity-40">›</span>
                  <p className="flex-1" style={{ color:'var(--text-secondary)' }}>{s.text}</p>
                  <span className="font-mono flex-shrink-0" style={{ color:'var(--accent-light)' }}>{Math.round(s.score*100)}%</span>
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  )
}

function ThinkingIndicator({ elapsed }) {
  const msg = elapsed < 10 ? 'Routing to expert…'
    : elapsed < 20 ? 'Retrieving knowledge…'
    : elapsed < 35 ? 'Gemini is thinking…'
    : elapsed < 60 ? 'Generating answer… (this can take a minute)'
    : `Still working… ${elapsed}s (large model = slower first response)`
  return (
    <div className="flex gap-3 animate-fade-in">
      <div className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center"
        style={{ background:'rgba(99,102,241,0.15)', border:'1px solid rgba(99,102,241,0.3)' }}>🧠</div>
      <div className="glass rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-3">
        <div className="flex gap-1">
          <div className="typing-dot" /><div className="typing-dot" /><div className="typing-dot" />
        </div>
        <span className="text-xs" style={{ color:'var(--text-muted)' }}>{msg}</span>
      </div>
    </div>
  )
}

/* ── Chat context menu ── */
function ChatContextMenu({ chat, position, onClose, onRename, onDelete, onPin, onArchive, onShare }) {
  const ref = useRef(null)

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) onClose() }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [onClose])

  const items = [
    { icon: '✏️', label: 'Rename', action: onRename },
    { icon: chat.pinned ? '📌 Unpin' : '📌', label: chat.pinned ? 'Unpin' : 'Pin', action: onPin },
    { icon: '📦', label: chat.archived ? 'Unarchive' : 'Archive', action: onArchive },
    { icon: '🔗', label: 'Share', action: onShare },
    { icon: '🗑️', label: 'Delete', action: onDelete, danger: true },
  ]

  return (
    <div ref={ref}
      className="fixed z-50 rounded-xl shadow-xl py-1 min-w-[160px]"
      style={{
        top: position.y, left: position.x,
        background: 'var(--bg-elevated)',
        border: '1px solid var(--border)',
        backdropFilter: 'blur(12px)',
      }}>
      {items.map((item, i) => (
        <button key={i}
          onClick={(e) => { e.stopPropagation(); item.action(); onClose() }}
          className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-left transition-colors hover:bg-white/5"
          style={{ color: item.danger ? '#f87171' : 'var(--text-primary)' }}>
          <span>{item.icon}</span>
          <span>{item.label}</span>
        </button>
      ))}
    </div>
  )
}

/* ── Rename modal ── */
function RenameModal({ chat, onConfirm, onClose }) {
  const [value, setValue] = useState(chat.title || '')
  const inputRef = useRef(null)
  useEffect(() => { inputRef.current?.focus(); inputRef.current?.select() }, [])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.5)' }}>
      <div className="rounded-2xl p-5 w-80 shadow-2xl" style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
        <h3 className="text-sm font-600 mb-3" style={{ color: 'var(--text-primary)' }}>Rename Chat</h3>
        <input ref={inputRef} value={value} onChange={e => setValue(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') onConfirm(value); if (e.key === 'Escape') onClose() }}
          className="w-full rounded-xl px-3 py-2 text-sm outline-none mb-4"
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--text-primary)' }} />
        <div className="flex gap-2 justify-end">
          <button onClick={onClose} className="px-3 py-1.5 rounded-lg text-xs" style={{ color: 'var(--text-muted)', background: 'var(--bg-card)' }}>Cancel</button>
          <button onClick={() => onConfirm(value)} className="btn-primary px-3 py-1.5 text-xs">Save</button>
        </div>
      </div>
    </div>
  )
}

/* ── Share modal ── */
function ShareModal({ chat, messages, onClose }) {
  const shareText = messages.map(m => `${m.role === 'user' ? 'You' : m.expert_used || 'AI'}: ${m.content}`).join('\n\n')
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(shareText).then(() => { setCopied(true); setTimeout(() => setCopied(false), 1500) })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.5)' }}>
      <div className="rounded-2xl p-5 w-96 shadow-2xl" style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
        <h3 className="text-sm font-600 mb-1" style={{ color: 'var(--text-primary)' }}>Share Chat</h3>
        <p className="text-xs mb-3" style={{ color: 'var(--text-muted)' }}>{chat.title}</p>
        <textarea readOnly value={shareText} rows={6}
          className="w-full rounded-xl px-3 py-2 text-xs outline-none resize-none mb-3"
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }} />
        <div className="flex gap-2 justify-end">
          <button onClick={onClose} className="px-3 py-1.5 rounded-lg text-xs" style={{ color: 'var(--text-muted)', background: 'var(--bg-card)' }}>Close</button>
          <button onClick={copy} className="btn-primary px-3 py-1.5 text-xs">{copied ? '✓ Copied!' : '⎘ Copy All'}</button>
        </div>
      </div>
    </div>
  )
}

/* ── Main ChatPage ── */
export default function ChatPage() {
  const { chatId } = useParams()
  const navigate = useNavigate()
  const [chats, setChats]             = useState([])
  const [activeChatId, setActiveChatId] = useState(chatId ? parseInt(chatId) : null)
  const [messages, setMessages]       = useState([])
  const [input, setInput]             = useState('')
  const [sending, setSending]         = useState(false)
  const [elapsed, setElapsed]         = useState(0)
  const [loadingMsgs, setLoadingMsgs] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [contextMenu, setContextMenu] = useState(null) // { chat, x, y }
  const [renaming, setRenaming]       = useState(null) // chat
  const [sharing, setSharing]         = useState(null) // chat
  const [showArchived, setShowArchived] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef       = useRef(null)
  const timerRef       = useRef(null)

  useEffect(() => { loadChats() }, [])
  useEffect(() => {
    if (activeChatId) loadMessages(activeChatId)
    else setMessages([])
  }, [activeChatId])
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior:'smooth' })
  }, [messages, sending])
  useEffect(() => {
    if (sending) {
      setElapsed(0)
      timerRef.current = setInterval(() => setElapsed(e => e + 1), 1000)
    } else {
      clearInterval(timerRef.current); setElapsed(0)
    }
    return () => clearInterval(timerRef.current)
  }, [sending])

  const loadChats  = async () => {
    try { const r = await api.get('/chats'); setChats(r.data) } catch {}
  }
  const loadMessages = async (id) => {
    setLoadingMsgs(true)
    try { const r = await api.get(`/chats/${id}/messages`); setMessages(r.data) }
    catch (err) { toast.error('Could not load messages: ' + getErrorMessage(err)) }
    finally { setLoadingMsgs(false) }
  }

  const newChat = async () => {
    try {
      const r = await api.post('/chats', { title:'New Chat' })
      setChats(c => [r.data, ...c])
      setActiveChatId(r.data.id)
      navigate(`/chat/${r.data.id}`)
    } catch (err) { toast.error(getErrorMessage(err)) }
  }

  const selectChat = (id) => { setActiveChatId(id); navigate(`/chat/${id}`) }

  const deleteChat = async (id) => {
    try {
      await api.delete(`/chats/${id}`)
      setChats(c => c.filter(ch => ch.id !== id))
      if (activeChatId === id) { setActiveChatId(null); setMessages([]); navigate('/chat') }
    } catch { toast.error('Could not delete chat') }
  }

  const renameChat = async (chat, newTitle) => {
    if (!newTitle.trim()) return
    try {
      const r = await api.patch(`/chats/${chat.id}`, { title: newTitle.trim() })
      setChats(c => c.map(ch => ch.id === chat.id ? { ...ch, title: r.data.title } : ch))
      setRenaming(null)
    } catch { toast.error('Could not rename chat') }
  }

  const togglePin = async (chat) => {
    try {
      const r = await api.patch(`/chats/${chat.id}`, { pinned: !chat.pinned })
      setChats(c => c.map(ch => ch.id === chat.id ? { ...ch, pinned: r.data.pinned } : ch))
      toast.success(r.data.pinned ? 'Chat pinned' : 'Chat unpinned')
    } catch { toast.error('Could not update chat') }
  }

  const toggleArchive = async (chat) => {
    try {
      const r = await api.patch(`/chats/${chat.id}`, { archived: !chat.archived })
      setChats(c => c.map(ch => ch.id === chat.id ? { ...ch, archived: r.data.archived } : ch))
      toast.success(r.data.archived ? 'Chat archived' : 'Chat unarchived')
    } catch { toast.error('Could not update chat') }
  }

  const openContextMenu = (e, chat) => {
    e.preventDefault(); e.stopPropagation()
    const x = Math.min(e.clientX, window.innerWidth - 180)
    const y = Math.min(e.clientY, window.innerHeight - 200)
    setContextMenu({ chat, x, y })
  }

  const sendMessage = async (content = input.trim()) => {
    if (!content || sending) return
    let cid = activeChatId
    if (!cid) {
      try {
        const r = await api.post('/chats', { title: content.slice(0, 60) })
        cid = r.data.id
        setChats(c => [r.data, ...c])
        setActiveChatId(cid)
        navigate(`/chat/${cid}`)
      } catch (err) { toast.error(getErrorMessage(err)); return }
    }
    const tempId = Date.now()
    setMessages(m => [...m, { id:tempId, role:'user', content, created_at:new Date().toISOString() }])
    setInput('')
    setSending(true)
    try {
      const r = await api.post(`/chats/${cid}/messages`, { content })
      setMessages(m => [...m.filter(x => x.id !== tempId), r.data.user_message, r.data.assistant_message])
      loadChats()
    } catch (err) {
      setMessages(m => m.filter(x => x.id !== tempId))
      const errMsg = getErrorMessage(err)
      setMessages(m => [...m, {
        id: Date.now(), role: 'assistant',
        content: `❌ **Failed to get response**\n\n${errMsg}\n\n---\n**Common fixes:**\n- Check \`GEMINI_API_KEY\` is set in \`backend/.env\`\n- Get a free key at https://aistudio.google.com`,
        expert_used: null, sources: [], created_at: new Date().toISOString(),
      }])
    } finally {
      setSending(false)
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
  }

  const visibleChats = chats.filter(c => showArchived ? c.archived : !c.archived)
  const pinned = visibleChats.filter(c => c.pinned)
  const unpinned = visibleChats.filter(c => !c.pinned)
  const activeChat = chats.find(c => c.id === activeChatId)

  return (
    <div className="flex h-full" style={{ background:'var(--bg-primary)' }}>
      {/* Sidebar */}
      {sidebarOpen && (
        <div className="flex flex-col glass border-r" style={{ width:'260px', borderColor:'var(--border)', flexShrink:0 }}>
          <div className="p-3 border-b" style={{ borderColor:'var(--border)' }}>
            <button onClick={newChat} className="btn-primary w-full text-sm flex items-center justify-center gap-2">
              <span>✏️</span> New Chat
            </button>
          </div>

          {/* Archive toggle */}
          <div className="px-3 pt-2">
            <button onClick={() => setShowArchived(a => !a)}
              className="w-full flex items-center gap-2 text-xs px-2 py-1.5 rounded-lg transition-colors hover:bg-white/5"
              style={{ color: showArchived ? '#6366f1' : 'var(--text-muted)' }}>
              <span>📦</span>
              <span>{showArchived ? 'Archived Chats' : 'All Chats'}</span>
              <span className="ml-auto">{showArchived ? '←' : ''}</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {/* Pinned section */}
            {pinned.length > 0 && (
              <>
                <p className="text-xs px-2 py-1" style={{ color:'var(--text-muted)', opacity: 0.6 }}>📌 Pinned</p>
                {pinned.map(chat => (
                  <ChatItem key={chat.id} chat={chat} active={activeChatId===chat.id}
                    onSelect={() => selectChat(chat.id)}
                    onContextMenu={(e) => openContextMenu(e, chat)} />
                ))}
                {unpinned.length > 0 && <div className="my-1 border-t" style={{ borderColor:'var(--border)' }} />}
              </>
            )}

            {/* Regular chats */}
            {unpinned.length === 0 && pinned.length === 0
              ? <p className="text-center text-xs py-8" style={{ color:'var(--text-muted)' }}>No chats yet</p>
              : unpinned.map(chat => (
                <ChatItem key={chat.id} chat={chat} active={activeChatId===chat.id}
                  onSelect={() => selectChat(chat.id)}
                  onContextMenu={(e) => openContextMenu(e, chat)} />
              ))
            }
          </div>
        </div>
      )}

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="flex items-center gap-3 px-4 py-3 border-b flex-shrink-0"
          style={{ borderColor:'var(--border)', background:'var(--bg-secondary)' }}>
          <button onClick={() => setSidebarOpen(o => !o)}
            className="p-2 rounded-lg hover:bg-white/5" style={{ color:'var(--text-muted)' }}>☰</button>
          <h2 className="font-display font-600 text-sm flex-1 truncate">
            {activeChatId ? (activeChat?.title || 'Chat') : 'Ask Anything'}
          </h2>
          <div className="flex items-center gap-1.5 text-xs px-3 py-1 rounded-full flex-shrink-0"
            style={{ background:'rgba(16,185,129,0.1)', color:'#10b981', border:'1px solid rgba(16,185,129,0.2)' }}>
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Gemini · RAG · MoE
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {!activeChatId && messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full gap-6 animate-fade-in">
              <div className="text-5xl">🧠</div>
              <div className="text-center">
                <h2 className="text-2xl font-display font-700 gradient-text mb-2">Ask Anything</h2>
                <p className="text-sm" style={{ color:'var(--text-muted)' }}>
                  14 expert domains • RAG retrieval • Gemini 2.5 Flash
                </p>
                <p className="text-xs mt-1" style={{ color:'var(--text-muted)' }}>
                  ✨ Powered by Google Gemini — fast, accurate, always online
                </p>
              </div>
              <div className="grid grid-cols-3 gap-2 w-full max-w-2xl">
                {SUGGESTIONS.map((s, i) => (
                  <button key={i} onClick={() => sendMessage(s.text)}
                    className="glass text-left rounded-xl p-3 text-xs hover:border-indigo-500/30 transition-all flex items-start gap-2"
                    style={{ color:'var(--text-secondary)' }}>
                    <span className="text-base flex-shrink-0">{s.icon}</span>
                    <span>{s.text}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
          {loadingMsgs
            ? <div className="flex justify-center py-8">
                <div className="w-6 h-6 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
              </div>
            : messages.map(msg => <Message key={msg.id} msg={msg} />)
          }
          {sending && <ThinkingIndicator elapsed={elapsed} />}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t flex-shrink-0"
          style={{ borderColor:'var(--border)', background:'var(--bg-secondary)' }}>
          {sending && elapsed > 15 && (
            <div className="mb-3 px-3 py-2 rounded-xl text-xs flex items-center gap-2"
              style={{ background:'rgba(99,102,241,0.08)', border:'1px solid rgba(99,102,241,0.2)', color:'var(--text-secondary)' }}>
              <div className="w-4 h-4 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin flex-shrink-0" />
              Gemini is generating your answer…
            </div>
          )}
          <div className="flex items-end gap-3 p-3 rounded-2xl"
            style={{ background:'var(--bg-elevated)', border:'1px solid var(--border)' }}>
            <textarea ref={inputRef} value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown} rows={1} disabled={sending}
              placeholder={sending ? 'Waiting for Gemini response…' : 'Ask about any subject — Maths, Physics, CS, History, Biology… (Enter to send)'}
              className="flex-1 bg-transparent outline-none resize-none text-sm"
              style={{ color:'var(--text-primary)', fontFamily:'DM Sans,sans-serif', maxHeight:'120px', lineHeight:1.6, opacity: sending ? 0.5 : 1 }}
              onInput={e => { e.target.style.height='auto'; e.target.style.height=Math.min(e.target.scrollHeight,120)+'px' }}
            />
            <button onClick={() => sendMessage()} disabled={!input.trim() || sending}
              className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-all"
              style={{
                background: input.trim() && !sending ? 'linear-gradient(135deg,#6366f1,#8b5cf6)' : 'var(--bg-card)',
                color: input.trim() && !sending ? '#fff' : 'var(--text-muted)',
                cursor: input.trim() && !sending ? 'pointer' : 'not-allowed',
              }}>
              {sending
                ? <div className="w-4 h-4 border-2 border-white/20 border-t-white/70 rounded-full animate-spin" />
                : '↑'}
            </button>
          </div>
          <p className="text-center text-xs mt-2" style={{ color:'var(--text-muted)' }}>
            Powered by Gemini 2.5 Flash · 14 expert domains · RAG knowledge retrieval
          </p>
        </div>
      </div>

      {/* Context menu */}
      {contextMenu && (
        <ChatContextMenu
          chat={contextMenu.chat}
          position={{ x: contextMenu.x, y: contextMenu.y }}
          onClose={() => setContextMenu(null)}
          onRename={() => setRenaming(contextMenu.chat)}
          onDelete={() => deleteChat(contextMenu.chat.id)}
          onPin={() => togglePin(contextMenu.chat)}
          onArchive={() => toggleArchive(contextMenu.chat)}
          onShare={() => setSharing(contextMenu.chat)}
        />
      )}

      {/* Rename modal */}
      {renaming && (
        <RenameModal chat={renaming}
          onConfirm={(title) => renameChat(renaming, title)}
          onClose={() => setRenaming(null)} />
      )}

      {/* Share modal */}
      {sharing && (
        <ShareModal chat={sharing} messages={messages}
          onClose={() => setSharing(null)} />
      )}
    </div>
  )
}

/* ── Sidebar chat item ── */
function ChatItem({ chat, active, onSelect, onContextMenu }) {
  return (
    <div onClick={onSelect} onContextMenu={onContextMenu}
      className={`flex items-center gap-2 p-2.5 rounded-xl cursor-pointer transition-all group ${active ? 'nav-active' : 'hover:bg-white/5'}`}>
      <span className="text-base flex-shrink-0">{SUBJECT_ICONS[chat.subject] || '💬'}</span>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-500 truncate flex items-center gap-1">
          {chat.pinned && <span className="text-indigo-400 text-xs">📌</span>}
          {chat.title || 'New Chat'}
        </p>
        <p className="text-xs" style={{ color:'var(--text-muted)' }}>{chat.message_count} msgs</p>
      </div>
      {/* Three-dot menu trigger */}
      <button onClick={onContextMenu}
        className="opacity-0 group-hover:opacity-100 text-xs p-1 rounded hover:bg-white/10 transition-all flex-shrink-0"
        style={{ color:'var(--text-muted)' }}>⋮</button>
    </div>
  )
}
