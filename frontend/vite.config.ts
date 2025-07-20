import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      // Proxy API calls to Flask backend
      '/api': {
        target: 'http://localhost:5050',
        changeOrigin: true,
      },
      '/video_feed': {
        target: 'http://localhost:5050',
        changeOrigin: true,
      },
      '/snapshot': {
        target: 'http://localhost:5050',
        changeOrigin: true,
      },
      '/socket.io': {
        target: 'http://localhost:5050',
        changeOrigin: true,
        ws: true,
      }
    }
  },
  build: {
    outDir: '../web/static',
    emptyOutDir: true,
  }
})
