import type { Question } from '../types'
import { getSectionStats } from '../services/storage'

interface HomeProps {
  username: string
  questions: Record<string, Question[]>
  onStart: () => void
  onSettings: () => void
  onLogout: () => void
}

export function Home({ username, questions, onStart, onSettings, onLogout }: HomeProps) {
  const stats = getSectionStats(username, questions)

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 py-8">
      <div className="text-center">
        <h1 className="text-5xl font-bold tracking-tight">MedAT KFF Trainer</h1>
        <p className="mt-3 text-lg text-zinc-500">
          Realistisches Zeitmanagement für den kognitiven Teil
        </p>
        <p className="mt-1 text-sm text-emerald-500">Angemeldet als: {username}</p>
      </div>

      <div className="w-[28rem] rounded-xl border border-zinc-800 bg-zinc-900 p-5 text-center transition-shadow duration-300 hover:border-zinc-700">
        <p className="text-sm text-zinc-500">Gesamtfortschritt</p>
        <p className="mt-1 text-3xl font-bold tabular-nums text-emerald-400">
          {stats.totalPercentage !== null ? `${stats.totalPercentage}%` : '—'}
        </p>
        <p className="text-sm tabular-nums text-zinc-500">
          {stats.totalCorrect}/{stats.totalAttempted} richtig
        </p>
      </div>

      <div className="w-[28rem] rounded-xl border border-zinc-800 bg-zinc-900 p-5 transition-shadow duration-300 hover:border-zinc-700">
        <h2 className="mb-3 text-sm font-semibold text-zinc-400">Testabschnitte</h2>
        <ul className="space-y-2">
          {stats.sections.map((s) => (
            <li
              key={s.key}
              className="flex items-center justify-between gap-4 text-sm"
            >
              <span className="text-zinc-400 truncate">{s.label}</span>
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
                <span className="ml-2 text-zinc-600">
                  Set {s.currentSet + 1}/{s.totalSets}
                </span>
              </span>
            </li>
          ))}
        </ul>
      </div>

      <div className="flex gap-4">
        <button
          onClick={onStart}
          className="animate-breathe rounded-xl bg-emerald-600 px-10 py-4 text-lg font-semibold text-white transition-all duration-200 hover:scale-[1.05] hover:bg-emerald-500 active:scale-95"
        >
          Test starten
        </button>
        <button
          onClick={onSettings}
          className="rounded-xl bg-zinc-800 px-6 py-4 text-lg font-semibold text-zinc-300 transition-all duration-200 hover:scale-[1.03] hover:bg-zinc-700 active:scale-95"
        >
          Einstellungen
        </button>
      </div>

      <button
        onClick={onLogout}
        className="text-sm text-zinc-600 transition-colors duration-200 hover:text-zinc-400"
      >
        Abmelden
      </button>
    </div>
  )
}
