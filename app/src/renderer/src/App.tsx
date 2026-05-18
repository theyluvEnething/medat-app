import { useState } from 'react'
import type { Question } from './types'
import { Home } from './pages/Home'
import { Test } from './pages/Test'

import questionsData from './assets/questions.json'

const questions = questionsData as Record<string, Question[]>

export function App() {
  const [screen, setScreen] = useState<'home' | 'test'>('home')

  if (screen === 'test') {
    return <Test questions={questions} onExit={() => setScreen('home')} />
  }

  return <Home onStart={() => setScreen('test')} />
}
