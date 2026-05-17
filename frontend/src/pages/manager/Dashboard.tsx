import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Users, CheckSquare, TrendingUp, AlertTriangle } from 'lucide-react'
import api from '../../api/client'
import type { EscalationItem } from '../../types'
import StatCard from '../../components/StatCard'
import { PageSpinner } from '../../components/Spinner'

interface Overview { total_goals: number; locked_goals: number; pending_approvals: number; avg_tracking_score: number; team_size: number }

export default function ManagerDashboard() {
  const navigate = useNavigate()
  const [overview, setOverview] = useState<Overview | null>(null)
  const [escalations, setEscalations] = useState<EscalationItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/analytics/overview'),
      api.get('/escalations/my-team'),
    ]).then(([o, e]) => {
      setOverview(o.data)
      setEscalations(e.data.items)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <PageSpinner />

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Manager Dashboard</h1>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Team Size" value={overview?.team_size ?? 0} icon={Users} />
        <StatCard label="Pending Approvals" value={overview?.pending_approvals ?? 0} icon={CheckSquare} color="text-amber-600" />
        <StatCard label="Locked Goals" value={overview?.locked_goals ?? 0} icon={CheckSquare} color="text-green-600" />
        <StatCard label="Avg Tracking Score" value={`${overview?.avg_tracking_score ?? 0}%`} icon={TrendingUp} color="text-primary-600" />
      </div>

      {/* Pending approvals quick link */}
      {(overview?.pending_approvals ?? 0) > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CheckSquare size={18} className="text-amber-600" />
            <p className="text-sm font-medium text-amber-800">
              {overview?.pending_approvals} goal{overview?.pending_approvals !== 1 ? 's' : ''} waiting for your approval
            </p>
          </div>
          <Link to="/manager/approvals" className="btn-primary text-xs py-1.5">Review Now</Link>
        </div>
      )}

      {/* Escalation Alerts Widget */}
      <div className="card">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle size={18} className="text-red-500" />
            <h2 className="font-semibold text-gray-900">Escalation Alerts</h2>
            {escalations.length > 0 && (
              <span className="bg-red-500 text-white text-xs rounded-full px-2 py-0.5">{escalations.length}</span>
            )}
          </div>
        </div>
        {escalations.length === 0
          ? <div className="p-6 text-center text-gray-400 text-sm">No open escalations for your team 🎉</div>
          : <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                  <tr>
                    <th className="px-5 py-3 text-left">Employee</th>
                    <th className="px-5 py-3 text-left">Rule</th>
                    <th className="px-5 py-3 text-left">Days Overdue</th>
                    <th className="px-5 py-3 text-left">Level</th>
                    <th className="px-5 py-3 text-left"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {escalations.map(e => (
                    <tr key={e.escalation_id} className="hover:bg-gray-50">
                      <td className="px-5 py-3 font-medium">{e.employee_name}</td>
                      <td className="px-5 py-3 text-gray-500">{e.rule_name}</td>
                      <td className="px-5 py-3">
                        <span className="text-red-600 font-medium">{e.days_overdue}d</span>
                      </td>
                      <td className="px-5 py-3">
                        <span className={`badge ${e.level_reached >= 3 ? 'bg-red-100 text-red-700' : e.level_reached === 2 ? 'bg-orange-100 text-orange-700' : 'bg-amber-100 text-amber-700'}`}>
                          L{e.level_reached}
                        </span>
                      </td>
                      <td className="px-5 py-3">
                        <button onClick={() => navigate(`/manager/team/${e.employee_id}`)}
                          className="text-primary-600 hover:underline text-xs">View →</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
        }
      </div>
    </div>
  )
}
