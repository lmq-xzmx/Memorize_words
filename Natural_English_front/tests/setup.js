// Jest 测试环境设置文件
import { config } from '@vue/test-utils'

// 全局 mock 配置
global.console = {
  ...console,
  // 在测试中静默某些日志
  warn: jest.fn(),
  error: jest.fn()
}

// Mock window 对象
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000',
    origin: 'http://localhost:3000'
  },
  writable: true
})

// Mock navigator
Object.defineProperty(navigator, 'onLine', {
  writable: true,
  value: true
})

// Mock speechSynthesis
Object.defineProperty(window, 'speechSynthesis', {
  value: {
    speak: jest.fn(),
    cancel: jest.fn(),
    pause: jest.fn(),
    resume: jest.fn(),
    getVoices: jest.fn(() => [])
  },
  writable: true
})

// Mock Audio
global.Audio = jest.fn().mockImplementation(() => ({
  play: jest.fn().mockResolvedValue(undefined),
  pause: jest.fn(),
  load: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  onerror: null
}))

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn()
}))

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn()
}))

// 配置 Vue Test Utils
config.mocks = {
  $t: (key) => key, // i18n mock
  $route: {
    path: '/',
    params: {},
    query: {}
  },
  $router: {
    push: jest.fn(),
    go: jest.fn(),
    back: jest.fn()
  },
  $message: {
    success: jest.fn(),
    error: jest.fn(),
    warning: jest.fn(),
    info: jest.fn()
  }
}

// 设置测试超时
jest.setTimeout(10000)

// 清理函数
afterEach(() => {
  jest.clearAllMocks()
})