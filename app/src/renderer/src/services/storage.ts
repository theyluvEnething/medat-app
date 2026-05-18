import type { SectionKey, SectionProgress, UserProgress } from '../types'
import { SECTION_ORDER } from '../types'

const KEY_USERS = 'medat_users'
const KEY_LAST_USER = 'medat_last_user'

function loadJson<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    if (raw === null) return fallback
    return JSON.parse(raw) as T
  } catch {
    return fallback
  }
}

function saveJson(key: string, value: unknown): void {
  localStorage.setItem(key, JSON.stringify(value))
}

export function loadUsers(): Record<string, UserProgress> {
  return loadJson<Record<string, UserProgress>>(KEY_USERS, {})
}

export function saveUsers(users: Record<string, UserProgress>): void {
  saveJson(KEY_USERS, users)
}

export function loadLastUsername(): string | null {
  return loadJson<string | null>(KEY_LAST_USER, null)
}

export function saveLastUsername(name: string): void {
  saveJson(KEY_LAST_USER, name)
}

export function getUserProgress(username: string): UserProgress | null {
  const users = loadUsers()
  return users[username] ?? null
}

export function saveUserProgress(username: string, progress: UserProgress): void {
  const users = loadUsers()
  users[username] = progress
  saveUsers(users)
}

function emptySectionProgress(): SectionProgress {
  return { currentSetIndex: 0, completed: [], wrongIds: [] }
}

export function ensureUserProgress(username: string): UserProgress {
  let progress = getUserProgress(username)
  if (!progress) {
    const sections: Record<string, SectionProgress> = {}
    for (const sec of SECTION_ORDER) {
      sections[sec.key] = emptySectionProgress()
    }
    progress = { sections: sections as Record<SectionKey, SectionProgress> }
    saveUserProgress(username, progress)
  }
  return progress
}

export function resetSectionProgress(username: string, sectionKey: SectionKey): void {
  const progress = ensureUserProgress(username)
  progress.sections[sectionKey] = emptySectionProgress()
  saveUserProgress(username, progress)
}

export interface SectionStats {
  key: SectionKey
  label: string
  setSize: number
  totalSets: number
  currentSet: number
  correct: number
  attempted: number
  percentage: number | null
}

export function getSectionStats(
  username: string,
  questions: Record<string, { id: number }[]>,
): {
  sections: SectionStats[]
  totalCorrect: number
  totalAttempted: number
  totalPercentage: number | null
} {
  const progress = ensureUserProgress(username)
  const sections: SectionStats[] = SECTION_ORDER.map((sec) => {
    const sp = progress.sections[sec.key]
    const pool = questions[sec.key] ?? []
    const setSize = sec.count
    const totalSets = setSize > 0 ? Math.ceil(pool.length / setSize) : 1
    const correct = sp.completed.length
    const attempted = correct + sp.wrongIds.length
    const percentage = attempted > 0 ? Math.round((correct / attempted) * 100) : null
    return {
      key: sec.key,
      label: sec.label,
      setSize,
      totalSets,
      currentSet: sp.currentSetIndex,
      correct,
      attempted,
      percentage,
    }
  })

  const totalCorrect = sections.reduce((s, x) => s + x.correct, 0)
  const totalAttempted = sections.reduce((s, x) => s + x.attempted, 0)
  const totalPercentage =
    totalAttempted > 0 ? Math.round((totalCorrect / totalAttempted) * 100) : null

  return { sections, totalCorrect, totalAttempted, totalPercentage }
}
