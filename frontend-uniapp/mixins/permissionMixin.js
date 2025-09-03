/**
 * 权限检查混入
 * 为页面组件提供权限检查功能
 */

import { mapState, mapActions } from 'vuex'
import routeGuard from '@/utils/routeGuard'

export default {
  computed: {
    ...mapState('user', ['userInfo', 'isLoggedIn']),
    ...mapState('permission', ['currentRole', 'menuTree', 'userMenuPermissions']),
    
    // 当前页面路径
    currentPagePath() {
      const pages = getCurrentPages()
      if (pages.length > 0) {
        const currentPage = pages[pages.length - 1]
        return '/' + currentPage.route
      }
      return ''
    },
    
    // 是否有当前页面权限
    hasCurrentPagePermission() {
      if (!this.currentPagePath) {
        return true
      }
      return this.checkPagePermission(this.currentPagePath)
    }
  },
  
  methods: {
    ...mapActions('permission', [
      'checkMenuPermission',
      'loadPermissionData',
      'setCurrentRole'
    ]),
    
    /**
     * 检查页面权限
     * @param {string} path 页面路径
     * @returns {Promise<boolean>} 是否有权限
     */
    async checkPagePermission(path) {
      try {
        return await routeGuard.checkPagePermission(path)
      } catch (error) {
        console.error('页面权限检查失败:', error)
        return false
      }
    },
    
    /**
     * 检查菜单权限
     * @param {string} menuId 菜单ID
     * @returns {Promise<boolean>} 是否有权限
     */
    async checkMenuPermissionById(menuId) {
      try {
        if (!this.userInfo?.id) {
          return false
        }
        
        return await this.checkMenuPermission({
          menuId,
          userId: this.userInfo.id
        })
      } catch (error) {
        console.error('菜单权限检查失败:', error)
        return false
      }
    },
    
    /**
     * 检查功能权限
     * @param {string} permission 权限标识
     * @returns {boolean} 是否有权限
     */
    hasPermission(permission) {
      if (!this.isLoggedIn || !this.userMenuPermissions) {
        return false
      }
      
      // 检查用户权限列表
      return this.userMenuPermissions.some(p => 
        p.permission === permission || p.code === permission
      )
    },
    
    /**
     * 检查角色权限
     * @param {string|Array} roles 角色或角色数组
     * @returns {boolean} 是否有权限
     */
    hasRole(roles) {
      if (!this.currentRole) {
        return false
      }
      
      if (Array.isArray(roles)) {
        return roles.includes(this.currentRole)
      }
      
      return this.currentRole === roles
    },
    
    /**
     * 检查是否为管理员
     * @returns {boolean} 是否为管理员
     */
    isAdmin() {
      return this.hasRole(['admin', 'super_admin'])
    },
    
    /**
     * 检查是否为教师
     * @returns {boolean} 是否为教师
     */
    isTeacher() {
      return this.hasRole(['teacher', 'admin', 'super_admin'])
    },
    
    /**
     * 检查是否为学生
     * @returns {boolean} 是否为学生
     */
    isStudent() {
      return this.hasRole('student')
    },
    
    /**
     * 检查是否为游客
     * @returns {boolean} 是否为游客
     */
    isGuest() {
      return !this.isLoggedIn || this.hasRole('guest')
    },
    
    /**
     * 权限验证失败处理
     * @param {string} message 提示信息
     */
    handlePermissionDenied(message = '您没有权限执行此操作') {
      uni.showModal({
        title: '权限不足',
        content: message,
        showCancel: false,
        confirmText: '确定'
      })
    },
    
    /**
     * 需要登录提示
     */
    requireLogin() {
      uni.showModal({
        title: '需要登录',
        content: '请先登录后再进行操作',
        confirmText: '去登录',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            uni.navigateTo({
              url: '/pages/login/login'
            })
          }
        }
      })
    },
    
    /**
     * 安全导航 - 带权限检查的页面跳转
     * @param {Object} options 导航选项
     * @param {string} options.url 目标页面路径
     * @param {string} options.method 导航方法 (navigateTo|redirectTo|reLaunch|switchTab)
     * @param {boolean} options.checkPermission 是否检查权限
     */
    async safeNavigate(options) {
      const { 
        url, 
        method = 'navigateTo', 
        checkPermission = true,
        ...otherOptions 
      } = options
      
      try {
        // 权限检查
        if (checkPermission) {
          const hasPermission = await this.checkPagePermission(url)
          if (!hasPermission) {
            return false
          }
        }
        
        // 执行导航
        const navigateMethod = uni[method]
        if (typeof navigateMethod === 'function') {
          return navigateMethod({
            url,
            ...otherOptions
          })
        } else {
          console.error('无效的导航方法:', method)
          return false
        }
      } catch (error) {
        console.error('安全导航失败:', error)
        return false
      }
    },
    
    /**
     * 初始化页面权限
     */
    async initPagePermission() {
      try {
        // 检查当前页面权限
        const hasPermission = await this.checkPagePermission(this.currentPagePath)
        
        if (!hasPermission) {
          // 权限不足，返回上一页或首页
          const pages = getCurrentPages()
          if (pages.length > 1) {
            uni.navigateBack()
          } else {
            uni.reLaunch({
              url: '/pages/index/index'
            })
          }
          return false
        }
        
        return true
      } catch (error) {
        console.error('页面权限初始化失败:', error)
        return false
      }
    }
  },
  
  // 页面生命周期
  async onLoad() {
    // 在页面加载时检查权限
    await this.initPagePermission()
  }
}