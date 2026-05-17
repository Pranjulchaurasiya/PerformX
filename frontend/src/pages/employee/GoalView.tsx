import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { Lock, Share2, AlertTriangle, Users, Edit2 } from 'lucide-react'
import api from '../../api/client'
import toast from 'react-hot-toast'
import type { Goal } from '../../types'
import { GoalStatusBadge } from '../../components/StatusBadge'
import { PageSpinner } from '../../components/Spinner'
import { useAuth } from '../../context/AuthContext'

export default function GoalView() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [goal, setGoal] = useState<Goal | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    api.get(`/goals/${id}`).then(r => setGoal(r.data)).catch(() => navigate('/employee/goals')).finally(() => setLoading(false))
  }, [id])

  const handleSubmit = async () => {
    if (!goal) return
    // Validate total weightage via API
    setSubmitting(true)
    try {
      const { data } = await api.post(`/goals/${goal.id}/submit`)
      setGoal(data)
      toast.success(data.status === 'resubmitted' ? 'Goal resubmitted for approval!' : 'Goal submitted for approval!')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Submission failed')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <PageSpinner />
  if (!goal) return null

  const isShared = goal.is_shared
  const isPrimaryOwner = isShared && goal.primary_owner_id === user?.id
  const isReadOnlyShared = isShared && !isPrimaryOwner
  const canEdit = ['draft', 'returned'].includes(goal.status) && !isReadOnlyShared
  const canSubmit = ['draft', 'returned'].includes(goal.status)

  return (
    <div className="p-6 max-w-2xl space-y-5">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="text-gray-400 hover:text-gray-600 text-sm">← Back</button>
      </div>

      {/* Returned banner */}
      {goal.status === 'returned' && goal.rework_comment && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex gap-3">
          <AlertTriangle size={18} className="text-amber-600 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-amber-800">Returned for rework</p>
            <p className="text-sm text-amber-700 mt-1">{goal.rework_comment}</p>
            <Link to={`/employee/goals/${goal.id}/edit`} className="text-xs text-amber-600 underline mt-2 inline-block">
              Click here to revise →
            </Link>
          </div>
        </div>
      )}

      <div className="card p-6 space-y-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-xl font-bold text-gray-900">{goal.title}</h1>
            {isShared && (
              <span className="badge bg-purple-100 text-purple-700 flex items-center gap-1">
                <Share2 size={10} /> Shared Goal
              </span>
            )}
            {goal.status === 'locked' && <Lock size={16} className="text-gray-400" />}
          </div>
          <GoalStatusBadge status={goal.status} />
        </div>

        {/* Shared goal info banners */}
        {isPrimaryOwner && goal.linked_employee_count && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center gap-2 text-sm text-blue-700">
            <Users size={15} />
            You are the primary owner — your updates sync to {goal.linked_employee_count} team member{goal.linked_employee_count > 1 ? 's' : ''}.
          </div>
        )}
        {isReadOnlyShared && goal.primary_owner_name && (
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 text-sm text-purple-700">
            Synced from <strong>{goal.primary_owner_name}</strong>. Title and target are read-only.
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-400 text-xs mb-1">Thrust Area</p>
            <p className="font-medium">{goal.thrust_area?.name || '—'}</p>
          </div>
          <div>
            <p className="text-gray-400 text-xs mb-1">UoM Type</p>
            <p className="font-medium uppercase">{goal.uom_type}</p>
          </div>
          <div>
            <p className="text-gray-400 text-xs mb-1">Target</p>
            <p className="font-medium">{goal.target ?? goal.target_date ?? '—'}</p>
          </div>
          <div>
            <p className="text-gray-400 text-xs mb-1">Weightage</p>
            <p className="font-medium">{goal.weightage}%</p>
          </div>
        </div>

        {goal.description && (
          <div>
            <p className="text-gray-400 text-xs mb-1">Description</p>
            <p className="text-sm text-gray-700">{goal.description}</p>
          </div>
        )}

        <div className="flex gap-3 pt-2 border-t border-gray-100">
          {canEdit && (
            <Link to={`/employee/goals/${goal.id}/edit`} className="btn-secondary">
              <Edit2 size={15} /> Edit
            </Link>
          )}
          {canSubmit && (
            <button onClick={handleSubmit} disabled={submitting} className="btn-primary">
              {submitting ? 'Submitting…' : goal.status === 'returned' ? 'Resubmit for Approval' : 'Submit for Approval'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
