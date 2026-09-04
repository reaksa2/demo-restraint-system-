import { useEffect, useState } from 'react'
import { useAuth } from '../stores/authStore'
import { usersApi, groupsApi, brandsApi, zonesApi } from '../services/resources'
import { Button, Input, Select, Badge, EmptyState } from '../components/ui'
import { Modal } from '../components/Modal'
import { Plus, Trash2 } from 'lucide-react'

const ROLE_LABELS = { level1: 'Developer', level2: 'Group Manager', level3: 'Brand Manager', staff: 'Staff' }
const ROLE_TONES = { level1: 'accent', level2: 'accent', level3: 'default', staff: 'success' }

const CREATABLE_ROLES = {
  level1: ['level2', 'level3', 'staff'],
  level2: ['level3', 'staff'],
  level3: ['staff'],
}

export default function UsersPage() {
  const { user } = useAuth()
  const [users, setUsers] = useState([])
  const [groups, setGroups] = useState([])
  const [brands, setBrands] = useState([])
  const [zones, setZones] = useState([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [error, setError] = useState('')

  const creatableRoles = CREATABLE_ROLES[user.role] || []
  const [form, setForm] = useState({ email: '', password: '', full_name: '', role: creatableRoles[0] || '', group_id: '', brand_id: '', zone_id: '' })

  const load = async () => {
    const [u, b] = await Promise.all([usersApi.list(), brandsApi.list()])
    setUsers(u)
    setBrands(b)
    if (user.role === 'level1') setGroups(await groupsApi.list())
    setLoading(false)
  }
  useEffect(() => { load() }, [])

  useEffect(() => {
    if (form.role === 'staff' && form.brand_id) {
      zonesApi.list(form.brand_id).then(setZones)
    } else {
      setZones([])
    }
  }, [form.role, form.brand_id])

  const openCreate = () => {
    setForm({ email: '', password: '', full_name: '', role: creatableRoles[0] || '', group_id: '', brand_id: '', zone_id: '' })
    setError('')
    setModalOpen(true)
  }

  const save = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const payload = { email: form.email, password: form.password, full_name: form.full_name, role: form.role }
      if (form.role === 'level2') payload.group_id = form.group_id
      if (form.role === 'level3') payload.brand_id = form.brand_id
      if (form.role === 'staff') { payload.brand_id = form.brand_id; payload.zone_id = form.zone_id }
      await usersApi.create(payload)
      setModalOpen(false)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong.')
    }
  }

  const remove = async (u) => {
    if (!confirm(`Delete user "${u.full_name}"?`)) return
    await usersApi.remove(u.id)
    load()
  }

  const brandName = (id) => brands.find((b) => b.id === id)?.name_en
  const groupName = (id) => groups.find((g) => g.id === id)?.name

  if (loading) return <p className="text-sm text-slate">Loading…</p>

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl text-ink">Users</h1>
          <p className="mt-1 text-sm text-slate">People who can manage or operate your menus.</p>
        </div>
        {creatableRoles.length > 0 && <Button onClick={openCreate}><Plus size={16} /> New user</Button>}
      </div>

      {users.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="No users yet" action={creatableRoles.length > 0 && <Button onClick={openCreate}>Create user</Button>} />
        </div>
      ) : (
        <div className="mt-6 divide-y divide-sand rounded-lg border border-sand bg-white">
          {users.map((u) => (
            <div key={u.id} className="flex items-center justify-between px-5 py-3">
              <div>
                <div className="flex items-center gap-2">
                  <p className="font-medium text-ink">{u.full_name}</p>
                  <Badge tone={ROLE_TONES[u.role]}>{ROLE_LABELS[u.role]}</Badge>
                  {!u.is_active && <Badge tone="danger">Inactive</Badge>}
                </div>
                <p className="text-sm text-slate">
                  {u.email}
                  {u.group_id && ` · ${groupName(u.group_id) || 'group'}`}
                  {u.brand_id && ` · ${brandName(u.brand_id) || 'brand'}`}
                </p>
              </div>
              <Button variant="ghost" onClick={() => remove(u)}><Trash2 size={15} /></Button>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New user">
        <form onSubmit={save} className="space-y-4">
          <Input label="Full name" required value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
          <Input label="Email" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <Input label="Password" type="password" required minLength={8} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />

          <Select label="Role" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value, brand_id: '', group_id: '', zone_id: '' })}>
            {creatableRoles.map((r) => <option key={r} value={r}>{ROLE_LABELS[r]}</option>)}
          </Select>

          {form.role === 'level2' && (
            <Select label="Group" required value={form.group_id} onChange={(e) => setForm({ ...form, group_id: e.target.value })}>
              <option value="">Select a group</option>
              {groups.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
            </Select>
          )}

          {(form.role === 'level3' || form.role === 'staff') && (
            <Select label="Brand" required value={form.brand_id} onChange={(e) => setForm({ ...form, brand_id: e.target.value })}>
              <option value="">Select a brand</option>
              {brands.map((b) => <option key={b.id} value={b.id}>{b.name_en}</option>)}
            </Select>
          )}

          {form.role === 'staff' && form.brand_id && (
            <Select label="Zone" required value={form.zone_id} onChange={(e) => setForm({ ...form, zone_id: e.target.value })}>
              <option value="">Select a zone</option>
              {zones.map((z) => <option key={z.id} value={z.id}>{z.name_en}</option>)}
            </Select>
          )}

          {error && <p className="text-sm text-clay">{error}</p>}
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit">Create user</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
