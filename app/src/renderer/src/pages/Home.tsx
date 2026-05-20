import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAppStore } from '../store/useAppStore'
import { SECTION_ORDER } from '../types'

import questionsData from '../assets/questions.json'
const questions = questionsData as Record<string, { id: number }[]>

function computeStats() {
  const state = useAppStore.getState()
  const progress = state.progress

  const sections = SECTION_ORDER.map((sec) => {
    const sp = progress[sec.key]
    if (!sp) return { key: sec.key, label: sec.label, correct: 0, attempted: 0, percentage: null as number | null, currentSet: 0, totalSets: 1 }
    const pool = questions[sec.key] ?? []
    const setSize = sec.count
    const totalSets = setSize > 0 ? Math.ceil(pool.length / setSize) : 1
    const correct = sp.completed.length
    const attempted = correct + sp.wrongIds.length
    const percentage = attempted > 0 ? Math.round((correct / attempted) * 100) : null
    return { key: sec.key, label: sec.label, correct, attempted, percentage, currentSet: sp.currentSetIndex, totalSets }
  })

  const totalCorrect = sections.reduce((s, x) => s + x.correct, 0)
  const totalAttempted = sections.reduce((s, x) => s + x.attempted, 0)
  const totalPercentage = totalAttempted > 0 ? Math.round((totalCorrect / totalAttempted) * 100) : null

  return { sections, totalCorrect, totalAttempted, totalPercentage }
}

export function Home() {
  const navigate = useNavigate()
  const username = useAppStore((s) => s.user.username)
  const logout = useAppStore((s) => s.logout)
  const dailyStreak = useAppStore((s) => s.gamification.dailyStreak)
  const masteryLevels = useAppStore((s) => s.gamification.masteryLevels)
  const updateDailyStreak = useAppStore((s) => s.updateDailyStreak)

  useEffect(() => {
    updateDailyStreak()
  }, [updateDailyStreak])

  const stats = computeStats()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 py-8">
      <div className="text-center">
        <h1 className="text-5xl font-bold tracking-tight">MedAT KFF Trainer</h1>
        <p className="mt-3 text-lg text-zinc-500">
          Realistisches Zeitmanagement für den kognitiven Teil
        </p>
        <p className="mt-1 text-sm text-emerald-500">Angemeldet als: {username}</p>
        {dailyStreak > 0 && (
          <p className="mt-2 inline-flex items-center gap-1.5 rounded-full bg-amber-950/40 border border-amber-500/30 px-3 py-1 text-xs text-amber-300">
            {'\u{1F525}'} {dailyStreak}-Tage-Streak
          </p>
        )}
      </div>

      <div className="w-[32rem] rounded-xl border border-zinc-800 bg-zinc-900 p-5 text-center transition-shadow duration-300 hover:border-zinc-700">
        <p className="text-sm text-zinc-500">Gesamtfortschritt</p>
        <p className="mt-1 text-3xl font-bold tabular-nums text-emerald-400">
          {stats.totalPercentage !== null ? `${stats.totalPercentage}%` : '—'}
        </p>
        <p className="text-sm tabular-nums text-zinc-500">
          {stats.totalCorrect}/{stats.totalAttempted} richtig
        </p>
      </div>

      <div className="w-[32rem] rounded-xl border border-zinc-800 bg-zinc-900 p-5 transition-shadow duration-300 hover:border-zinc-700">
        <h2 className="mb-3 text-sm font-semibold text-zinc-400">Testabschnitte</h2>
        <ul className="space-y-2">
          {stats.sections.map((s) => {
            const mastery = masteryLevels[s.key] ?? 0
            return (
              <li key={s.key} className="flex items-center justify-between gap-4 text-sm">
                <span className="w-48 truncate text-zinc-400">{s.label}</span>
                <span className="shrink-0 tabular-nums text-zinc-500">
                  {s.attempted > 0 ? (
                    <>
                      <span className="text-emerald-400">{s.correct}</span>
                      <span className="text-zinc-600">/{s.attempted}</span>
                      <span className="ml-1 text-zinc-500">({s.percentage}%)</span>
                    </>
                  ) : (
                    <span className="text-zinc-600">—</span>
                  )}
                </span>
                <span className="shrink-0 w-12 text-right text-xs text-zinc-500">
                  {mastery > 0 ? `${mastery}%` : '—'}
                </span>
                <span className="shrink-0 w-16 text-right text-xs text-zinc-600">
                  Set {s.currentSet + 1}/{s.totalSets}
                </span>
              </li>
            )
          })}
        </ul>
      </div>

      <div className="flex gap-4">
        <button
          onClick={() => navigate('/setup')}
          className="animate-breathe rounded-xl bg-emerald-600 px-10 py-4 text-lg font-semibold text-white transition-all duration-200 hover:scale-[1.05] hover:bg-emerald-500 active:scale-95"
        >
          Test starten
        </button>
        <button
          onClick={() => navigate('/settings')}
          className="rounded-xl bg-zinc-800 px-6 py-4 text-lg font-semibold text-zinc-300 transition-all duration-200 hover:scale-[1.03] hover:bg-zinc-700 active:scale-95"
        >
          Einstellungen
        </button>
      </div>

      <button
        onClick={handleLogout}
        className="text-sm text-zinc-600 transition-colors duration-200 hover:text-zinc-400"
      >
        Abmelden
      </button>
    </div>
  )
}
