import { useState } from 'react'
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
  correctAnswer: string | null
  setSize: number
  onSelect: (choice: string) => void
  onNext: () => void
  progressAnswers: Record<number, 'correct' | 'wrong' | 'pending'>
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
  setSize,
  onSelect,
  onNext,
  progressAnswers,
}: QuizCardProps) {
  const [revealed, setRevealed] = useState(false)
  const needsAnswers = section !== 'ausweise_memorize'
  const setIndex = Math.floor((questionId - 1) / setSize)
  const showAnswers = needsAnswers
  const hasAnswered = selectedAnswer !== null
  const isCorrect = hasAnswered && selectedAnswer === correctAnswer

  const handleSelect = (choice: string) => {
    if (hasAnswered) return
    onSelect(choice)
    setRevealed(true)
  }

  return (
    <div className="mx-auto w-full max-w-2xl animate-fade-in rounded-2xl bg-blue-600 shadow-2xl">
      {/* Header */}
      <div className="border-b border-white/10 px-6 py-4">
        <p className="text-lg font-semibold text-white">
          {section === 'ausweise_memorize' ? 'Ausweis' : 'Frage'} {number} von {total}
        </p>
      </div>

      {/* Content */}
      <div className="px-6 py-6">
        {section === 'figuren' ? (
          <div className="flex justify-center rounded-xl bg-white/10 p-4">
            {getImageSrc(figurenImages, `${fmtId(questionId)}.png`) ? (
              <img
                src={getImageSrc(figurenImages, `${fmtId(questionId)}.png`)!}
                alt={`Figur ${questionId}`}
                className="max-h-[45vh] max-w-full object-contain"
              />
            ) : (
              <p className="text-blue-200">Bild nicht verfügbar</p>
            )}
          </div>
        ) : section === 'ausweise_memorize' ? (
          <div className="space-y-4">
            {image ? (
              <div className="flex justify-center rounded-xl bg-white/10 p-4">
                <img
                  src={getImageSrc(ausweiseImages, image) ?? ''}
                  alt={`Ausweis ${questionId}`}
                  className="max-h-[40vh] max-w-full rounded object-contain"
                />
              </div>
            ) : null}
            <p className="text-center text-lg leading-relaxed whitespace-pre-line text-white">
              {content}
            </p>
          </div>
        ) : (
          <p className="text-xl leading-relaxed whitespace-pre-line text-white">
            {content}
          </p>
        )}
      </div>

      {/* Solution reveal */}
      {revealed && correctAnswer !== null && (
        <div className="animate-fade-in mx-6 mb-4 rounded-xl bg-white/15 px-5 py-4">
          <p className="text-sm font-semibold text-white">
            Richtige Antwort: {correctAnswer}
            {isCorrect ? (
              <span className="ml-2 text-green-300">✓ Richtig!</span>
            ) : (
              <span className="ml-2 text-red-300">✗ Falsch</span>
            )}
          </p>
          {section === 'figuren' && (
            <div className="mt-3 flex justify-center">
              {getSolutionSrc(setIndex) ? (
                <div>
                  <p className="mb-2 text-xs text-blue-200">
                    Auflösung (aus welchen Figuren setzt sich das große Bild zusammen):
                  </p>
                  <img
                    src={getSolutionSrc(setIndex)!}
                    alt={`Lösung Set ${setIndex + 1}`}
                    className="max-h-[40vh] max-w-full rounded object-contain border border-white/10"
                  />
                </div>
              ) : (
                <p className="text-xs text-blue-200/60">Kein Lösungsbild verfügbar</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Answer buttons */}
      {showAnswers && (
        <div className="px-6 pb-4">
          <div className="grid grid-cols-1 gap-3">
            {CHOICES.map((choice) => {
              const isSelected = selectedAnswer === choice
              const isCorrectChoice = correctAnswer !== null && choice === correctAnswer
              const isWrongChoice = revealed && isSelected && !isCorrectChoice

              let bg = 'bg-white hover:bg-gray-50'
              let border = 'border-b-4 border-gray-300'
              let text = 'text-gray-800'

              if (revealed && isCorrectChoice) {
                bg = 'bg-green-500'
                border = 'border-b-4 border-green-700'
                text = 'text-white'
              } else if (isWrongChoice) {
                bg = 'bg-red-500'
                border = 'border-b-4 border-red-700'
                text = 'text-white'
              } else if (isSelected && !revealed) {
                bg = 'bg-blue-100'
                border = 'border-b-4 border-blue-300'
                text = 'text-blue-800'
              }

              return (
                <button
                  key={choice}
                  onClick={() => handleSelect(choice)}
                  disabled={hasAnswered}
                  className={`w-full rounded-xl px-5 py-4 text-left text-lg font-medium transition-all duration-150 active:scale-[0.98] ${bg} ${border} ${text} ${
                    hasAnswered ? 'cursor-default' : 'cursor-pointer'
                  } ${isCorrectChoice && revealed ? 'animate-pulse-warn' : ''}`}
                >
                  <span className="font-bold">{choice}</span>
                  {isSelected ? <span className="ml-2 text-sm opacity-70">— Ausgewählt</span> : null}
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* Next button */}
      {revealed && (
        <div className="px-6 pb-5">
          <button
            onClick={onNext}
            className="w-full rounded-xl bg-orange-500 border-b-4 border-orange-700 px-6 py-3.5 text-center text-lg font-semibold text-white transition-all duration-150 hover:bg-orange-400 hover:border-orange-600 active:scale-[0.98]"
          >
            {number < total ? 'Weiter' : 'Fertig'}
          </button>
        </div>
      )}

      {/* Progress tracker */}
      <div className="border-t border-white/10 px-6 py-4">
        <ProgressTracker total={total} current={number - 1} answers={progressAnswers} />
      </div>
    </div>
  )
}
