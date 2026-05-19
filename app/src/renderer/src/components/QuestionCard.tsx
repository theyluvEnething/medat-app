import type { SectionKey } from '../types'

const figurenImages = import.meta.glob<{ default: string }>(
  '../assets/figuren/*.png',
  { eager: true },
)

const ausweiseImages = import.meta.glob<{ default: string }>(
  '../assets/ausweise/*.png',
  { eager: true },
)

const solutionImages = import.meta.glob<{ default: string }>(
  '../assets/solutions/*.png',
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
  correctAnswer: string | null
  setSize: number
  onSelect: (choice: string) => void
}

const CHOICES = ['A', 'B', 'C', 'D', 'E'] as const

function fmtId(n: number): string {
  return n.toString().padStart(3, '0')
}

function getImageSrc(
  glob: Record<string, { default: string }>,
  filename: string,
): string | null {
  const key = Object.keys(glob).find((k) => k.endsWith(filename))
  return key ? glob[key]!.default : null
}

function getSolutionSrc(setIndex: number): string | null {
  // Matches sol_map from figuren_parser.py: {1:0, 2:0, 3:0, 4:1, 5:2, 6:3, 7:3}
  // answer_start in the current PDF batch is page 37
  const solMap: Record<number, number> = { 1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 3, 7: 3 }
  const setNum = setIndex + 1
  const offset = solMap[setNum] ?? 0
  const page = 37 + offset
  return getImageSrc(solutionImages, `page_${page}.png`)
}

export function QuestionCard({
  section,
  number,
  total,
  content,
  questionId,
  image,
  selectedAnswer,
  correctAnswer,
  setSize,
  onSelect,
}: QuestionCardProps) {
  const needsAnswers = section !== 'ausweise_memorize'
  const setIndex = Math.floor((questionId - 1) / setSize)

  return (
    <div className="flex flex-col gap-6">
      {/* Progress dots */}
      <div className="flex items-center gap-2 text-sm text-zinc-500">
        <span>
          {section === 'ausweise_memorize' ? 'Ausweis' : 'Frage'} {number} von {total}
        </span>
        <div className="flex gap-1">
          {Array.from({ length: total }, (_, i) => (
            <div
              key={i}
              className={`h-1 rounded-full transition-all duration-300 ${
                i + 1 === number ? 'w-5 bg-emerald-500' : 'w-3 bg-zinc-800'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Content area */}
      {section === 'figuren' ? (
        <div className="flex justify-center rounded-xl border border-zinc-800 bg-zinc-900 p-6 transition-shadow duration-300 hover:border-zinc-700">
          {getImageSrc(figurenImages, `${fmtId(questionId)}.png`) ? (
            <img
              src={getImageSrc(figurenImages, `${fmtId(questionId)}.png`)!}
              alt={`Figur ${questionId}`}
              className="max-h-[55vh] max-w-full object-contain"
            />
          ) : (
            <p className="text-zinc-500">Bild nicht verfügbar</p>
          )}
        </div>
      ) : section === 'ausweise_memorize' ? (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 transition-shadow duration-300 hover:border-zinc-700">
          {image ? (
            <div className="mb-6 flex justify-center">
              <img
                src={getImageSrc(ausweiseImages, image) ?? ''}
                alt={`Ausweis ${questionId}`}
                className="max-h-[50vh] max-w-full rounded object-contain"
              />
            </div>
          ) : null}
          <div className="text-center">
            <p className="text-lg leading-relaxed whitespace-pre-line">{content}</p>
          </div>
        </div>
      ) : (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 text-lg leading-relaxed whitespace-pre-line transition-shadow duration-300 hover:border-zinc-700">
          {content}
        </div>
      )}

      {/* Solution display */}
      {correctAnswer !== null && (
        <div className="animate-fade-in rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-5">
          <p className="text-sm font-semibold text-emerald-400">
            Richtige Antwort: {correctAnswer}
          </p>
          {section === 'figuren' && (
            <div className="mt-3 flex justify-center">
              {getSolutionSrc(setIndex) ? (
                <div>
                  <p className="mb-2 text-xs text-zinc-500">
                    Auflösung (aus welchen Figuren setzt sich das große Bild zusammen):
                  </p>
                  <img
                    src={getSolutionSrc(setIndex)!}
                    alt={`Lösung Set ${setIndex + 1}`}
                    className="max-h-[50vh] max-w-full rounded object-contain border border-zinc-800"
                  />
                </div>
              ) : (
                <p className="text-xs text-zinc-600">Kein Lösungsbild verfügbar</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Answer buttons */}
      {needsAnswers && (
        <div className="grid grid-cols-5 gap-3">
          {CHOICES.map((choice) => {
            const isCorrect = correctAnswer !== null && choice === correctAnswer
            const isWrong =
              correctAnswer !== null &&
              selectedAnswer === choice &&
              choice !== correctAnswer

            let border = 'border-zinc-800'
            let bg = 'bg-zinc-900'
            let text = 'text-zinc-400'
            let hover =
              'hover:border-zinc-600 hover:text-zinc-200 hover:scale-[1.03]'

            if (isCorrect) {
              border = 'border-emerald-500'
              bg = 'bg-emerald-500/20'
              text = 'text-emerald-400'
              hover = ''
            } else if (isWrong) {
              border = 'border-red-500'
              bg = 'bg-red-500/10'
              text = 'text-red-400'
              hover = ''
            } else if (selectedAnswer === choice) {
              border = 'border-emerald-500'
              bg = 'bg-emerald-500/10'
              text = 'text-emerald-400'
              hover = 'hover:scale-[1.03]'
            }

            return (
              <button
                key={choice}
                onClick={() => onSelect(choice)}
                className={`rounded-xl border px-4 py-3 text-center text-lg font-medium transition-all duration-150 active:scale-95 ${border} ${bg} ${text} ${correctAnswer === null ? hover : ''}`}
              >
                <span className="text-xs opacity-60">{choice}</span>
                <br />
                <span className="select-none">{choice}</span>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
