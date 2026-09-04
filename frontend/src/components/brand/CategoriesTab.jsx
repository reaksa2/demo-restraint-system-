import { useEffect, useState } from 'react'
import { categoriesApi } from '../../services/resources'
import { Button, Input, EmptyState } from '../ui'
import { Modal } from '../Modal'
import { Plus, Pencil, Trash2 } from 'lucide-react'

export default function CategoriesTab({ brandId }) {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ name_en: '', name_kh: '', sort_order: 0 })
  const [error, setError] = useState('')

  const load = () => categoriesApi.list(brandId).then((data) => { setCategories(data); setLoading(false) })
  useEffect(() => { load() }, [brandId])

  const openCreate = () => { setEditing(null); setForm({ name_en: '', name_kh: '', sort_order: categories.length }); setError(''); setModalOpen(true) }
  const openEdit = (c) => { setEditing(c); setForm({ name_en: c.name_en, name_kh: c.name_kh, sort_order: c.sort_order }); setError(''); setModalOpen(true) }

  const save = async (e) => {
    e.preventDefault()
    setError('')
    try {
      if (editing) await categoriesApi.update(brandId, editing.id, form)
      else await categoriesApi.create(brandId, form)
      setModalOpen(false)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong.')
    }
  }

  const remove = async (c) => {
    if (!confirm(`Delete category "${c.name_en}"? Foods in it will become uncategorized.`)) return
    await categoriesApi.remove(brandId, c.id)
    load()
  }

  if (loading) return <p className="text-sm text-slate">Loading…</p>

  return (
    <div>
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate">Categories organize the menu (e.g. Chicken, Rice, Drinks).</p>
        <Button onClick={openCreate}><Plus size={16} /> New category</Button>
      </div>

      {categories.length === 0 ? (
        <div className="mt-4">
          <EmptyState title="No categories yet" action={<Button onClick={openCreate}>Add a category</Button>} />
        </div>
      ) : (
        <div className="mt-4 divide-y divide-sand rounded-lg border border-sand bg-white">
          {categories.map((c) => (
            <div key={c.id} className="flex items-center justify-between px-5 py-3">
              <div>
                <p className="font-khmer font-medium text-ink">{c.name_kh}</p>
                <p className="text-sm text-slate">{c.name_en}</p>
              </div>
              <div className="flex gap-1">
                <Button variant="ghost" onClick={() => openEdit(c)}><Pencil size={14} /></Button>
                <Button variant="ghost" onClick={() => remove(c)}><Trash2 size={14} /></Button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit category' : 'New category'}>
        <form onSubmit={save} className="space-y-4">
          <Input label="Name (English)" required value={form.name_en} onChange={(e) => setForm({ ...form, name_en: e.target.value })} />
          <Input label="Name (Khmer)" required value={form.name_kh} onChange={(e) => setForm({ ...form, name_kh: e.target.value })} className="font-khmer" />
          <Input label="Sort order" type="number" value={form.sort_order} onChange={(e) => setForm({ ...form, sort_order: Number(e.target.value) })} />
          {error && <p className="text-sm text-clay">{error}</p>}
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit">{editing ? 'Save changes' : 'Create category'}</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
