import { useCallback, useEffect, useRef, useState } from 'react'

export function useTimer(initialSeconds: number, onExpire: () => void) {
  const [remaining, setRemaining] = useState(initialSeconds)
  const [isRunning, setIsRunning] = useState(false)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const onExpireRef = useRef(onExpire)
  onExpireRef.current = onExpire

  // Reset timer when initialSeconds changes (section switch)
  useEffect(() => {
    setRemaining(initialSeconds)
    setIsRunning(false)
  }, [initialSeconds])

  const clear = useCallback(() => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [])

  const tick = useCallback(() => {
    setRemaining((prev) => {
      if (prev <= 1) {
        clear()
        onExpireRef.current()
        return 0
      }
      return prev - 1
    })
  }, [clear])

  const start = useCallback(() => {
    setIsRunning(true)
  }, [])

  useEffect(() => {
    if (isRunning) {
      intervalRef.current = setInterval(tick, 1000)
    }
    return clear
  }, [isRunning, tick, clear])

  const pause = useCallback(() => {
    setIsRunning(false)
    clear()
  }, [clear])

  const reset = useCallback(
    (seconds?: number) => {
      clear()
      setIsRunning(false)
      setRemaining(seconds ?? initialSeconds)
    },
    [clear, initialSeconds],
  )

  return { remaining, isRunning, start, pause, reset }
}
