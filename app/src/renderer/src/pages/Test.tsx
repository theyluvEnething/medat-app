import { useCallback, useMemo, useState } from 'react'
import type { Question, SectionConfig, SectionProgress } from '../types'
import { SECTION_ORDER } from '../types'
import { Timer } from '../components/Timer'
import { QuestionCard } from '../components/QuestionCard'
import { HintBanner } from '../components/HintBanner'
import { useTimer } from '../hooks/useTimer'
import { ensureUserProgress, saveUserProgress } from '../services/storage'

interface TestProps {
  questions: Record<string, Question[]>
  username: string
  onExit: () => void
}

type Step = 'intro' | 'active' | 'section-done' | 'results'

function selectQuestions(
  allPool: Question[],
  progress: SectionProgress,
  count: number,
): { questions: Question[] } {
  const poolSize = allPool.length
  const totalSets = Math.ceil(poolSize / count)
  const setIndex = progress.currentSetIndex

  // Clamp set index in case it got out of range
  const safeSet = Math.min(setIndex, totalSets - 1)
  const start = safeSet * count
  const setQuestions = allPool.slice(start, start + count)

  const completedSet = new Set(progress.completed)
  const wrongSet = new Set(progress.wrongIds)

  // Filter out already-correctly-answered questions from this set
  const remaining = setQuestions.filter((q) => !completedSet.has(q.id))

  // If all questions in set are completed, advance to next set
  if (remaining.length === 0 && setQuestions.length > 0) {
    const nextSet = safeSet + 1
    const wrappedSet = nextSet >= totalSets ? 0 : nextSet
    const newStart = wrappedSet * count
    const freshQuestions = allPool.slice(newStart, newStart + count)
    return { questions: freshQuestions }
  }

  // Fill up to count with wrong answers from this set
  if (remaining.length < count) {
    const wrongInSet = setQuestions.filter(
      (q) => wrongSet.has(q.id) && !completedSet.has(q.id),
    )
    const extra = wrongInSet.slice(0, count - remaining.length)
    return { questions: [...remaining, ...extra] }
  }

  return { questions: remaining.slice(0, count) }
}

export function Test({ questions, username, onExit }: TestProps) {
  const [progress, setProgress] = useState(() => ensureUserProgress(username))

  const [sectionIndex, setSectionIndex] = useState(0)
  const [questionIndex, setQuestionIndex] = useState(0)
  const [step, setStep] = useState<Step>('intro')
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [showTimer, setShowTimer] = useState(true)

  const section = SECTION_ORDER[sectionIndex]
  if (!section) return null

  const allPool: Question[] = questions[section.key] ?? []
  const sp: SectionProgress | undefined = progress.sections[section.key]

  const displayedQuestions: Question[] = useMemo(() => {
    if (!sp) return []
    const result = selectQuestions(allPool, sp, section.count)
    // If set changed (all completed → next set), persist the new set index
    if (result.questions.length > 0) {
      const firstId = result.questions[0]!.id
      const newSetIndex = Math.floor((firstId - 1) / section.count)
      if (newSetIndex !== sp.currentSetIndex) {
        const updated = { ...sp, currentSetIndex: newSetIndex }
        setProgress((prev) => {
          const next = {
            ...prev,
            sections: { ...prev.sections, [section.key]: updated },
          }
          saveUserProgress(username, next)
          return next
        })
      }
    }
    return result.questions
  }, [section, sp, allPool])

  const currentQuestion = displayedQuestions[questionIndex]

  const handleExpire = useCallback(() => {
    if (sectionIndex < SECTION_ORDER.length - 1) {
      setStep('section-done')
    } else {
      setStep('results')
    }
  }, [sectionIndex])

  const timerSeconds = section.timeMin * 60
  const { remaining, start } = useTimer(timerSeconds, handleExpire)

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
    if (section.timeMin > 0) {
      start()
    }
  }

  const goNext = () => {
    if (questionIndex < displayedQuestions.length - 1) {
      setQuestionIndex((i) => i + 1)
    }
  }

  const goPrev = () => {
    if (questionIndex > 0) {
      setQuestionIndex((i) => i - 1)
    }
  }

  const skipQuestion = () => {
    if (!currentQuestion) return
    const key = `${section.key}-${currentQuestion.id}`
    setAnswers((prev) => ({ ...prev, [key]: '__SKIPPED__' }))
    if (questionIndex < displayedQuestions.length - 1) {
      setQuestionIndex((i) => i + 1)
    }
  }

  const persistSectionProgress = () => {
    if (!sp) return
    const completedSet = new Set(sp.completed)
    const wrongSet = new Set(sp.wrongIds)

    for (const q of displayedQuestions) {
      const key = `${section.key}-${q.id}`
      const choice = answers[key]
      if (choice === undefined) continue
      if (choice === q.answer) {
        completedSet.add(q.id)
        wrongSet.delete(q.id)
      } else {
        wrongSet.add(q.id)
        completedSet.delete(q.id)
      }
    }

    // Check if all questions in the current set are completed
    const setStart = sp.currentSetIndex * section.count
    const setEnd = setStart + section.count
    const setIds = allPool.slice(setStart, setEnd).map((q) => q.id)
    const allSetDone = setIds.every((id) => completedSet.has(id))
    const totalSets =
      section.count > 0 ? Math.ceil(allPool.length / section.count) : 1

    let newSetIndex = sp.currentSetIndex
    if (allSetDone) {
      newSetIndex = sp.currentSetIndex + 1
      if (newSetIndex >= totalSets) {
        newSetIndex = 0
      }
    }

    const updated: SectionProgress = {
      currentSetIndex: newSetIndex,
      completed: [...completedSet].sort((a, b) => a - b),
      wrongIds: [...wrongSet].sort((a, b) => a - b),
    }

    const next = {
      ...progress,
      sections: { ...progress.sections, [section.key]: updated },
    }
    setProgress(next)
    saveUserProgress(username, next)
  }

  const advanceSection = () => {
    persistSectionProgress()
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
      const parts = key.split('-')
      const sectionKey = parts[0]
      const idStr = parts[1]
      if (!sectionKey || !idStr) continue
      const qs = questions[sectionKey] ?? []
      const q = qs.find((q: Question) => q.id === Number(idStr))
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
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <span className="text-sm text-zinc-500">
            Abschnitt {sectionIndex + 1}/{SECTION_ORDER.length}
          </span>
          <button
            onClick={onExit}
            className="text-xs text-red-400/70 hover:text-red-400"
          >
            Abbrechen
          </button>
        </div>
        <div className="flex items-center gap-3">
          {step === 'active' && section.timeMin > 0 && showTimer && (
            <Timer remaining={remaining} total={timerSeconds} />
          )}
          {step === 'active' && section.timeMin > 0 && (
            <button
              onClick={() => setShowTimer((v) => !v)}
              className="text-xs text-zinc-600 hover:text-zinc-400"
            >
              {showTimer ? 'Timer ausblenden' : 'Timer einblenden'}
            </button>
          )}
        </div>
      </div>

      <h2 className="text-2xl font-semibold">{section.label}</h2>

      <HintBanner sectionKey={section.key} />

      {step === 'intro' && (
        <div className="flex flex-col items-center gap-6 py-16">
          <p className="text-zinc-400">
            {section.timeMin > 0
              ? `${section.timeMin} Minuten · ${displayedQuestions.length} ${section.key === 'ausweise_memorize' ? 'Ausweise' : 'Fragen'}`
              : `${displayedQuestions.length} Fragen`}
          </p>
          <button
            onClick={startSection}
            className="rounded-xl bg-emerald-600 px-8 py-3 text-lg font-semibold text-white hover:bg-emerald-500"
          >
            Start
          </button>
        </div>
      )}

      {step === 'active' && currentQuestion && (
        <>
          <QuestionCard
            section={section.key}
            number={questionIndex + 1}
            total={displayedQuestions.length}
            content={currentQuestion.content}
            questionId={currentQuestion.id}
            image={currentQuestion.image}
            selectedAnswer={selectedAnswer}
            onSelect={selectAnswer}
          />

          <div className="flex items-center justify-between">
            <button
              onClick={goPrev}
              disabled={questionIndex === 0}
              className="rounded-lg bg-zinc-800 px-4 py-2 text-sm text-zinc-300 disabled:opacity-30"
            >
              Zurück
            </button>

            <button
              onClick={skipQuestion}
              className="rounded-lg border border-amber-700/50 bg-amber-950/20 px-4 py-2 text-sm text-amber-300 hover:border-amber-600/70 hover:bg-amber-950/40"
            >
              Überspringen
            </button>

            <button
              onClick={goNext}
              disabled={questionIndex === displayedQuestions.length - 1}
              className="rounded-lg bg-zinc-800 px-4 py-2 text-sm text-zinc-300 disabled:opacity-30"
            >
              Weiter
            </button>
          </div>
        </>
      )}

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
