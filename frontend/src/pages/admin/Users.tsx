import { useEffect, useState } from 'react'
import { Plus, Edit2 } from 'lucide-react'
import api from '../../api/client'
import toast from 'react-hot-toast'
import type { User } from '../../types'
import Modal from '../../components/Modal'
import { PageSpinner } from '../../components/Spinner'

interface Dept { id: number; name: string }

export default function AdminUsers() {
  const [users, setUsers] = useState<User[]>([])
  const [depts, setDepts] = useState<Dept[]>([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(false)
  const [editing, setEditing] = useState<User | null>(null)
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'employee', department_id: '', manager_id: '' })
  const [saving, setSaving] = useState(false)

  const load = () => {
    Promise.all([api.get('/admin/users?page_size=100'), api.get('/admin/departments')])
      .then(([u, d]) => { setUsers(u.data); setDepts(d.data) })
      .finally(() => setLoading(false))
  }
  useEffect(load, [])

  const openCreate = () => { setEditing(null); setForm({ name: '', email: '', password: '', role: 'employee', department_id: '', manager_id: '' }); setModal(true) }
  const openEdit = (u: User) => { setEditing(u); setForm({ name: u.name, email: u.email, password: '', role: u.role, department_id: String(u.department_id || ''), manager_id: String(u.manager_id || '') }); setModal(true) }

  const handleSave = async () => {
    setSaving(true)
    try {
      const payload: any = { name: form.name, email: form.email, role: form.role, department_id: form.department_id ? parseInt(form.department_id) : null, manager_id: form.manager_id ? parseInt(form.manager_id) : null }
      if (!editing) { payload.password = form.password; await api.post('/admin/users', payload) }
      else await api.put(`/admin/users/${editing.id}`, payload)
      toast.success(editing ? 'User updated' : 'User created')
      setModal(false); load()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Save failed')
    } finally { setSaving(false) }
  }

  if (loading) return <PageSpinner />

  const managers = users.filter(u => u.role === 'manager')

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Users</h1>
        <button onClick={openCreate} className="btn-primary"><Plus size={16} /> Add User</button>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th className="px-5 py-3 text-left">Name</th>
              <th className="px-5 py-3 text-left">Email</th>
              <th className="px-5 py-3 text-left">Role</th>
              <th className="px-5 py-3 text-left">Department</th>
              <th className="px-5 py-3 text-left"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {users.map(u => (
              <tr key={u.id} className="hover:bg-gray-50">
                <td className="px-5 py-3 font-medium">{u.name}</td>
                <td className="px-5 py-3 text-gray-500">{u.email}</td>
                <td className="px-5 py-3"><span className={`badge ${u.role === 'admin' ? 'bg-red-100 text-red-700' : u.role === 'manager' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'}`}>{u.role}</span></td>
                <td className="px-5 py-3 text-gray-500">{depts.find(d => d.id === u.department_id)?.name || '—'}</td>
                <td className="px-5 py-3"><button onClick={() => openEdit(u)} className="text-primary-600 hover:underline flex items-center gap-1"><Edit2 size={13} /> Edit</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal open={modal} onClose={() => setModal(false)} title={editing ? 'Edit User' : 'Add User'}>
        <div className="space-y-4">
          <div><label className="label">Name *</label><input className="input" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} /></div>
          <div><label className="label">Email *</label><input type="email" className="input" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} /></div>
          {!editing && <div><label className="label">Password *</label><input type="password" className="input" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} /></div>}
          <div><label className="label">Role *</label>
            <select className="input" value={form.role} onChange={e => setForm(f => ({ ...f, role: e.target.value }))}>
              <option value="employee">Employee</option>
              <option value="manager">Manager</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div><label className="label">Department</label>
            <select className="input" value={form.department_id} onChange={e => setForm(f => ({ ...f, department_id: e.target.value }))}>
              <option value="">None</option>
              {depts.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>
          <div><label className="label">Manager</label>
            <select className="input" value={form.manager_id} onChange={e => setForm(f => ({ ...f, manager_id: e.target.value }))}>
              <option value="">None</option>
              {managers.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
            </select>
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
