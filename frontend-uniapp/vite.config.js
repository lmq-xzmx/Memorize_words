import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import { resolve } from 'path'

export default defineConfig({
  plugins: [uni()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '~': resolve(__dirname, './'),
      '@components': resolve(__dirname, 'components'),
      '@pages': resolve(__dirname, 'pages'),
      '@static': resolve(__dirname, 'static'),
      '@utils': resolve(__dirname, 'utils'),
      '@api': resolve(__dirname, 'api'),
      '@store': resolve(__dirname, 'store'),
      '@styles': resolve(__dirname, 'styles'),
      '@services': resolve(__dirname, 'services')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    open: true,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8003',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/permissions': {
        target: 'http://127.0.0.1:8003',
        changeOrigin: true
      }
    }
  },
  build: {
    target: 'es6',
    outDir: 'dist',
    assetsDir: 'static',
    sourcemap: process.env.NODE_ENV === 'development',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: process.env.NODE_ENV === 'production',
        drop_debugger: process.env.NODE_ENV === 'production'
      }
    },
    rollupOptions: {
      output: {
        chunkFileNames: 'static/js/[name]-[hash].js',
        entryFileNames: 'static/js/[name]-[hash].js',
        assetFileNames: 'static/[ext]/[name]-[hash].[ext]',
        manualChunks: {
          vue: ['vue', 'vuex', 'pinia'],
          utils: ['lodash-es', 'dayjs', 'crypto-js'],
          ui: ['uview-ui']
        }
      }
    }
  },
  define: {
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false,
    __UNI_FEATURE_PROMISE__: false,
    __UNI_FEATURE_I18N_EN__: false,
    __UNI_FEATURE_I18N_ES__: false,
    __UNI_FEATURE_I18N_FR__: false,
    __UNI_FEATURE_I18N_ZH_HANS__: true,
    __UNI_FEATURE_I18N_ZH_HANT__: false
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          @import "@/styles/variables.scss";
          @import "@/styles/mixins.scss";
        `
      }
    }
  },
  optimizeDeps: {
    include: [
      'vue',
      'vuex',
      'pinia',
      'lodash-es',
      'dayjs',
      'crypto-js',
      'js-cookie',
      '@vueuse/core',
      'uview-ui'
    ]
  },
  
  // esbuild 配置
  esbuild: {
    drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : []
  }
})