import { useEffect, useState } from 'react'
import { groupsApi } from '../services/resources'
import { Button, Input, Textarea, EmptyState } from '../components/ui'
import { Modal } from '../components/Modal'
import { Plus, Pencil, Trash2 } from 'lucide-react'

export default function GroupsPage() {
  const [groups, setGroups] = useState([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ name: '', description: '' })
  const [error, setError] = useState('')

  const load = () => groupsApi.list().then((data) => { setGroups(data); setLoading(false) })
  useEffect(() => { load() }, [])

  const openCreate = () => { setEditing(null); setForm({ name: '', description: '' }); setError(''); setModalOpen(true) }
  const openEdit = (g) => { setEditing(g); setForm({ name: g.name, description: g.description || '' }); setError(''); setModalOpen(true) }

  const save = async (e) => {
    e.preventDefault()
    setError('')
    try {
      if (editing) await groupsApi.update(editing.id, form)
      else await groupsApi.create(form)
      setModalOpen(false)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong.')
    }
  }

  const remove = async (g) => {
    if (!confirm(`Delete "${g.name}"? This also deletes every brand inside it.`)) return
    await groupsApi.remove(g.id)
    load()
  }

  if (loading) return <p className="text-sm text-slate">Loading…</p>

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl text-ink">Groups</h1>
          <p className="mt-1 text-sm text-slate">Each group manages a set of restaurant brands.</p>
        </div>
        <Button onClick={openCreate}><Plus size={16} /> New group</Button>
      </div>

      {groups.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="No groups yet" description="Create your first group to start adding brands." action={<Button onClick={openCreate}>Create group</Button>} />
        </div>
      ) : (
        <div className="mt-6 divide-y divide-sand rounded-lg border border-sand bg-white">
          {groups.map((g) => (
            <div key={g.id} className="flex items-center justify-between px-5 py-4">
              <div>
                <p className="font-medium text-ink">{g.name}</p>
                {g.description && <p className="text-sm text-slate">{g.description}</p>}
              </div>
              <div className="flex gap-1">
                <Button variant="ghost" onClick={() => openEdit(g)}><Pencil size={15} /></Button>
                <Button variant="ghost" onClick={() => remove(g)}><Trash2 size={15} /></Button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit group' : 'New group'}>
        <form onSubmit={save} className="space-y-4">
          <Input label="Name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <Textarea label="Description (optional)" rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          {error && <p className="text-sm text-clay">{error}</p>}
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit">{editing ? 'Save changes' : 'Create group'}</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
