import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Lock, Share2 } from 'lucide-react'
import api from '../../api/client'
import type { Goal } from '../../types'
import { GoalStatusBadge } from '../../components/StatusBadge'
import { PageSpinner } from '../../components/Spinner'
import WeightageBar from '../../components/WeightageBar'

export default function GoalList() {
  const [goals, setGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/goals').then(r => setGoals(r.data.items)).finally(() => setLoading(false))
  }, [])

  if (loading) return <PageSpinner />

  const totalW = goals.reduce((s, g) => s + g.weightage, 0)
  const canAdd = goals.filter(g => g.status !== 'rejected').length < 8

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">My Goals</h1>
        {canAdd && (
          <Link to="/employee/goals/new" className="btn-primary">
            <Plus size={16} /> Add Goal
          </Link>
        )}
      </div>

      <div className="card p-4">
        <WeightageBar used={totalW} />
        {totalW === 100 && <p className="text-xs text-green-600 mt-2">✓ Weightage is balanced. You can submit your goals.</p>}
        {!canAdd && <p className="text-xs text-amber-600 mt-2">Maximum 8 goals reached.</p>}
      </div>

      {goals.length === 0
        ? <div className="card p-12 text-center text-gray-400">
            <p className="text-lg font-medium mb-2">No goals yet</p>
            <Link to="/employee/goals/new" className="btn-primary inline-flex">
              <Plus size={16} /> Create your first goal
            </Link>
          </div>
        : <div className="space-y-3">
            {goals.map(g => (
              <div key={g.id} className="card p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Link to={`/employee/goals/${g.id}`}
                        className="text-sm font-semibold text-gray-900 hover:text-primary-600 transition-colors">
                        {g.title}
                      </Link>
                      {g.is_shared && (
                        <span className="badge bg-purple-100 text-purple-700 flex items-center gap-1">
                          <Share2 size={10} /> Shared
                        </span>
                      )}
                      {g.status === 'locked' && <Lock size={13} className="text-gray-400" />}
                    </div>
                    <p className="text-xs text-gray-400 mt-1">{g.thrust_area?.name} · {g.uom_type.toUpperCase()} · {g.weightage}% weight</p>
                    {g.description && <p className="text-xs text-gray-500 mt-1 line-clamp-1">{g.description}</p>}
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <GoalStatusBadge status={g.status} />
                    {g.status === 'returned' && (
                      <Link to={`/employee/goals/${g.id}/edit`} className="btn-secondary text-xs py-1 px-2">
                        Revise
                      </Link>
                    )}
                    {['draft','returned'].includes(g.status) && (
                      <Link to={`/employee/goals/${g.id}/edit`} className="text-xs text-primary-600 hover:underline">
                        Edit
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
      }
    </div>
  )
}
