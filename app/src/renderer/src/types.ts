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
}

export interface AusweiseItem {
  id: number
  content: string
  fields: Record<string, string>
}

export interface QuestionSet {
  figuren: Question[]
  zahlenfolgen: Question[]
  wortfluessigkeit: Question[]
  implikationen: Question[]
  ausweise: AusweiseItem[]
  ausweise_recall: Question[]
}

export const SECTION_ORDER: SectionConfig[] = [
  { key: 'figuren', label: 'Figuren zusammensetzen', timeMin: 20, count: 15 },
  { key: 'ausweise_memorize', label: 'Ausweise Merken — Einprägen', timeMin: 8, count: 25 },
  { key: 'zahlenfolgen', label: 'Zahlenfolgen', timeMin: 15, count: 10 },
  { key: 'wortfluessigkeit', label: 'Wortflüssigkeit', timeMin: 20, count: 15 },
  { key: 'ausweise_recall', label: 'Ausweise Merken — Abfrage', timeMin: 0, count: 25 },
  { key: 'implikationen', label: 'Implikationen erkennen', timeMin: 10, count: 10 },
]
