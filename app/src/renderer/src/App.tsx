import { Routes, Route, Navigate } from 'react-router-dom'
import { useAppStore } from './store/useAppStore'
import { Login } from './pages/Login'
import { Home } from './pages/Home'
import { Setup } from './pages/Setup'
import { Session } from './pages/Session'
import { Results } from './pages/Results'
import { Settings } from './pages/Settings'
import { Leaderboard } from './pages/Leaderboard'

export function App() {
  const username = useAppStore((s) => s.user.username)

  return (
    <Routes>
      <Route
        path="/"
        element={<Navigate to={username ? '/home' : '/login'} replace />}
      />
      <Route path="/login" element={<Login />} />
      <Route path="/home" element={<Home />} />
      <Route path="/setup" element={<Setup />} />
      <Route path="/session/:type" element={<Session />} />
      <Route path="/results" element={<Results />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="/leaderboard" element={<Leaderboard />} />
    </Routes>
  )
}
