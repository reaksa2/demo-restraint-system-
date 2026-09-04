import { useEffect, useState } from 'react'
import { brandsApi, cloneApi } from '../services/resources'
import { Button, Select, Card } from '../components/ui'
import { Copy, ArrowRight, AlertTriangle, CheckCircle2 } from 'lucide-react'

export default function ClonePage() {
  const [brands, setBrands] = useState([])
  const [sourceId, setSourceId] = useState('')
  const [targetId, setTargetId] = useState('')
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    brandsApi.list().then((data) => {
      setBrands(data)
      if (data.length >= 2) { setSourceId(data[0].id); setTargetId(data[1].id) }
      setLoading(false)
    })
  }, [])

  const run = async () => {
    setError('')
    setResult(null)
    if (sourceId === targetId) { setError('Source and target must be different brands.'); return }
    setRunning(true)
    try {
      const res = await cloneApi.cloneFoods(sourceId, targetId)
      setResult(res)
    } catch (err) {
      setError(err.response?.data?.detail || 'Clone failed.')
    } finally {
      setRunning(false)
    }
  }

  const brandLabel = (id) => {
    const b = brands.find((x) => x.id === id)
    return b ? `${b.name_en}` : ''
  }

  if (loading) return <p className="text-sm text-slate">Loading…</p>

  if (brands.length < 2) {
    return (
      <div>
        <h1 className="font-display text-2xl text-ink">Clone Menu</h1>
        <p className="mt-2 text-sm text-slate">You need at least two brands in your group to clone a menu between them.</p>
      </div>
    )
  }

  return (
    <div className="max-w-xl">
      <h1 className="font-display text-2xl text-ink">Clone Menu</h1>
      <p className="mt-1 text-sm text-slate">
        Copy every food, category, image, and price from one brand to another within your group.
        The copies become fully independent — changing one brand's menu afterward never affects the other.
      </p>

      <Card className="mt-6 p-5">
        <div className="flex items-center gap-3">
          <Select label="From" value={sourceId} onChange={(e) => setSourceId(e.target.value)} className="flex-1">
            {brands.map((b) => <option key={b.id} value={b.id}>{b.name_en}</option>)}
          </Select>
          <ArrowRight size={18} className="mt-6 flex-shrink-0 text-slate" />
          <Select label="To" value={targetId} onChange={(e) => setTargetId(e.target.value)} className="flex-1">
            {brands.map((b) => <option key={b.id} value={b.id}>{b.name_en}</option>)}
          </Select>
        </div>

        {error && <p className="mt-3 text-sm text-clay">{error}</p>}

        <Button onClick={run} disabled={running} className="mt-4 w-full">
          <Copy size={16} /> {running ? 'Cloning…' : `Clone ${brandLabel(sourceId)} → ${brandLabel(targetId)}`}
        </Button>
      </Card>

      {result && (
        <Card className="mt-4 p-5">
          <div className="flex items-center gap-2 text-moss">
            <CheckCircle2 size={18} />
            <p className="font-medium">Clone complete</p>
          </div>
          <ul className="mt-2 space-y-1 text-sm text-slate">
            <li>{result.foods_cloned} food{result.foods_cloned === 1 ? '' : 's'} cloned</li>
            <li>{result.categories_created} new categor{result.categories_created === 1 ? 'y' : 'ies'} created</li>
          </ul>
          {result.warnings.length > 0 && (
            <div className="mt-3 rounded-md bg-marigold-light p-3">
              <div className="flex items-center gap-2 text-marigold-dark">
                <AlertTriangle size={15} />
                <p className="text-sm font-medium">{result.warnings.length} price{result.warnings.length === 1 ? '' : 's'} skipped</p>
              </div>
              <ul className="mt-1.5 space-y-0.5 text-sm text-marigold-dark/90">
                {result.warnings.map((w, i) => <li key={i}>{w}</li>)}
              </ul>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
