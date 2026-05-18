import type { SectionKey } from '../types'

interface HintBannerProps {
  sectionKey: SectionKey
}

const HINTS: Partial<Record<SectionKey, string>> = {
  figuren:
    '✗ Notizen VERBOTEN: Keine Notizen, Markierungen oder Kreise im Heft erlaubt. Auch das Drehen des Blatts ist verboten.',
  ausweise_memorize:
    '✗ Notizen VERBOTEN: In der Merkphase darfst du nichts aufschreiben und nichts in der Hand halten.',
}

export function HintBanner({ sectionKey }: HintBannerProps) {
  const text = HINTS[sectionKey]
  if (!text) return null

  return (
    <div className="animate-fade-in rounded-lg border border-amber-600/30 bg-amber-950/40 px-5 py-3 text-sm text-amber-200">
      {text}
    </div>
  )
}
