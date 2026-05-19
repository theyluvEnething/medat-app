/**
 * Platform abstraction layer.
 *
 * In Electron, the preload script exposes `window.api` via contextBridge.
 * In the browser, `window.api` is undefined and we fall back to standard
 * Web APIs.
 *
 * Since the current app uses localStorage directly (services/storage.ts),
 * this module exists for future Electron-specific IPC needs.
 */

interface ElectronAPI {
  ping: () => Promise<string>
}

function getElectronAPI(): ElectronAPI | null {
  if (typeof window !== 'undefined' && window.api) {
    return window.api
  }
  return null
}

export function ping(): Promise<string> {
  const api = getElectronAPI()
  if (api) {
    return api.ping()
  }
  return Promise.resolve('pong (web)')
}

export function isElectron(): boolean {
  return getElectronAPI() !== null
}
