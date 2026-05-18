interface QuestionCardProps {
  number: number
  total: number
  content: string
  selectedAnswer: string | null
  onSelect: (choice: string) => void
}

const CHOICES = ['A', 'B', 'C', 'D', 'E'] as const

export function QuestionCard({ number, total, content, selectedAnswer, onSelect }: QuestionCardProps) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-2 text-sm text-zinc-500">
        <span>
          Frage {number} von {total}
        </span>
        <div className="flex gap-1">
          {Array.from({ length: total }, (_, i) => (
            <div
              key={i}
              className={`h-1 w-4 rounded ${i + 1 === number ? 'bg-emerald-500' : 'bg-zinc-800'}`}
            />
          ))}
        </div>
      </div>

      <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6 text-lg leading-relaxed">
        {content}
      </div>

      <div className="grid grid-cols-5 gap-3">
        {CHOICES.map((choice) => (
          <button
            key={choice}
            onClick={() => onSelect(choice)}
            className={`rounded-lg border px-4 py-3 text-center text-lg font-medium transition-colors ${
              selectedAnswer === choice
                ? 'border-emerald-500 bg-emerald-500/10 text-emerald-400'
                : 'border-zinc-800 bg-zinc-900 text-zinc-400 hover:border-zinc-600 hover:text-zinc-200'
            }`}
          >
            <span className="text-xs text-zinc-500">{choice}</span>
            <br />
            <span>{choice}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
