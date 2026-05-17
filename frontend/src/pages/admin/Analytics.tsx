import { useEffect, useState } from 'react'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import api from '../../api/client'
import { PageSpinner } from '../../components/Spinner'

const COLORS = ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export default function AdminAnalytics() {
  const [orgQoq, setOrgQoq] = useState<any[]>([])
  const [heatmap, setHeatmap] = useState<any[]>([])
  const [dist, setDist] = useState<any>(null)
  const [mgrEff, setMgrEff] = useState<any[]>([])
  const [sortKey, setSortKey] = useState('manager_name')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/analytics/admin/org-qoq-trends'),
      api.get('/analytics/admin/department-completion-heatmap'),
      api.get('/analytics/admin/goal-distribution'),
      api.get('/analytics/admin/manager-effectiveness'),
    ]).then(([q, h, d, m]) => {
      // Flatten QoQ for recharts: [{quarter, Dept1, Dept2, ...}]
      const quarters = q.data[0]?.series?.map((s: any) => s.quarter) || []
      const flat = quarters.map((qtr: string) => {
        const row: any = { quarter: qtr }
        q.data.forEach((dept: any) => {
          const s = dept.series.find((x: any) => x.quarter === qtr)
          row[dept.department] = s?.avg_tracking_score || 0
        })
        return row
      })
      setOrgQoq(flat)
      setHeatmap(h.data)
      setDist(d.data)
      setMgrEff(m.data)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <PageSpinner />

  const deptNames = heatmap.map(d => d.department)
  const quarters = heatmap[0]?.cells?.map((c: any) => c.quarter) || []

  const cellColor = (pct: number) => pct >= 80 ? 'bg-green-100 text-green-800' : pct >= 50 ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'

  const sorted = [...mgrEff].sort((a, b) => {
    const av = a[sortKey], bv = b[sortKey]
    return typeof av === 'string' ? av.localeCompare(bv) : bv - av
  })

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Org-Wide Analytics</h1>

      {/* QoQ by Department */}
      <div className="card p-5">
        <h2 className="font-semibold text-gray-900 mb-4">Quarter-on-Quarter Achievement by Department</h2>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={orgQoq}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="quarter" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} unit="%" />
            <Tooltip formatter={(v: any) => `${v}%`} />
            <Legend />
            {deptNames.map((dept, i) => (
              <Line key={dept} type="monotone" dataKey={dept} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={{ r: 3 }} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Department Completion Heatmap */}
      <div className="card p-5">
        <h2 className="font-semibold text-gray-900 mb-4">Department Check-in Completion Heatmap</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className="text-left px-3 py-2 text-gray-500 font-medium">Department</th>
                {quarters.map((q: string) => <th key={q} className="px-3 py-2 text-gray-500 font-medium">{q}</th>)}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {heatmap.map(dept => (
                <tr key={dept.department}>
                  <td className="px-3 py-2 font-medium text-gray-900">{dept.department}</td>
                  {dept.cells.map((cell: any) => (
                    <td key={cell.quarter} className="px-3 py-2 text-center">
                      <span className={`badge ${cellColor(cell.completion_pct)}`}>{cell.completion_pct}%</span>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-green-200 inline-block" /> ≥80%</span>
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-amber-200 inline-block" /> 50–79%</span>
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-red-200 inline-block" /> &lt;50%</span>
        </div>
      </div>

      {/* Goal Distribution */}
      {dist && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="card p-5">
            <h3 className="font-semibold text-gray-900 mb-3 text-sm">By Thrust Area</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={dist.by_thrust_area} dataKey="count" nameKey="thrust_area" cx="50%" cy="50%" outerRadius={70} label={({ thrust_area, percent }) => `${thrust_area} ${(percent * 100).toFixed(0)}%`} labelLine={false}>
                  {dist.by_thrust_area.map((_: any, i: number) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="card p-5">
            <h3 className="font-semibold text-gray-900 mb-3 text-sm">By UoM Type</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={dist.by_uom_type} layout="vertical">
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="uom_type" tick={{ fontSize: 11 }} width={60} />
                <Tooltip />
                <Bar dataKey="count" fill="#4f46e5" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="card p-5">
            <h3 className="font-semibold text-gray-900 mb-3 text-sm">By Status</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={dist.by_status} layout="vertical">
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="status" tick={{ fontSize: 11 }} width={70} />
                <Tooltip />
                <Bar dataKey="count" fill="#06b6d4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Manager Effectiveness Table */}
      <div className="card p-5">
        <h2 className="font-semibold text-gray-900 mb-4">Manager Effectiveness</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
              <tr>
                {[
                  { key: 'manager_name', label: 'Manager' },
                  { key: 'team_size', label: 'Team Size' },
                  { key: 'checkin_completion_pct', label: 'Check-in %' },
                  { key: 'avg_team_tracking_score', label: 'Avg Score' },
                  { key: 'escalations_triggered', label: 'Escalations' },
                ].map(col => (
                  <th key={col.key} className="px-5 py-3 text-left cursor-pointer hover:text-gray-800"
                    onClick={() => setSortKey(col.key)}>
                    {col.label} {sortKey === col.key ? '↓' : ''}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {sorted.map(m => (
                <tr key={m.manager_id} className="hover:bg-gray-50">
                  <td className="px-5 py-3 font-medium">{m.manager_name}</td>
                  <td className="px-5 py-3">{m.team_size}</td>
                  <td className="px-5 py-3">
                    <span className={m.checkin_completion_pct >= 80 ? 'text-green-600 font-semibold' : m.checkin_completion_pct >= 50 ? 'text-amber-600' : 'text-red-600'}>
                      {m.checkin_completion_pct}%
                    </span>
                  </td>
                  <td className="px-5 py-3 font-semibold text-primary-600">{m.avg_team_tracking_score}%</td>
                  <td className="px-5 py-3">
                    <span className={m.escalations_triggered > 0 ? 'text-red-600 font-medium' : 'text-gray-400'}>{m.escalations_triggered}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
