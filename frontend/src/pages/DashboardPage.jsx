import { useEffect, useState } from 'react'
import { Navigate, Link } from 'react-router-dom'
import { useAuth } from '../stores/authStore'
import { groupsApi, brandsApi, usersApi } from '../services/resources'
import { Card } from '../components/ui'
import { Building2, UtensilsCrossed, Users } from 'lucide-react'

export default function DashboardPage() {
  const { user } = useAuth()
  const [counts, setCounts] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user.role === 'level3') return // redirected below
    async function load() {
      const [brands, users] = await Promise.all([brandsApi.list(), usersApi.list()])
      let groups = []
      if (user.role === 'level1') groups = await groupsApi.list()
      setCounts({ groups: groups.length, brands: brands.length, users: users.length, brandList: brands })
      setLoading(false)
    }
    load()
  }, [user.role])

  // Level 3 manages exactly one brand — skip the overview and go straight there.
  if (user.role === 'level3') {
    return <Navigate to={`/admin/brands/${user.brand_id}`} replace />
  }

  if (loading) return <p className="text-sm text-slate">Loading…</p>

  return (
    <div>
      <h1 className="font-display text-2xl text-ink">Welcome back, {user.full_name.split(' ')[0]}</h1>
      <p className="mt-1 text-sm text-slate">Here's what's happening across your menus.</p>

      <div className="mt-6 grid grid-cols-3 gap-4">
        {user.role === 'level1' && (
          <StatCard icon={Building2} label="Groups" value={counts.groups} to="/admin/groups" />
        )}
        <StatCard icon={UtensilsCrossed} label="Brands" value={counts.brands} to="/admin/brands" />
        <StatCard icon={Users} label="Users" value={counts.users} to="/admin/users" />
      </div>

      <h2 className="mt-10 mb-3 text-sm font-semibold text-ink">Your brands</h2>
      <div className="grid grid-cols-2 gap-3">
        {counts.brandList.map((b) => (
          <Link
            key={b.id}
            to={`/admin/brands/${b.id}`}
            className="rounded-lg border border-sand bg-white p-4 transition-colors hover:border-marigold"
          >
            <p className="font-khmer text-base text-ink">{b.name_kh}</p>
            <p className="text-sm text-slate">{b.name_en}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}

function StatCard({ icon: Icon, label, value, to }) {
  return (
    <Link to={to}>
      <Card className="p-4 transition-colors hover:border-marigold">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-marigold-light text-marigold-dark">
            <Icon size={17} />
          </div>
          <div>
            <p className="text-2xl font-semibold text-ink leading-none">{value}</p>
            <p className="text-xs text-slate">{label}</p>
          </div>
        </div>
      </Card>
    </Link>
  )
}
