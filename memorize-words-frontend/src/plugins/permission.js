/**
 * 权限控制插件
 * 提供全局权限检查和路由守卫功能
 */

import menuManager from '@/utils/menuManager.js'

class PermissionPlugin {
  constructor() {
    this.routeGuards = []
    this.permissionCache = new Map()
  }

  /**
   * 安装插件
   */
  install(app) {
    // 全局属性注入
    app.config.globalProperties.$permission = this
    app.config.globalProperties.$hasPermission = this.hasPermission.bind(this)
    app.config.globalProperties.$checkPagePermission = this.checkPagePermission.bind(this)
    
    // 全局混入
    app.mixin({
      methods: {
        $hasPermission: this.hasPermission.bind(this),
        $checkPagePermission: this.checkPagePermission.bind(this),
        $requirePermission: this.requirePermission.bind(this)
      }
    })
  }

  /**
   * 检查用户权限
   */
  hasPermission(permission) {
    if (!permission) return true
    
    // 检查缓存
    const cacheKey = `perm_${permission}`
    if (this.permissionCache.has(cacheKey)) {
      return this.permissionCache.get(cacheKey)
    }
    
    const result = menuManager.hasPermission(permission)
    
    // 缓存结果（5分钟）
    this.permissionCache.set(cacheKey, result)
    setTimeout(() => {
      this.permissionCache.delete(cacheKey)
    }, 5 * 60 * 1000)
    
    return result
  }

  /**
   * 检查页面访问权限
   */
  checkPagePermission(path) {
    return menuManager.checkPagePermission(path)
  }

  /**
   * 要求特定权限（用于组件内部）
   */
  requirePermission(permission, options = {}) {
    if (this.hasPermission(permission)) {
      return true
    }
    
    const {
      showToast = true,
      toastMessage = '没有访问权限',
      redirectTo = null,
      callback = null
    } = options
    
    if (showToast) {
      uni.showToast({
        title: toastMessage,
        icon: 'none',
        duration: 2000
      })
    }
    
    if (redirectTo) {
      setTimeout(() => {
        uni.navigateTo({ url: redirectTo })
      }, 1000)
    }
    
    if (callback && typeof callback === 'function') {
      callback()
    }
    
    return false
  }

  /**
   * 添加路由守卫
   */
  addRouteGuard(guard) {
    if (typeof guard === 'function') {
      this.routeGuards.push(guard)
    }
  }

  /**
   * 执行路由守卫检查
   */
  async executeRouteGuards(to, from) {
    for (const guard of this.routeGuards) {
      try {
        const result = await guard(to, from, this)
        if (result === false) {
          return false
        }
      } catch (error) {
        console.error('路由守卫执行失败:', error)
        return false
      }
    }
    return true
  }

  /**
   * 清除权限缓存
   */
  clearCache() {
    this.permissionCache.clear()
    menuManager.clearCache()
  }

  /**
   * 刷新用户权限
   */
  refreshPermissions() {
    this.clearCache()
    menuManager.refreshMenus()
  }
}

// 创建插件实例
const permissionPlugin = new PermissionPlugin()

// 默认路由守卫
permissionPlugin.addRouteGuard(async (to, from, permission) => {
  // 检查用户是否已登录
  if (!menuManager.isAuthenticated()) {
    // 需要登录的页面
    const requireAuthPages = [
      '/pages/profile/profile',
      '/pages/settings/settings',
      '/pages/dev/api-test',
      '/pages/dev/performance'
    ]
    
    if (requireAuthPages.includes(to)) {
      uni.showToast({
        title: '请先登录',
        icon: 'none'
      })
      
      setTimeout(() => {
        uni.navigateTo({ url: '/pages/login/login' })
      }, 1000)
      
      return false
    }
  }
  
  // 检查页面权限
  if (!permission.checkPagePermission(to)) {
    uni.showToast({
      title: '没有访问权限',
      icon: 'none'
    })
    
    // 返回上一页或首页
    setTimeout(() => {
      const pages = getCurrentPages()
      if (pages.length > 1) {
        uni.navigateBack()
      } else {
        uni.reLaunch({ url: '/pages/index/index' })
      }
    }, 1000)
    
    return false
  }
  
  return true
})

export default permissionPlugin

// 导出常用方法
export const {
  hasPermission,
  checkPagePermission,
  requirePermission,
  addRouteGuard,
  clearCache,
  refreshPermissions
} = permissionPlugin