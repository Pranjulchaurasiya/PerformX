import clsx from 'clsx'
import type { GoalStatus, ProgressStatus } from '../types'

const goalColors: Record<GoalStatus, string> = {
  draft:       'bg-gray-100 text-gray-700',
  submitted:   'bg-blue-100 text-blue-700',
  resubmitted: 'bg-amber-100 text-amber-700',
  returned:    'bg-orange-100 text-orange-700',
  approved:    'bg-green-100 text-green-700',
  locked:      'bg-primary-100 text-primary-700',
  rejected:    'bg-red-100 text-red-700',
}

const progressColors: Record<ProgressStatus, string> = {
  not_started: 'bg-gray-100 text-gray-600',
  on_track:    'bg-green-100 text-green-700',
  completed:   'bg-primary-100 text-primary-700',
}

export function GoalStatusBadge({ status }: { status: GoalStatus }) {
  return (
    <span className={clsx('badge', goalColors[status])}>
      {status.replace('_', ' ')}
    </span>
  )
}

export function ProgressBadge({ status }: { status: ProgressStatus }) {
  return (
    <span className={clsx('badge', progressColors[status])}>
      {status.replace('_', ' ')}
    </span>
  )
}

export function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) return <span className="text-gray-400 text-sm">—</span>
  const color = score >= 80 ? 'text-green-600' : score >= 50 ? 'text-amber-600' : 'text-red-600'
  return <span className={clsx('font-semibold text-sm', color)}>{score.toFixed(1)}%</span>
}
