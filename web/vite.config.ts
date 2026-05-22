import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const __dirname = dirname(fileURLToPath(import.meta.url))
const appSrc = resolve(__dirname, '../app/src/renderer/src')
const dataDir = resolve(__dirname, '../data')

export default defineConfig({
  resolve: {
    alias: {
      '@app': appSrc,
      '@data': dataDir,
    },
    dedupe: ['react', 'react-dom', 'react-router', 'react-router-dom'],
  },
  server: {
    fs: {
      allow: [resolve(__dirname, '..'), dataDir],
    },
  },
  plugins: [react(), tailwindcss()],
  base: '/medat-app/',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
