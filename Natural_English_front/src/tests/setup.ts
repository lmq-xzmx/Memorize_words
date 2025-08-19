/**
 * 测试环境设置
 */

import { vi } from 'vitest'
import { config } from '@vue/test-utils'

// 全局测试配置
config.global.mocks = {
  $t: (key: string) => key,
  $route: {
    path: '/',
    params: {},
    query: {}
  },
  $router: {
    push: vi.fn(),
    replace: vi.fn(),
    go: vi.fn(),
    back: vi.fn(),
    forward: vi.fn()
  }
}

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn()
}

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn()
}

Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock
})

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  readyState = MockWebSocket.CONNECTING
  url: string
  onopen: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null

  constructor(url: string) {
    this.url = url
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      if (this.onopen) {
        this.onopen(new Event('open'))
      }
    }, 100)
  }

  send(data: string | ArrayBufferLike | Blob | ArrayBufferView) {
    // Mock send implementation
  }

  close(code?: number, reason?: string) {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close', { code, reason }))
    }
  }

  addEventListener(type: string, listener: EventListener) {
    // Mock addEventListener
  }

  removeEventListener(type: string, listener: EventListener) {
    // Mock removeEventListener
  }

  dispatchEvent(event: Event): boolean {
    return true
  }
}

Object.defineProperty(window, 'WebSocket', {
  value: MockWebSocket
})

// Mock fetch
global.fetch = vi.fn()

// Mock console methods for cleaner test output
const originalConsoleError = console.error
const originalConsoleWarn = console.warn

console.error = (...args: any[]) => {
  // 过滤掉一些预期的错误信息
  const message = args[0]
  if (typeof message === 'string') {
    if (message.includes('Vue warn') || message.includes('Warning')) {
      return
    }
  }
  originalConsoleError(...args)
}

console.warn = (...args: any[]) => {
  // 过滤掉一些预期的警告信息
  const message = args[0]
  if (typeof message === 'string') {
    if (message.includes('Vue warn') || message.includes('Warning')) {
      return
    }
  }
  originalConsoleWarn(...args)
}

// Mock IntersectionObserver
class MockIntersectionObserver {
  observe = vi.fn()
  disconnect = vi.fn()
  unobserve = vi.fn()
}

Object.defineProperty(window, 'IntersectionObserver', {
  value: MockIntersectionObserver,
  writable: true
})

// Mock ResizeObserver
class MockResizeObserver {
  observe = vi.fn()
  disconnect = vi.fn()
  unobserve = vi.fn()
}

Object.defineProperty(window, 'ResizeObserver', {
  value: MockResizeObserver,
  writable: true
})

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn()
  }))
})

// 设置测试超时
vi.setConfig({
  testTimeout: 10000,
  hookTimeout: 10000
})

// 在每个测试前清理mock
beforeEach(() => {
  vi.clearAllMocks()
  localStorageMock.getItem.mockClear()
  localStorageMock.setItem.mockClear()
  localStorageMock.removeItem.mockClear()
  localStorageMock.clear.mockClear()
  
  sessionStorageMock.getItem.mockClear()
  sessionStorageMock.setItem.mockClear()
  sessionStorageMock.removeItem.mockClear()
  sessionStorageMock.clear.mockClear()
})