import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          // 生产环境移除注释
          comments: false
        }
      }
    })
  ],
  
  // 路径解析
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '~': resolve(__dirname, './')
    }
  },
  
  // 开发服务器配置
  server: {
    port: 3000,
    host: true,
    open: false,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/accounts': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/ws': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: true
      },
      '/static': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  },
  
  // 构建配置
  build: {
    target: 'es2015',
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
      }
    }
  },
  
  // 优化配置
  optimizeDeps: {
    exclude: ['fsevents'],
    include: [
      'vue',
      'vue-router',
      'vuex',
      'axios',
      'element-plus'
    ]
  },
  
  // CSS 配置
  css: {
    preprocessorOptions: {
      scss: {
        // 使用现代编译器
        api: 'modern-compiler',
        silenceDeprecations: ['legacy-js-api'],
        additionalData: `@import "@/styles/variables.scss";`
      }
    }
  },
  
  // 定义全局常量
  define: {
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false,
    global: 'globalThis'
  }
})