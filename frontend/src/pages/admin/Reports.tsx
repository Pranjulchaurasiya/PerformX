import { useState, useEffect } from 'react'
import { Download } from 'lucide-react'
import type { GoalCycle } from '../../types'
import api from '../../api/client'
import { PageSpinner } from '../../components/Spinner'

export default function AdminReports() {
  const [cycles, setCycles] = useState<GoalCycle[]>([])
  const [cycleId, setCycleId] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/admin/cycles').then(r => {
      setCycles(r.data)
      const active = r.data.find((c: GoalCycle) => c.is_active)
      if (active) setCycleId(String(active.id))
    }).finally(() => setLoading(false))
  }, [])

  const download = (format: 'csv' | 'excel') => {
    const token = localStorage.getItem('token')
    const params = cycleId ? `?cycle_id=${cycleId}` : ''
    const ext = format === 'csv' ? 'csv' : 'xlsx'
    const url = `/api/reports/achievement/${format}${params}`
    const a = document.createElement('a')
    a.href = url
    a.download = `achievement_report.${ext}`
    // Add auth header via fetch
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.blob())
      .then(blob => {
        const burl = URL.createObjectURL(blob)
        a.href = burl
        a.click()
        URL.revokeObjectURL(burl)
      })
  }

  if (loading) return <PageSpinner />

  return (
    <div className="p-6 space-y-5">
      <h1 className="text-2xl font-bold text-gray-900">Achievement Reports</h1>

      <div className="card p-6 space-y-5 max-w-lg">
        <div>
          <label className="label">Filter by Cycle</label>
          <select className="input" value={cycleId} onChange={e => setCycleId(e.target.value)}>
            <option value="">All Cycles</option>
            {cycles.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>

        <div className="flex gap-3">
          <button onClick={() => download('csv')} className="btn-secondary flex-1 justify-center">
            <Download size={16} /> Export CSV
          </button>
          <button onClick={() => download('excel')} className="btn-primary flex-1 justify-center">
            <Download size={16} /> Export Excel
          </button>
        </div>

        <p className="text-xs text-gray-400">
          Report includes: Employee Name, Goal Title, Thrust Area, UoM Type, Target, Actual Achievement, Tracking Score, Status, Cycle.
        </p>
      </div>
    </div>
  )
}
