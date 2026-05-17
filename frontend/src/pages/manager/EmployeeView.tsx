import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import api from '../../api/client'
import type { Goal, Achievement } from '../../types'
import { GoalStatusBadge, ScoreBadge, ProgressBadge } from '../../components/StatusBadge'
import { PageSpinner } from '../../components/Spinner'

export default function ManagerEmployeeView() {
  const { employeeId } = useParams()
  const navigate = useNavigate()
  const [goals, setGoals] = useState<Goal[]>([])
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [empName, setEmpName] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get(`/goals?employee_id=${employeeId}&page_size=50`),
      api.get(`/achievements?employee_id=${employeeId}&page_size=50`),
    ]).then(([g, a]) => {
      setGoals(g.data.items)
      setAchievements(a.data.items)
      if (g.data.items.length > 0) setEmpName(`Employee #${employeeId}`)
    }).finally(() => setLoading(false))
  }, [employeeId])

  if (loading) return <PageSpinner />

  const getAch = (goalId: number) => achievements.find(a => a.goal_id === goalId)

  return (
    <div className="p-6 space-y-5">
      <button onClick={() => navigate(-1)} className="text-gray-400 hover:text-gray-600 text-sm">← Back to Team</button>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">{empName || `Employee #${employeeId}`}</h1>
        <Link to={`/manager/checkin/${employeeId}`} className="btn-primary">Add Check-in</Link>
      </div>

      {goals.length === 0
        ? <div className="card p-10 text-center text-gray-400">No goals found for this employee.</div>
        : <div className="space-y-3">
            {goals.map(g => {
              const ach = getAch(g.id)
              return (
                <div key={g.id} className="card p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="font-semibold text-gray-900">{g.title}</p>
                      <p className="text-xs text-gray-400 mt-0.5">{g.thrust_area?.name} · {g.uom_type.toUpperCase()} · {g.weightage}%</p>
                    </div>
                    <GoalStatusBadge status={g.status} />
                  </div>
                  {ach && (
                    <div className="flex items-center gap-4 text-sm pt-3 border-t border-gray-100">
                      <div><span className="text-gray-400 text-xs">Target: </span><span className="font-medium">{g.target ?? g.target_date}</span></div>
                      <div><span className="text-gray-400 text-xs">Actual: </span><span className="font-medium">{ach.actual_value ?? ach.actual_date ?? '—'}</span></div>
                      <div><span className="text-gray-400 text-xs">Score: </span><ScoreBadge score={ach.tracking_score} /></div>
                      <ProgressBadge status={ach.goal_status} />
                    </div>
                  )}
                </div>
              )
            })}
          </div>
      }
    </div>
  )
}
