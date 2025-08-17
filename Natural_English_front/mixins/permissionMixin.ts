// Vue权限混入 - 简化版
// 提供基础权限检查功能

import { defineComponent } from 'vue'

// 基础权限导入
import {
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  PAGE_PERMISSIONS,
  canAccessPage,
  isAuthenticated,
  getCurrentUser,
  getRoleDisplayName
} from '../utils/permission'

// 用户信息接口
interface UserInfo {
  id: string
  username: string
  role: string
}

export default defineComponent({
  name: 'PermissionMixin',
  
  data() {
    return {
      userInfo: null as UserInfo | null
    }
  },
  
  computed: {
    // 检查用户是否已认证
    isUserAuthenticated(): boolean {
      return this.userInfo !== null
    },
    
    // 获取当前用户角色显示名称
    roleDisplayName(): string {
      if (!this.userInfo) return '未登录'
      return getRoleDisplayName(this.userInfo.role)
    }
  },
  
  methods: {
    // 检查是否有指定权限
    $hasPermission(permission: string): boolean {
      if (!this.userInfo) return false
      return hasPermission(this.userInfo.role, permission)
    },
    
    // 检查是否有任一权限
    $hasAnyPermission(permissions: string[]): boolean {
      if (!this.userInfo) return false
      return hasAnyPermission(this.userInfo.role, permissions)
    },
    
    // 检查是否有所有权限
    $hasAllPermissions(permissions: string[]): boolean {
      if (!this.userInfo) return false
      return hasAllPermissions(this.userInfo.role, permissions)
    },
    
    // 检查是否可以访问页面
    $canAccessPage(path: string): boolean {
      if (!this.userInfo) return false
      return canAccessPage(this.userInfo.role, path)
    },
    
    // 检查用户是否已认证
    async $isAuthenticated(): Promise<boolean> {
      return await isAuthenticated()
    },
    
    // 更新用户信息
    async $updateUserInfo(): Promise<void> {
      try {
        const user = getCurrentUser()
        if (user) {
          this.userInfo = {
            id: user.id || user.user_id || '',
            username: user.username,
            role: user.role
          }
        } else {
          this.userInfo = null
        }
      } catch (error) {
        console.error('更新用户信息失败:', error)
        this.userInfo = null
      }
    }
  },
  
  async created() {
    // 组件创建时更新用户信息
    await this.$updateUserInfo()
  }
})

// 权限指令
export const permissionDirective = {
  mounted(el: HTMLElement, binding: any) {
    // 简化的权限指令实现
    if (!binding.value) {
      el.style.display = 'none'
    }
  },
  
  updated(el: HTMLElement, binding: any) {
    if (!binding.value) {
      el.style.display = 'none'
    } else {
      el.style.display = ''
    }
  }
}

// 角色指令
export const roleDirective = {
  mounted(el: HTMLElement, binding: any) {
    // 简化的角色指令实现
    if (!binding.value) {
      el.style.display = 'none'
    }
  },
  
  updated(el: HTMLElement, binding: any) {
    if (!binding.value) {
      el.style.display = 'none'
    } else {
      el.style.display = ''
    }
  }
}

export type { UserInfo }