/**
 * Playwright全局清理
 */

import { chromium, FullConfig } from '@playwright/test'

async function globalTeardown(config: FullConfig) {
  console.log('🧹 开始端到端测试全局清理...')
  
  const browser = await chromium.launch()
  const context = await browser.newContext()
  const page = await context.newPage()
  
  try {
    // 清理测试数据
    console.log('🗑️ 清理测试数据...')
    await page.goto('http://localhost:3000')
    await page.evaluate(() => {
      // 清理所有存储
      localStorage.clear()
      sessionStorage.clear()
      
      // 清理IndexedDB（如果使用）
      if (window.indexedDB) {
        const deleteReq = indexedDB.deleteDatabase('menu-cache-db')
        deleteReq.onsuccess = () => console.log('IndexedDB cleared')
      }
    })
    
    // 关闭WebSocket连接
    console.log('🔌 关闭WebSocket连接...')
    await page.evaluate(() => {
      // 触发WebSocket断开
      window.dispatchEvent(new CustomEvent('test-cleanup', {
        detail: { action: 'disconnect-websocket' }
      }))
    })
    
    console.log('✨ 全局清理完成')
    
  } catch (error) {
    console.error('❌ 全局清理失败:', error)
    // 不抛出错误，避免影响测试结果
  } finally {
    await context.close()
    await browser.close()
  }
}

export default globalTeardown