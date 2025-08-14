// 权限同步管理器
import { getCurrentUser } from './permission.js'
import { fetchUserMenuPermissions } from './dynamicPermission.js'

// 权限同步管理器类
class PermissionSyncManager {
  constructor() {
    this.listeners = []
    this.isAutoSyncEnabled = false
    this.syncInterval = null
    this.syncIntervalTime = 5 * 60 * 1000 // 5分钟
  }

  // 添加权限变更监听器
  addListener(callback) {
    this.listeners.push(callback)
  }

  // 移除权限变更监听器
  removeListener(callback) {
    const index = this.listeners.indexOf(callback)
    if (index > -1) {
      this.listeners.splice(index, 1)
    }
  }

  // 通知所有监听器
  notifyListeners(type, data) {
    this.listeners.forEach(callback => {
      try {
        callback(type, data)
      } catch (error) {
        console.error('权限同步监听器执行失败:', error)
      }
    })
  }

  // 启动自动同步
  startAutoSync() {
    if (this.isAutoSyncEnabled) {
      return
    }

    this.isAutoSyncEnabled = true
    this.syncInterval = setInterval(async () => {
      try {
        await this.syncUserPermissions()
      } catch (error) {
        console.error('自动权限同步失败:', error)
      }
    }, this.syncIntervalTime)

    console.log('权限自动同步已启动')
  }

  // 停止自动同步
  stopAutoSync() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval)
      this.syncInterval = null
    }
    this.isAutoSyncEnabled = false
    console.log('权限自动同步已停止')
  }

  // 同步用户权限
  async syncUserPermissions() {
    try {
      const user = getCurrentUser()
      if (!user) {
        console.log('用户未登录，跳过权限同步')
        return null
      }

      const permissionData = await fetchUserMenuPermissions()
      if (permissionData && permissionData.success) {
        console.log('权限同步成功:', permissionData)
        this.notifyListeners('userPermissions', permissionData)
        return permissionData
      } else {
        console.warn('权限同步失败:', permissionData)
        return null
      }
    } catch (error) {
      console.error('权限同步异常:', error)
      return null
    }
  }

  // 清除认证信息
  clearAuth() {
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    this.notifyListeners('authCleared', null)
    console.log('认证信息已清除')
  }
}

// 创建全局实例
const permissionSyncManager = new PermissionSyncManager()

// 导出便捷函数
export async function syncUserPermissions() {
  return await permissionSyncManager.syncUserPermissions()
}

export function startAutoSync() {
  permissionSyncManager.startAutoSync()
}

export function stopAutoSync() {
  permissionSyncManager.stopAutoSync()
}

export function addPermissionListener(callback) {
  permissionSyncManager.addListener(callback)
}

export function removePermissionListener(callback) {
  permissionSyncManager.removeListener(callback)
}

export function clearAuth() {
  permissionSyncManager.clearAuth()
}

// 默认导出管理器实例
export default permissionSyncManager