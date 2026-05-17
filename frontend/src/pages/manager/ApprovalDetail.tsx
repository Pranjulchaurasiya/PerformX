import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { CheckCircle, XCircle, RotateCcw } from 'lucide-react'
import api from '../../api/client'
import toast from 'react-hot-toast'
import type { Goal } from '../../types'
import { GoalStatusBadge } from '../../components/StatusBadge'
import { PageSpinner } from '../../components/Spinner'
import Modal from '../../components/Modal'

export default function ManagerApprovalDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [goal, setGoal] = useState<Goal | null>(null)
  const [loading, setLoading] = useState(true)
  const [returnModal, setReturnModal] = useState(false)
  const [returnComment, setReturnComment] = useState('')
  const [editTarget, setEditTarget] = useState('')
  const [editWeightage, setEditWeightage] = useState('')
  const [saving, setSaving] = useState(false)
  const [diff, setDiff] = useState<any>(null)

  useEffect(() => {
    api.get(`/goals/${id}`).then(r => {
      setGoal(r.data)
      setEditTarget(r.data.target != null ? String(r.data.target) : '')
      setEditWeightage(String(r.data.weightage))
      if (r.data.status === 'resubmitted') {
        api.get(`/goals/${id}/resubmission-diff`).then(d => setDiff(d.data)).catch(() => {})
      }
    }).catch(() => navigate('/manager/approvals')).finally(() => setLoading(false))
  }, [id])

  const handleApprove = async () => {
    if (!goal) return
    setSaving(true)
    try {
      // Save inline edits first if changed
      if (editTarget !== String(goal.target) || editWeightage !== String(goal.weightage)) {
        await api.put(`/goals/${goal.id}/manager-edit`, {
          target: editTarget ? parseFloat(editTarget) : undefined,
          weightage: parseFloat(editWeightage),
        })
      }
      await api.post(`/goals/${goal.id}/approve`)
      toast.success('Goal approved and locked!')
      navigate('/manager/approvals')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Approval failed')
    } finally {
      setSaving(false)
    }
  }

  const handleReturn = async () => {
    if (!goal || !returnComment.trim()) { toast.error('Comment is required'); return }
    setSaving(true)
    try {
      await api.post(`/goals/${goal.id}/return`, { comment: returnComment })
      toast.success('Goal returned for rework')
      navigate('/manager/approvals')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Return failed')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <PageSpinner />
  if (!goal) return null

  return (
    <div className="p-6 max-w-2xl space-y-5">
      <button onClick={() => navigate(-1)} className="text-gray-400 hover:text-gray-600 text-sm">← Back to Approvals</button>

      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Review Goal</h1>
        <div className="flex items-center gap-2">
          {goal.status === 'resubmitted' && <span className="badge bg-amber-100 text-amber-700">Resubmission</span>}
          <GoalStatusBadge status={goal.status} />
        </div>
      </div>

      {/* Resubmission diff */}
      {diff && diff.changes?.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <p className="text-sm font-semibold text-blue-800 mb-2">Changes since last submission</p>
          {diff.changes.map((c: any, i: number) => (
            <div key={i} className="text-xs text-blue-700 flex gap-2">
              <span className="font-medium">{c.field}:</span>
              <span className="line-through text-blue-400">{c.old_value}</span>
              <span>→</span>
              <span>{c.new_value}</span>
            </div>
          ))}
        </div>
      )}

      <div className="card p-6 space-y-5">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div><p className="text-gray-400 text-xs mb-1">Title</p><p className="font-medium">{goal.title}</p></div>
          <div><p className="text-gray-400 text-xs mb-1">Thrust Area</p><p className="font-medium">{goal.thrust_area?.name}</p></div>
          <div><p className="text-gray-400 text-xs mb-1">UoM Type</p><p className="font-medium uppercase">{goal.uom_type}</p></div>
          <div><p className="text-gray-400 text-xs mb-1">Employee ID</p><p className="font-medium">#{goal.employee_id}</p></div>
        </div>

        {goal.description && (
          <div><p className="text-gray-400 text-xs mb-1">Description</p><p className="text-sm">{goal.description}</p></div>
        )}

        {/* Inline editable fields */}
        <div className="grid grid-cols-2 gap-4 pt-3 border-t border-gray-100">
          {goal.uom_type !== 'timeline' && goal.uom_type !== 'zero' && (
            <div>
              <label className="label">Target (editable)</label>
              <input type="number" className="input" value={editTarget} onChange={e => setEditTarget(e.target.value)} />
            </div>
          )}
          <div>
            <label className="label">Weightage % (editable)</label>
            <input type="number" className="input" min={10} max={100} value={editWeightage} onChange={e => setEditWeightage(e.target.value)} />
            {editWeightage !== '' && parseFloat(editWeightage) < 10 && (
              <p className="text-red-500 text-xs mt-1">Minimum 10% weightage required per goal</p>
            )}
          </div>
        </div>

        <div className="flex gap-3 pt-2">
          <button onClick={handleApprove} disabled={saving || parseFloat(editWeightage) < 10} className="btn-primary">
            <CheckCircle size={16} /> Approve & Lock
          </button>
          <button onClick={() => setReturnModal(true)} disabled={saving} className="btn-secondary">
            <RotateCcw size={16} /> Return for Rework
          </button>
        </div>
      </div>

      <Modal open={returnModal} onClose={() => setReturnModal(false)} title="Return Goal for Rework">
        <div className="space-y-4">
          <p className="text-sm text-gray-600">Provide a comment explaining what needs to be revised. The employee will be notified.</p>
          <div>
            <label className="label">Comment *</label>
            <textarea className="input" rows={4} value={returnComment}
              onChange={e => setReturnComment(e.target.value)}
              placeholder="e.g. Please increase the target value and clarify the description…" />
          </div>
          <div className="flex gap-3">
            <button onClick={handleReturn} disabled={saving || !returnComment.trim()} className="btn-danger">
              <XCircle size={16} /> Return Goal
            </button>
            <button onClick={() => setReturnModal(false)} className="btn-secondary">Cancel</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
