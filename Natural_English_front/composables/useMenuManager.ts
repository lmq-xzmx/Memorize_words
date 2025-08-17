/**
 * 菜单管理器 Composable
 * 统一管理菜单状态、权限检查、位置计算等逻辑
 */

import { ref, reactive, computed, nextTick, onMounted, onUnmounted, Ref, ComputedRef } from 'vue'
import { useRouter, Router } from 'vue-router'
import { calculatePopupPosition, calculateSubmenuPosition, createPositionObserver } from '../utils/menuPositioning'
import { getCurrentUser, isAuthenticated } from '../utils/permission'
import { hasPermission, fetchUserMenuPermissions } from '../utils/dynamicPermission'

// 类型定义
interface UserInfo {
  id?: string | number;
  user_id?: string | number;
  username?: string;
  email?: string;
  role?: string;
}

interface MenuPosition {
  top: number;
  left: number;
  width?: number;
  height?: number;
}

interface MenuManagerReturn {
  activeMenu: Ref<string | null>;
  activeSubmenu: Ref<string | null>;
  menuPositions: Record<string, MenuPosition>;
  userInfo: Ref<UserInfo | null>;
  userAuthState: Ref<boolean>;
  isUserLoggedIn: ComputedRef<boolean>;
  currentUserId: ComputedRef<string | number | null>;
  updateUserState: () => Promise<void>;
  loadDynamicMenuPermissions: () => Promise<void>;
  checkMenuPermission: (menuKey: string) => boolean;
  setActiveMenu: (menuKey: string | null) => void;
  setActiveSubmenu: (submenuKey: string | null) => void;
  calculateMenuPosition: (element: HTMLElement, menuKey: string) => void;
  calculateSubmenuPosition: (element: HTMLElement, submenuKey: string) => void;
  clearMenuPositions: () => void;
  initializePositionObserver: () => void;
  cleanup: () => void;
}

export function useMenuManager(): MenuManagerReturn {
  const router: Router = useRouter()
  
  // 菜单状态
  const activeMenu: Ref<string | null> = ref(null)
  const activeSubmenu: Ref<string | null> = ref(null)
  const menuPositions: Record<string, MenuPosition> = reactive({})
  const userInfo: Ref<UserInfo | null> = ref(null)
  const userAuthState: Ref<boolean> = ref(false)
  
  // 位置观察器清理函数
  let positionCleanup: (() => void) | null = null
  
  // 计算属性
  const isUserLoggedIn = computed(() => {
    return userAuthState.value && userInfo.value
  })
  
  const currentUserId = computed(() => {
    return userInfo.value?.id || userInfo.value?.user_id || null
  })
  
  // 更新用户状态
  const updateUserState = async () => {
    try {
      userInfo.value = getCurrentUser()
      userAuthState.value = await isAuthenticated()
      
      if (userInfo.value && userAuthState.value) {
        await loadDynamicMenuPermissions()
      }
    } catch (error) {
      console.error('更新用户状态失败:', error)
      userInfo.value = null
      userAuthState.value = false
    }
  }
  
  // 加载动态菜单权限
  const loadDynamicMenuPermissions = async (): Promise<void> => {
    try {
      const permissionData = await fetchUserMenuPermissions()
      if (permissionData && Array.isArray(permissionData)) {
        // 可以在这里处理权限数据
        console.log('动态菜单权限加载成功:', permissionData)
      }
    } catch (error) {
      console.error('加载动态菜单权限失败:', error)
    }
  }
  
  // 计算菜单位置
  const calculateMenuPosition = async (menuType: string, triggerRef: Ref<HTMLElement | null>, options: any = {}): Promise<void> => {
    await nextTick()
    
    if (!triggerRef?.value) {
      console.warn(`${menuType} 触发元素不存在`)
      return
    }
    
    const position = calculatePopupPosition(triggerRef.value, {
      menuWidth: options.width || 200,
      placement: options.placement || 'top',
      offset: options.offset || 12,
      ...options
    }) as MenuPosition
    
    menuPositions[menuType] = position
  }
  
  // 计算子菜单位置 - 重构版本
  const calculateSubmenuPositionLocal = async (submenuType: string, parentMenuElement: Element, options: any = {}): Promise<void> => {
    await nextTick()
    
    // 直接接受DOM元素而不是选择器字符串
    if (!parentMenuElement) {
      console.warn(`${submenuType} 父菜单元素不存在`)
      return
    }
    
    // 检查是否为有效的DOM元素
    if (!(parentMenuElement instanceof Element)) {
      console.warn(`${submenuType} 父菜单参数必须是DOM元素`)
      return
    }
    
    try {
      // 使用calculateSubmenuPosition工具函数计算位置
      const position = calculateSubmenuPosition(parentMenuElement, {
        menuWidth: options.width || 320,
        offset: options.offset || 12,
        ...options
      }) as MenuPosition
      
      menuPositions[submenuType] = position
      console.log(`${submenuType} 子菜单位置计算完成:`, position)
    } catch (error) {
      console.error(`${submenuType} 位置计算失败:`, error)
    }
  }
  
  // 打开菜单
  const openMenu = async (menuType: string, triggerRef: Ref<HTMLElement | null>, options: any = {}): Promise<void> => {
    // 如果当前菜单已经是要打开的菜单，则关闭
    if (activeMenu.value === menuType) {
      closeMenu()
      return
    }
    
    // 关闭其他菜单
    closeSubmenu()
    
    // 打开新菜单
    activeMenu.value = menuType
    
    // 计算位置
    await calculateMenuPosition(menuType, triggerRef, options)
    
    // 设置位置观察器
    if (triggerRef?.value) {
      positionCleanup = createPositionObserver(triggerRef.value, () => {
        calculateMenuPosition(menuType, triggerRef, options)
      })
    }
  }
  
  // 打开子菜单 - 重构版本
  const openSubmenu = async (submenuType, parentMenuElement, options = {}) => {
    try {
      activeSubmenu.value = submenuType
      await calculateSubmenuPositionLocal(submenuType, parentMenuElement, options)
      console.log(`子菜单 ${submenuType} 已打开`)
    } catch (error) {
      console.error(`打开子菜单 ${submenuType} 失败:`, error)
      activeSubmenu.value = null
    }
  }
  
  // 关闭菜单
  const closeMenu = () => {
    activeMenu.value = null
    closeSubmenu()
    
    // 清理位置观察器
    if (positionCleanup) {
      positionCleanup()
      positionCleanup = null
    }
  }
  
  // 关闭子菜单
  const closeSubmenu = () => {
    activeSubmenu.value = null
  }
  
  // 切换菜单
  const toggleMenu = async (menuType, triggerRef, options = {}) => {
    if (activeMenu.value === menuType) {
      closeMenu()
    } else {
      await openMenu(menuType, triggerRef, options)
    }
  }
  
  // 切换子菜单 - 重构版本
  const toggleSubmenu = async (submenuType, parentMenuElementOrType, options = {}) => {
    try {
      if (activeSubmenu.value === submenuType) {
        closeSubmenu()
      } else {
        let parentMenuElement = parentMenuElementOrType
        
        // 如果传入的是字符串（菜单类型），则查找对应的DOM元素
        if (typeof parentMenuElementOrType === 'string') {
          const menuType = parentMenuElementOrType
          console.log(`查找菜单类型 ${menuType} 的DOM元素`)
          
          // 尝试多种选择器查找菜单元素
          const selectors = [
            `[data-menu-type="${menuType}"]`,
            `.base-menu--dropdown[data-menu-type="${menuType}"]`,
            `.${menuType}-menu`,
            `.menu-overlay .base-menu`
          ]
          
          for (const selector of selectors) {
            try {
              parentMenuElement = document.querySelector(selector)
              if (parentMenuElement) {
                console.log(`找到菜单元素，使用选择器: ${selector}`)
                break
              }
            } catch (error) {
              console.warn(`选择器 ${selector} 查找失败:`, error)
            }
          }
          
          // 如果还是找不到，尝试通过类名查找
          if (!parentMenuElement) {
            const allMenus = document.querySelectorAll('.base-menu--dropdown, .base-menu')
            for (const menu of allMenus) {
              if (menu.getAttribute('data-menu-type') === menuType || 
                  menu.classList.contains(`${menuType}-menu`)) {
                parentMenuElement = menu
                console.log(`通过遍历找到菜单元素: ${menuType}`)
                break
              }
            }
          }
        }
        
        if (!parentMenuElement) {
          console.error(`无法找到父菜单元素: ${parentMenuElementOrType}`)
          return
        }
        
        await openSubmenu(submenuType, parentMenuElement, options)
      }
    } catch (error) {
      console.error(`切换子菜单 ${submenuType} 失败:`, error)
    }
  }
  
  // 权限检查 - 修复版本
  const checkPermission = async (permission) => {
    try {
      if (!isUserLoggedIn.value) {
        return false
      }
      
      // 获取用户角色
      const user = getCurrentUser()
      if (!user || !user.role) {
        return false
      }
      
      // 调用hasPermission并传递用户角色
      return await hasPermission(user.role, permission)
    } catch (error) {
      console.error('权限检查失败:', error)
      return false
    }
  }
  
  // 导航到页面（带权限检查）
  const navigateWithPermission = async (path, requiredPermission = null) => {
    try {
      // 检查认证状态
      if (requiresAuth(path) && !isUserLoggedIn.value) {
        router.push({
          path: '/error',
          query: {
            type: 'auth',
            message: '请先登录后再访问此功能'
          }
        })
        return false
      }
      
      // 检查权限
      if (requiredPermission) {
        const hasPermission = await checkPermission(requiredPermission)
        if (!hasPermission) {
          const roleDisplay = getRoleDisplayName(userInfo.value?.role)
          router.push({
            path: '/error',
            query: {
              type: 'permission',
              message: `${roleDisplay}暂无权限访问此功能`
            }
          })
          return false
        }
      }
      
      // 导航到目标页面
      router.push(path)
      closeMenu()
      return true
    } catch (error) {
      console.error('导航失败:', error)
      return false
    }
  }
  
  // 检查页面是否需要认证
  const requiresAuth = (path) => {
    const authRequiredPaths = [
      '/dashboard', '/profile', '/settings', '/word-learning',
      '/word-detail', '/word-root-analysis', '/story-reading',
      '/pattern-memory', '/resource-auth', '/subscription-management'
    ]
    return authRequiredPaths.some(authPath => path.startsWith(authPath))
  }
  
  // 获取角色显示名称 - 统一使用roleDefinitions.ts
  const getRoleDisplayName = (role) => {
    // 导入统一的角色定义
    import('../utils/roleDefinitions.js').then(({ ROLE_DISPLAY_NAMES }) => {
      return ROLE_DISPLAY_NAMES[role] || role || '当前角色'
    })
    
    // 临时兼容性映射
    const roleNames = {
      'admin': '管理员',
      'dean': '教导主任',
      'academic_director': '教务主任',
      'research_leader': '教研组长',
      'teacher': '自由老师',
      'parent': '家长',
      'student': '学生'
    }
    return roleNames[role] || role || '当前角色'
  }
  
  // 处理点击外部区域
  const handleClickOutside = (event) => {
    // 检查点击是否在菜单外部
    const menuElements = document.querySelectorAll('.base-menu, .bottom-navigation')
    const isClickInside = Array.from(menuElements).some(el => el.contains(event.target))
    
    if (!isClickInside) {
      closeMenu()
    }
  }
  
  // 处理存储变化
  const handleStorageChange = (event) => {
    if (event.key === 'user' || event.key === 'token') {
      updateUserState()
    }
  }
  
  // 生命周期钩子
  onMounted(() => {
    updateUserState()
    
    // 监听点击外部区域
    document.addEventListener('click', handleClickOutside)
    
    // 监听存储变化
    window.addEventListener('storage', handleStorageChange)
    
    // 监听权限变更
    if (window.permissionWatcher) {
      window.permissionWatcher.addListener(updateUserState)
    }
  })
  
  onUnmounted(() => {
    // 清理事件监听器
    document.removeEventListener('click', handleClickOutside)
    window.removeEventListener('storage', handleStorageChange)
    
    if (window.permissionWatcher) {
      window.permissionWatcher.removeListener(updateUserState)
    }
    
    // 清理位置观察器
    if (positionCleanup) {
      positionCleanup()
    }
  })
  
  return {
    // 状态
    activeMenu,
    activeSubmenu,
    menuPositions,
    userInfo,
    userAuthState,
    isUserLoggedIn,
    currentUserId,
    
    // 方法
    updateUserState,
    openMenu,
    closeMenu,
    toggleMenu,
    openSubmenu,
    closeSubmenu,
    toggleSubmenu,
    calculateMenuPosition,
    checkPermission,
    navigateWithPermission,
    requiresAuth,
    getRoleDisplayName
  }
}