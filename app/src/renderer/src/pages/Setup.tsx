import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/useAppStore'
import { SECTION_ORDER } from '../types'
import type { SectionKey } from '../types'

const SECTION_EMOJI: Record<SectionKey, string> = {
  figuren: '\u{1F9E9}',
  ausweise_memorize: '\u{1FAAA}',
  wortfluessigkeit: '\u{1F4DD}',
  zahlenfolgen: '\u{1F522}',
  ausweise_recall: '\u{1F9E0}',
  implikationen: '\u{1F9E9}',
}

const SECTION_COLORS: Record<SectionKey, string> = {
  figuren: 'border-l-emerald-500',
  ausweise_memorize: 'border-l-amber-500',
  wortfluessigkeit: 'border-l-blue-500',
  zahlenfolgen: 'border-l-purple-500',
  ausweise_recall: 'border-l-rose-500',
  implikationen: 'border-l-cyan-500',
}

function masteryLabel(pct: number): { text: string; color: string } {
  if (pct >= 80) return { text: 'Gold', color: 'text-amber-400' }
  if (pct >= 50) return { text: 'Silber', color: 'text-zinc-300' }
  if (pct > 0) return { text: 'Bronze', color: 'text-amber-600' }
  return { text: 'Neu', color: 'text-zinc-500' }
}

export function Setup() {
  const navigate = useNavigate()
  const masteryLevels = useAppStore((s) => s.gamification.masteryLevels)
  const dailyStreak = useAppStore((s) => s.gamification.dailyStreak)
  const updateDailyStreak = useAppStore((s) => s.updateDailyStreak)

  useEffect(() => {
    updateDailyStreak()
  }, [updateDailyStreak])

  return (
    <div className="mx-auto flex min-h-screen max-w-5xl flex-col gap-8 px-6 py-10">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-zinc-100">Was möchtest du üben?</h1>
        <p className="mt-2 text-zinc-500">
          Wähle eine komplette Simulation oder eine einzelne Kategorie
        </p>
        {dailyStreak > 0 && (
          <p className="mt-2 inline-flex items-center gap-1.5 rounded-full bg-amber-950/40 border border-amber-500/30 px-3 py-1 text-sm text-amber-300">
            {'\u{1F525}'} {dailyStreak}-Tage-Streak
          </p>
        )}
      </div>

      {/* Full KFF Simulation */}
      <button
        onClick={() => navigate('/session/full')}
        className="w-full rounded-2xl border-2 border-emerald-500/40 bg-gradient-to-br from-emerald-950/40 to-zinc-900 p-6 text-left transition-all duration-200 hover:scale-[1.01] hover:border-emerald-400/60 hover:shadow-lg hover:shadow-emerald-500/10 active:scale-[0.99]"
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xl font-bold text-emerald-400">
              Komplette KFF Simulation
            </p>
            <p className="mt-1 text-sm text-zinc-400">
              Alle 6 Abschnitte nacheinander mit realistischer Zeitbegrenzung
            </p>
          </div>
          <span className="text-2xl">{'\u{1F3AF}'}</span>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {SECTION_ORDER.map((sec) => (
            <span
              key={sec.key}
              className="rounded-full bg-zinc-800 px-2.5 py-0.5 text-xs text-zinc-400"
            >
              {sec.label} ({sec.timeMin} min)
            </span>
          ))}
        </div>
      </button>

      {/* Category grid */}
      <div>
        <h2 className="mb-4 text-lg font-semibold text-zinc-300">Einzelne Kategorien</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {SECTION_ORDER.map((sec) => {
            const pct = masteryLevels[sec.key] ?? 0
            const mastery = masteryLabel(pct)
            return (
              <button
                key={sec.key}
                onClick={() => navigate(`/session/${sec.key}`)}
                className={`rounded-xl border-l-4 bg-zinc-900 p-5 text-left transition-all duration-200 hover:scale-[1.02] hover:bg-zinc-800 hover:shadow-lg active:scale-[0.98] ${SECTION_COLORS[sec.key]}`}
              >
                <div className="flex items-start justify-between">
                  <span className="text-2xl">{SECTION_EMOJI[sec.key]}</span>
                  <span className={`text-xs font-semibold ${mastery.color}`}>
                    {pct > 0 ? `${pct}%` : mastery.text}
                  </span>
                </div>
                <p className="mt-2 font-semibold text-zinc-200">{sec.label}</p>
                <p className="mt-1 text-xs text-zinc-500">
                  {sec.timeMin} min · {sec.count} Fragen pro Set
                </p>
              </button>
            )
          })}
        </div>
      </div>

      <button
        onClick={() => navigate('/home')}
        className="mx-auto rounded-lg bg-zinc-800 px-6 py-2.5 text-sm text-zinc-400 transition-all duration-200 hover:bg-zinc-700 hover:text-zinc-200 active:scale-95"
      >
        Zurück
      </button>
    </div>
  )
}
