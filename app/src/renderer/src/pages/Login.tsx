import { useEffect, useState } from 'react'
import { loadLastUsername } from '../services/storage'

interface LoginProps {
  onLogin: (username: string) => void
}

export function Login({ onLogin }: LoginProps) {
  const [name, setName] = useState('')

  useEffect(() => {
    const last = loadLastUsername()
    if (last) setName(last)
  }, [])

  const submit = () => {
    const trimmed = name.trim()
    if (trimmed) onLogin(trimmed)
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8">
      <div className="text-center">
        <h1 className="text-5xl font-bold tracking-tight">MedAT KFF Trainer</h1>
        <p className="mt-3 text-lg text-zinc-500">
          Realistisches Zeitmanagement für den kognitiven Teil
        </p>
      </div>

      <div className="w-96 rounded-xl border border-zinc-800 bg-zinc-900 p-6">
        <label htmlFor="username" className="mb-2 block text-sm text-zinc-400">
          Benutzername
        </label>
        <input
          id="username"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
          placeholder="Dein Name"
          autoFocus
          className="w-full rounded-lg border border-zinc-700 bg-zinc-950 px-4 py-3 text-lg text-zinc-100 placeholder-zinc-600 outline-none focus:border-emerald-500"
        />
      </div>

      <button
        onClick={submit}
        disabled={name.trim().length === 0}
        className="rounded-xl bg-emerald-600 px-10 py-4 text-lg font-semibold text-white transition-colors hover:bg-emerald-500 active:bg-emerald-700 disabled:opacity-40"
      >
        Starten
      </button>
    </div>
  )
}
