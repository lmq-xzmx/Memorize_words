module.exports = {
  // 测试环境
  testEnvironment: 'jsdom',
  
  // 模块文件扩展名
  moduleFileExtensions: [
    'js',
    'json',
    'vue'
  ],
  
  // 模块名映射
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/$1',
    '^~/(.*)$': '<rootDir>/$1'
  },
  
  // 转换器配置
  transform: {
    '^.+\.js$': 'babel-jest',
    '.*\.(vue)$': '@vue/vue3-jest'
  },
  
  // 收集覆盖率的文件
  collectCoverageFrom: [
    'pages/**/*.{js,vue}',
    'components/**/*.{js,vue}',
    '!**/node_modules/**'
  ],
  
  // 测试文件匹配模式
  testMatch: [
    '**/tests/**/*.test.js',
    '**/tests/**/*.spec.js'
  ],
  
  // 设置文件
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  
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
  
  // 忽略的文件
  testPathIgnorePatterns: [
    '/node_modules/',
    '/.nuxt/'
  ]
}