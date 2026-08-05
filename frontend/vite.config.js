import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// The /api proxy lets the dev server forward API calls to the FastAPI backend,
// so the frontend uses same-origin relative URLs (no CORS config needed in dev).
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Plotly.js references `global` (a Node.js global absent in browsers). Map it
  // to `globalThis` so the dev server can evaluate the module (the production
  // build handles this via Rollup, but the dev server needs this shim).
  define: {
    global: 'globalThis',
  },
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
