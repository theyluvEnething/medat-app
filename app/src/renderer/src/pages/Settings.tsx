import { useState } from 'react'
import type { Question, SectionKey } from '../types'
import { SECTION_ORDER } from '../types'
import { ensureUserProgress, saveUserProgress, resetSectionProgress } from '../services/storage'

interface SettingsProps {
  username: string
  questions: Record<string, Question[]>
  onBack: () => void
}

export function Settings({ username, questions, onBack }: SettingsProps) {
  const progress = ensureUserProgress(username)
  const [sections, setSections] = useState(progress.sections)

  const updateSetIndex = (sectionKey: SectionKey, value: number) => {
    const updated = {
      ...sections,
      [sectionKey]: { ...sections[sectionKey]!, currentSetIndex: value },
    }
    setSections(updated)
    saveUserProgress(username, { sections: updated })
  }

  const resetSection = (sectionKey: SectionKey) => {
    resetSectionProgress(username, sectionKey)
    const fresh = { currentSetIndex: 0, completed: [], wrongIds: [] }
    setSections((prev) => ({ ...prev, [sectionKey]: fresh }))
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-2xl flex-col gap-6 px-6 py-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Einstellungen</h1>
        <button
          onClick={onBack}
          className="rounded-lg bg-zinc-800 px-4 py-2 text-sm text-zinc-300 hover:bg-zinc-700"
        >
          Zurück
        </button>
      </div>

      <p className="text-sm text-zinc-500">
        Wähle das Set, mit dem du fortfahren möchtest. Jedes Set enthält eine feste Anzahl von Fragen.
      </p>

      <div className="flex flex-col gap-4">
        {SECTION_ORDER.map((sec) => {
          const sp = sections[sec.key]!
          const pool = questions[sec.key] ?? []
          const setSize = sec.count
          const totalSets = setSize > 0 ? Math.ceil(pool.length / setSize) : 1
          const startId = sp.currentSetIndex * setSize + 1
          const endId = Math.min(startId + setSize - 1, pool.length)

          return (
            <div
              key={sec.key}
              className="rounded-lg border border-zinc-800 bg-zinc-900 p-4"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-zinc-200">{sec.label}</span>
                <button
                  onClick={() => resetSection(sec.key)}
                  className="text-xs text-red-400 hover:text-red-300"
                >
                  Zurücksetzen
                </button>
              </div>
              <div className="mt-2 flex items-center gap-4 text-sm text-zinc-400">
                <span>Set:</span>
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
                  className="w-20 rounded border border-zinc-700 bg-zinc-950 px-2 py-1 text-center text-zinc-200"
                />
                <span className="text-zinc-600">
                  von {totalSets - 1} (Fragen {startId}–{endId})
                </span>
              </div>
              <div className="mt-1 flex gap-4 text-xs text-zinc-500">
                <span className="text-emerald-500">Richtig: {sp.completed.length}</span>
                <span className="text-red-400">Falsch: {sp.wrongIds.length}</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
