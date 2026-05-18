import type { ElectronAPI } from '@electron-toolkit/preload'

declare global {
  interface Window {
    api: {
      ping: () => Promise<string>
    }
  }
}
