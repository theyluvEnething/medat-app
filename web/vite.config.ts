import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const __dirname = dirname(fileURLToPath(import.meta.url))
const appSrc = resolve(__dirname, '../app/src/renderer/src')

export default defineConfig({
  resolve: {
    alias: {
      '@app': appSrc,
    },
  },
  plugins: [react(), tailwindcss()],
  base: '/medat-app/',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
