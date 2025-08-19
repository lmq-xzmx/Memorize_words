/**
 * 权限指令 - v-permission
 * 用于组件级别的权限控制
 */

// Vue 3 权限指令
import { PermissionCache } from '@/services/permissionCacheService'
import { ElMessage } from 'element-plus'
import { usePermissionDirective } from '@/composables/usePermission'

// 权限指令接口
interface PermissionBinding {
  value: string | string[] | {
    permissions: string | string[]
    mode?: 'all' | 'any'
    fallback?: 'hide' | 'disable' | 'readonly'
    showTooltip?: boolean
    tooltipText?: string
  }
  arg?: string // 可选参数，如 v-permission:button="'user.create'"
  modifiers?: {
    hide?: boolean
    disable?: boolean
    readonly?: boolean
    tooltip?: boolean
  }
}

// 获取用户ID的辅助函数
function getUserId(): string | null {
  try {
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    return (userInfo.id || userInfo.user_id)?.toString() || null
  } catch {
    return null
  }
}

// 权限检查函数
async function checkPermissions(
  permissions: string | string[],
  mode: 'all' | 'any' = 'all'
): Promise<boolean> {
  const userId = getUserId()
  if (!userId) {
    console.warn('[v-permission] 无法获取用户ID')
    return false
  }

  const permissionList = Array.isArray(permissions) ? permissions : [permissions]
  
  try {
    if (mode === 'any') {
      // 任一权限满足即可
      const results = await Promise.all(
        permissionList.map(permission => 
          PermissionCache.checkComponent(permission, userId)
        )
      )
      return results.some(result => result)
    } else {
      // 所有权限都必须满足
      const results = await Promise.all(
        permissionList.map(permission => 
          PermissionCache.checkComponent(permission, userId)
        )
      )
      return results.every(result => result)
    }
  } catch (error) {
    console.error('[v-permission] 权限检查失败:', error)
    return false
  }
}

// 处理元素的权限状态
function handleElementPermission(
  el: HTMLElement,
  hasPermission: boolean,
  binding: PermissionBinding
) {
  const { modifiers = {}, value } = binding
  
  // 解析配置
  let fallback: 'hide' | 'disable' | 'readonly' = 'hide'
  let showTooltip = false
  let tooltipText = '权限不足'
  
  if (typeof value === 'object' && !Array.isArray(value)) {
    fallback = value.fallback || 'hide'
    showTooltip = value.showTooltip || false
    tooltipText = value.tooltipText || '权限不足'
  }
  
  // 修饰符优先级更高
  if (modifiers.hide) fallback = 'hide'
  if (modifiers.disable) fallback = 'disable'
  if (modifiers.readonly) fallback = 'readonly'
  if (modifiers.tooltip) showTooltip = true
  
  if (hasPermission) {
    // 有权限时恢复元素状态
    el.style.display = ''
    el.removeAttribute('disabled')
    el.removeAttribute('readonly')
    el.removeAttribute('title')
    el.classList.remove('permission-denied')
  } else {
    // 无权限时根据配置处理
    switch (fallback) {
      case 'hide':
        el.style.display = 'none'
        break
      case 'disable':
        el.setAttribute('disabled', 'true')
        if (el.tagName === 'BUTTON' || el.tagName === 'INPUT') {
          (el as HTMLButtonElement | HTMLInputElement).disabled = true
        }
        el.classList.add('permission-denied')
        break
      case 'readonly':
        el.setAttribute('readonly', 'true')
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          (el as HTMLInputElement | HTMLTextAreaElement).readOnly = true
        }
        el.classList.add('permission-denied')
        break
    }
    
    // 添加提示
    if (showTooltip) {
      el.setAttribute('title', tooltipText)
    }
    
    // 添加点击事件处理（可选）
    if (!el.dataset.permissionClickHandlerAdded) {
      el.addEventListener('click', (e) => {
        if (!hasPermission) {
          e.preventDefault()
          e.stopPropagation()
          if (showTooltip) {
            ElMessage.warning(tooltipText)
          }
        }
      })
      el.dataset.permissionClickHandlerAdded = 'true'
    }
  }
}

// 权限指令实现
export const permission = {
  async mounted(el: HTMLElement, binding: any) {
    const { value, modifiers = {} } = binding
    
    if (!value) {
      console.warn('[v-permission] 权限值不能为空')
      return
    }
    
    // 解析权限配置
    let permissions: string | string[]
    let mode: 'all' | 'any' = 'all'
    
    if (typeof value === 'string') {
      permissions = value
    } else if (Array.isArray(value)) {
      permissions = value
    } else if (typeof value === 'object') {
      permissions = value.permissions
      mode = value.mode || 'all'
    } else {
      console.warn('[v-permission] 无效的权限配置')
      return
    }
    
    try {
      // 检查权限
      const hasPermission = await checkPermissions(permissions, mode)
      
      // 处理元素状态
      handleElementPermission(el, hasPermission, { value, modifiers })
      
      // 存储权限状态到元素上，供后续更新使用
      el.dataset.permissionValue = JSON.stringify({ permissions, mode })
      el.dataset.hasPermission = hasPermission.toString()
      
    } catch (error) {
      console.error('[v-permission] 权限检查失败:', error)
      // 权限检查失败时，为了安全起见，隐藏元素
      handleElementPermission(el, false, { value, modifiers })
    }
  },
  
  async updated(el: HTMLElement, binding: any) {
    const { value, modifiers = {} } = binding
    
    if (!value) {
      return
    }
    
    // 检查权限配置是否发生变化
    let permissions: string | string[]
    let mode: 'all' | 'any' = 'all'
    
    if (typeof value === 'string') {
      permissions = value
    } else if (Array.isArray(value)) {
      permissions = value
    } else if (typeof value === 'object') {
      permissions = value.permissions
      mode = value.mode || 'all'
    } else {
      return
    }
    
    const newConfig = JSON.stringify({ permissions, mode })
    const oldConfig = el.dataset.permissionValue
    
    // 如果权限配置没有变化，跳过检查
    if (newConfig === oldConfig) {
      return
    }
    
    try {
      // 重新检查权限
      const hasPermission = await checkPermissions(permissions, mode)
      
      // 更新元素状态
      handleElementPermission(el, hasPermission, { value, modifiers })
      
      // 更新存储的权限状态
      el.dataset.permissionValue = newConfig
      el.dataset.hasPermission = hasPermission.toString()
      
    } catch (error) {
      console.error('[v-permission] 权限更新检查失败:', error)
      handleElementPermission(el, false, { value, modifiers })
    }
  },
  
  unmounted(el: HTMLElement) {
    // 清理数据
    delete el.dataset.permissionValue
    delete el.dataset.hasPermission
    delete el.dataset.permissionClickHandlerAdded
  }
}

// 权限刷新函数 - 可以手动调用来刷新页面上所有权限指令
export async function refreshAllPermissions(): Promise<void> {
  const elements = document.querySelectorAll('[data-permission-value]')
  
  for (const el of elements) {
    const htmlEl = el as HTMLElement
    const configStr = htmlEl.dataset.permissionValue
    
    if (!configStr) continue
    
    try {
      const { permissions, mode } = JSON.parse(configStr)
      const hasPermission = await checkPermissions(permissions, mode)
      
      // 重新应用权限状态
      handleElementPermission(htmlEl, hasPermission, {
        value: { permissions, mode },
        modifiers: {}
      })
      
      htmlEl.dataset.hasPermission = hasPermission.toString()
    } catch (error) {
      console.error('[refreshAllPermissions] 刷新权限失败:', error)
    }
  }
}

// 导出便捷函数
export const PermissionDirective = {
  install(app: any) {
    app.directive('permission', permission)
  },
  
  // 手动刷新所有权限
  refresh: refreshAllPermissions,
  
  // 检查权限（可在组件中使用）
  check: checkPermissions
}

// 在开发环境下暴露到全局对象
if (process.env.NODE_ENV === 'development') {
  const globalWindow = window as any
  globalWindow.PermissionDirective = PermissionDirective
  globalWindow.refreshAllPermissions = refreshAllPermissions
  globalWindow.checkPermissions = checkPermissions
}

// 默认导出
export default permission