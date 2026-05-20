interface ProgressTrackerProps {
  total: number
  current: number
  answers: Record<number, 'correct' | 'wrong' | 'pending'>
}

export function ProgressTracker({ total, current, answers }: ProgressTrackerProps) {
  return (
    <div className="flex flex-wrap justify-center gap-2">
      {Array.from({ length: total }, (_, i) => {
        const status = answers[i] ?? 'pending'
        let bg = 'bg-gray-600'
        if (status === 'correct') bg = 'bg-green-500'
        else if (status === 'wrong') bg = 'bg-red-500'

        const isCurrent = i === current
        return (
          <div
            key={i}
            className={`h-2 rounded-full transition-all duration-300 ${bg} ${
              isCurrent ? 'w-6 bg-blue-500' : 'w-2'
            }`}
          />
        )
      })}
    </div>
  )
}
