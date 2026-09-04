import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../stores/authStore'
import { brandsApi, groupsApi } from '../services/resources'
import { Button, Input, EmptyState } from '../components/ui'
import { Modal } from '../components/Modal'
import { Plus, ChevronRight } from 'lucide-react'

export default function BrandsPage() {
  const { user } = useAuth()
  const [brands, setBrands] = useState([])
  const [groups, setGroups] = useState([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState({ group_id: '', slug: '', name_en: '', name_kh: '' })
  const [error, setError] = useState('')

  const load = async () => {
    const b = await brandsApi.list()
    setBrands(b)
    if (user.role === 'level1') {
      const g = await groupsApi.list()
      setGroups(g)
      if (g.length && !form.group_id) setForm((f) => ({ ...f, group_id: g[0].id }))
    }
    setLoading(false)
  }
  useEffect(() => { load() }, [])

  const openCreate = () => { setError(''); setModalOpen(true) }

  const save = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await brandsApi.create(form)
      setModalOpen(false)
      setForm({ ...form, slug: '', name_en: '', name_kh: '' })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong.')
    }
  }

  if (loading) return <p className="text-sm text-slate">Loading…</p>

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl text-ink">Brands</h1>
          <p className="mt-1 text-sm text-slate">
            {user.role === 'level1' ? 'Every brand across every group.' : 'Brands you manage.'}
          </p>
        </div>
        {user.role === 'level1' && <Button onClick={openCreate}><Plus size={16} /> New brand</Button>}
      </div>

      {brands.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="No brands yet" description="Brands are created by the system owner." />
        </div>
      ) : (
        <div className="mt-6 divide-y divide-sand rounded-lg border border-sand bg-white">
          {brands.map((b) => (
            <Link key={b.id} to={`/admin/brands/${b.id}`} className="flex items-center justify-between px-5 py-4 hover:bg-paper">
              <div>
                <p className="font-khmer font-medium text-ink">{b.name_kh}</p>
                <p className="text-sm text-slate">{b.name_en} · /menu/{b.slug}</p>
              </div>
              <ChevronRight size={16} className="text-slate" />
            </Link>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New brand">
        <form onSubmit={save} className="space-y-4">
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-ink">Group</span>
            <select
              className="w-full rounded-md border border-sand bg-white px-3 py-2 text-sm"
              value={form.group_id}
              onChange={(e) => setForm({ ...form, group_id: e.target.value })}
            >
              {groups.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
            </select>
          </label>
          <Input label="Name (English)" required value={form.name_en} onChange={(e) => setForm({ ...form, name_en: e.target.value })} />
          <Input label="Name (Khmer)" required value={form.name_kh} onChange={(e) => setForm({ ...form, name_kh: e.target.value })} className="font-khmer" />
          <Input
            label="URL slug"
            required
            placeholder="e.g. abc-restaurant"
            value={form.slug}
            onChange={(e) => setForm({ ...form, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') })}
          />
          {error && <p className="text-sm text-clay">{error}</p>}
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit">Create brand</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
