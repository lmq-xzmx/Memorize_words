import { getRolePermissions, hasPermission, hasAnyPermission, hasAllPermissions } from '../config/permissions'

// 权限检查类
export class PermissionChecker {
  private userPermissions: string[] = []
  private userRole: string = ''

  constructor(permissions: string[] = [], role: string = '') {
    this.userPermissions = permissions
    this.userRole = role
  }

  // 更新用户权限
  updatePermissions(permissions: string[], role: string = '') {
    this.userPermissions = permissions
    if (role) {
      this.userRole = role
    }
  }

  // 检查单个权限
  check(permission: string): boolean {
    return hasPermission(this.userPermissions, permission)
  }

  // 检查任意权限
  checkAny(permissions: string[]): boolean {
    return hasAnyPermission(this.userPermissions, permissions)
  }

  // 检查所有权限
  checkAll(permissions: string[]): boolean {
    return hasAllPermissions(this.userPermissions, permissions)
  }

  // 检查角色
  hasRole(role: string): boolean {
    return this.userRole === role
  }

  // 检查是否为管理员
  isAdmin(): boolean {
    return this.hasRole('admin')
  }

  // 检查是否为教师
  isTeacher(): boolean {
    return this.hasRole('teacher')
  }

  // 检查是否为学生
  isStudent(): boolean {
    return this.hasRole('student')
  }

  // 获取用户权限列表
  getPermissions(): string[] {
    return [...this.userPermissions]
  }

  // 获取用户角色
  getRole(): string {
    return this.userRole
  }
}

// 全局权限检查器实例
export const permissionChecker = new PermissionChecker()

// 权限装饰器（用于组件方法）
export function requirePermission(permission: string) {
  return function (_target: any, _propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value
    
    descriptor.value = function (...args: any[]) {
      if (!permissionChecker.check(permission)) {
        throw new Error(`权限不足: 需要 ${permission} 权限`)
      }
      return originalMethod.apply(this, args)
    }
    
    return descriptor
  }
}

// 权限指令工具函数
export const createPermissionDirective = () => {
  return {
    mounted(el: HTMLElement, binding: any) {
      const { value } = binding
      
      if (!value) {
        return
      }
      
      let hasPermissionFlag = false
      
      if (typeof value === 'string') {
        // 单个权限
        hasPermissionFlag = permissionChecker.check(value)
      } else if (Array.isArray(value)) {
        // 多个权限（默认需要所有权限）
        hasPermissionFlag = permissionChecker.checkAll(value)
      } else if (typeof value === 'object') {
        // 对象形式，支持 any 和 all 模式
        const { permissions, mode = 'all' } = value
        
        if (mode === 'any') {
          hasPermissionFlag = permissionChecker.checkAny(permissions)
        } else {
          hasPermissionFlag = permissionChecker.checkAll(permissions)
        }
      }
      
      if (!hasPermissionFlag) {
        // 移除元素或隐藏
        el.style.display = 'none'
        // 或者完全移除: el.parentNode?.removeChild(el)
      }
    },
    
    updated(el: HTMLElement, binding: any) {
      // 权限更新时重新检查
      const { value } = binding
      
      if (!value) {
        el.style.display = ''
        return
      }
      
      let hasPermissionFlag = false
      
      if (typeof value === 'string') {
        hasPermissionFlag = permissionChecker.check(value)
      } else if (Array.isArray(value)) {
        hasPermissionFlag = permissionChecker.checkAll(value)
      } else if (typeof value === 'object') {
        const { permissions, mode = 'all' } = value
        
        if (mode === 'any') {
          hasPermissionFlag = permissionChecker.checkAny(permissions)
        } else {
          hasPermissionFlag = permissionChecker.checkAll(permissions)
        }
      }
      
      el.style.display = hasPermissionFlag ? '' : 'none'
    }
  }
}

// 路由权限检查
export const checkRoutePermission = (to: any, userPermissions: string[]): boolean => {
  // 如果路由没有定义权限要求，则允许访问
  if (!to.meta?.permission) {
    return true
  }
  
  const requiredPermission = to.meta.permission
  
  if (typeof requiredPermission === 'string') {
    return hasPermission(userPermissions, requiredPermission)
  }
  
  if (Array.isArray(requiredPermission)) {
    // 默认需要所有权限
    return hasAllPermissions(userPermissions, requiredPermission)
  }
  
  if (typeof requiredPermission === 'object') {
    const { permissions, mode = 'all' } = requiredPermission
    
    if (mode === 'any') {
      return hasAnyPermission(userPermissions, permissions)
    } else {
      return hasAllPermissions(userPermissions, permissions)
    }
  }
  
  return false
}

// 菜单权限过滤
export const filterMenuByPermissions = (menuItems: any[], userPermissions: string[]): any[] => {
  return menuItems.filter(item => {
    // 检查当前菜单项权限
    if (item.permission && !hasPermission(userPermissions, item.permission)) {
      return false
    }
    
    // 递归过滤子菜单
    if (item.children && item.children.length > 0) {
      item.children = filterMenuByPermissions(item.children, userPermissions)
      // 如果子菜单全部被过滤掉，且当前菜单项没有直接路径，则隐藏当前菜单项
      if (item.children.length === 0 && !item.path) {
        return false
      }
    }
    
    return true
  })
}

// 权限错误处理
export const handlePermissionError = (permission: string, action: string = '执行此操作') => {
  console.warn(`权限不足: 需要 ${permission} 权限才能${action}`)
  
  // 可以在这里添加用户友好的提示
  // 例如显示 toast 消息或跳转到权限申请页面
  
  return {
    success: false,
    message: `权限不足: 需要 ${permission} 权限才能${action}`,
    code: 'PERMISSION_DENIED'
  }
}

// 权限缓存管理
class PermissionCache {
  private cache = new Map<string, boolean>()
  private cacheTimeout = 5 * 60 * 1000 // 5分钟缓存
  private timestamps = new Map<string, number>()

  set(key: string, value: boolean) {
    this.cache.set(key, value)
    this.timestamps.set(key, Date.now())
  }

  get(key: string): boolean | null {
    const timestamp = this.timestamps.get(key)
    if (!timestamp || Date.now() - timestamp > this.cacheTimeout) {
      this.cache.delete(key)
      this.timestamps.delete(key)
      return null
    }
    return this.cache.get(key) ?? null
  }

  clear() {
    this.cache.clear()
    this.timestamps.clear()
  }

  // 清理过期缓存
  cleanup() {
    const now = Date.now()
    for (const entry of Array.from(this.timestamps.entries())) {
      const [key, timestamp] = entry
      if (now - timestamp > this.cacheTimeout) {
        this.cache.delete(key)
        this.timestamps.delete(key)
      }
    }
  }
}

export const permissionCache = new PermissionCache()

// 定期清理缓存
setInterval(() => {
  permissionCache.cleanup()
}, 60 * 1000) // 每分钟清理一次