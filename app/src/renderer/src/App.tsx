import { useState } from 'react'
import type { Question, Screen } from './types'
import { Login } from './pages/Login'
import { Home } from './pages/Home'
import { Test } from './pages/Test'
import { Settings } from './pages/Settings'
import { ensureUserProgress, saveLastUsername } from './services/storage'

import questionsData from './assets/questions.json'

const questions = questionsData as Record<string, Question[]>

export function App() {
  const [screen, setScreen] = useState<Screen>('login')
  const [username, setUsername] = useState('')

  const handleLogin = (name: string) => {
    setUsername(name)
    saveLastUsername(name)
    ensureUserProgress(name)
    setScreen('home')
  }

  const handleLogout = () => {
    setUsername('')
    setScreen('login')
  }

  if (screen === 'login') {
    return <Login onLogin={handleLogin} />
  }

  if (screen === 'settings') {
    return (
      <Settings
        username={username}
        questions={questions}
        onBack={() => setScreen('home')}
      />
    )
  }

  if (screen === 'test') {
    return (
      <Test
        questions={questions}
        username={username}
        onExit={() => setScreen('home')}
      />
    )
  }

  return (
    <Home
      username={username}
      questions={questions}
      onStart={() => setScreen('test')}
      onSettings={() => setScreen('settings')}
      onLogout={handleLogout}
    />
  )
}
