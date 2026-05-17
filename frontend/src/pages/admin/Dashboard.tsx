import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Users, Target, RefreshCw, TrendingUp, Unlock } from 'lucide-react'
import api from '../../api/client'
import toast from 'react-hot-toast'
import StatCard from '../../components/StatCard'
import { PageSpinner } from '../../components/Spinner'
import Modal from '../../components/Modal'
import type { Goal } from '../../types'

export default function AdminDashboard() {
  const [overview, setOverview] = useState<any>(null)
  const [lockedGoals, setLockedGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(true)

  // Unlock modal state
  const [unlockModal, setUnlockModal] = useState(false)
  const [unlockGoalId, setUnlockGoalId] = useState<number | null>(null)
  const [unlockReason, setUnlockReason] = useState('')
  const [reasonError, setReasonError] = useState('')
  const [unlocking, setUnlocking] = useState(false)

  const loadData = () => {
    Promise.all([
      api.get('/analytics/overview'),
      api.get('/goals?status=locked&page_size=50'),
    ]).then(([o, g]) => {
      setOverview(o.data)
      setLockedGoals(g.data.items)
    }).finally(() => setLoading(false))
  }

  useEffect(loadData, [])

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
      loadData() // refresh stats + goal list
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Unlock failed')
    } finally {
      setUnlocking(false)
    }
  }

  if (loading) return <PageSpinner />

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Employees" value={overview?.team_size ?? 0} icon={Users} />
        <StatCard label="Total Goals" value={overview?.total_goals ?? 0} icon={Target} />
        <StatCard label="Locked Goals" value={overview?.locked_goals ?? 0} icon={Target} color="text-green-600" />
        <StatCard label="Avg Tracking Score" value={`${overview?.avg_tracking_score ?? 0}%`} icon={TrendingUp} color="text-primary-600" />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {[
          { to: '/admin/users',        label: 'Manage Users',   icon: Users,      desc: 'Add, edit, assign roles' },
          { to: '/admin/cycles',       label: 'Goal Cycles',    icon: RefreshCw,  desc: 'Configure windows & penalties' },
          { to: '/admin/reports',      label: 'Export Reports', icon: Target,     desc: 'CSV / Excel achievement data' },
          { to: '/admin/audit',        label: 'Audit Logs',     icon: Target,     desc: 'Track all changes' },
          { to: '/admin/analytics',    label: 'Analytics',      icon: TrendingUp, desc: 'Org-wide insights' },
          { to: '/admin/shared-goals', label: 'Shared Goals',   icon: Target,     desc: 'Push departmental KPIs' },
        ].map(item => (
          <Link key={item.to} to={item.to} className="card p-5 hover:shadow-md transition-shadow">
            <item.icon size={22} className="text-primary-600 mb-3" />
            <p className="font-semibold text-gray-900">{item.label}</p>
            <p className="text-xs text-gray-400 mt-1">{item.desc}</p>
          </Link>
        ))}
      </div>

      {/* Locked Goals — with Unlock button per goal */}
      {lockedGoals.length > 0 && (
        <div className="card">
          <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">Locked Goals</h2>
            <span className="text-xs text-gray-400">{lockedGoals.length} goals</span>
          </div>
          <div className="divide-y divide-gray-100">
            {lockedGoals.map(g => (
              <div key={g.id} className="flex items-center justify-between px-5 py-3.5 hover:bg-gray-50">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{g.title}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {g.thrust_area?.name} · Employee #{g.employee_id} · {g.weightage}%
                  </p>
                </div>
                <button
                  onClick={() => openUnlock(g.id)}
                  className="ml-4 shrink-0 flex items-center gap-1.5 text-xs text-amber-600 hover:text-amber-800 font-medium border border-amber-200 hover:border-amber-400 px-2.5 py-1.5 rounded-lg transition-colors"
                >
                  <Unlock size={13} /> Unlock
                </button>
              </div>
            ))}
          </div>
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
