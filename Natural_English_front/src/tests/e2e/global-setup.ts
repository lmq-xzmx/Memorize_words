/**
 * Playwright全局设置
 */

import { chromium, FullConfig } from '@playwright/test'

async function globalSetup(config: FullConfig) {
  console.log('🚀 开始端到端测试全局设置...')
  
  // 启动浏览器进行预热
  const browser = await chromium.launch()
  const context = await browser.newContext()
  const page = await context.newPage()
  
  try {
    // 预热应用
    console.log('📱 预热应用...')
    await page.goto('http://localhost:3000')
    await page.waitForLoadState('networkidle')
    
    // 设置测试数据
    console.log('📊 设置测试数据...')
    await page.evaluate(() => {
      // 清理localStorage
      localStorage.clear()
      sessionStorage.clear()
      
      // 设置测试用户数据
      localStorage.setItem('test-user', JSON.stringify({
        id: 'test-user',
        name: '测试用户',
        permissions: ['read', 'write'],
        roles: ['admin']
      }))
      
      // 设置测试菜单缓存
      localStorage.setItem('menu-cache-version', '1')
    })
    
    // 验证应用可访问性
    console.log('✅ 验证应用可访问性...')
    const title = await page.title()
    if (!title) {
      throw new Error('应用无法正常加载')
    }
    
    console.log('✨ 全局设置完成')
    
  } catch (error) {
    console.error('❌ 全局设置失败:', error)
    throw error
  } finally {
    await context.close()
    await browser.close()
  }
}

export default globalSetup