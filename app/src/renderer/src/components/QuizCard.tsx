import type { SectionKey } from '../types'
import { ProgressTracker } from './ProgressTracker'

const figurenImages = import.meta.glob<{ default: string }>(
  '../assets/figuren/*.png',
  { eager: true },
)

const ausweiseImages = import.meta.glob<{ default: string }>(
  '../assets/ausweise/*.png',
  { eager: true },
)

const recallImages = import.meta.glob<{ default: string }>(
  '../assets/ausweise/recall/*.png',
  { eager: true },
)

const solutionImages = import.meta.glob<{ default: string }>(
  '../assets/solutions/*.png',
  { eager: true },
)

interface QuizCardProps {
  section: SectionKey
  number: number
  total: number
  content: string
  questionId: number
  image?: string
  selectedAnswer: string | null
  correctAnswer: string
  showSolution: boolean
  setSize: number
  onSelect: (choice: string) => void
  onNext: () => void
  progressAnswers: Record<number, 'correct' | 'wrong' | 'pending'>
}

const CHOICES = ['A', 'B', 'C', 'D', 'E'] as const

function fmtId(n: number, width = 3): string {
  return n.toString().padStart(width, '0')
}

function getImageSrc(
  glob: Record<string, { default: string }>,
  filename: string,
): string | null {
  const key = Object.keys(glob).find((k) => k.endsWith(filename))
  return key ? glob[key]!.default : null
}

function getSolutionSrc(setIndex: number): string | null {
  const solMap: Record<number, number> = { 1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 3, 7: 3 }
  const setNum = setIndex + 1
  const offset = solMap[setNum] ?? 0
  const page = 37 + offset
  return getImageSrc(solutionImages, `page_${page}.png`)
}

export function QuizCard({
  section,
  number,
  total,
  content,
  questionId,
  image,
  selectedAnswer,
  correctAnswer,
  showSolution,
  setSize,
  onSelect,
  onNext,
  progressAnswers,
}: QuizCardProps) {
  const isMemorize = section === 'ausweise_memorize'
  const isRecall = section === 'ausweise_recall'
  const hasAnswered = selectedAnswer !== null
  const isCorrect = hasAnswered && selectedAnswer === correctAnswer
  const setIndex = Math.floor((questionId - 1) / setSize)
  const isLast = number >= total

  return (
    <div className="mx-auto w-full max-w-2xl animate-fade-in rounded-2xl bg-gray-900 shadow-2xl border border-gray-700">
      {/* Header */}
      <div className="border-b border-gray-700 px-6 py-4">
        <p className="text-sm text-white/70">
          {isMemorize ? 'Ausweis' : 'Frage'} {number} von {total}
        </p>
      </div>

      {/* Content */}
      <div className="px-6 py-6">
        {section === 'figuren' ? (
          <div className="mb-6 flex justify-center rounded-xl bg-gray-800/50 p-4">
            {getImageSrc(figurenImages, `${fmtId(questionId)}.png`) ? (
              <img
                src={getImageSrc(figurenImages, `${fmtId(questionId)}.png`)!}
                alt={`Figur ${questionId}`}
                className="max-h-[45vh] max-w-full object-contain rounded"
              />
            ) : (
              <p className="text-gray-400">Bild nicht verfügbar</p>
            )}
          </div>
        ) : null}

        {isRecall ? (
          <div className="mb-6 flex justify-center rounded-xl bg-gray-800/50 p-4">
            {getImageSrc(recallImages, `${fmtId(questionId, 4)}.png`) ? (
              <img
                src={getImageSrc(recallImages, `${fmtId(questionId, 4)}.png`)!}
                alt={`Recall ${questionId}`}
                className="max-h-[45vh] max-w-full object-contain rounded"
              />
            ) : (
              <p className="text-gray-400">Bild nicht verfügbar</p>
            )}
          </div>
        ) : null}

        {isMemorize && image ? (
          <div className="mb-6 flex justify-center rounded-xl bg-gray-800/50 p-4">
            <img
              src={getImageSrc(ausweiseImages, image) ?? ''}
              alt={`Ausweis ${questionId}`}
              className="max-h-[40vh] max-w-full rounded object-contain"
            />
          </div>
        ) : null}

        <h2 className="text-center text-2xl font-bold leading-relaxed whitespace-pre-line text-white">
          {content}
        </h2>
      </div>

      {/* Answer buttons — all sections except memorize */}
      {!isMemorize && (
        <div className="px-6 pb-4">
          <div className="flex flex-col gap-3">
            {CHOICES.map((choice) => {
              const isSelected = selectedAnswer === choice
              const isCorrectChoice = choice === correctAnswer

              let border = 'border-gray-600'
              let bg = 'bg-gray-800 hover:border-gray-400'
              let badgeBg = 'bg-gray-600'

              if (showSolution && isCorrectChoice) {
                border = 'border-green-500'
                bg = 'bg-green-500/10'
                badgeBg = 'bg-green-500'
              } else if (isSelected) {
                border = 'border-blue-500'
                bg = 'bg-blue-500/10'
                badgeBg = 'bg-blue-500'
              }

              return (
                <button
                  key={choice}
                  onClick={() => onSelect(choice)}
                  className={`flex w-full items-center gap-4 rounded-xl border px-4 py-3 text-left text-lg transition-all duration-200 cursor-pointer active:scale-[0.98]
                    ${border} ${bg}
                  `}
                >
                  <span
                    className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg text-sm font-bold text-white ${badgeBg}`}
                  >
                    {choice}
                  </span>
                  <span className="text-gray-200">
                    {isSelected && !showSolution ? 'Ausgewählt' : ''}
                  </span>
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* Solution reveal when user toggles "Lösung anzeigen" */}
      {showSolution && !isMemorize && (
        <div className="animate-fade-in px-6 pb-2 text-center">
          {isCorrect ? (
            <p className="font-semibold text-green-400">✓ Richtig!</p>
          ) : (
            <p className="font-semibold text-red-400">
              ✗ Falsch. Die richtige Antwort ist {correctAnswer}.
            </p>
          )}
        </div>
      )}

      {/* Solution image for figuren */}
      {showSolution && section === 'figuren' && (
        <div className="animate-fade-in px-6 pb-4">
          <div className="rounded-xl bg-gray-800/50 px-5 py-4">
            <p className="mb-3 text-sm text-gray-400">
              Auflösung (aus welchen Figuren setzt sich das große Bild zusammen):
            </p>
            {getSolutionSrc(setIndex) ? (
              <div className="flex justify-center">
                <img
                  src={getSolutionSrc(setIndex)!}
                  alt={`Lösung Set ${setIndex + 1}`}
                  className="max-h-[40vh] max-w-full rounded object-contain"
                />
              </div>
            ) : (
              <p className="text-sm text-gray-500">Kein Lösungsbild verfügbar</p>
            )}
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="px-6 pb-6">
        {isMemorize ? (
          <button
            onClick={onNext}
            className="w-full rounded-xl bg-gradient-to-r from-emerald-600 to-emerald-500 px-6 py-3.5 text-center text-lg font-semibold text-white transition-all duration-200 hover:from-emerald-500 hover:to-emerald-600 active:scale-[0.98] shadow-lg shadow-emerald-500/25"
          >
            {isLast ? 'Fertig' : 'Weiter →'}
          </button>
        ) : (
          <button
            onClick={onNext}
            disabled={!hasAnswered}
            className={`w-full rounded-xl px-8 py-3.5 font-semibold transition-all duration-200 text-lg text-center
              ${hasAnswered
                ? 'bg-gradient-to-r from-emerald-600 to-emerald-500 text-white hover:from-emerald-500 hover:to-emerald-600 active:scale-[0.98] shadow-lg shadow-emerald-500/25'
                : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              }
            `}
          >
            {isLast ? 'Fertig' : 'Weiter →'}
          </button>
        )}
      </div>

      {/* ProgressTracker */}
      <div className="border-t border-gray-700 px-6 py-4">
        <ProgressTracker total={total} current={number - 1} answers={progressAnswers} />
      </div>
    </div>
  )
}
