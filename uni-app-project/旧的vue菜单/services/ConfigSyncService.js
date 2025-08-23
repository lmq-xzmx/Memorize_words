/**
 * 配置同步服务
 * 负责前后端配置的同步和一致性维护
 */

import api from '../utils/api.js'
import { MENU_ITEMS, ROLE_PERMISSION_INHERITANCE, PAGE_PERMISSIONS } from '../config/menuConfig.js'
import permissionService from './PermissionService.js'
import menuDataService from './MenuDataService.js'

class ConfigSyncService {
  constructor() {
    this.syncInProgress = false
    this.lastSyncTime = null
    this.syncInterval = 5 * 60 * 1000 // 5分钟同步一次
    this.configDifferences = []
    this.initialized = false
  }

  /**
   * 初始化配置同步服务
   */
  async init() {
    if (this.initialized) {
      console.log('配置同步服务已初始化')
      return
    }

    try {
      console.log('🔄 初始化配置同步服务...')
      this.initialized = true
      console.log('✅ 配置同步服务初始化完成')
    } catch (error) {
      console.error('❌ 配置同步服务初始化失败:', error)
      this.initialized = false
      throw error
    }
  }

  /**
   * 启动配置同步
   */
  async startSync() {
    if (this.syncInProgress) {
      console.log('配置同步已在进行中')
      return
    }

    try {
      await this.performSync()
      this.scheduleNextSync()
    } catch (error) {
      console.error('配置同步启动失败:', error)
    }
  }

  /**
   * 执行配置同步
   */
  async performSync() {
    this.syncInProgress = true
    console.log('开始配置同步...')

    try {
      // 1. 同步菜单配置
      await this.syncMenuConfig()
      
      // 2. 同步权限配置
      await this.syncPermissionConfig()
      
      // 3. 同步页面权限配置
      await this.syncPagePermissionConfig()
      
      // 4. 验证配置一致性
      await this.validateConfigConsistency()
      
      this.lastSyncTime = Date.now()
      console.log('配置同步完成')
      
    } catch (error) {
      console.error('配置同步失败:', error)
      throw error
    } finally {
      this.syncInProgress = false
    }
  }

  // API端点配置
  static API_ENDPOINTS = {
    MENU_CONFIG: '/permissions/api/menu-config/',
    ROLE_PERMISSIONS: '/permissions/api/role-permissions/',
    PAGE_PERMISSIONS: '/permissions/api/page-permissions/',
    USER_PERMISSIONS: '/permissions/api/user-permissions/'
  };

  /**
   * 同步菜单配置
   */
  async syncMenuConfig() {
    try {
      const response = await api.get(ConfigSyncService.API_ENDPOINTS.MENU_CONFIG)
      const backendMenus = response.data
      
      if (!Array.isArray(backendMenus)) {
        console.warn('后端菜单配置格式无效，使用前端配置')
        return
      }
      
      // 比较前后端菜单配置
      const differences = this.compareMenuConfigs(MENU_ITEMS, backendMenus)
      
      if (differences.length > 0) {
        console.warn('发现菜单配置差异:', differences)
        this.configDifferences.push(...differences)
        
        // 可选：自动更新前端配置或提示用户
        await this.handleMenuConfigDifferences(differences)
      }
      
    } catch (error) {
      console.warn('同步菜单配置失败，使用前端配置:', error.message)
      // 如果后端不可用，使用前端配置
    }
  }

  /**
   * 同步权限配置
   */
  async syncPermissionConfig() {
    try {
      const response = await api.get(ConfigSyncService.API_ENDPOINTS.ROLE_PERMISSIONS)
      const backendPermissions = response.data
      
      if (!backendPermissions || typeof backendPermissions !== 'object') {
        console.warn('后端权限配置格式无效，使用前端配置')
        return
      }
      
      // 比较前后端权限配置
      const differences = this.comparePermissionConfigs(
        ROLE_PERMISSION_INHERITANCE, 
        backendPermissions
      )
      
      if (differences.length > 0) {
        console.warn('发现权限配置差异:', differences)
        this.configDifferences.push(...differences)
        
        await this.handlePermissionConfigDifferences(differences)
      }
      
    } catch (error) {
      console.warn('同步权限配置失败，使用前端配置:', error.message)
    }
  }

  /**
   * 同步页面权限配置
   */
  async syncPagePermissionConfig() {
    try {
      const response = await api.get(ConfigSyncService.API_ENDPOINTS.PAGE_PERMISSIONS)
      const backendPagePermissions = response.data
      
      if (!backendPagePermissions || typeof backendPagePermissions !== 'object') {
        console.warn('后端页面权限配置格式无效，使用前端配置')
        return
      }
      
      const differences = this.comparePagePermissionConfigs(
        PAGE_PERMISSIONS, 
        backendPagePermissions
      )
      
      if (differences.length > 0) {
        console.warn('发现页面权限配置差异:', differences)
        this.configDifferences.push(...differences)
        
        await this.handlePagePermissionConfigDifferences(differences)
      }
      
    } catch (error) {
      console.warn('同步页面权限配置失败，使用前端配置:', error.message)
    }
  }

  /**
   * 比较菜单配置
   */
  compareMenuConfigs(frontendMenus, backendMenus) {
    const differences = []
    
    // 创建后端菜单映射
    const backendMenuMap = new Map()
    backendMenus.forEach(menu => {
      backendMenuMap.set(menu.id || menu.path, menu)
    })
    
    // 检查前端菜单在后端是否存在
    Object.values(frontendMenus).flat().forEach(menu => {
      const backendMenu = backendMenuMap.get(menu.id)
      
      if (!backendMenu) {
        differences.push({
          type: 'menu_missing_in_backend',
          item: menu,
          message: `前端菜单 ${menu.id} 在后端不存在`
        })
      } else {
        // 检查菜单属性差异
        const menuDiffs = this.compareMenuItems(menu, backendMenu)
        differences.push(...menuDiffs)
      }
    })
    
    return differences
  }

  /**
   * 比较单个菜单项
   */
  compareMenuItems(frontendMenu, backendMenu) {
    const differences = []
    const fieldsToCompare = ['title', 'path', 'permission', 'category']
    
    fieldsToCompare.forEach(field => {
      if (frontendMenu[field] !== backendMenu[field]) {
        differences.push({
          type: 'menu_field_mismatch',
          menuId: frontendMenu.id,
          field,
          frontend: frontendMenu[field],
          backend: backendMenu[field],
          message: `菜单 ${frontendMenu.id} 的 ${field} 字段不匹配`
        })
      }
    })
    
    return differences
  }

  /**
   * 比较权限配置
   */
  comparePermissionConfigs(frontendPermissions, backendPermissions) {
    const differences = []
    
    if (!frontendPermissions || !backendPermissions) {
      console.warn('权限配置数据不完整，跳过比较')
      return differences
    }
    
    Object.keys(frontendPermissions).forEach(role => {
      const frontendRolePerms = frontendPermissions[role]
      const backendRolePerms = backendPermissions[role]
      
      if (!Array.isArray(frontendRolePerms)) {
        console.warn(`前端角色 ${role} 权限配置格式无效`)
        return
      }
      
      if (!backendRolePerms) {
        differences.push({
          type: 'role_missing_in_backend',
          role,
          message: `角色 ${role} 在后端不存在`
        })
      } else if (Array.isArray(backendRolePerms)) {
        const permDiffs = this.compareArrays(
          frontendRolePerms, 
          backendRolePerms,
          `角色 ${role} 权限`
        )
        differences.push(...permDiffs)
      } else {
        console.warn(`后端角色 ${role} 权限配置格式无效`)
      }
    })
    
    return differences
  }

  /**
   * 比较页面权限配置
   */
  comparePagePermissionConfigs(frontendPagePerms, backendPagePerms) {
    const differences = []
    
    if (!frontendPagePerms || !backendPagePerms) {
      console.warn('页面权限配置数据不完整，跳过比较')
      return differences
    }
    
    Object.keys(frontendPagePerms).forEach(page => {
      const frontendPerm = frontendPagePerms[page]
      const backendPerm = backendPagePerms[page]
      
      if (frontendPerm && backendPerm && frontendPerm !== backendPerm) {
        differences.push({
          type: 'page_permission_mismatch',
          page,
          frontend: frontendPerm,
          backend: backendPerm,
          message: `页面 ${page} 权限配置不匹配`
        })
      }
    })
    
    return differences
  }

  /**
   * 比较数组
   */
  compareArrays(arr1, arr2, context) {
    const differences = []
    
    const set1 = new Set(arr1)
    const set2 = new Set(arr2)
    
    // 检查前端有但后端没有的项
    set1.forEach(item => {
      if (!set2.has(item)) {
        differences.push({
          type: 'item_missing_in_backend',
          context,
          item,
          message: `${context}: ${item} 在后端不存在`
        })
      }
    })
    
    // 检查后端有但前端没有的项
    set2.forEach(item => {
      if (!set1.has(item)) {
        differences.push({
          type: 'item_missing_in_frontend',
          context,
          item,
          message: `${context}: ${item} 在前端不存在`
        })
      }
    })
    
    return differences
  }

  /**
   * 处理菜单配置差异
   */
  async handleMenuConfigDifferences(differences) {
    // 可以选择自动修复或提示用户
    console.log('处理菜单配置差异:', differences)
    
    // 清除菜单缓存，强制重新获取
    menuDataService.clearAllCache()
  }

  /**
   * 处理权限配置差异
   */
  async handlePermissionConfigDifferences(differences) {
    console.log('处理权限配置差异:', differences)
    
    // 清除权限缓存
    permissionService.clearAllCache()
  }

  /**
   * 处理页面权限配置差异
   */
  async handlePagePermissionConfigDifferences(differences) {
    console.log('处理页面权限配置差异:', differences)
  }

  /**
   * 验证配置一致性
   */
  async validateConfigConsistency() {
    const user = permissionService.getCurrentUser()
    if (!user || !user.id || !user.role) {
      console.warn('用户信息不完整，跳过配置一致性验证')
      return
    }
    
    // 验证用户权限是否一致
    const frontendPermissions = permissionService.getUserPermissions(user.role)
    
    try {
      const response = await api.get(`${ConfigSyncService.API_ENDPOINTS.USER_PERMISSIONS}${user.id}/`)
      const backendData = response.data
      
      if (!backendData || !Array.isArray(backendData.permissions)) {
        console.warn('后端用户权限数据格式无效，跳过一致性验证')
        return
      }
      
      const backendPermissions = backendData.permissions
      
      const permissionDiffs = this.compareArrays(
        frontendPermissions,
        backendPermissions,
        '用户权限'
      )
      
      if (permissionDiffs.length > 0) {
        console.warn('用户权限不一致:', permissionDiffs)
        this.configDifferences.push(...permissionDiffs)
      }
      
    } catch (error) {
      console.warn('验证用户权限一致性失败，跳过验证:', error.message)
    }
  }

  /**
   * 调度下次同步
   */
  scheduleNextSync() {
    setTimeout(() => {
      this.startSync()
    }, this.syncInterval)
  }

  /**
   * 获取配置差异报告
   */
  getConfigDifferences() {
    return {
      differences: this.configDifferences,
      lastSyncTime: this.lastSyncTime,
      totalDifferences: this.configDifferences.length
    }
  }

  /**
   * 清除配置差异记录
   */
  clearConfigDifferences() {
    this.configDifferences = []
  }

  /**
   * 手动触发同步
   */
  async forcSync() {
    this.clearConfigDifferences()
    await this.performSync()
  }
}

const configSyncService = new ConfigSyncService()

// 在权限服务初始化后启动配置同步
if (typeof window !== 'undefined') {
  window.configSyncService = configSyncService
  
  // 监听用户登录事件，触发配置同步
  permissionService.addPermissionListener((user) => {
    if (user) {
      configSyncService.startSync()
    }
  })
}

export default configSyncService

export const {
  startSync,
  performSync,
  getConfigDifferences,
  clearConfigDifferences,
  forcSync
} = configSyncService