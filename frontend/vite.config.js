import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // --- THIS IS THE FIX ---
      // Any request starting with /api will be proxied to the backend
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    }
  }
})
