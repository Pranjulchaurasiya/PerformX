import { useEffect, useState } from 'react'
import { Plus, Edit2, CheckCircle, XCircle } from 'lucide-react'
import api from '../../api/client'
import toast from 'react-hot-toast'
import type { GoalCycle } from '../../types'
import Modal from '../../components/Modal'
import { PageSpinner } from '../../components/Spinner'

export default function AdminCycles() {
  const [cycles, setCycles] = useState<GoalCycle[]>([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(false)
  const [editing, setEditing] = useState<GoalCycle | null>(null)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({ name: '', phase: 'q1', window_open: '', window_close: '', penalty_factor: '5' })

  const load = () => { api.get('/admin/cycles').then(r => setCycles(r.data)).finally(() => setLoading(false)) }
  useEffect(load, [])

  const openCreate = () => { setEditing(null); setForm({ name: '', phase: 'q1', window_open: '', window_close: '', penalty_factor: '5' }); setModal(true) }
  const openEdit = (c: GoalCycle) => {
    setEditing(c)
    setForm({ name: c.name, phase: c.phase, window_open: c.window_open || '', window_close: c.window_close || '', penalty_factor: String((c.penalty_factor * 100).toFixed(0)) })
    setModal(true)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const payload = { name: form.name, phase: form.phase, window_open: form.window_open || null, window_close: form.window_close || null, penalty_factor: parseFloat(form.penalty_factor) / 100 }
      if (editing) await api.put(`/admin/cycles/${editing.id}`, payload)
      else await api.post('/admin/cycles', payload)
      toast.success(editing ? 'Cycle updated' : 'Cycle created')
      setModal(false); load()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Save failed')
    } finally { setSaving(false) }
  }

  const toggleActive = async (c: GoalCycle) => {
    try {
      if (c.is_active) await api.post(`/admin/cycles/${c.id}/deactivate`)
      else await api.post(`/admin/cycles/${c.id}/activate`)
      toast.success(c.is_active ? 'Cycle deactivated' : 'Cycle activated')
      load()
    } catch { toast.error('Failed') }
  }

  if (loading) return <PageSpinner />

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Goal Cycles</h1>
        <button onClick={openCreate} className="btn-primary"><Plus size={16} /> Add Cycle</button>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th className="px-5 py-3 text-left">Name</th>
              <th className="px-5 py-3 text-left">Phase</th>
              <th className="px-5 py-3 text-left">Window</th>
              <th className="px-5 py-3 text-left">Penalty/day</th>
              <th className="px-5 py-3 text-left">Status</th>
              <th className="px-5 py-3 text-left"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {cycles.map(c => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="px-5 py-3 font-medium">{c.name}</td>
                <td className="px-5 py-3"><span className="badge bg-gray-100 text-gray-700 uppercase">{c.phase}</span></td>
                <td className="px-5 py-3 text-gray-500 text-xs">{c.window_open} → {c.window_close}</td>
                <td className="px-5 py-3 text-gray-700 font-medium">{(c.penalty_factor * 100).toFixed(0)}%</td>
                <td className="px-5 py-3">
                  <span className={`badge ${c.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                    {c.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-5 py-3">
                  <div className="flex items-center gap-2">
                    <button onClick={() => openEdit(c)} className="text-primary-600 hover:underline flex items-center gap-1 text-xs"><Edit2 size={12} /> Edit</button>
                    <button onClick={() => toggleActive(c)} className={`flex items-center gap-1 text-xs ${c.is_active ? 'text-red-500' : 'text-green-600'}`}>
                      {c.is_active ? <><XCircle size={12} /> Deactivate</> : <><CheckCircle size={12} /> Activate</>}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal open={modal} onClose={() => setModal(false)} title={editing ? 'Edit Cycle' : 'Add Cycle'}>
        <div className="space-y-4">
          <div><label className="label">Name *</label><input className="input" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="e.g. FY 2026 Q1" /></div>
          <div><label className="label">Phase *</label>
            <select className="input" value={form.phase} onChange={e => setForm(f => ({ ...f, phase: e.target.value }))}>
              <option value="goal_setting">Goal Setting</option>
              <option value="q1">Q1</option>
              <option value="q2">Q2</option>
              <option value="q3">Q3</option>
              <option value="q4">Q4</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label">Window Opens</label><input type="date" className="input" value={form.window_open} onChange={e => setForm(f => ({ ...f, window_open: e.target.value }))} /></div>
            <div><label className="label">Window Closes</label><input type="date" className="input" value={form.window_close} onChange={e => setForm(f => ({ ...f, window_close: e.target.value }))} /></div>
          </div>
          <div>
            <label className="label">Late Completion Penalty (% per day)</label>
            <input type="number" className="input" min={0} max={20} value={form.penalty_factor}
              onChange={e => setForm(f => ({ ...f, penalty_factor: e.target.value }))}
              placeholder="Default: 5" />
            <p className="text-xs text-gray-400 mt-1">Applied to Timeline goals completed after deadline. 0–20%.</p>
          </div>
          <div className="flex gap-3 pt-2">
            <button onClick={handleSave} disabled={saving} className="btn-primary">{saving ? 'Saving…' : 'Save'}</button>
            <button onClick={() => setModal(false)} className="btn-secondary">Cancel</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
