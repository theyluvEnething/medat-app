/// <reference types="vite/client" />

export {}

declare global {
  interface Window {
    api?: {
      ping: () => Promise<string>
    }
  }
}
