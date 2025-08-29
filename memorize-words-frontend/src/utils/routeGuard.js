/**
 * 路由守卫工具
 * 处理Uni-App页面跳转时的权限检查和路由拦截
 */

import permissionPlugin from '@/plugins/permission.js'

class RouteGuard {
  constructor() {
    this.isInitialized = false
    this.originalMethods = {}
  }

  /**
   * 初始化路由守卫
   */
  init() {
    if (this.isInitialized) return
    
    // 拦截uni的导航方法
    this.interceptNavigationMethods()
    
    this.isInitialized = true
    console.log('路由守卫已初始化')
  }

  /**
   * 拦截导航方法
   */
  interceptNavigationMethods() {
    const methods = [
      'navigateTo',
      'redirectTo',
      'reLaunch',
      'switchTab',
      'navigateBack'
    ]
    
    methods.forEach(method => {
      if (uni[method]) {
        this.originalMethods[method] = uni[method]
        uni[method] = this.createInterceptor(method)
      }
    })
  }

  /**
   * 创建拦截器
   */
  createInterceptor(method) {
    return async (options = {}) => {
      try {
        // navigateBack 不需要权限检查
        if (method === 'navigateBack') {
          return this.originalMethods[method](options)
        }
        
        const { url, ...otherOptions } = options
        
        if (!url) {
          return this.originalMethods[method](options)
        }
        
        // 解析路径和参数
        const { path, query } = this.parseUrl(url)
        
        // 获取当前页面信息
        const currentPath = this.getCurrentPath()
        
        // 执行路由守卫
        const canNavigate = await permissionPlugin.executeRouteGuards(path, currentPath)
        
        if (!canNavigate) {
          console.warn(`导航被拦截: ${currentPath} -> ${path}`)
          return
        }
        
        // 执行原始导航
        return this.originalMethods[method]({
          url,
          ...otherOptions
        })
        
      } catch (error) {
        console.error(`路由守卫执行失败 (${method}):`, error)
        
        // 发生错误时仍然执行原始导航
        return this.originalMethods[method](options)
      }
    }
  }

  /**
   * 解析URL
   */
  parseUrl(url) {
    if (!url) return { path: '', query: {} }
    
    const [path, queryString] = url.split('?')
    const query = {}
    
    if (queryString) {
      queryString.split('&').forEach(param => {
        const [key, value] = param.split('=')
        if (key) {
          query[decodeURIComponent(key)] = decodeURIComponent(value || '')
        }
      })
    }
    
    return { path, query }
  }

  /**
   * 获取当前页面路径
   */
  getCurrentPath() {
    const pages = getCurrentPages()
    if (pages.length === 0) return '/'
    
    const currentPage = pages[pages.length - 1]
    return `/${currentPage.route}`
  }

  /**
   * 检查页面是否需要登录
   */
  requiresAuth(path) {
    const authRequiredPages = [
      '/pages/profile/profile',
      '/pages/settings/settings',
      '/pages/dev/api-test',
      '/pages/dev/performance',
      '/pages/dev/console'
    ]
    
    return authRequiredPages.includes(path)
  }

  /**
   * 检查页面是否为公开页面
   */
  isPublicPage(path) {
    const publicPages = [
      '/pages/index/index',
      '/pages/login/login',
      '/pages/register/register',
      '/pages/splash/splash'
    ]
    
    return publicPages.includes(path)
  }

  /**
   * 获取登录重定向URL
   */
  getLoginRedirectUrl(targetPath) {
    const encodedPath = encodeURIComponent(targetPath)
    return `/pages/login/login?redirect=${encodedPath}`
  }

  /**
   * 处理登录重定向
   */
  handleLoginRedirect() {
    const pages = getCurrentPages()
    if (pages.length === 0) return
    
    const currentPage = pages[pages.length - 1]
    const options = currentPage.options || {}
    
    if (options.redirect) {
      const redirectPath = decodeURIComponent(options.redirect)
      
      // 验证重定向路径的安全性
      if (this.isValidRedirectPath(redirectPath)) {
        uni.reLaunch({ url: redirectPath })
        return
      }
    }
    
    // 默认跳转到首页
    uni.reLaunch({ url: '/pages/index/index' })
  }

  /**
   * 验证重定向路径是否安全
   */
  isValidRedirectPath(path) {
    // 检查是否为内部路径
    if (!path.startsWith('/pages/')) {
      return false
    }
    
    // 检查是否为危险页面
    const dangerousPages = [
      '/pages/login/login',
      '/pages/register/register'
    ]
    
    return !dangerousPages.includes(path)
  }

  /**
   * 恢复原始导航方法
   */
  restore() {
    Object.keys(this.originalMethods).forEach(method => {
      if (uni[method] && this.originalMethods[method]) {
        uni[method] = this.originalMethods[method]
      }
    })
    
    this.isInitialized = false
    console.log('路由守卫已恢复')
  }

  /**
   * 手动导航（绕过守卫）
   */
  navigateWithoutGuard(method, options) {
    const originalMethod = this.originalMethods[method]
    if (originalMethod) {
      return originalMethod(options)
    } else {
      console.error(`未找到原始方法: ${method}`)
    }
  }
}

// 创建路由守卫实例
const routeGuard = new RouteGuard()

// 自动初始化
// #ifdef H5
// H5环境下延迟初始化，确保uni对象完全加载
setTimeout(() => {
  routeGuard.init()
}, 100)
// #endif

// #ifdef MP
// 小程序环境下立即初始化
routeGuard.init()
// #endif

// #ifdef APP-PLUS
// App环境下立即初始化
routeGuard.init()
// #endif

export default routeGuard

// 导出常用方法
export const {
  getCurrentPath,
  requiresAuth,
  isPublicPage,
  handleLoginRedirect,
  navigateWithoutGuard
} = routeGuard