interface Props { used: number; max?: number }

export default function WeightageBar({ used, max = 100 }: Props) {
  const pct = Math.min(100, (used / max) * 100)
  const color = used === 100 ? 'bg-green-500' : used > 100 ? 'bg-red-500' : 'bg-primary-500'
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-500">
        <span>Weightage used</span>
        <span className={used === 100 ? 'text-green-600 font-semibold' : used > 100 ? 'text-red-600 font-semibold' : ''}>
          {used}% / {max}%
        </span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
