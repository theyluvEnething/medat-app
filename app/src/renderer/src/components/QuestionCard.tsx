import type { SectionKey } from '../types'

const figurenImages = import.meta.glob<{ default: string }>(
  '../assets/figuren/*.png',
  { eager: true },
)

const ausweiseImages = import.meta.glob<{ default: string }>(
  '../assets/ausweise/*.png',
  { eager: true },
)

interface QuestionCardProps {
  section: SectionKey
  number: number
  total: number
  content: string
  questionId: number
  image?: string
  selectedAnswer: string | null
  onSelect: (choice: string) => void
}

const CHOICES = ['A', 'B', 'C', 'D', 'E'] as const

function fmtId(n: number): string {
  return n.toString().padStart(3, '0')
}

function getImageSrc(glob: Record<string, { default: string }>, filename: string): string | null {
  const key = Object.keys(glob).find((k) => k.endsWith(filename))
  return key ? glob[key]!.default : null
}

export function QuestionCard({
  section,
  number,
  total,
  content,
  questionId,
  image,
  selectedAnswer,
  onSelect,
}: QuestionCardProps) {
  const needsAnswers = section !== 'ausweise_memorize'

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-2 text-sm text-zinc-500">
        <span>
          {section === 'ausweise_memorize' ? 'Ausweis' : 'Frage'} {number} von {total}
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

      {section === 'figuren' ? (
        <div className="flex justify-center rounded-lg border border-zinc-800 bg-zinc-900 p-6">
          {getImageSrc(figurenImages, `${fmtId(questionId)}.png`) ? (
            <img
              src={getImageSrc(figurenImages, `${fmtId(questionId)}.png`)!}
              alt={`Figur ${questionId}`}
              className="max-h-[60vh] max-w-full object-contain"
            />
          ) : (
            <p className="text-zinc-500">Bild nicht verfügbar</p>
          )}
        </div>
      ) : section === 'ausweise_memorize' ? (
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
          {image ? (
            <div className="flex justify-center mb-6">
              <img
                src={getImageSrc(ausweiseImages, image) ?? ''}
                alt={`Ausweis ${questionId}`}
                className="max-h-[50vh] max-w-full object-contain rounded"
              />
            </div>
          ) : null}
          <div className="text-center">
            <p className="text-lg leading-relaxed whitespace-pre-line">{content}</p>
          </div>
        </div>
      ) : (
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6 text-lg leading-relaxed whitespace-pre-line">
          {content}
        </div>
      )}

      {needsAnswers && (
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
      )}
    </div>
  )
}
