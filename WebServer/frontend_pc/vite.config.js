import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5100',
        changeOrigin: true,
      },
      '/api/data': {
        target: 'http://localhost:5100',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/video': {
        target: 'http://localhost:5100',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:5100',
        ws: true,
        changeOrigin: true,
      },
    },
  }
})