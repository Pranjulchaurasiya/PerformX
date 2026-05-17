import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../api/client'
import toast from 'react-hot-toast'
import type { ThrustArea } from '../../types'
import Spinner from '../../components/Spinner'

export default function GoalCreate() {
  const navigate = useNavigate()
  const [thrustAreas, setThrustAreas] = useState<ThrustArea[]>([])
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    thrust_area_id: '',
    title: '',
    description: '',
    uom_type: 'min',
    target: '',
    target_date: '',
    weightage: '',
  })

  useEffect(() => {
    api.get('/goals/thrust-areas').then(r => setThrustAreas(r.data))
  }, [])

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const isValid =
    !!form.thrust_area_id &&
    !!form.title.trim() &&
    parseFloat(form.weightage) >= 10 &&
    (form.uom_type === 'timeline'
      ? !!form.target_date
      : form.uom_type === 'zero' || !!form.target)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.thrust_area_id) { toast.error('Select a thrust area'); return }
    const w = parseFloat(form.weightage)
    if (isNaN(w) || w < 10) { toast.error('Minimum weightage is 10%'); return }

    const payload: any = {
      thrust_area_id: parseInt(form.thrust_area_id),
      title: form.title,
      description: form.description || null,
      uom_type: form.uom_type,
      weightage: w,
    }
    if (form.uom_type === 'timeline') {
      if (!form.target_date) { toast.error('Target date is required for Timeline goals'); return }
      payload.target_date = form.target_date
    } else {
      if (!form.target) { toast.error('Target value is required'); return }
      payload.target = parseFloat(form.target)
    }

    setLoading(true)
    try {
      const { data } = await api.post('/goals', payload)
      toast.success('Goal created!')
      navigate(`/employee/goals/${data.id}`)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to create goal')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Create New Goal</h1>
      <form onSubmit={handleSubmit} className="card p-6 space-y-5">
        <div>
          <label className="label">Thrust Area *</label>
          <select className="input" value={form.thrust_area_id} onChange={e => set('thrust_area_id', e.target.value)} required>
            <option value="">Select thrust area…</option>
            {thrustAreas.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Goal Title *</label>
          <input className="input" value={form.title} onChange={e => set('title', e.target.value)} required placeholder="e.g. Achieve Q1 Sales Target" />
        </div>
        <div>
          <label className="label">Description</label>
          <textarea className="input" rows={3} value={form.description} onChange={e => set('description', e.target.value)} placeholder="Optional details…" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Unit of Measurement *</label>
            <select className="input" value={form.uom_type} onChange={e => set('uom_type', e.target.value)}>
              <option value="min">Numeric MIN (higher is better)</option>
              <option value="max">Numeric MAX (lower is better)</option>
              <option value="timeline">Timeline (date-based)</option>
              <option value="zero">Zero-based (0 = success)</option>
            </select>
          </div>
          <div>
            <label className="label">Weightage (%) *</label>
            <input type="number" className="input" min={10} max={100} step={1}
              value={form.weightage} onChange={e => set('weightage', e.target.value)} required placeholder="Min 10%" />
            {form.weightage !== '' && parseFloat(form.weightage) < 10 && (
              <p className="text-red-500 text-xs mt-1">Minimum 10% weightage required per goal</p>
            )}
          </div>
        </div>
        {form.uom_type === 'timeline'
          ? <div>
              <label className="label">Target Date *</label>
              <input type="date" className="input" value={form.target_date} onChange={e => set('target_date', e.target.value)} required />
            </div>
          : form.uom_type !== 'zero' && (
              <div>
                <label className="label">Target Value *</label>
                <input type="number" className="input" value={form.target} onChange={e => set('target', e.target.value)} required placeholder="e.g. 500000" />
              </div>
            )
        }
        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={loading || !isValid} className="btn-primary">
            {loading ? <Spinner size="sm" /> : null} Save Goal
          </button>
          <button type="button" onClick={() => navigate(-1)} className="btn-secondary">Cancel</button>
        </div>
      </form>
    </div>
  )
}
