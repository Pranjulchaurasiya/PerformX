import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import api from '../../api/client'
import toast from 'react-hot-toast'
import type { ThrustArea, User } from '../../types'
import Modal from '../../components/Modal'
import { PageSpinner } from '../../components/Spinner'

export default function AdminSharedGoals() {
  const [thrustAreas, setThrustAreas] = useState<ThrustArea[]>([])
  const [employees, setEmployees] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(false)
  const [saving, setSaving] = useState(false)
  const [selected, setSelected] = useState<number[]>([])
  const [form, setForm] = useState({ thrust_area_id: '', title: '', description: '', uom_type: 'min', target: '', default_weightage: '10' })

  useEffect(() => {
    Promise.all([api.get('/goals/thrust-areas'), api.get('/admin/users?role=employee&page_size=100')])
      .then(([t, u]) => { setThrustAreas(t.data); setEmployees(u.data) })
      .finally(() => setLoading(false))
  }, [])

  const toggleEmp = (id: number) => setSelected(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id])

  const handleCreate = async () => {
    if (!form.thrust_area_id || !form.title || selected.length === 0) { toast.error('Fill all fields and select employees'); return }
    setSaving(true)
    try {
      await api.post('/shared-goals', {
        thrust_area_id: parseInt(form.thrust_area_id),
        title: form.title,
        description: form.description || null,
        uom_type: form.uom_type,
        target: form.target ? parseFloat(form.target) : null,
        employee_ids: selected,
        default_weightage: parseFloat(form.default_weightage),
      })
      toast.success(`Shared goal pushed to ${selected.length} employees`)
      setModal(false); setSelected([])
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed')
    } finally { setSaving(false) }
  }

  if (loading) return <PageSpinner />

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Shared Goals</h1>
          <p className="text-sm text-gray-500 mt-1">Push departmental KPIs to multiple employees at once</p>
        </div>
        <button onClick={() => setModal(true)} className="btn-primary"><Plus size={16} /> Push Shared Goal</button>
      </div>

      <div className="card p-8 text-center text-gray-400">
        <p>Use the button above to push a shared/departmental KPI to your team.</p>
        <p className="text-xs mt-2">Recipients can only adjust weightage — title and target are read-only.</p>
      </div>

      <Modal open={modal} onClose={() => setModal(false)} title="Push Shared Goal" size="lg">
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">Thrust Area *</label>
              <select className="input" value={form.thrust_area_id} onChange={e => setForm(f => ({ ...f, thrust_area_id: e.target.value }))}>
                <option value="">Select…</option>
                {thrustAreas.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            </div>
            <div><label className="label">UoM Type *</label>
              <select className="input" value={form.uom_type} onChange={e => setForm(f => ({ ...f, uom_type: e.target.value }))}>
                <option value="min">Numeric MIN</option>
                <option value="max">Numeric MAX</option>
                <option value="timeline">Timeline</option>
                <option value="zero">Zero-based</option>
              </select>
            </div>
          </div>
          <div><label className="label">Goal Title *</label><input className="input" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} /></div>
          <div><label className="label">Description</label><textarea className="input" rows={2} value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} /></div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">Target Value</label><input type="number" className="input" value={form.target} onChange={e => setForm(f => ({ ...f, target: e.target.value }))} /></div>
            <div><label className="label">Default Weightage (%)</label><input type="number" className="input" min={10} max={100} value={form.default_weightage} onChange={e => setForm(f => ({ ...f, default_weightage: e.target.value }))} /></div>
          </div>
          <div>
            <label className="label">Assign to Employees * ({selected.length} selected)</label>
            <div className="border border-gray-200 rounded-lg max-h-40 overflow-y-auto divide-y divide-gray-100">
              {employees.map(emp => (
                <label key={emp.id} className="flex items-center gap-3 px-3 py-2 hover:bg-gray-50 cursor-pointer">
                  <input type="checkbox" checked={selected.includes(emp.id)} onChange={() => toggleEmp(emp.id)} className="rounded" />
                  <span className="text-sm">{emp.name}</span>
                  <span className="text-xs text-gray-400">{emp.email}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <button onClick={handleCreate} disabled={saving} className="btn-primary">{saving ? 'Pushing…' : 'Push to Team'}</button>
            <button onClick={() => setModal(false)} className="btn-secondary">Cancel</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
