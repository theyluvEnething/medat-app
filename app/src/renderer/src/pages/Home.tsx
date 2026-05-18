interface HomeProps {
  onStart: () => void
}

export function Home({ onStart }: HomeProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8">
      <div className="text-center">
        <h1 className="text-5xl font-bold tracking-tight">MedAT KFF Trainer</h1>
        <p className="mt-3 text-lg text-zinc-500">
          Realistisches Zeitmanagement für den kognitiven Teil
        </p>
      </div>

      <div className="w-96 rounded-xl border border-zinc-800 bg-zinc-900 p-6">
        <h2 className="mb-3 text-sm font-semibold text-zinc-400">Testabschnitte</h2>
        <ul className="space-y-2 text-sm text-zinc-400">
          <li className="flex justify-between">
            <span>Figuren zusammensetzen</span>
            <span className="text-zinc-500">20 min · 15 Fragen</span>
          </li>
          <li className="flex justify-between">
            <span>Ausweise Merken</span>
            <span className="text-zinc-500">8 min · 25 Items</span>
          </li>
          <li className="flex justify-between">
            <span>Zahlenfolgen</span>
            <span className="text-zinc-500">15 min · 10 Fragen</span>
          </li>
          <li className="flex justify-between">
            <span>Wortflüssigkeit</span>
            <span className="text-zinc-500">20 min · 15 Fragen</span>
          </li>
          <li className="flex justify-between">
            <span>Ausweise Merken — Abfrage</span>
            <span className="text-zinc-500">25 Fragen</span>
          </li>
          <li className="flex justify-between">
            <span>Implikationen erkennen</span>
            <span className="text-zinc-500">10 min · 10 Fragen</span>
          </li>
        </ul>
      </div>

      <button
        onClick={onStart}
        className="rounded-xl bg-emerald-600 px-10 py-4 text-lg font-semibold text-white transition-colors hover:bg-emerald-500 active:bg-emerald-700"
      >
        Test starten
      </button>
    </div>
  )
}
