/**
 * 路由守卫工具
 * 实现基于角色的页面权限控制
 */

import store from '@/store'
import { PermissionService } from '@/services/permissionService'

class RouteGuard {
  constructor() {
    this.permissionService = new PermissionService()
    this.publicPages = [
      '/pages/index/index',
      '/pages/login/login',
      '/pages/register/register',
      '/pages/about/about'
    ]
    this.guestPages = [
      '/pages/index/index',
      '/pages/word/word',
      '/pages/tools/tools'
    ]
  }

  /**
   * 检查页面访问权限
   * @param {string} path 页面路径
   * @param {Object} options 导航选项
   * @returns {Promise<boolean>} 是否有权限访问
   */
  async checkPagePermission(path, options = {}) {
    try {
      // 获取当前用户信息
      const userInfo = store.state.user?.userInfo
      const isLoggedIn = store.state.user?.isLoggedIn
      const currentRole = store.state.permission?.currentRole

      // 公共页面，无需权限检查
      if (this.isPublicPage(path)) {
        return true
      }

      // 未登录用户只能访问游客页面
      if (!isLoggedIn) {
        if (this.isGuestPage(path)) {
          // 设置为游客角色
          await store.dispatch('permission/setCurrentRole', 'guest')
          return true
        } else {
          // 重定向到登录页面
          this.redirectToLogin(path)
          return false
        }
      }

      // 已登录用户权限检查
      if (isLoggedIn && userInfo) {
        // 获取用户菜单权限
        const userMenuPermissions = store.state.permission?.userMenuPermissions
        
        if (!userMenuPermissions) {
          // 加载用户权限数据
          await store.dispatch('permission/loadPermissionData')
        }

        // 检查菜单权限
        const hasPermission = await this.checkMenuPermission(path, userInfo.id)
        
        if (!hasPermission) {
          this.showNoPermissionMessage()
          return false
        }

        return true
      }

      return false
    } catch (error) {
      console.error('权限检查失败:', error)
      return false
    }
  }

  /**
   * 检查菜单权限
   * @param {string} path 页面路径
   * @param {string} userId 用户ID
   * @returns {Promise<boolean>} 是否有权限
   */
  async checkMenuPermission(path, userId) {
    try {
      // 从菜单配置中查找对应的菜单项
      const menuConfig = store.state.permission?.menuConfig
      if (!menuConfig) {
        return false
      }

      // 查找匹配的菜单项
      const menuItem = this.findMenuByPath(menuConfig, path)
      if (!menuItem) {
        // 如果没有找到对应的菜单项，检查是否为子页面
        return this.checkSubPagePermission(path)
      }

      // 检查用户是否有该菜单的权限
      const hasPermission = await store.dispatch('permission/checkMenuPermission', {
        menuId: menuItem.id,
        userId: userId
      })

      return hasPermission
    } catch (error) {
      console.error('菜单权限检查失败:', error)
      return false
    }
  }

  /**
   * 检查子页面权限
   * @param {string} path 页面路径
   * @returns {boolean} 是否有权限
   */
  checkSubPagePermission(path) {
    // 提取父页面路径
    const parentPath = this.getParentPath(path)
    
    if (parentPath) {
      // 递归检查父页面权限
      return this.checkMenuPermission(parentPath)
    }

    return false
  }

  /**
   * 获取父页面路径
   * @param {string} path 页面路径
   * @returns {string|null} 父页面路径
   */
  getParentPath(path) {
    // 移除查询参数
    const cleanPath = path.split('?')[0]
    
    // 常见的子页面模式
    const subPagePatterns = [
      { pattern: /\/detail$/, parent: '' },
      { pattern: /\/edit$/, parent: '' },
      { pattern: /\/add$/, parent: '' },
      { pattern: /\/view$/, parent: '' }
    ]

    for (const { pattern, parent } of subPagePatterns) {
      if (pattern.test(cleanPath)) {
        return cleanPath.replace(pattern, parent)
      }
    }

    return null
  }

  /**
   * 从菜单配置中查找指定路径的菜单项
   * @param {Array} menuConfig 菜单配置
   * @param {string} path 页面路径
   * @returns {Object|null} 菜单项
   */
  findMenuByPath(menuConfig, path) {
    const cleanPath = path.split('?')[0] // 移除查询参数
    
    for (const menu of menuConfig) {
      if (menu.path === cleanPath) {
        return menu
      }
      
      // 递归查找子菜单
      if (menu.children && menu.children.length > 0) {
        const found = this.findMenuByPath(menu.children, path)
        if (found) {
          return found
        }
      }
    }
    
    return null
  }

  /**
   * 是否为公共页面
   * @param {string} path 页面路径
   * @returns {boolean}
   */
  isPublicPage(path) {
    const cleanPath = path.split('?')[0]
    return this.publicPages.includes(cleanPath)
  }

  /**
   * 是否为游客页面
   * @param {string} path 页面路径
   * @returns {boolean}
   */
  isGuestPage(path) {
    const cleanPath = path.split('?')[0]
    return this.guestPages.includes(cleanPath)
  }

  /**
   * 重定向到登录页面
   * @param {string} redirectPath 登录后重定向的路径
   */
  redirectToLogin(redirectPath) {
    const loginUrl = `/pages/login/login?redirect=${encodeURIComponent(redirectPath)}`
    
    uni.reLaunch({
      url: loginUrl,
      fail: (err) => {
        console.error('重定向到登录页面失败:', err)
      }
    })
  }

  /**
   * 显示无权限提示
   */
  showNoPermissionMessage() {
    uni.showModal({
      title: '访问受限',
      content: '您没有权限访问此页面，请联系管理员',
      showCancel: false,
      confirmText: '确定',
      success: () => {
        // 返回上一页或首页
        const pages = getCurrentPages()
        if (pages.length > 1) {
          uni.navigateBack()
        } else {
          uni.reLaunch({
            url: '/pages/index/index'
          })
        }
      }
    })
  }

  /**
   * 页面导航拦截
   * @param {string} method 导航方法名
   * @param {Object} options 导航选项
   * @returns {Promise<boolean>} 是否允许导航
   */
  async interceptNavigation(method, options) {
    const { url } = options
    
    if (!url) {
      return true
    }

    // 检查页面权限
    const hasPermission = await this.checkPagePermission(url, options)
    
    if (!hasPermission) {
      return false
    }

    return true
  }

  /**
   * 安装路由守卫
   */
  install() {
    const originalNavigateTo = uni.navigateTo
    const originalRedirectTo = uni.redirectTo
    const originalReLaunch = uni.reLaunch
    const originalSwitchTab = uni.switchTab

    // 拦截 navigateTo
    uni.navigateTo = async (options) => {
      const canNavigate = await this.interceptNavigation('navigateTo', options)
      if (canNavigate) {
        return originalNavigateTo.call(uni, options)
      }
    }

    // 拦截 redirectTo
    uni.redirectTo = async (options) => {
      const canNavigate = await this.interceptNavigation('redirectTo', options)
      if (canNavigate) {
        return originalRedirectTo.call(uni, options)
      }
    }

    // 拦截 reLaunch
    uni.reLaunch = async (options) => {
      const canNavigate = await this.interceptNavigation('reLaunch', options)
      if (canNavigate) {
        return originalReLaunch.call(uni, options)
      }
    }

    // 拦截 switchTab
    uni.switchTab = async (options) => {
      const canNavigate = await this.interceptNavigation('switchTab', options)
      if (canNavigate) {
        return originalSwitchTab.call(uni, options)
      }
    }
  }
}

// 创建路由守卫实例
const routeGuard = new RouteGuard()

// 导出
export default routeGuard
export { RouteGuard }