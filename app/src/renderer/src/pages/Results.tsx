import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/useAppStore'
import { SECTION_ORDER } from '../types'
import type { SessionRecord, SectionKey } from '../types'

import questionsData from '../assets/questions.json'
const questions = questionsData as Record<string, { id: number; content: string; section: string; answer: string }[]>

function scoreColor(pct: number): string {
  if (pct >= 70) return 'text-emerald-400'
  if (pct >= 40) return 'text-amber-400'
  return 'text-red-400'
}

function sectionLabel(key: SectionKey): string {
  return SECTION_ORDER.find((s) => s.key === key)?.label ?? key
}

export function Results() {
  const navigate = useNavigate()
  const sessionHistory = useAppStore((s) => s.sessionHistory)
  const latest = sessionHistory[sessionHistory.length - 1] as SessionRecord | undefined

  if (!latest) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-6">
        <p className="text-zinc-400">Noch keine Sitzung abgeschlossen.</p>
        <button
          onClick={() => navigate('/setup')}
          className="rounded-xl bg-emerald-600 px-6 py-3 text-lg font-semibold text-white transition-all duration-200 hover:scale-[1.03] hover:bg-emerald-500 active:scale-95"
        >
          Test starten
        </button>
      </div>
    )
  }

  const pct = latest.score.total > 0
    ? Math.round((latest.score.correct / latest.score.total) * 100)
    : 0
  const minutes = Math.floor(latest.duration / 60)
  const seconds = latest.duration % 60

  // Build wrong-answer list
  const wrongAnswers: Array<{ section: SectionKey; questionId: string; content: string; chosen: string; correct: string }> = []
  for (const [key, choice] of Object.entries(latest.answers)) {
    if (key.startsWith('ausweise_memorize')) continue
    const parts = key.split('-')
    const sectionKey = parts[0] as SectionKey
    const idStr = parts[1]
    if (!sectionKey || !idStr) continue
    const pool = questions[sectionKey] ?? []
    const q = pool.find((q) => q.id === Number(idStr))
    if (q && choice !== q.answer && choice !== '__SKIPPED__') {
      wrongAnswers.push({
        section: sectionKey,
        questionId: idStr,
        content: q.content,
        chosen: choice,
        correct: q.answer,
      })
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-4xl flex-col gap-8 px-6 py-10">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-zinc-100">Ergebnis</h1>
        <p className="mt-1 text-zinc-500">
          {latest.type === 'full' ? 'Komplette KFF Simulation' : sectionLabel(latest.type)}
        </p>
      </div>

      {/* Overall score */}
      <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-8 text-center">
        <p className={`text-6xl font-bold tabular-nums ${scoreColor(pct)}`}>
          {latest.score.correct}/{latest.score.total}
        </p>
        <p className={`mt-2 text-3xl font-semibold ${scoreColor(pct)}`}>{pct}%</p>
        <p className="mt-2 text-sm text-zinc-500">
          Dauer: {minutes}:{seconds.toString().padStart(2, '0')}
        </p>
      </div>

      {/* Per-section breakdown */}
      {latest.sectionBreakdown.length > 0 && (
        <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
          <h2 className="mb-4 text-lg font-semibold text-zinc-300">Abschnitte</h2>
          <div className="space-y-3">
            {latest.sectionBreakdown.map((sb) => {
              const spct = sb.total > 0 ? Math.round((sb.correct / sb.total) * 100) : 0
              const mins = Math.floor(sb.timeSpent / 60)
              const secs = sb.timeSpent % 60
              return (
                <div key={sb.sectionKey} className="flex items-center gap-4">
                  <span className="w-40 shrink-0 text-sm text-zinc-400">
                    {sectionLabel(sb.sectionKey)}
                  </span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-zinc-800">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${spct >= 70 ? 'bg-emerald-500' : spct >= 40 ? 'bg-amber-500' : 'bg-red-500'}`}
                      style={{ width: `${spct}%` }}
                    />
                  </div>
                  <span className="w-20 shrink-0 text-right text-sm tabular-nums text-zinc-400">
                    {sb.correct}/{sb.total} ({spct}%)
                  </span>
                  <span className="w-20 shrink-0 text-right text-xs text-zinc-500">
                    {mins}:{secs.toString().padStart(2, '0')}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Wrong answers */}
      {wrongAnswers.length > 0 && (
        <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
          <h2 className="mb-4 text-lg font-semibold text-red-400">
            Falsche Antworten ({wrongAnswers.length})
          </h2>
          <div className="space-y-4">
            {wrongAnswers.map((wa, i) => (
              <div
                key={i}
                className="rounded-lg border border-red-500/20 bg-red-950/20 p-4"
              >
                <p className="text-xs text-zinc-500">{sectionLabel(wa.section)} · Frage #{wa.questionId}</p>
                <p className="mt-1 text-sm whitespace-pre-line text-zinc-300">{wa.content}</p>
                <p className="mt-2 text-sm">
                  <span className="text-red-400">Deine Antwort: {wa.chosen}</span>
                  <span className="mx-2 text-zinc-600">|</span>
                  <span className="text-emerald-400">Richtig: {wa.correct}</span>
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={() => navigate('/home')}
        className="mx-auto rounded-xl bg-emerald-600 px-8 py-3 text-lg font-semibold text-white transition-all duration-200 hover:scale-[1.03] hover:bg-emerald-500 active:scale-95"
      >
        Zurück zum Dashboard
      </button>
    </div>
  )
}
