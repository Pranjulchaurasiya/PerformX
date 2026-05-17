import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../../api/client'
import toast from 'react-hot-toast'
import type { GoalCycle } from '../../types'
import { PageSpinner } from '../../components/Spinner'

export default function ManagerCheckin() {
  const { employeeId } = useParams()
  const navigate = useNavigate()
  const [cycles, setCycles] = useState<GoalCycle[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({ cycle_id: '', comment_type: 'note', comment_text: '' })

  useEffect(() => {
    api.get('/admin/cycles').then(r => {
      setCycles(r.data)
      const active = r.data.find((c: GoalCycle) => c.is_active)
      if (active) setForm(f => ({ ...f, cycle_id: String(active.id) }))
    }).finally(() => setLoading(false))
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.cycle_id || !form.comment_text.trim()) { toast.error('All fields required'); return }
    setSaving(true)
    try {
      await api.post('/checkins', {
        employee_id: parseInt(employeeId!),
        cycle_id: parseInt(form.cycle_id),
        comment_type: form.comment_type,
        comment_text: form.comment_text,
      })
      toast.success('Check-in saved!')
      navigate(`/manager/team/${employeeId}`)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to save check-in')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <PageSpinner />

  return (
    <div className="p-6 max-w-lg space-y-5">
      <button onClick={() => navigate(-1)} className="text-gray-400 hover:text-gray-600 text-sm">← Back</button>
      <h1 className="text-2xl font-bold text-gray-900">Add Check-in Comment</h1>
      <p className="text-sm text-gray-500">Employee #{employeeId}</p>

      <form onSubmit={handleSubmit} className="card p-6 space-y-4">
        <div>
          <label className="label">Cycle *</label>
          <select className="input" value={form.cycle_id} onChange={e => setForm(f => ({ ...f, cycle_id: e.target.value }))} required>
            <option value="">Select cycle…</option>
            {cycles.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Comment Type *</label>
          <select className="input" value={form.comment_type} onChange={e => setForm(f => ({ ...f, comment_type: e.target.value }))}>
            <option value="positive_feedback">Positive Feedback</option>
            <option value="needs_improvement">Needs Improvement</option>
            <option value="at_risk">At Risk</option>
            <option value="note">General Note</option>
          </select>
        </div>
        <div>
          <label className="label">Comment *</label>
          <textarea className="input" rows={5} value={form.comment_text}
            onChange={e => setForm(f => ({ ...f, comment_text: e.target.value }))}
            placeholder="Document your check-in discussion…" required />
        </div>
        <div className="flex gap-3">
          <button type="submit" disabled={saving} className="btn-primary">
            {saving ? 'Saving…' : 'Save Check-in'}
          </button>
          <button type="button" onClick={() => navigate(-1)} className="btn-secondary">Cancel</button>
        </div>
      </form>
    </div>
  )
}
