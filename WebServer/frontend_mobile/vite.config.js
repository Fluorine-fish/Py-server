import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/mobile/', // 关键：确保资源加载路径以/mobile/开头
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
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  }
})