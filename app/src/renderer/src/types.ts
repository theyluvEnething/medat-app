export type SectionKey =
  | 'figuren'
  | 'ausweise_memorize'
  | 'zahlenfolgen'
  | 'wortfluessigkeit'
  | 'ausweise_recall'
  | 'implikationen'

export interface SectionConfig {
  key: SectionKey
  label: string
  timeMin: number
  count: number
}

export interface Question {
  section: string
  id: number
  answer: string
  content: string
  image?: string
}

export interface SectionProgress {
  currentSetIndex: number
  completed: number[]
  wrongIds: number[]
}

export interface UserProgress {
  sections: Record<SectionKey, SectionProgress>
}

export interface SectionResult {
  sectionKey: SectionKey
  correct: number
  total: number
  timeSpent: number
}

export interface SessionRecord {
  date: string
  type: 'full' | SectionKey
  score: { correct: number; total: number }
  sectionBreakdown: SectionResult[]
  answers: Record<string, string>
  duration: number
}

export const SECTION_ORDER: SectionConfig[] = [
  { key: 'figuren', label: 'Figuren zusammensetzen', timeMin: 20, count: 15 },
  { key: 'ausweise_memorize', label: 'Ausweise Merken — Einprägen', timeMin: 8, count: 8 },
  { key: 'wortfluessigkeit', label: 'Wortflüssigkeit', timeMin: 20, count: 15 },
  { key: 'zahlenfolgen', label: 'Zahlenfolgen', timeMin: 15, count: 10 },
  { key: 'ausweise_recall', label: 'Ausweise Merken — Abfrage', timeMin: 8, count: 25 },
  { key: 'implikationen', label: 'Implikationen erkennen', timeMin: 10, count: 10 },
]
