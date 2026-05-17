import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { User, TrendingUp } from 'lucide-react'
import api from '../../api/client'
import { PageSpinner } from '../../components/Spinner'

interface EmpProgress { employee_id: number; employee_name: string; total_goals: number; current_quarter: string | null; avg_tracking_score: number }

export default function ManagerTeam() {
  const [team, setTeam] = useState<EmpProgress[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/analytics/manager/employee-progress').then(r => setTeam(r.data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <PageSpinner />

  return (
    <div className="p-6 space-y-5">
      <h1 className="text-2xl font-bold text-gray-900">My Team</h1>
      {team.length === 0
        ? <div className="card p-10 text-center text-gray-400">No team members found.</div>
        : <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {team.map(emp => (
              <div key={emp.employee_id} className="card p-5 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                      <User size={18} className="text-primary-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{emp.employee_name}</p>
                      <p className="text-xs text-gray-400">{emp.total_goals} goals</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-1 text-primary-600">
                      <TrendingUp size={14} />
                      <span className="font-bold text-lg">{emp.avg_tracking_score}%</span>
                    </div>
                    {emp.current_quarter && <p className="text-xs text-gray-400">{emp.current_quarter}</p>}
                  </div>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden mb-4">
                  <div className="h-full bg-primary-500 rounded-full transition-all"
                    style={{ width: `${Math.min(100, emp.avg_tracking_score)}%` }} />
                </div>
                <div className="flex gap-2">
                  <Link to={`/manager/team/${emp.employee_id}`} className="btn-secondary text-xs py-1.5 flex-1 justify-center">
                    View Goals
                  </Link>
                  <Link to={`/manager/checkin/${emp.employee_id}`} className="btn-primary text-xs py-1.5 flex-1 justify-center">
                    Check-in
                  </Link>
                </div>
              </div>
            ))}
          </div>
      }
    </div>
  )
}
