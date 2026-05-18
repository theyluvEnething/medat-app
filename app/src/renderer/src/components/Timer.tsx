interface TimerProps {
  remaining: number
  total: number
}

function fmt(s: number): string {
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${m}:${sec.toString().padStart(2, '0')}`
}

export function Timer({ remaining, total }: TimerProps) {
  const pct = total > 0 ? (remaining / total) * 100 : 0
  const warn = remaining <= 60

  return (
    <div className="flex items-center gap-3">
      <div className="h-2 w-32 overflow-hidden rounded-full bg-zinc-800">
        <div
          className={`h-full rounded-full transition-all duration-700 ${
            warn ? 'bg-red-500 animate-pulse-warn' : 'bg-emerald-500'
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span
        className={`font-mono text-lg tabular-nums transition-colors duration-300 ${
          warn ? 'text-red-400 animate-pulse-warn' : 'text-zinc-300'
        }`}
      >
        {fmt(remaining)}
      </span>
    </div>
  )
}
