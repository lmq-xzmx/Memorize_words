import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/accounts/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/words/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  esbuild: {
    target: 'es2015'
  },
  build: {
    rollupOptions: {
      external: []
    }
  }
})