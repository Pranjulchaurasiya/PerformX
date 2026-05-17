import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Target, CheckCircle, Clock, AlertCircle, Plus } from 'lucide-react'
import api from '../../api/client'
import { useAuth } from '../../context/AuthContext'
import type { Goal, WindowStatus } from '../../types'
import { GoalStatusBadge, ScoreBadge } from '../../components/StatusBadge'
import StatCard from '../../components/StatCard'
import { PageSpinner } from '../../components/Spinner'
import WeightageBar from '../../components/WeightageBar'

export default function EmployeeDashboard() {
  const { user } = useAuth()
  const [goals, setGoals] = useState<Goal[]>([])
  const [window, setWindow] = useState<WindowStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/goals'),
      api.get('/checkins/window-status'),
    ]).then(([g, w]) => {
      setGoals(g.data.items)
      setWindow(w.data)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <PageSpinner />

  const locked = goals.filter(g => g.status === 'locked').length
  const pending = goals.filter(g => ['submitted','resubmitted'].includes(g.status)).length
  const returned = goals.filter(g => g.status === 'returned').length
  const totalW = goals.reduce((s, g) => s + g.weightage, 0)

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Welcome back, {user?.name?.split(' ')[0]} 👋</h1>
          <p className="text-gray-500 text-sm mt-1">Here's your goal progress overview</p>
        </div>
        <Link to="/employee/goals/new" className="btn-primary">
          <Plus size={16} /> New Goal
        </Link>
      </div>

      {/* Window alert */}
      {window && (
        <div className={`rounded-xl p-4 flex items-start gap-3 ${window.open_quarter ? 'bg-green-50 border border-green-200' : 'bg-amber-50 border border-amber-200'}`}>
          <Clock size={18} className={window.open_quarter ? 'text-green-600 mt-0.5' : 'text-amber-600 mt-0.5'} />
          <div>
            {window.open_quarter
              ? <p className="text-sm font-medium text-green-800">{window.open_quarter.toUpperCase()} check-in window is open until {window.window_close}</p>
              : <p className="text-sm font-medium text-amber-800">No check-in window is currently open.{window.next_window_opens ? ` Next: ${window.next_phase} opens ${window.next_window_opens}` : ''}</p>
            }
          </div>
        </div>
      )}

      {/* Returned goals alert */}
      {returned > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle size={18} className="text-orange-600 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-orange-800">{returned} goal{returned > 1 ? 's' : ''} returned for rework</p>
            <Link to="/employee/goals" className="text-xs text-orange-600 underline mt-0.5 inline-block">View and revise →</Link>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Goals" value={goals.length} icon={Target} />
        <StatCard label="Approved & Locked" value={locked} icon={CheckCircle} color="text-green-600" />
        <StatCard label="Pending Approval" value={pending} icon={Clock} color="text-blue-600" />
        <StatCard label="Needs Rework" value={returned} icon={AlertCircle} color="text-orange-600" />
      </div>

      {/* Weightage bar */}
      <div className="card p-5">
        <WeightageBar used={totalW} />
      </div>

      {/* Goals list */}
      <div className="card">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="font-semibold text-gray-900">My Goals</h2>
          <Link to="/employee/goals" className="text-sm text-primary-600 hover:underline">View all</Link>
        </div>
        {goals.length === 0
          ? <div className="p-8 text-center text-gray-400">No goals yet. <Link to="/employee/goals/new" className="text-primary-600 underline">Create your first goal</Link></div>
          : <div className="divide-y divide-gray-100">
              {goals.slice(0, 5).map(g => (
                <Link key={g.id} to={`/employee/goals/${g.id}`}
                  className="flex items-center justify-between px-5 py-3.5 hover:bg-gray-50 transition-colors">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{g.title}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{g.thrust_area?.name} · {g.weightage}%</p>
                  </div>
                  <div className="flex items-center gap-3 ml-4 shrink-0">
                    {g.is_shared && <span className="badge bg-purple-100 text-purple-700">Shared</span>}
                    <GoalStatusBadge status={g.status} />
                  </div>
                </Link>
              ))}
            </div>
        }
      </div>
    </div>
  )
}
