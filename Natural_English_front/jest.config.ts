import type { Config } from 'jest'

const config: Config = {
  // 测试环境
  testEnvironment: 'jsdom',
  
  // 模块文件扩展名
  moduleFileExtensions: [
    'ts',
    'tsx',
    'js',
    'jsx',
    'json',
    'vue'
  ],
  
  // 模块名映射
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
    '^~/(.*)$': '<rootDir>/$1'
  },
  
  // 转换器配置
  transform: {
    '^.+\.ts$': 'babel-jest',
    '^.+\.tsx$': 'babel-jest',
    '^.+\.js$': 'babel-jest',
    '^.+\.jsx$': 'babel-jest',
    '.*\.(vue)$': '@vue/vue3-jest'
  },
  
  // 收集覆盖率的文件
  collectCoverageFrom: [
    'pages/**/*.{ts,tsx,js,jsx,vue}',
    'components/**/*.{ts,tsx,js,jsx,vue}',
    'utils/**/*.{ts,tsx,js,jsx}',
    'composables/**/*.{ts,tsx,js,jsx}',
    '!**/node_modules/**',
    '!**/*.d.ts'
  ],
  
  // 测试文件匹配模式
  testMatch: [
    '**/tests/**/*.test.{ts,tsx,js,jsx}',
    '**/tests/**/*.spec.{ts,tsx,js,jsx}',
    '**/__tests__/**/*.{ts,tsx,js,jsx}'
  ],
  
  // 设置文件
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  
  // 覆盖率报告
  coverageReporters: [
    'text',
    'lcov',
    'html'
  ],
  
  // 覆盖率阈值
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  
  // 忽略的测试路径
  testPathIgnorePatterns: [
    '/node_modules/',
    '/.nuxt/',
    '/dist/'
  ],
  
  // TypeScript 支持
  preset: 'ts-jest/presets/default-esm',
  extensionsToTreatAsEsm: ['.ts', '.tsx'],
  globals: {
    'ts-jest': {
      useESM: true
    }
  }
}

export default config