import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { LeaderboardEntry } from '../services/supabase'
import { fetchLeaderboard } from '../services/supabase'

function rankEmoji(rank: number): string {
  if (rank === 1) return '\u{1F947}'
  if (rank === 2) return '\u{1F948}'
  if (rank === 3) return '\u{1F949}'
  return `#${rank}`
}

export function Leaderboard() {
  const navigate = useNavigate()
  const [entries, setEntries] = useState<LeaderboardEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchLeaderboard()
      setEntries(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fehler beim Laden')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    const interval = setInterval(load, 30000)
    return () => clearInterval(interval)
  }, [])

  const topThree = entries.slice(0, 3)
  const rest = entries.slice(3)

  return (
    <div className="mx-auto flex min-h-screen max-w-4xl flex-col gap-6 px-6 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-zinc-100">Bestenliste</h1>
        <button
          onClick={() => navigate('/home')}
          className="rounded-lg bg-zinc-800 px-4 py-2 text-sm text-zinc-300 transition-all duration-200 hover:scale-[1.03] hover:bg-zinc-700 active:scale-95"
        >
          Zurück
        </button>
      </div>

      {loading && entries.length === 0 && (
        <div className="flex items-center justify-center py-20">
          <p className="text-zinc-400">Lade Bestenliste...</p>
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-950/20 px-4 py-3 text-sm text-red-400">
          {error}
          <button onClick={load} className="ml-2 underline hover:text-red-300">
            Erneut versuchen
          </button>
        </div>
      )}

      {!loading && !error && entries.length === 0 && (
        <div className="flex items-center justify-center py-20">
          <p className="text-zinc-400">Noch keine Einträge vorhanden.</p>
        </div>
      )}

      {entries.length > 0 && (
        <>
          {/* Top 3 Podium */}
          <div className="grid grid-cols-3 gap-4">
            {topThree.map((entry, i) => {
              const rank = i + 1
              const isFirst = rank === 1
              const pct = entry.questions_solved > 0
                ? Math.round((entry.questions_correct / entry.questions_solved) * 100)
                : 0
              return (
                <div
                  key={entry.id}
                  className={`rounded-xl border p-5 text-center transition-all duration-200 hover:scale-[1.02] ${
                    isFirst
                      ? 'border-amber-400/40 bg-amber-950/20'
                      : rank === 2
                        ? 'border-zinc-400/30 bg-zinc-900'
                        : 'border-amber-700/30 bg-zinc-900'
                  }`}
                >
                  <p className="text-3xl">{rankEmoji(rank)}</p>
                  <p className="mt-2 font-semibold text-zinc-200">{entry.username}</p>
                  <p className="mt-1 text-2xl font-bold text-emerald-400">
                    {entry.total_score.toLocaleString()}
                  </p>
                  <p className="mt-1 text-xs text-zinc-500">
                    {entry.questions_solved} Fragen · {pct}% richtig
                  </p>
                </div>
              )
            })}
          </div>

          {/* Full Table */}
          <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900">
            <table className="w-full">
              <thead>
                <tr className="border-b border-zinc-800 text-left text-xs font-semibold uppercase text-zinc-500">
                  <th className="px-5 py-3">Rang</th>
                  <th className="px-5 py-3">Benutzer</th>
                  <th className="px-5 py-3 text-right">Punkte</th>
                  <th className="px-5 py-3 text-right">Gelöst</th>
                  <th className="px-5 py-3 text-right">Richtig %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {entries.map((entry, i) => {
                  const rank = i + 1
                  const pct = entry.questions_solved > 0
                    ? Math.round((entry.questions_correct / entry.questions_solved) * 100)
                    : 0
                  const pctColor =
                    pct >= 90
                      ? 'text-emerald-400'
                      : pct >= 70
                        ? 'text-emerald-300'
                        : pct >= 50
                          ? 'text-amber-400'
                          : 'text-red-400'

                  return (
                    <tr
                      key={entry.id}
                      className="transition-colors duration-150 hover:bg-zinc-800/50"
                    >
                      <td className="px-5 py-3 text-sm tabular-nums text-zinc-400">
                        {rank <= 3 ? rankEmoji(rank) : `#${rank}`}
                      </td>
                      <td className="px-5 py-3 text-sm font-medium text-zinc-200">
                        {entry.username}
                      </td>
                      <td className="px-5 py-3 text-right text-sm font-semibold tabular-nums text-emerald-400">
                        {entry.total_score.toLocaleString()}
                      </td>
                      <td className="px-5 py-3 text-right text-sm tabular-nums text-zinc-400">
                        {entry.questions_solved}
                      </td>
                      <td
                        className={`px-5 py-3 text-right text-sm font-medium tabular-nums ${pctColor}`}
                      >
                        {pct}%
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          <p className="text-center text-xs text-zinc-600">
            Aktualisiert sich automatisch alle 30 Sekunden
          </p>
        </>
      )}
    </div>
  )
}
