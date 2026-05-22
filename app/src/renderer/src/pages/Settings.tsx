import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { SectionKey } from '../types'
import { SECTION_ORDER } from '../types'
import { useAppStore } from '../store/useAppStore'

import { questions } from '../data/questions'

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

export function Settings() {
  const navigate = useNavigate()
  const storeProgress = useAppStore((s) => s.progress)
  const updateProgress = useAppStore((s) => s.updateProgress)
  const resetSectionProgress = useAppStore((s) => s.resetSectionProgress)
  const resetAllProgress = useAppStore((s) => s.resetAllProgress)

  const [sections, setSections] = useState(storeProgress)

  const updateSetIndex = (sectionKey: SectionKey, value: number) => {
    const updated = {
      ...sections,
      [sectionKey]: { ...sections[sectionKey]!, currentSetIndex: value },
    }
    setSections(updated)
    updateProgress(sectionKey, updated[sectionKey]!)
  }

  const resetSection = (sectionKey: SectionKey) => {
    if (!window.confirm(`Fortschritt für diesen Abschnitt wirklich zurücksetzen?`)) return
    resetSectionProgress(sectionKey)
    const fresh = { currentSetIndex: 0, completed: [], wrongIds: [] }
    setSections((prev) => ({ ...prev, [sectionKey]: fresh }))
  }

  const handleResetAll = () => {
    if (window.confirm('Gesamten Fortschritt zurücksetzen? Diese Aktion kann nicht rückgängig gemacht werden.')) {
      resetAllProgress()
      setSections(useAppStore.getState().progress)
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-4xl flex-col gap-8 px-6 py-10">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-zinc-100">Einstellungen</h1>
          <p className="mt-1 text-sm text-zinc-500">
            Wähle das Fragen-Set für jeden Abschnitt
          </p>
        </div>
        <button
          onClick={() => navigate('/home')}
          className="rounded-lg bg-zinc-800 px-4 py-2 text-sm text-zinc-300 transition-all duration-200 hover:scale-[1.03] hover:bg-zinc-700 active:scale-95"
        >
          Zurück
        </button>
      </div>

      {/* Section Cards */}
      <div className="flex flex-col gap-4">
        {SECTION_ORDER.map((sec) => {
          const sp = sections[sec.key] ?? { currentSetIndex: 0, completed: [], wrongIds: [] }
          const pool = questions[sec.key] ?? []
          const setSize = sec.count
          const totalSets = setSize > 0 ? Math.ceil(pool.length / setSize) : 1
          const startId = sp.currentSetIndex * setSize + 1
          const endId = Math.min(startId + setSize - 1, pool.length)
          const attempted = sp.completed.length + sp.wrongIds.length
          const totalInSet = pool.length
          const setPct = totalInSet > 0 ? Math.round((attempted / totalInSet) * 100) : 0

          return (
            <div
              key={sec.key}
              className={`rounded-xl border-l-4 bg-zinc-900 p-5 transition-all duration-200 hover:bg-zinc-800/50 ${SECTION_COLORS[sec.key]}`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{SECTION_EMOJI[sec.key]}</span>
                  <div>
                    <h3 className="font-semibold text-zinc-200">{sec.label}</h3>
                    <p className="text-xs text-zinc-500">
                      {sec.timeMin} min · {pool.length} Fragen ({setSize} pro Set)
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => resetSection(sec.key)}
                  className="shrink-0 text-xs text-red-400/70 transition-colors duration-200 hover:text-red-400"
                >
                  Zurücksetzen
                </button>
              </div>

              {/* Progress bar */}
              <div className="mt-4">
                <div className="flex items-center justify-between text-xs text-zinc-500">
                  <span>Fortschritt</span>
                  <span>{attempted}/{totalInSet} Fragen ({setPct}%)</span>
                </div>
                <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-zinc-800">
                  <div
                    className="h-full rounded-full bg-emerald-500 transition-all duration-500"
                    style={{ width: `${setPct}%` }}
                  />
                </div>
              </div>

              {/* Set selector */}
              <div className="mt-4 flex items-center gap-3">
                <span className="text-xs font-medium text-zinc-500">Set:</span>
                <button
                  onClick={() =>
                    updateSetIndex(sec.key, sp.currentSetIndex > 0 ? sp.currentSetIndex - 1 : 0)
                  }
                  disabled={sp.currentSetIndex === 0}
                  className="rounded-lg bg-zinc-800 px-3 py-1.5 text-sm text-zinc-300 transition-all duration-200 hover:bg-zinc-700 disabled:opacity-30 disabled:hover:bg-zinc-800"
                >
                  −
                </button>
                <input
                  type="number"
                  min={0}
                  max={totalSets - 1}
                  value={sp.currentSetIndex}
                  onChange={(e) =>
                    updateSetIndex(
                      sec.key,
                      Math.max(0, Math.min(totalSets - 1, Number(e.target.value))),
                    )
                  }
                  className="w-16 rounded-lg border border-zinc-700 bg-zinc-950 px-2 py-1.5 text-center text-sm text-zinc-200 transition-all duration-200 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/30"
                />
                <button
                  onClick={() =>
                    updateSetIndex(
                      sec.key,
                      sp.currentSetIndex < totalSets - 1 ? sp.currentSetIndex + 1 : totalSets - 1,
                    )
                  }
                  disabled={sp.currentSetIndex >= totalSets - 1}
                  className="rounded-lg bg-zinc-800 px-3 py-1.5 text-sm text-zinc-300 transition-all duration-200 hover:bg-zinc-700 disabled:opacity-30 disabled:hover:bg-zinc-800"
                >
                  +
                </button>
                <span className="text-xs text-zinc-600">
                  von {totalSets - 1} · Fragen {startId}–{endId}
                </span>
              </div>

              {/* Stats */}
              <div className="mt-3 flex gap-6 text-xs">
                <span className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-emerald-500" />
                  <span className="text-zinc-400">Richtig:</span>
                  <span className="font-medium tabular-nums text-emerald-400">{sp.completed.length}</span>
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-red-500" />
                  <span className="text-zinc-400">Falsch:</span>
                  <span className="font-medium tabular-nums text-red-400">{sp.wrongIds.length}</span>
                </span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Danger Zone */}
      <div className="rounded-xl border border-red-500/20 bg-red-950/10 p-5">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h3 className="font-semibold text-red-400">Gefahrenzone</h3>
            <p className="text-xs text-zinc-500">
              Setzt alle Fortschritte, Meisterschaften und Statistiken zurück
            </p>
          </div>
          <button
            onClick={handleResetAll}
            className="shrink-0 rounded-lg border border-red-500/30 bg-red-950/20 px-5 py-2.5 text-sm font-medium text-red-400 transition-all duration-200 hover:scale-[1.03] hover:border-red-500/50 hover:bg-red-950/40 active:scale-95"
          >
            Alles zurücksetzen
          </button>
        </div>
      </div>
    </div>
  )
}
