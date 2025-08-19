/**
 * 菜单系统端到端测试
 * 验证完整的用户体验和系统集成
 */

import { test, expect, Page } from '@playwright/test'

// 测试配置
const TEST_CONFIG = {
  baseURL: 'http://localhost:3000',
  timeout: 30000,
  retries: 2
}

test.describe('菜单系统端到端测试', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage()
    
    // 设置网络拦截器来模拟API响应
    await page.route('**/api/menu/**', async (route) => {
      const url = route.request().url()
      
      if (url.includes('/config')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: [
              {
                id: 'dashboard',
                name: '仪表板',
                path: '/dashboard',
                icon: 'dashboard',
                enabled: true,
                children: []
              },
              {
                id: 'words',
                name: '单词管理',
                path: '/words',
                icon: 'book',
                enabled: true,
                children: [
                  {
                    id: 'word-list',
                    name: '单词列表',
                    path: '/words/list',
                    enabled: true
                  },
                  {
                    id: 'word-add',
                    name: '添加单词',
                    path: '/words/add',
                    enabled: true
                  }
                ]
              }
            ],
            version: 1
          })
        })
      } else if (url.includes('/tools')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: [
              {
                id: 'export-tool',
                name: '导出工具',
                enabled: true,
                config: { format: 'excel' }
              },
              {
                id: 'import-tool',
                name: '导入工具',
                enabled: false,
                config: { maxSize: '10MB' }
              }
            ]
          })
        })
      } else if (url.includes('/version')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              version: 1,
              timestamp: Date.now()
            }
          })
        })
      }
    })

    // 导航到应用
    await page.goto(TEST_CONFIG.baseURL)
    await page.waitForLoadState('networkidle')
  })

  test.afterEach(async () => {
    await page.close()
  })

  test.describe('菜单加载和显示', () => {
    test('应该正确加载和显示菜单结构', async () => {
      // 等待菜单加载
      await page.waitForSelector('[data-testid="main-menu"]', { timeout: 10000 })

      // 验证主菜单项
      const dashboardMenu = page.locator('[data-testid="menu-dashboard"]')
      await expect(dashboardMenu).toBeVisible()
      await expect(dashboardMenu).toContainText('仪表板')

      const wordsMenu = page.locator('[data-testid="menu-words"]')
      await expect(wordsMenu).toBeVisible()
      await expect(wordsMenu).toContainText('单词管理')

      // 验证子菜单
      await wordsMenu.click()
      await page.waitForTimeout(500) // 等待展开动画

      const wordListMenu = page.locator('[data-testid="menu-word-list"]')
      await expect(wordListMenu).toBeVisible()
      await expect(wordListMenu).toContainText('单词列表')

      const wordAddMenu = page.locator('[data-testid="menu-word-add"]')
      await expect(wordAddMenu).toBeVisible()
      await expect(wordAddMenu).toContainText('添加单词')
    })

    test('应该正确处理菜单导航', async () => {
      // 等待菜单加载
      await page.waitForSelector('[data-testid="main-menu"]')

      // 点击仪表板菜单
      await page.click('[data-testid="menu-dashboard"]')
      await page.waitForURL('**/dashboard')
      expect(page.url()).toContain('/dashboard')

      // 导航到单词列表
      await page.click('[data-testid="menu-words"]')
      await page.waitForTimeout(500)
      await page.click('[data-testid="menu-word-list"]')
      await page.waitForURL('**/words/list')
      expect(page.url()).toContain('/words/list')
    })
  })

  test.describe('实时推送功能', () => {
    test('应该正确处理菜单实时更新', async () => {
      // 等待菜单加载
      await page.waitForSelector('[data-testid="main-menu"]')

      // 模拟WebSocket连接和消息
      await page.evaluate(() => {
        // 模拟WebSocket推送菜单更新
        const mockUpdate = {
          type: 'menuUpdated',
          data: {
            incremental: true,
            action: 'update',
            updates: [
              {
                id: 'dashboard',
                name: '实时更新的仪表板',
                path: '/dashboard',
                icon: 'dashboard-new',
                enabled: true
              }
            ],
            version: 2
          }
        }

        // 触发菜单更新事件
        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: mockUpdate
        }))
      })

      // 等待菜单更新
      await page.waitForTimeout(1000)

      // 验证菜单已更新
      const updatedDashboard = page.locator('[data-testid="menu-dashboard"]')
      await expect(updatedDashboard).toContainText('实时更新的仪表板')
    })

    test('应该正确处理工具状态变更推送', async () => {
      // 等待页面加载
      await page.waitForSelector('[data-testid="main-menu"]')

      // 打开工具面板
      await page.click('[data-testid="tools-panel-toggle"]')
      await page.waitForSelector('[data-testid="tools-panel"]')

      // 验证初始工具状态
      const exportTool = page.locator('[data-testid="tool-export-tool"]')
      await expect(exportTool).toHaveClass(/enabled/)

      const importTool = page.locator('[data-testid="tool-import-tool"]')
      await expect(importTool).toHaveClass(/disabled/)

      // 模拟工具状态变更推送
      await page.evaluate(() => {
        const mockUpdate = {
          type: 'toolStatusChanged',
          data: {
            toolId: 'import-tool',
            enabled: true,
            incremental: false
          }
        }

        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: mockUpdate
        }))
      })

      // 等待状态更新
      await page.waitForTimeout(1000)

      // 验证工具状态已更新
      await expect(importTool).toHaveClass(/enabled/)
    })
  })

  test.describe('缓存机制验证', () => {
    test('应该正确使用缓存加速菜单加载', async () => {
      // 第一次加载 - 记录加载时间
      const startTime1 = Date.now()
      await page.goto(TEST_CONFIG.baseURL)
      await page.waitForSelector('[data-testid="main-menu"]')
      const loadTime1 = Date.now() - startTime1

      // 刷新页面 - 应该使用缓存，加载更快
      const startTime2 = Date.now()
      await page.reload()
      await page.waitForSelector('[data-testid="main-menu"]')
      const loadTime2 = Date.now() - startTime2

      // 验证缓存效果（第二次加载应该更快）
      expect(loadTime2).toBeLessThan(loadTime1 * 0.8)

      // 验证缓存状态指示器
      const cacheIndicator = page.locator('[data-testid="cache-status"]')
      await expect(cacheIndicator).toHaveAttribute('data-cache-hit', 'true')
    })

    test('应该正确处理缓存失效', async () => {
      // 等待菜单加载
      await page.waitForSelector('[data-testid="main-menu"]')

      // 模拟缓存失效推送
      await page.evaluate(() => {
        const mockUpdate = {
          type: 'cacheInvalidated',
          data: {
            pattern: '.*menu.*'
          }
        }

        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: mockUpdate
        }))
      })

      // 等待缓存清理
      await page.waitForTimeout(1000)

      // 验证缓存状态
      const cacheIndicator = page.locator('[data-testid="cache-status"]')
      await expect(cacheIndicator).toHaveAttribute('data-cache-cleared', 'true')
    })
  })

  test.describe('版本控制功能', () => {
    test('应该正确显示版本信息', async () => {
      // 等待菜单加载
      await page.waitForSelector('[data-testid="main-menu"]')

      // 打开版本信息面板
      await page.click('[data-testid="version-info-toggle"]')
      await page.waitForSelector('[data-testid="version-panel"]')

      // 验证版本信息显示
      const currentVersion = page.locator('[data-testid="current-version"]')
      await expect(currentVersion).toContainText('1')

      const serverVersion = page.locator('[data-testid="server-version"]')
      await expect(serverVersion).toContainText('1')

      const syncStatus = page.locator('[data-testid="sync-status"]')
      await expect(syncStatus).toContainText('已同步')
    })

    test('应该正确处理版本冲突', async () => {
      // 模拟版本冲突
      await page.route('**/api/menu/version', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              version: 3,
              timestamp: Date.now()
            }
          })
        })
      })

      await page.route('**/api/menu/sync', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: false,
            hasConflicts: true,
            conflicts: ['dashboard'],
            message: '检测到版本冲突'
          })
        })
      })

      // 等待菜单加载
      await page.waitForSelector('[data-testid="main-menu"]')

      // 触发版本同步
      await page.click('[data-testid="sync-version-btn"]')

      // 等待冲突提示
      await page.waitForSelector('[data-testid="conflict-dialog"]')

      // 验证冲突信息显示
      const conflictMessage = page.locator('[data-testid="conflict-message"]')
      await expect(conflictMessage).toContainText('检测到版本冲突')

      const conflictItems = page.locator('[data-testid="conflict-items"]')
      await expect(conflictItems).toContainText('dashboard')
    })
  })

  test.describe('错误处理和用户体验', () => {
    test('应该正确处理网络错误', async () => {
      // 模拟网络错误
      await page.route('**/api/menu/**', async (route) => {
        await route.abort('failed')
      })

      await page.goto(TEST_CONFIG.baseURL)

      // 等待错误提示
      await page.waitForSelector('[data-testid="error-message"]')

      // 验证错误信息显示
      const errorMessage = page.locator('[data-testid="error-message"]')
      await expect(errorMessage).toContainText('网络连接失败')

      // 验证重试按钮
      const retryButton = page.locator('[data-testid="retry-button"]')
      await expect(retryButton).toBeVisible()
    })

    test('应该正确处理加载状态', async () => {
      // 模拟慢速网络
      await page.route('**/api/menu/**', async (route) => {
        await new Promise(resolve => setTimeout(resolve, 2000))
        await route.continue()
      })

      await page.goto(TEST_CONFIG.baseURL)

      // 验证加载状态显示
      const loadingIndicator = page.locator('[data-testid="menu-loading"]')
      await expect(loadingIndicator).toBeVisible()

      // 等待加载完成
      await page.waitForSelector('[data-testid="main-menu"]', { timeout: 10000 })

      // 验证加载状态消失
      await expect(loadingIndicator).not.toBeVisible()
    })

    test('应该正确处理权限变更', async () => {
      // 等待菜单加载
      await page.waitForSelector('[data-testid="main-menu"]')

      // 验证初始菜单可见
      const wordsMenu = page.locator('[data-testid="menu-words"]')
      await expect(wordsMenu).toBeVisible()

      // 模拟权限变更推送
      await page.evaluate(() => {
        const mockUpdate = {
          type: 'permissionChanged',
          data: {
            userId: 'test-user',
            permissions: ['read'] // 移除写权限
          }
        }

        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: mockUpdate
        }))
      })

      // 等待菜单更新
      await page.waitForTimeout(1000)

      // 验证受权限影响的菜单项被隐藏或禁用
      const wordAddMenu = page.locator('[data-testid="menu-word-add"]')
      await expect(wordAddMenu).toHaveClass(/disabled/)
    })
  })

  test.describe('性能和用户体验', () => {
    test('菜单响应时间应该在可接受范围内', async () => {
      await page.goto(TEST_CONFIG.baseURL)

      // 测试菜单点击响应时间
      const startTime = Date.now()
      await page.click('[data-testid="menu-dashboard"]')
      await page.waitForURL('**/dashboard')
      const responseTime = Date.now() - startTime

      // 响应时间应该小于500ms
      expect(responseTime).toBeLessThan(500)
    })

    test('应该正确处理大量菜单项', async () => {
      // 模拟大量菜单项
      await page.route('**/api/permissions/frontend-menu-config/', async (route) => {
        const largeMenuData = Array.from({ length: 100 }, (_, i) => ({
          id: `menu-${i}`,
          name: `菜单项 ${i}`,
          path: `/menu-${i}`,
          enabled: true,
          children: Array.from({ length: 10 }, (_, j) => ({
            id: `submenu-${i}-${j}`,
            name: `子菜单 ${i}-${j}`,
            path: `/menu-${i}/sub-${j}`,
            enabled: true
          }))
        }))

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: largeMenuData,
            version: 1
          })
        })
      })

      await page.goto(TEST_CONFIG.baseURL)
      await page.waitForSelector('[data-testid="main-menu"]')

      // 验证虚拟滚动或分页加载
      const menuContainer = page.locator('[data-testid="menu-container"]')
      await expect(menuContainer).toBeVisible()

      // 验证性能指标
      const performanceMetrics = await page.evaluate(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
        return {
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          loadComplete: navigation.loadEventEnd - navigation.loadEventStart
        }
      })

      // DOM加载时间应该合理
      expect(performanceMetrics.domContentLoaded).toBeLessThan(2000)
    })
  })
})