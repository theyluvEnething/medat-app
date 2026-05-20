import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/useAppStore'

export function Login() {
  const navigate = useNavigate()
  const username = useAppStore((s) => s.user.username)
  const login = useAppStore((s) => s.login)
  const [name, setName] = useState('')

  useEffect(() => {
    if (username) setName(username)
  }, [username])

  const submit = () => {
    const trimmed = name.trim()
    if (trimmed) {
      login(trimmed)
      navigate('/home')
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8">
      <div className="text-center">
        <h1 className="text-5xl font-bold tracking-tight">MedAT KFF Trainer</h1>
        <p className="mt-3 text-lg text-zinc-500">
          Realistisches Zeitmanagement für den kognitiven Teil
        </p>
      </div>

      <div className="w-[28rem] rounded-xl border border-zinc-800 bg-zinc-900 p-6 transition-shadow duration-300 hover:border-zinc-700">
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
          className="w-full rounded-lg border border-zinc-700 bg-zinc-950 px-4 py-3 text-lg text-zinc-100 placeholder-zinc-600 outline-none transition-all duration-200 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/30"
        />
      </div>

      <button
        onClick={submit}
        disabled={name.trim().length === 0}
        className="rounded-xl bg-emerald-600 px-10 py-4 text-lg font-semibold text-white transition-all duration-200 hover:scale-[1.05] hover:bg-emerald-500 active:scale-95 disabled:opacity-40 disabled:hover:scale-100"
      >
        Starten
      </button>
    </div>
  )
}
