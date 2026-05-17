import { useEffect, useState } from 'react'
import { Unlock } from 'lucide-react'
import api from '../../api/client'
import toast from 'react-hot-toast'
import { PageSpinner } from '../../components/Spinner'
import Modal from '../../components/Modal'

export default function AdminAuditLogs() {
  const [logs, setLogs] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)

  // Unlock modal state
  const [unlockModal, setUnlockModal] = useState(false)
  const [unlockGoalId, setUnlockGoalId] = useState<number | null>(null)
  const [unlockReason, setUnlockReason] = useState('')
  const [reasonError, setReasonError] = useState('')
  const [unlocking, setUnlocking] = useState(false)

  const loadLogs = () => {
    setLoading(true)
    api.get(`/audit?page=${page}&page_size=20`).then(r => {
      setLogs(r.data.items)
      setTotal(r.data.total)
    }).finally(() => setLoading(false))
  }

  useEffect(loadLogs, [page])

  const openUnlock = (goalId: number) => {
    setUnlockGoalId(goalId)
    setUnlockReason('')
    setReasonError('')
    setUnlockModal(true)
  }

  const handleUnlock = async () => {
    if (!unlockReason.trim()) {
      setReasonError('Please provide a reason')
      return
    }
    if (unlockReason.trim().length < 10) {
      setReasonError('Reason must be at least 10 characters')
      return
    }
    setUnlocking(true)
    try {
      await api.post(`/goals/${unlockGoalId}/unlock`, { reason: unlockReason.trim() })
      toast.success('Goal unlocked successfully')
      setUnlockModal(false)
      loadLogs() // refresh table
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Unlock failed')
    } finally {
      setUnlocking(false)
    }
  }

  if (loading) return <PageSpinner />

  return (
    <div className="p-6 space-y-5">
      <h1 className="text-2xl font-bold text-gray-900">Audit Logs</h1>
      <p className="text-sm text-gray-500">{total} total entries</p>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th className="px-5 py-3 text-left">When</th>
              <th className="px-5 py-3 text-left">User</th>
              <th className="px-5 py-3 text-left">Goal</th>
              <th className="px-5 py-3 text-left">Field</th>
              <th className="px-5 py-3 text-left">Old → New</th>
              <th className="px-5 py-3 text-left">Reason</th>
              <th className="px-5 py-3 text-left">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {logs.length === 0
              ? <tr><td colSpan={7} className="px-5 py-8 text-center text-gray-400">No audit logs yet.</td></tr>
              : logs.map(log => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-5 py-3 text-gray-400 text-xs whitespace-nowrap">{new Date(log.changed_at).toLocaleString()}</td>
                    <td className="px-5 py-3 font-medium">{log.user_name || `#${log.user_id}`}</td>
                    <td className="px-5 py-3 text-gray-500">#{log.goal_id}</td>
                    <td className="px-5 py-3"><span className="badge bg-gray-100 text-gray-700">{log.field_changed}</span></td>
                    <td className="px-5 py-3 text-xs">
                      <span className="text-red-500 line-through">{log.old_value}</span>
                      <span className="mx-1 text-gray-400">→</span>
                      <span className="text-green-600">{log.new_value}</span>
                    </td>
                    <td className="px-5 py-3 text-gray-400 text-xs">{log.reason || '—'}</td>
                    <td className="px-5 py-3">
                      {/* Show Unlock button only when the goal's latest recorded status is locked */}
                      {log.new_value === 'locked' && log.goal_id && (
                        <button
                          onClick={() => openUnlock(log.goal_id)}
                          className="flex items-center gap-1 text-xs text-amber-600 hover:text-amber-800 font-medium transition-colors"
                        >
                          <Unlock size={13} /> Unlock
                        </button>
                      )}
                    </td>
                  </tr>
                ))
            }
          </tbody>
        </table>
      </div>

      {total > 20 && (
        <div className="flex items-center justify-between">
          <button disabled={page === 1} onClick={() => setPage(p => p - 1)} className="btn-secondary text-xs py-1.5">← Prev</button>
          <span className="text-sm text-gray-500">Page {page} of {Math.ceil(total / 20)}</span>
          <button disabled={page * 20 >= total} onClick={() => setPage(p => p + 1)} className="btn-secondary text-xs py-1.5">Next →</button>
        </div>
      )}

      {/* Unlock Goal Modal */}
      <Modal open={unlockModal} onClose={() => setUnlockModal(false)} title="Unlock Goal">
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            This will allow the employee to edit this goal.
            All changes will be logged.
          </p>
          <div>
            <label className="label">Reason for unlock *</label>
            <textarea
              className="input"
              rows={4}
              value={unlockReason}
              onChange={e => { setUnlockReason(e.target.value); setReasonError('') }}
              placeholder="Provide a reason (min 10 characters)…"
            />
            {reasonError && <p className="text-red-500 text-xs mt-1">{reasonError}</p>}
          </div>
          <div className="flex gap-3 pt-1">
            <button onClick={handleUnlock} disabled={unlocking} className="btn-danger">
              {unlocking ? 'Unlocking…' : 'Confirm Unlock'}
            </button>
            <button onClick={() => setUnlockModal(false)} className="btn-secondary">Cancel</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
