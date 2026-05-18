import { useCallback, useState } from 'react'
import type { Question, SectionConfig } from '../types'
import { SECTION_ORDER } from '../types'
import { Timer } from '../components/Timer'
import { QuestionCard } from '../components/QuestionCard'
import { useTimer } from '../hooks/useTimer'

interface TestProps {
  questions: Record<string, Question[]>
  onExit: () => void
}

type Step = 'intro' | 'active' | 'section-done' | 'results'

export function Test({ questions, onExit }: TestProps) {
  const [sectionIndex, setSectionIndex] = useState(0)
  const [questionIndex, setQuestionIndex] = useState(0)
  const [step, setStep] = useState<Step>('intro')
  const [answers, setAnswers] = useState<Record<string, string>>({})

  const section = SECTION_ORDER[sectionIndex]
  if (!section) return null

  const sectionQuestions = questions[section.key] ?? []
  const currentQuestion = sectionQuestions[questionIndex]

  const handleExpire = useCallback(() => {
    if (sectionIndex < SECTION_ORDER.length - 1) {
      setStep('section-done')
    } else {
      setStep('results')
    }
  }, [sectionIndex])

  const { remaining, start } = useTimer(section.timeMin * 60, handleExpire)

  const selectAnswer = (choice: string) => {
    if (!currentQuestion) return
    const key = `${section.key}-${currentQuestion.id}`
    setAnswers((prev) => ({ ...prev, [key]: choice }))
  }

  const answerKey = currentQuestion ? `${section.key}-${currentQuestion.id}` : ''
  const selectedAnswer = answers[answerKey] ?? null

  const startSection = () => {
    setStep('active')
    setQuestionIndex(0)
    start()
  }

  const goNext = () => {
    if (questionIndex < sectionQuestions.length - 1) {
      setQuestionIndex((i) => i + 1)
    }
  }

  const goPrev = () => {
    if (questionIndex > 0) {
      setQuestionIndex((i) => i - 1)
    }
  }

  const advanceSection = () => {
    const next = sectionIndex + 1
    if (next < SECTION_ORDER.length) {
      setSectionIndex(next)
      setQuestionIndex(0)
      setStep('intro')
    } else {
      setStep('results')
    }
  }

  const score = (): [number, number] => {
    let correct = 0
    let total = 0
    for (const [key, choice] of Object.entries(answers)) {
      if (key.startsWith('ausweise_memorize')) continue
      const [sectionKey, idStr] = key.split('-', 2)
      const qs = questions[sectionKey] ?? []
      const q = qs.find((q) => q.id === Number(idStr))
      if (q) {
        total++
        if (q.answer === choice) correct++
      }
    }
    return [correct, total]
  }

  if (step === 'results') {
    const [correct, total] = score()
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-8">
        <h1 className="text-4xl font-bold">Ergebnis</h1>
        <p className="text-6xl font-mono tabular-nums text-emerald-400">
          {correct}/{total}
        </p>
        <button
          onClick={onExit}
          className="rounded-lg bg-zinc-800 px-6 py-3 text-sm text-zinc-300 hover:bg-zinc-700"
        >
          Zurück zum Start
        </button>
      </div>
    )
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-3xl flex-col gap-6 px-6 py-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="text-sm text-zinc-500">
          Abschnitt {sectionIndex + 1}/{SECTION_ORDER.length}
        </span>
        {step === 'active' && section.timeMin > 0 && (
          <Timer remaining={remaining} total={section.timeMin * 60} />
        )}
      </div>

      <h2 className="text-2xl font-semibold">{section.label}</h2>

      {/* Intro */}
      {step === 'intro' && (
        <div className="flex flex-col items-center gap-6 py-16">
          <p className="text-zinc-400">
            {section.timeMin > 0
              ? `${section.timeMin} Minuten · ${section.count} ${section.key === 'ausweise_memorize' ? 'Items' : 'Fragen'}`
              : `${section.count} Fragen`}
          </p>
          <button
            onClick={startSection}
            className="rounded-xl bg-emerald-600 px-8 py-3 text-lg font-semibold text-white hover:bg-emerald-500"
          >
            Start
          </button>
        </div>
      )}

      {/* Active */}
      {step === 'active' && currentQuestion && (
        <>
          <QuestionCard
            number={questionIndex + 1}
            total={sectionQuestions.length}
            content={currentQuestion.content}
            selectedAnswer={selectedAnswer}
            onSelect={selectAnswer}
          />

          <div className="flex justify-between">
            <button
              onClick={goPrev}
              disabled={questionIndex === 0}
              className="rounded-lg bg-zinc-800 px-4 py-2 text-sm text-zinc-300 disabled:opacity-30"
            >
              Zurück
            </button>
            <button
              onClick={goNext}
              disabled={questionIndex === sectionQuestions.length - 1}
              className="rounded-lg bg-zinc-800 px-4 py-2 text-sm text-zinc-300 disabled:opacity-30"
            >
              Weiter
            </button>
          </div>
        </>
      )}

      {/* Section Done */}
      {step === 'section-done' && (
        <div className="flex flex-col items-center gap-4 py-16">
          <p className="text-zinc-400">Zeit abgelaufen</p>
          <button
            onClick={advanceSection}
            className="rounded-xl bg-emerald-600 px-8 py-3 text-lg font-semibold text-white hover:bg-emerald-500"
          >
            Nächster Abschnitt
          </button>
        </div>
      )}
    </div>
  )
}
