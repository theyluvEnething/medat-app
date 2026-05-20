interface ProgressTrackerProps {
  total: number
  current: number
  answers: Record<number, 'correct' | 'wrong' | 'pending'>
}

export function ProgressTracker({ total, current, answers }: ProgressTrackerProps) {
  return (
    <div className="flex flex-wrap justify-center gap-1.5">
      {Array.from({ length: total }, (_, i) => {
        const status = answers[i] ?? 'pending'
        let bg = 'bg-zinc-600/50'
        if (status === 'correct') bg = 'bg-green-500'
        else if (status === 'wrong') bg = 'bg-red-500'

        const isCurrent = i === current
        return (
          <div
            key={i}
            className={`h-3 w-3 rounded-sm transition-all duration-300 ${bg} ${
              isCurrent ? 'ring-2 ring-white/60 scale-110' : ''
            }`}
          />
        )
      })}
    </div>
  )
}
