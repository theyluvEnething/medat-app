import { useEffect, useMemo, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import type { Question, SectionProgress, SectionKey } from '../types'
import { SECTION_ORDER } from '../types'
import { Timer } from '../components/Timer'
import { QuizCard } from '../components/QuizCard'
import { HintBanner } from '../components/HintBanner'
import { useTimer } from '../hooks/useTimer'
import { useAppStore } from '../store/useAppStore'

import { questions } from '../data/questions'

function emptyProgress(): SectionProgress {
  return { currentSetIndex: 0, completed: [], wrongIds: [] }
}

function selectQuestions(
  allPool: Question[],
  progress: SectionProgress,
  count: number,
): { questions: Question[] } {
  const totalSets = Math.ceil(allPool.length / count)
  const setIndex = progress.currentSetIndex
  const safeSet = Math.min(setIndex, totalSets - 1)
  const start = safeSet * count
  const setQuestions = allPool.slice(start, start + count)

  const completedSet = new Set(progress.completed)
  const wrongSet = new Set(progress.wrongIds)
  const remaining = setQuestions.filter((q) => !completedSet.has(q.id))

  if (remaining.length === 0 && setQuestions.length > 0) {
    const nextSet = safeSet + 1
    const wrappedSet = nextSet >= totalSets ? 0 : nextSet
    return { questions: allPool.slice(wrappedSet * count, wrappedSet * count + count) }
  }

  if (remaining.length < count) {
    const wrongInSet = setQuestions.filter(
      (q) =>
        wrongSet.has(q.id) &&
        !completedSet.has(q.id) &&
        !remaining.some((r) => r.id === q.id),
    )
    const filled = [...remaining, ...wrongInSet.slice(0, count - remaining.length)]
    if (filled.length === 0 && allPool.length > 0) {
      const nextSet = safeSet + 1
      const wrappedSet = nextSet >= totalSets ? 0 : nextSet
      return { questions: allPool.slice(wrappedSet * count, wrappedSet * count + count) }
    }
    return { questions: filled }
  }

  return { questions: remaining.slice(0, count) }
}

type Step = 'intro' | 'active' | 'section-done'

export function Session() {
  const { type } = useParams<{ type: string }>()
  const navigate = useNavigate()

  const storeProgress = useAppStore((s) => s.progress)
  const updateProgress = useAppStore((s) => s.updateProgress)
  const startSession = useAppStore((s) => s.startSession)
  const completeSession = useAppStore((s) => s.completeSession)
  const recordWrongAnswer = useAppStore((s) => s.recordWrongAnswer)
  const recalculateMastery = useAppStore((s) => s.recalculateMastery)
  const updateDailyStreak = useAppStore((s) => s.updateDailyStreak)

  // Determine sections to run
  const sectionsToRun = useMemo(() => {
    if (!type) return []
    if (type === 'full') return [...SECTION_ORDER]
    const sec = SECTION_ORDER.find((s) => s.key === type)
    return sec ? [sec] : []
  }, [type])

  const [sectionIndex, setSectionIndex] = useState(0)
  const [questionIndex, setQuestionIndex] = useState(0)
  const [step, setStep] = useState<Step>('intro')
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [showTimer, setShowTimer] = useState(true)
  const [showSolution, setShowSolution] = useState(false)
  const [zoom, setZoom] = useState(1)
  const [sessionStarted, setSessionStarted] = useState(false)

  const section = sectionsToRun[sectionIndex]
  if (!section) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-6">
        <p className="text-zinc-400">Ungültiger Testtyp</p>
        <button
          onClick={() => navigate('/setup')}
          className="rounded-xl bg-emerald-600 px-6 py-3 text-lg font-semibold text-white"
        >
          Zurück
        </button>
      </div>
    )
  }

  const allPool: Question[] = questions[section.key] ?? []
  const sp: SectionProgress = storeProgress[section.key] ?? emptyProgress()

  const displayedQuestions: Question[] = useMemo(() => {
    const result = selectQuestions(allPool, sp, section.count)
    if (result.questions.length > 0) {
      const firstId = result.questions[0]!.id
      const newSetIndex = Math.floor((firstId - 1) / section.count)
      if (newSetIndex !== sp.currentSetIndex) {
        updateProgress(section.key, { ...sp, currentSetIndex: newSetIndex })
      }
    }
    return result.questions
  }, [section.key, sp.currentSetIndex, sp.completed.length, sp.wrongIds.length, allPool.length])

  const currentQuestion = displayedQuestions[questionIndex]

  const timerSeconds = section.timeMin * 60
  const handleExpire = () => {
    persistSectionProgress()
    setStep('section-done')
  }
  const { remaining, isRunning, start, pause } = useTimer(timerSeconds, handleExpire)

  // Initialize session on first mount
  useEffect(() => {
    if (!sessionStarted && type) {
      startSession(type as 'full' | SectionKey)
      setSessionStarted(true)
      updateDailyStreak()
    }
  }, [sessionStarted, type, startSession, updateDailyStreak])

  // Reset solution visibility on section/question change
  useEffect(() => {
    setShowSolution(false)
  }, [sectionIndex, questionIndex])

  // Ctrl+Wheel zoom
  useEffect(() => {
    const handler = (e: WheelEvent) => {
      if (e.ctrlKey) {
        e.preventDefault()
        setZoom((z) => Math.round(Math.min(3, Math.max(0.5, z - e.deltaY * 0.001)) * 1000) / 1000)
      }
    }
    window.addEventListener('wheel', handler, { passive: false })
    return () => window.removeEventListener('wheel', handler)
  }, [])

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
    if (section.timeMin > 0) start()
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

  const togglePause = () => {
    if (isRunning) pause()
    else start()
  }

  const finishEarly = () => {
    persistSectionProgress()
    setStep('section-done')
  }

  const persistSectionProgress = () => {
    const completedSet = new Set(sp.completed)
    const wrongSet = new Set(sp.wrongIds)

    for (const q of displayedQuestions) {
      const key = `${section.key}-${q.id}`
      const choice = answers[key]
      if (choice === undefined) continue
      if (choice === q.answer) {
        completedSet.add(q.id)
        wrongSet.delete(q.id)
      } else if (choice !== '__SKIPPED__') {
        wrongSet.add(q.id)
        completedSet.delete(q.id)
        recordWrongAnswer(section.key, q.id)
      }
    }

    const setStart = sp.currentSetIndex * section.count
    const setEnd = setStart + section.count
    const setIds = allPool.slice(setStart, setEnd).map((q) => q.id)
    const allSetDone = setIds.every((id) => completedSet.has(id))
    const totalSets = section.count > 0 ? Math.ceil(allPool.length / section.count) : 1

    let newSetIndex = sp.currentSetIndex
    if (allSetDone) {
      newSetIndex = sp.currentSetIndex + 1
      if (newSetIndex >= totalSets) newSetIndex = 0
    }

    const updated: SectionProgress = {
      currentSetIndex: newSetIndex,
      completed: [...completedSet].sort((a, b) => a - b),
      wrongIds: [...wrongSet].sort((a, b) => a - b),
    }

    updateProgress(section.key, updated)
  }

  const advanceSection = () => {
    persistSectionProgress()
    const next = sectionIndex + 1
    if (next < sectionsToRun.length) {
      setSectionIndex(next)
      setQuestionIndex(0)
      setStep('intro')
    } else {
      // Session complete
      recalculateMastery(questions)
      completeSession(questions)
      navigate('/results')
    }
  }

  // Build progress answers for ProgressTracker (answered / pending only during session)
  const progressAnswers: Record<number, 'correct' | 'wrong' | 'pending'> = {}
  for (let i = 0; i < displayedQuestions.length; i++) {
    const q = displayedQuestions[i]
    if (!q) continue
    const key = `${section.key}-${q.id}`
    progressAnswers[i] = answers[key] !== undefined ? 'correct' : 'pending'
  }

  return (
    <div
      className="mx-auto flex min-h-screen max-w-5xl flex-col gap-6 px-6 py-8"
      style={{ zoom }}
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <span className="text-sm text-zinc-500">
            Abschnitt {sectionIndex + 1}/{sectionsToRun.length}
          </span>
          <button
            onClick={() => navigate('/home')}
            className="text-xs text-red-400/70 transition-colors duration-200 hover:text-red-400"
          >
            Abbrechen
          </button>
        </div>
        <div className="flex items-center gap-3">
          {step === 'active' && section.timeMin > 0 && (
            <>
              <button
                onClick={togglePause}
                className="rounded-lg border border-zinc-800 px-2 py-1 text-xs text-zinc-400 transition-all duration-200 hover:border-zinc-600 hover:text-zinc-200 active:scale-95"
              >
                {isRunning ? 'Pause' : 'Fortsetzen'}
              </button>
              {showTimer && <Timer remaining={remaining} total={timerSeconds} />}
              <button
                onClick={() => setShowTimer((v) => !v)}
                className="text-xs text-zinc-600 transition-colors duration-200 hover:text-zinc-400"
              >
                {showTimer ? 'Ausblenden' : 'Einblenden'}
              </button>
            </>
          )}
        </div>
      </div>

      <h2 className="text-2xl font-semibold text-zinc-100">{section.label}</h2>

      <HintBanner sectionKey={section.key} />

      {/* Intro step */}
      {step === 'intro' && (
        <div className="flex animate-fade-in flex-col items-center gap-6 py-16">
          <p className="text-zinc-400">
            {section.timeMin > 0
              ? `${section.timeMin} Minuten · ${displayedQuestions.length} ${section.key === 'ausweise_memorize' ? 'Ausweise' : 'Fragen'}`
              : `${displayedQuestions.length} Fragen`}
          </p>
          <button
            onClick={startSection}
            className="animate-breathe rounded-xl bg-emerald-600 px-8 py-3 text-lg font-semibold text-white transition-all duration-200 hover:scale-[1.05] hover:bg-emerald-500 active:scale-95"
          >
            Start
          </button>
        </div>
      )}

      {/* Active step */}
      {step === 'active' && currentQuestion && (
        <div className="flex animate-fade-in flex-col gap-6">
          <QuizCard
            key={`${section.key}-${questionIndex}`}
            section={section.key}
            number={questionIndex + 1}
            total={displayedQuestions.length}
            content={currentQuestion.content}
            questionId={currentQuestion.id}
            image={currentQuestion.image}
            setSize={section.count}
            selectedAnswer={selectedAnswer}
            correctAnswer={currentQuestion.answer}
            showSolution={showSolution}
            onSelect={selectAnswer}
            onNext={goNext}
            progressAnswers={progressAnswers}
          />

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={goPrev}
                disabled={questionIndex === 0}
                className="rounded-lg bg-zinc-800 px-4 py-2 text-sm text-zinc-300 transition-all duration-200 hover:scale-[1.03] hover:bg-zinc-700 disabled:opacity-30 disabled:hover:scale-100"
              >
                Zurück
              </button>

              <button
                onClick={skipQuestion}
                className="rounded-lg border border-amber-700/50 bg-amber-950/20 px-4 py-2 text-sm text-amber-300 transition-all duration-200 hover:scale-[1.03] hover:border-amber-600/70 hover:bg-amber-950/40 active:scale-95"
              >
                Überspringen
              </button>

              <button
                onClick={() => setShowSolution((v) => !v)}
                className="text-xs text-zinc-500 transition-colors duration-200 hover:text-zinc-300"
              >
                {showSolution ? 'Lösung ausblenden' : 'Lösung anzeigen'}
              </button>
            </div>

            <button
              onClick={finishEarly}
              className="rounded-lg bg-zinc-800 px-4 py-2 text-sm text-zinc-300 transition-all duration-200 hover:scale-[1.03] hover:bg-zinc-700 active:scale-95"
            >
              Fertig → nächster Abschnitt
            </button>
          </div>
        </div>
      )}

      {/* Section-done step */}
      {step === 'section-done' && (
        <div className="flex animate-fade-in flex-col items-center gap-4 py-16">
          <p className="text-zinc-400">Zeit abgelaufen</p>
          <button
            onClick={advanceSection}
            className="rounded-xl bg-emerald-600 px-8 py-3 text-lg font-semibold text-white transition-all duration-200 hover:scale-[1.05] hover:bg-emerald-500 active:scale-95"
          >
            Nächster Abschnitt
          </button>
        </div>
      )}
    </div>
  )
}
