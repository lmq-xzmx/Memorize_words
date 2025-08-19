import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright端到端测试配置
 */
export default defineConfig({
  testDir: './src/tests/e2e',
  
  /* 并行运行测试 */
  fullyParallel: true,
  
  /* 在CI环境中失败时不重试 */
  forbidOnly: !!process.env.CI,
  
  /* 在CI环境中重试失败的测试 */
  retries: process.env.CI ? 2 : 0,
  
  /* 并行worker数量 */
  workers: process.env.CI ? 1 : undefined,
  
  /* 测试报告配置 */
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/results.xml' }]
  ],
  
  /* 全局测试配置 */
  use: {
    /* 基础URL */
    baseURL: 'http://localhost:3000',
    
    /* 在失败时收集trace */
    trace: 'on-first-retry',
    
    /* 截图配置 */
    screenshot: 'only-on-failure',
    
    /* 视频录制 */
    video: 'retain-on-failure',
    
    /* 浏览器上下文配置 */
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
    
    /* 等待策略 */
    actionTimeout: 10000,
    navigationTimeout: 30000
  },

  /* 项目配置 - 不同浏览器和设备 */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    },
    
    /* 移动端测试 */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] }
    },
    
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] }
    }
  ],

  /* 开发服务器配置 */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000
  },
  
  /* 输出目录 */
  outputDir: 'test-results/',
  
  /* 全局设置和拆卸 */
  globalSetup: require.resolve('./src/tests/e2e/global-setup.ts'),
  globalTeardown: require.resolve('./src/tests/e2e/global-teardown.ts'),
  
  /* 测试匹配模式 */
  testMatch: '**/*.e2e.test.ts',
  
  /* 超时配置 */
  timeout: 30000,
  expect: {
    timeout: 5000
  }
})