import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('api', {
  // Placeholder for future IPC needs (e.g., file dialogs for custom question sets)
  ping: () => ipcRenderer.invoke('ping'),
})
