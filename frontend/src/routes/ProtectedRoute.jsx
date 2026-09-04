import { Navigate } from 'react-router-dom'
import { useAuth } from '../stores/authStore'

export function ProtectedRoute({ roles, children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return <div className="flex h-screen items-center justify-center text-slate">Loading…</div>
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (roles && !roles.includes(user.role)) {
    // Staff who land on an admin URL go to their menu display instead of a dead end.
    return <Navigate to={user.role === 'staff' ? '/staff/menu' : '/admin'} replace />
  }

  return children
}
