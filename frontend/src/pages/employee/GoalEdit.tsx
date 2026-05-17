import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { AlertTriangle } from 'lucide-react'
import api from '../../api/client'
import toast from 'react-hot-toast'
import type { Goal, ThrustArea } from '../../types'
import { PageSpinner } from '../../components/Spinner'
import Spinner from '../../components/Spinner'

export default function GoalEdit() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [goal, setGoal] = useState<Goal | null>(null)
  const [thrustAreas, setThrustAreas] = useState<ThrustArea[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({
    thrust_area_id: '', title: '', description: '',
    uom_type: 'min', target: '', target_date: '', weightage: '',
  })

  useEffect(() => {
    Promise.all([api.get(`/goals/${id}`), api.get('/goals/thrust-areas')]).then(([g, t]) => {
      const goal = g.data as Goal
      // Only allow editing returned/draft goals
      if (!['draft', 'returned'].includes(goal.status)) {
        navigate(`/employee/goals/${id}`)
        return
      }
      setGoal(goal)
      setThrustAreas(t.data)
      setForm({
        thrust_area_id: String(goal.thrust_area_id),
        title: goal.title,
        description: goal.description || '',
        uom_type: goal.uom_type,
        target: goal.target != null ? String(goal.target) : '',
        target_date: goal.target_date || '',
        weightage: String(goal.weightage),
      })
    }).catch(() => navigate('/employee/goals')).finally(() => setLoading(false))
  }, [id])

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const isValid =
    !!form.thrust_area_id &&
    !!form.title.trim() &&
    parseFloat(form.weightage) >= 10 &&
    (form.uom_type === 'timeline'
      ? !!form.target_date
      : form.uom_type === 'zero' || !!form.target)

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!goal) return
    setSaving(true)
    try {
      const payload: any = {
        thrust_area_id: parseInt(form.thrust_area_id),
        title: form.title,
        description: form.description || null,
        uom_type: form.uom_type,
        weightage: parseFloat(form.weightage),
      }
      if (form.uom_type === 'timeline') payload.target_date = form.target_date
      else if (form.uom_type !== 'zero') payload.target = parseFloat(form.target)

      await api.put(`/goals/${goal.id}`, payload)
      toast.success('Goal saved')
      navigate(`/employee/goals/${goal.id}`)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <PageSpinner />
  if (!goal) return null

  return (
    <div className="p-6 max-w-2xl space-y-5">
      <button onClick={() => navigate(-1)} className="text-gray-400 hover:text-gray-600 text-sm">← Back</button>

      {/* Returned banner */}
      {goal.status === 'returned' && goal.rework_comment && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex gap-3">
          <AlertTriangle size={18} className="text-amber-600 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-amber-800">Returned by manager</p>
            <p className="text-sm text-amber-700 mt-1">{goal.rework_comment}</p>
          </div>
        </div>
      )}

      <h1 className="text-2xl font-bold text-gray-900">Edit Goal</h1>

      <form onSubmit={handleSave} className="card p-6 space-y-5">
        <div>
          <label className="label">Thrust Area *</label>
          <select className="input" value={form.thrust_area_id} onChange={e => set('thrust_area_id', e.target.value)} required>
            {thrustAreas.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Goal Title *</label>
          <input className="input" value={form.title} onChange={e => set('title', e.target.value)} required />
        </div>
        <div>
          <label className="label">Description</label>
          <textarea className="input" rows={3} value={form.description} onChange={e => set('description', e.target.value)} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">UoM Type *</label>
            <select className="input" value={form.uom_type} onChange={e => set('uom_type', e.target.value)}>
              <option value="min">Numeric MIN</option>
              <option value="max">Numeric MAX</option>
              <option value="timeline">Timeline</option>
              <option value="zero">Zero-based</option>
            </select>
          </div>
          <div>
            <label className="label">Weightage (%) *</label>
            <input type="number" className="input" min={10} max={100} step={5}
              value={form.weightage} onChange={e => set('weightage', e.target.value)} required />
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
                <input type="number" className="input" value={form.target} onChange={e => set('target', e.target.value)} required />
              </div>
            )
        }
        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={saving || !isValid} className="btn-primary">
            {saving ? <Spinner size="sm" /> : null} Save Changes
          </button>
          <button type="button" onClick={() => navigate(`/employee/goals/${goal.id}`)} className="btn-secondary">Cancel</button>
        </div>
      </form>
    </div>
  )
}
