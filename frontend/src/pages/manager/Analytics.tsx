import { useEffect, useState } from 'react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import api from '../../api/client'
import { PageSpinner } from '../../components/Spinner'

export default function ManagerAnalytics() {
  const [qoq, setQoq] = useState<any[]>([])
  const [statusBreakdown, setStatusBreakdown] = useState<any[]>([])
  const [checkinRate, setCheckinRate] = useState<any>(null)
  const [empProgress, setEmpProgress] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/analytics/manager/qoq-team'),
      api.get('/analytics/manager/goal-status-breakdown'),
      api.get('/analytics/manager/checkin-completion'),
      api.get('/analytics/manager/employee-progress'),
    ]).then(([q, s, c, e]) => {
      setQoq(q.data)
      setStatusBreakdown(s.data.map((emp: any) => ({
        name: emp.employee_name.split(' ')[0],
        ...emp.status_breakdown,
      })))
      setCheckinRate(c.data)
      setEmpProgress(e.data)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <PageSpinner />

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Team Analytics</h1>

      {/* QoQ Line Chart */}
      <div className="card p-5">
        <h2 className="font-semibold text-gray-900 mb-4">Quarter-on-Quarter Tracking Score</h2>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={qoq}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="quarter" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} unit="%" />
            <Tooltip formatter={(v: any) => `${v}%`} />
            <Line type="monotone" dataKey="avg_tracking_score" stroke="#4f46e5" strokeWidth={2}
              dot={{ fill: '#4f46e5', r: 4 }} name="Avg Score" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Goal Status Breakdown */}
      <div className="card p-5">
        <h2 className="font-semibold text-gray-900 mb-4">Goal Status by Team Member</h2>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={statusBreakdown}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="locked" fill="#4f46e5" name="Locked" stackId="a" />
            <Bar dataKey="submitted" fill="#3b82f6" name="Submitted" stackId="a" />
            <Bar dataKey="draft" fill="#9ca3af" name="Draft" stackId="a" />
            <Bar dataKey="returned" fill="#f97316" name="Returned" stackId="a" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Check-in Completion */}
      {checkinRate && (
        <div className="card p-5">
          <h2 className="font-semibold text-gray-900 mb-4">Check-in Completion Rate</h2>
          <div className="flex items-center gap-6 mb-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">{checkinRate.completion_rate}%</p>
              <p className="text-xs text-gray-400">Overall</p>
            </div>
            <div className="flex-1 grid grid-cols-4 gap-3">
              {checkinRate.by_quarter.map((q: any) => (
                <div key={q.quarter} className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm font-bold text-gray-900">{q.rate}%</p>
                  <p className="text-xs text-gray-400">{q.quarter}</p>
                  <p className="text-xs text-gray-300">{q.completed}/{q.total}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Employee Progress Cards */}
      <div className="card p-5">
        <h2 className="font-semibold text-gray-900 mb-4">Individual Progress</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {empProgress.map((emp: any) => (
            <div key={emp.employee_id} className="bg-gray-50 rounded-xl p-4">
              <p className="font-medium text-gray-900 text-sm">{emp.employee_name}</p>
              <p className="text-xs text-gray-400 mb-2">{emp.total_goals} goals · {emp.current_quarter || 'No active quarter'}</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-primary-500 rounded-full" style={{ width: `${Math.min(100, emp.avg_tracking_score)}%` }} />
                </div>
                <span className="text-xs font-semibold text-primary-600">{emp.avg_tracking_score}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
