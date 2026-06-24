import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

const NavItem = ({ to, icon, label, badge }) => (
  <NavLink to={to}
    className={({ isActive }) =>
      `flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-sm font-display border ${isActive ? 'nav-active' : 'border-transparent hover:bg-white/5'}`
    }
    style={({ isActive }) => ({ color: isActive ? '#a5b4fc' : 'var(--text-secondary)' })}>
    <span className="text-lg">{icon}</span>
    <span className="font-500">{label}</span>
    {badge && (
      <span className="ml-auto text-xs px-2 py-0.5 rounded-full font-mono"
        style={{background:'rgba(99,102,241,0.2)',color:'#a5b4fc'}}>{badge}</span>
    )}
  </NavLink>
)

export default function Sidebar({ children }) {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const initials = user?.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : user?.username?.[0]?.toUpperCase() || 'U'

  return (
    <div className="flex h-screen overflow-hidden" style={{background:'var(--bg-primary)'}}>
      {/* Sidebar */}
      <aside className="flex flex-col glass border-r"
        style={{
          width: collapsed ? '72px' : '240px',
          transition: 'width 0.3s ease',
          borderColor: 'var(--border)',
          flexShrink: 0,
        }}>
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-5 border-b" style={{borderColor:'var(--border)'}}>
          <div className="w-9 h-9 rounded-xl flex-shrink-0 flex items-center justify-center text-lg"
            style={{background:'linear-gradient(135deg,#6366f1,#8b5cf6)'}}>
            🧠
          </div>
          {!collapsed && (
            <div>
              <div className="font-display font-700 text-sm gradient-text">ExpertFlow</div>
              <div className="text-xs" style={{color:'var(--text-muted)'}}>AI Learning</div>
            </div>
          )}
          <button onClick={() => setCollapsed(c => !c)}
            className="ml-auto text-xs rounded-lg p-1 transition-colors hover:bg-white/5 flex-shrink-0"
            style={{color:'var(--text-muted)'}}>
            {collapsed ? '→' : '←'}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-1 overflow-hidden">
          {!collapsed ? (
            <>
              <NavItem to="/dashboard" icon="🏠" label="Dashboard" />
              <NavItem to="/chat" icon="💬" label="Chat" />
              <NavItem to="/history" icon="📋" label="History" />
              <NavItem to="/subjects" icon="📚" label="Subjects" />
              <NavItem to="/profile" icon="👤" label="Profile" />
            </>
          ) : (
            <div className="space-y-1">
              {[
                { to: '/dashboard', icon: '🏠' },
                { to: '/chat', icon: '💬' },
                { to: '/history', icon: '📋' },
                { to: '/subjects', icon: '📚' },
                { to: '/profile', icon: '👤' },
              ].map(({ to, icon }) => (
                <NavLink key={to} to={to}
                  className={({ isActive }) =>
                    `flex items-center justify-center p-2.5 rounded-xl transition-all border ${isActive ? 'nav-active' : 'border-transparent hover:bg-white/5'}`
                  }>
                  <span className="text-lg">{icon}</span>
                </NavLink>
              ))}
            </div>
          )}
        </nav>

        {/* User */}
        <div className="p-2 border-t" style={{borderColor:'var(--border)'}}>
          <div className="flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 transition-colors cursor-pointer"
            onClick={() => navigate('/profile')}>
            <div className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-display font-700"
              style={{background:'linear-gradient(135deg,#6366f1,#8b5cf6)',color:'#fff'}}>
              {initials}
            </div>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <div className="text-xs font-500 truncate">{user?.full_name || user?.username}</div>
                <div className="text-xs truncate" style={{color:'var(--text-muted)'}}>{user?.email}</div>
              </div>
            )}
            {!collapsed && (
              <button onClick={(e) => { e.stopPropagation(); handleLogout(); }}
                className="text-xs px-2 py-1 rounded-lg transition-colors hover:bg-red-500/20 flex-shrink-0"
                style={{color:'var(--text-muted)'}}>
                ⎋
              </button>
            )}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto" style={{background:'var(--bg-primary)'}}>
        {children}
      </main>
    </div>
  )
}
