import { useEffect, useState } from 'react'
import { Lock } from 'lucide-react'
import api from '../../api/client'
import toast from 'react-hot-toast'
import type { Goal, Achievement, GoalCycle, WindowStatus } from '../../types'
import { ScoreBadge, ProgressBadge } from '../../components/StatusBadge'
import { PageSpinner } from '../../components/Spinner'

export default function Achievements() {
  const [goals, setGoals] = useState<Goal[]>([])
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [cycles, setCycles] = useState<GoalCycle[]>([])
  const [window, setWindow] = useState<WindowStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState<number | null>(null)
  const [form, setForm] = useState<Record<number, { actual_value: string; actual_date: string; goal_status: string }>>({})

  useEffect(() => {
    Promise.all([
      api.get('/goals'),
      api.get('/achievements'),
      api.get('/admin/cycles'),
      api.get('/checkins/window-status'),
    ]).then(([g, a, c, w]) => {
      const locked = g.data.items.filter((x: Goal) => x.status === 'locked')
      setGoals(locked)
      setAchievements(a.data.items)
      setCycles(c.data)
      setWindow(w.data)
      // Pre-fill form from existing achievements
      const init: typeof form = {}
      a.data.items.forEach((ach: Achievement) => {
        init[ach.goal_id] = {
          actual_value: ach.actual_value != null ? String(ach.actual_value) : '',
          actual_date: ach.actual_date || '',
          goal_status: ach.goal_status,
        }
      })
      setForm(init)
    }).finally(() => setLoading(false))
  }, [])

  const activeCycle = cycles.find(c => c.is_active)
  const windowOpen = window?.open_cycle_id != null

  const getAch = (goalId: number) => achievements.find(a => a.goal_id === goalId && a.cycle_id === activeCycle?.id)

  const handleSave = async (goal: Goal) => {
    if (!activeCycle) return
    const f = form[goal.id]
    if (!f) return
    setSaving(goal.id)
    try {
      const payload: any = {
        goal_id: goal.id,
        cycle_id: activeCycle.id,
        goal_status: f.goal_status || 'not_started',
      }
      if (goal.uom_type === 'timeline') payload.actual_date = f.actual_date || null
      else payload.actual_value = f.actual_value ? parseFloat(f.actual_value) : null

      const existing = getAch(goal.id)
      if (existing) {
        await api.put(`/achievements/${existing.id}`, payload)
      } else {
        await api.post('/achievements', payload)
      }
      const updated = await api.get('/achievements')
      setAchievements(updated.data.items)
      toast.success('Achievement saved')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(null)
    }
  }

  if (loading) return <PageSpinner />

  return (
    <div className="p-6 space-y-5">
      <h1 className="text-2xl font-bold text-gray-900">Quarterly Achievements</h1>

      {/* Window status */}
      {window && (
        <div className={`rounded-xl p-4 border ${windowOpen ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'}`}>
          {windowOpen
            ? <p className="text-sm text-green-700 font-medium">✓ {window.open_quarter?.toUpperCase()} window is open — you can log achievements</p>
            : <p className="text-sm text-gray-600">No check-in window is currently open.{window.next_window_opens ? ` Next: ${window.next_phase} opens ${window.next_window_opens}` : ''}</p>
          }
        </div>
      )}

      {goals.length === 0
        ? <div className="card p-10 text-center text-gray-400">No locked goals to track achievements for.</div>
        : <div className="space-y-4">
            {goals.map(goal => {
              const ach = getAch(goal.id)
              const f = form[goal.id] || { actual_value: '', actual_date: '', goal_status: 'not_started' }
              const setF = (k: string, v: string) => setForm(prev => ({ ...prev, [goal.id]: { ...f, [k]: v } }))
              const isDisabled = !windowOpen

              return (
                <div key={goal.id} className="card p-5">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-gray-900">{goal.title}</h3>
                      <p className="text-xs text-gray-400 mt-0.5">{goal.thrust_area?.name} · {goal.uom_type.toUpperCase()} · Target: {goal.target ?? goal.target_date}</p>
                    </div>
                    {ach && <ScoreBadge score={ach.tracking_score} />}
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    {goal.uom_type === 'timeline'
                      ? <div>
                          <label className="label">Completion Date</label>
                          <input type="date" className="input" disabled={isDisabled}
                            value={f.actual_date} onChange={e => setF('actual_date', e.target.value)} />
                        </div>
                      : <div>
                          <label className="label">Actual Value</label>
                          <input type="number" className="input" disabled={isDisabled}
                            value={f.actual_value} onChange={e => setF('actual_value', e.target.value)}
                            placeholder={`Target: ${goal.target}`} />
                        </div>
                    }
                    <div>
                      <label className="label">Status</label>
                      <select className="input" disabled={isDisabled} value={f.goal_status} onChange={e => setF('goal_status', e.target.value)}>
                        <option value="not_started">Not Started</option>
                        <option value="on_track">On Track</option>
                        <option value="completed">Completed</option>
                      </select>
                    </div>
                    <div className="flex items-end">
                      {isDisabled
                        ? <div className="flex items-center gap-2 text-sm text-gray-400"><Lock size={14} /> Window closed</div>
                        : <button onClick={() => handleSave(goal)} disabled={saving === goal.id} className="btn-primary w-full justify-center">
                            {saving === goal.id ? 'Saving…' : ach ? 'Update' : 'Save'}
                          </button>
                      }
                    </div>
                  </div>

                  {ach && (
                    <div className="mt-3 pt-3 border-t border-gray-100 flex items-center gap-3">
                      <ProgressBadge status={ach.goal_status} />
                      <span className="text-xs text-gray-400">Last updated {new Date(ach.updated_at).toLocaleDateString()}</span>
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
