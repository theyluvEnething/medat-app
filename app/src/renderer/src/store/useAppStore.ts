import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { SectionKey, SectionProgress, Question } from '../types'
import { SECTION_ORDER } from '../types'
import { upsertUserScore } from '../services/supabase'

// ── Session-record types (appended to types.ts later) ──

interface SectionResult {
  sectionKey: SectionKey
  correct: number
  total: number
  timeSpent: number
}

interface SessionRecord {
  date: string
  type: 'full' | SectionKey
  score: { correct: number; total: number }
  sectionBreakdown: SectionResult[]
  answers: Record<string, string>
  duration: number
}

// ── Store shape ──

interface AppState {
  user: { username: string | null }
  progress: Record<SectionKey, SectionProgress>
  session: {
    type: 'full' | SectionKey | null
    currentSectionIndex: number
    currentQuestionIndex: number
    answers: Record<string, string>
    startTime: number | null
    duration: number
    isActive: boolean
  }
  sessionHistory: SessionRecord[]
  gamification: {
    dailyStreak: number
    lastActiveDate: string | null
    masteryLevels: Record<SectionKey, number>
    wrongCounts: Record<string, number>
  }

  // ── User actions ──
  login: (username: string) => void
  logout: () => void

  // ── Session actions ──
  startSession: (type: 'full' | SectionKey) => void
  submitAnswer: (questionKey: string, answer: string) => void
  nextQuestion: () => void
  prevQuestion: () => void
  setQuestionIndex: (index: number) => void
  setSectionIndex: (index: number) => void
  completeSession: (questions?: Record<string, Question[]>, answers?: Record<string, string>) => void
  resetSession: () => void

  // ── Progress actions ──
  updateProgress: (sectionKey: SectionKey, progress: SectionProgress) => void
  resetSectionProgress: (sectionKey: SectionKey) => void
  resetAllProgress: () => void

  // ── Gamification actions ──
  updateDailyStreak: () => void
  recalculateMastery: (questions: Record<string, Question[]>) => void
  recordWrongAnswer: (sectionKey: SectionKey, questionId: number) => void
}

// ── Helpers ──

function emptyProgress(): SectionProgress {
  return { currentSetIndex: 0, completed: [], wrongIds: [] }
}

function emptyGamification(): AppState['gamification'] {
  const masteryLevels: Record<string, number> = {}
  for (const sec of SECTION_ORDER) {
    masteryLevels[sec.key] = 0
  }
  return {
    dailyStreak: 0,
    lastActiveDate: null,
    masteryLevels: masteryLevels as Record<SectionKey, number>,
    wrongCounts: {},
  }
}

function todayStr(): string {
  return new Date().toISOString().slice(0, 10)
}

// ── Legacy migration ──

function migrateFromLegacy(): Partial<AppState> {
  const usersRaw = localStorage.getItem('medat_users')
  const lastUser = localStorage.getItem('medat_last_user')
  if (!usersRaw) return {}

  let progress: Record<SectionKey, SectionProgress> = {} as Record<SectionKey, SectionProgress>
  let username: string | null = null

  try {
    const users = JSON.parse(usersRaw) as Record<string, { sections: Record<string, SectionProgress> }>
    const last = lastUser ? JSON.parse(lastUser) : null
    username = typeof last === 'string' ? last : Object.keys(users)[0] ?? null

    if (username && users[username]) {
      const sections = users[username]!.sections
      for (const sec of SECTION_ORDER) {
        if (sections[sec.key]) {
          progress[sec.key] = sections[sec.key]!
        } else {
          progress[sec.key] = emptyProgress()
        }
      }
    }
  } catch {
    // corrupted data — start fresh
  }

  // Delete old keys after migration
  localStorage.removeItem('medat_users')
  localStorage.removeItem('medat_last_user')

  return {
    user: { username },
    progress: Object.keys(progress).length > 0 ? progress : undefined,
  }
}

// ── Store ──

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // ── Initial state ──
      user: { username: null },
      progress: {} as Record<SectionKey, SectionProgress>,
      session: {
        type: null,
        currentSectionIndex: 0,
        currentQuestionIndex: 0,
        answers: {},
        startTime: null,
        duration: 0,
        isActive: false,
      },
      sessionHistory: [],
      gamification: emptyGamification(),

      // ── User ──
      login: (username) => {
        set({ user: { username } })
        const progress = get().progress
        for (const sec of SECTION_ORDER) {
          if (!progress[sec.key]) {
            progress[sec.key] = emptyProgress()
          }
        }
        set({ progress: { ...progress } })
        get().updateDailyStreak()
      },

      logout: () => {
        set({
          user: { username: null },
          session: {
            type: null,
            currentSectionIndex: 0,
            currentQuestionIndex: 0,
            answers: {},
            startTime: null,
            duration: 0,
            isActive: false,
          },
        })
      },

      // ── Session ──
      startSession: (type) => {
        set({
          session: {
            type,
            currentSectionIndex: 0,
            currentQuestionIndex: 0,
            answers: {},
            startTime: Date.now(),
            duration: 0,
            isActive: true,
          },
        })
      },

      submitAnswer: (questionKey, answer) => {
        set((s) => ({
          session: {
            ...s.session,
            answers: { ...s.session.answers, [questionKey]: answer },
          },
        }))
      },

      nextQuestion: () => {
        set((s) => ({
          session: {
            ...s.session,
            currentQuestionIndex: s.session.currentQuestionIndex + 1,
          },
        }))
      },

      prevQuestion: () => {
        set((s) => ({
          session: {
            ...s.session,
            currentQuestionIndex: Math.max(0, s.session.currentQuestionIndex - 1),
          },
        }))
      },

      setQuestionIndex: (index) => {
        set((s) => ({
          session: { ...s.session, currentQuestionIndex: index },
        }))
      },

      setSectionIndex: (index) => {
        set((s) => ({
          session: { ...s.session, currentSectionIndex: index, currentQuestionIndex: 0 },
        }))
      },

      completeSession: (questions, answers) => {
        const { session, sessionHistory, progress, user } = get()
        if (!session.type) return

        const duration = Math.round(((Date.now() - (session.startTime ?? Date.now())) / 1000))
        const resolvedAnswers = answers ?? session.answers

        // Compute per-section breakdown from session answers
        const sectionBreakdown: SectionResult[] = []
        let sessionCorrect = 0
        let sessionTotal = 0

        if (questions) {
          const sectionKeys = session.type === 'full'
            ? SECTION_ORDER.map((s) => s.key)
            : [session.type]

          for (const sectionKey of sectionKeys) {
            const pool = questions[sectionKey] ?? []
            let correct = 0
            let total = 0
            for (const q of pool) {
              const key = `${sectionKey}-${q.id}`
              const choice = resolvedAnswers[key]
              if (choice === undefined) continue
              total++
              if (choice === q.answer) correct++
            }
            sessionCorrect += correct
            sessionTotal += total
            sectionBreakdown.push({
              sectionKey,
              correct,
              total,
              timeSpent: 0,
            })
          }
        }

        const record: SessionRecord = {
          date: new Date().toISOString(),
          type: session.type,
          score: { correct: sessionCorrect, total: sessionTotal },
          sectionBreakdown,
          answers: resolvedAnswers,
          duration,
        }

        // Compute cumulative stats from progress for leaderboard
        let cumulativeCorrect = 0
        let cumulativeSolved = 0
        for (const sec of SECTION_ORDER) {
          const sp = progress[sec.key]
          if (sp) {
            cumulativeCorrect += sp.completed.length
            cumulativeSolved += sp.completed.length + sp.wrongIds.length
          }
        }

        // Post to leaderboard (fire-and-forget)
        if (user.username) {
          upsertUserScore(user.username, cumulativeCorrect, cumulativeSolved, cumulativeCorrect).catch(() => {
            // leaderboard posting is non-critical
          })
        }

        set({
          sessionHistory: [...sessionHistory, record],
          session: {
            type: null,
            currentSectionIndex: 0,
            currentQuestionIndex: 0,
            answers: {},
            startTime: null,
            duration: 0,
            isActive: false,
          },
        })
      },

      resetSession: () => {
        set({
          session: {
            type: null,
            currentSectionIndex: 0,
            currentQuestionIndex: 0,
            answers: {},
            startTime: null,
            duration: 0,
            isActive: false,
          },
        })
      },

      // ── Progress ──
      updateProgress: (sectionKey, sectionProgress) => {
        set((s) => ({
          progress: { ...s.progress, [sectionKey]: sectionProgress },
        }))
      },

      resetSectionProgress: (sectionKey) => {
        set((s) => ({
          progress: { ...s.progress, [sectionKey]: emptyProgress() },
        }))
      },

      resetAllProgress: () => {
        const fresh: Record<string, SectionProgress> = {}
        for (const sec of SECTION_ORDER) {
          fresh[sec.key] = emptyProgress()
        }
        set({
          progress: fresh as Record<SectionKey, SectionProgress>,
          gamification: emptyGamification(),
          sessionHistory: [],
        })
      },

      // ── Gamification ──
      updateDailyStreak: () => {
        const today = todayStr()
        const { lastActiveDate, dailyStreak } = get().gamification
        if (lastActiveDate === today) return

        const yesterday = new Date()
        yesterday.setDate(yesterday.getDate() - 1)
        const yesterdayStr = yesterday.toISOString().slice(0, 10)

        const newStreak = lastActiveDate === yesterdayStr ? dailyStreak + 1 : 1
        set({
          gamification: {
            ...get().gamification,
            dailyStreak: newStreak,
            lastActiveDate: today,
          },
        })
      },

      recalculateMastery: (questions) => {
        const { progress } = get()
        const masteryLevels: Record<string, number> = {}
        for (const sec of SECTION_ORDER) {
          const sp = progress[sec.key]
          const pool = questions[sec.key] ?? []
          if (!sp || pool.length === 0) {
            masteryLevels[sec.key] = 0
            continue
          }
          const attempted = sp.completed.length + sp.wrongIds.length
          if (attempted === 0) {
            masteryLevels[sec.key] = 0
            continue
          }
          masteryLevels[sec.key] = Math.round((sp.completed.length / attempted) * 100)
        }
        set({
          gamification: {
            ...get().gamification,
            masteryLevels: masteryLevels as Record<SectionKey, number>,
          },
        })
      },

      recordWrongAnswer: (sectionKey: SectionKey, questionId: number) => {
        const key = `${sectionKey}-${questionId}`
        set((s: AppState) => ({
          gamification: {
            ...s.gamification,
            wrongCounts: {
              ...s.gamification.wrongCounts,
              [key]: (s.gamification.wrongCounts[key] ?? 0) + 1,
            },
          },
        }))
      },
    }),
    {
      name: 'medat-app-store',
      version: 1,
      partialize: (state: AppState) => {
        const { session, ...rest } = state
        return {
          ...rest,
          session: {
            type: null,
            currentSectionIndex: 0,
            currentQuestionIndex: 0,
            answers: {},
            startTime: null,
            duration: 0,
            isActive: false,
          },
        }
      },
      migrate: (persisted: unknown, version: number) => {
        if (version === 0) {
          const legacy = migrateFromLegacy()
          return { ...(persisted as object), ...legacy }
        }
        return persisted as AppState
      },
    },
  ),
)
