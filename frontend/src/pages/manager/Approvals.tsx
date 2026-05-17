import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { CheckSquare } from 'lucide-react'
import api from '../../api/client'
import type { Goal } from '../../types'
import { GoalStatusBadge } from '../../components/StatusBadge'
import { PageSpinner } from '../../components/Spinner'

export default function ManagerApprovals() {
  const [goals, setGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/goals?status=submitted&page_size=50').then(r => {
      const submitted = r.data.items
      api.get('/goals?status=resubmitted&page_size=50').then(r2 => {
        setGoals([...submitted, ...r2.data.items])
      })
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <PageSpinner />

  return (
    <div className="p-6 space-y-5">
      <h1 className="text-2xl font-bold text-gray-900">Pending Approvals</h1>

      {goals.length === 0
        ? <div className="card p-12 text-center text-gray-400">
            <CheckSquare size={40} className="mx-auto mb-3 text-green-400" />
            <p className="font-medium">All caught up! No pending approvals.</p>
          </div>
        : <div className="space-y-3">
            {goals.map(g => (
              <Link key={g.id} to={`/manager/approvals/${g.id}`}
                className="card p-4 flex items-center justify-between hover:shadow-md transition-shadow block">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-semibold text-gray-900">{g.title}</p>
                    {g.status === 'resubmitted' && (
                      <span className="badge bg-amber-100 text-amber-700">Resubmission</span>
                    )}
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{g.thrust_area?.name} · {g.weightage}% · Employee #{g.employee_id}</p>
                </div>
                <div className="flex items-center gap-3">
                  <GoalStatusBadge status={g.status} />
                  <span className="text-primary-600 text-sm">Review →</span>
                </div>
              </Link>
            ))}
          </div>
      }
    </div>
  )
}
