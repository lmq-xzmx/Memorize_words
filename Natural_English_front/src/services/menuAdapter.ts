/**
 * 菜单适配器服务
 * 用于将后台API返回的菜单数据转换为前端组件所需的格式
 */

import type { MenuItem, ToolItem, MenuConfig } from '@/composables/useMenuManager'
import { usePermission } from '@/composables/usePermission'

// 后台API返回的菜单数据结构
export interface BackendMenuItem {
  id: string
  key: string
  title: string
  url: string
  icon?: string
  permission_required?: string
  description?: string
  enabled: boolean
  sort_order: number
  parent_id?: string
  children?: BackendMenuItem[]
}

// 后台API返回的工具配置结构
export interface BackendToolConfig {
  id: string
  name: string
  title: string
  description: string
  icon: string
  enabled: boolean
  category: string
  url: string
  permission_required?: string
  sort_order: number
}

// 后台API返回的完整菜单配置
export interface BackendMenuConfig {
  bottomNavMenus: BackendMenuItem[]
  toolsMenuConfig: {
    items: BackendToolConfig[]
  }
  fashionMenuConfig: {
    items: BackendMenuItem[]
  }
  adminMenuConfig: {
    items: BackendMenuItem[]
  }
}

/**
 * 菜单适配器类
 */
export class MenuAdapter {
  private static instance: MenuAdapter
  private permissionService: ReturnType<typeof usePermission> | null = null

  static getInstance(): MenuAdapter {
    if (!MenuAdapter.instance) {
      MenuAdapter.instance = new MenuAdapter()
    }
    return MenuAdapter.instance
  }

  private getPermissionService() {
    if (!this.permissionService) {
      this.permissionService = usePermission()
    }
    return this.permissionService
  }

  /**
   * 将后台菜单项转换为前端菜单项
   */
  transformMenuItem(backendItem: BackendMenuItem): MenuItem {
    return {
      id: backendItem.id,
      name: backendItem.key,
      path: backendItem.url,
      icon: backendItem.icon,
      component: this.getComponentByPath(backendItem.url),
      meta: {
        title: backendItem.title,
        requiresAuth: true,
        permissions: backendItem.permission_required ? [backendItem.permission_required] : [],
        hideInMenu: !backendItem.enabled,
        order: backendItem.sort_order
      },
      children: backendItem.children?.map(child => this.transformMenuItem(child))
    }
  }

  /**
   * 将后台工具配置转换为前端工具项
   */
  transformToolItem(backendTool: BackendToolConfig): ToolItem {
    return {
      id: backendTool.id,
      name: backendTool.name,
      title: backendTool.title,
      description: backendTool.description,
      path: backendTool.url,
      icon: backendTool.icon,
      enabled: backendTool.enabled,
      category: backendTool.category,
      order: backendTool.sort_order
    }
  }

  /**
   * 转换完整的菜单配置
   */
  transformMenuConfig(backendConfig: BackendMenuConfig): {
    menuItems: MenuItem[]
    toolItems: ToolItem[]
  } {
    const menuItems: MenuItem[] = []
    const toolItems: ToolItem[] = []

    // 转换底部导航菜单
    if (backendConfig.bottomNavMenus) {
      menuItems.push(...backendConfig.bottomNavMenus.map(item => this.transformMenuItem(item)))
    }

    // 转换时尚菜单（如果有）
    if (backendConfig.fashionMenuConfig?.items) {
      menuItems.push(...backendConfig.fashionMenuConfig.items.map(item => this.transformMenuItem(item)))
    }

    // 转换管理员菜单（如果有）
    if (backendConfig.adminMenuConfig?.items) {
      menuItems.push(...backendConfig.adminMenuConfig.items.map(item => this.transformMenuItem(item)))
    }

    // 转换工具配置
    if (backendConfig.toolsMenuConfig?.items) {
      toolItems.push(...backendConfig.toolsMenuConfig.items.map(tool => this.transformToolItem(tool)))
    }

    return {
      menuItems: this.sortMenuItems(menuItems),
      toolItems: this.sortToolItems(toolItems)
    }
  }

  /**
   * 根据路径推断组件名称
   */
  private getComponentByPath(path: string): string | undefined {
    const pathMap: Record<string, string> = {
      '/dashboard': 'Dashboard',
      '/learning': 'Learning',
      '/learning/words': 'WordLearning',
      '/learning/sentences': 'SentenceLearning',
      '/learning/practice': 'Practice',
      '/progress': 'Progress',
      '/progress/statistics': 'Statistics',
      '/progress/achievements': 'Achievements',
      '/profile': 'Profile',
      '/profile/settings': 'Settings',
      '/profile/history': 'History',
      '/admin': 'AdminDashboard',
      '/admin/users': 'UserManagement',
      '/admin/content': 'ContentManagement',
      '/admin/system': 'SystemSettings',
      '/teacher': 'TeacherDashboard',
      '/teacher/classes': 'ClassManagement',
      '/teacher/courses': 'CourseManagement'
    }

    return pathMap[path]
  }

  /**
   * 排序菜单项
   */
  private sortMenuItems(items: MenuItem[]): MenuItem[] {
    return items.sort((a, b) => {
      const orderA = a.meta?.order || 0
      const orderB = b.meta?.order || 0
      return orderA - orderB
    })
  }

  /**
   * 排序工具项
   */
  private sortToolItems(items: ToolItem[]): ToolItem[] {
    return items.sort((a, b) => {
      const orderA = a.order || 0
      const orderB = b.order || 0
      return orderA - orderB
    })
  }

  /**
   * 过滤有权限的菜单项
   */
  filterMenuByPermissions(items: MenuItem[]): MenuItem[] {
    return items.filter(item => {
      // 检查权限
      if (item.meta?.permissions?.length) {
        const hasPermission = item.meta.permissions.some(permission => 
          this.getPermissionService().hasPermission(permission)
        )
        if (!hasPermission) return false
      }

      // 检查角色
      if (item.meta?.roles?.length) {
        const hasRole = item.meta.roles.some(role => 
          this.getPermissionService().hasRole(role)
        )
        if (!hasRole) return false
      }

      // 递归过滤子菜单
      if (item.children) {
        item.children = this.filterMenuByPermissions(item.children)
      }

      return !item.meta?.hideInMenu
    })
  }

  /**
   * 过滤有权限的工具项
   */
  filterToolsByPermissions(items: ToolItem[]): ToolItem[] {
    return items.filter(item => {
      // 这里可以根据工具的权限要求进行过滤
      // 暂时返回所有启用的工具
      return item.enabled
    })
  }

  /**
   * 将前端菜单项转换为移动端底部导航格式
   */
  transformToMobileNav(items: MenuItem[]): MenuItem[] {
    // 只保留主要的4个导航项用于底部导航
    const mobileNavItems = items.filter(item => {
      const mobileNavKeys = ['learning', 'tools', 'words', 'profile']
      return mobileNavKeys.includes(item.name)
    }).slice(0, 4)

    return mobileNavItems.map(item => ({
      ...item,
      meta: {
        ...item.meta,
        isMobileNav: true
      }
    }))
  }

  /**
   * 获取面包屑导航
   */
  getBreadcrumbs(items: MenuItem[], currentPath: string): MenuItem[] {
    const breadcrumbs: MenuItem[] = []
    
    const findPath = (menuItems: MenuItem[], targetPath: string, path: MenuItem[] = []): boolean => {
      for (const item of menuItems) {
        const currentPath = [...path, item]
        
        if (item.path === targetPath) {
          breadcrumbs.push(...currentPath)
          return true
        }
        
        if (item.children && findPath(item.children, targetPath, currentPath)) {
          return true
        }
      }
      return false
    }
    
    findPath(items, currentPath)
    return breadcrumbs
  }

  /**
   * 根据角色获取默认菜单
   */
  getDefaultMenuByRole(role: string): MenuItem[] {
    const defaultMenus: Record<string, MenuItem[]> = {
      'student': [
        {
          id: 'learning',
          name: 'learning',
          path: '/learning',
          icon: '📚',
          meta: { title: '学习中心', order: 1 }
        },
        {
          id: 'progress',
          name: 'progress',
          path: '/progress',
          icon: '📊',
          meta: { title: '学习进度', order: 2 }
        },
        {
          id: 'profile',
          name: 'profile',
          path: '/profile',
          icon: '👤',
          meta: { title: '个人中心', order: 3 }
        }
      ],
      'teacher': [
        {
          id: 'dashboard',
          name: 'dashboard',
          path: '/teacher/dashboard',
          icon: '🏠',
          meta: { title: '教师工作台', order: 1 }
        },
        {
          id: 'classes',
          name: 'classes',
          path: '/teacher/classes',
          icon: '👥',
          meta: { title: '班级管理', order: 2 }
        },
        {
          id: 'courses',
          name: 'courses',
          path: '/teacher/courses',
          icon: '📖',
          meta: { title: '课程管理', order: 3 }
        }
      ],
      'admin': [
        {
          id: 'admin-dashboard',
          name: 'admin-dashboard',
          path: '/admin/dashboard',
          icon: '⚙️',
          meta: { title: '管理控制台', order: 1 }
        },
        {
          id: 'user-management',
          name: 'user-management',
          path: '/admin/users',
          icon: '👤',
          meta: { title: '用户管理', order: 2 }
        },
        {
          id: 'system-settings',
          name: 'system-settings',
          path: '/admin/system',
          icon: '🔧',
          meta: { title: '系统设置', order: 3 }
        }
      ]
    }

    return defaultMenus[role] || defaultMenus['student']
  }

  /**
   * 根据角色获取默认工具配置
   */
  getDefaultToolsByRole(role: string): ToolItem[] {
    const defaultTools: Record<string, ToolItem[]> = {
      'student': [
        {
          id: 'vocabulary-builder',
          name: 'vocabulary-builder',
          title: '词汇构建器',
          description: '智能词汇学习工具',
          icon: '📝',
          enabled: true,
          category: 'learning',
          url: '/tools/vocabulary-builder',
          order: 1
        },
        {
          id: 'progress-tracker',
          name: 'progress-tracker',
          title: '进度跟踪',
          description: '学习进度可视化工具',
          icon: '📊',
          enabled: true,
          category: 'analytics',
          url: '/tools/progress-tracker',
          order: 2
        }
      ],
      'teacher': [
        {
          id: 'class-manager',
          name: 'class-manager',
          title: '班级管理器',
          description: '班级和学生管理工具',
          icon: '👥',
          enabled: true,
          category: 'management',
          url: '/tools/class-manager',
          order: 1
        },
        {
          id: 'assignment-creator',
          name: 'assignment-creator',
          title: '作业创建器',
          description: '智能作业生成工具',
          icon: '📋',
          enabled: true,
          category: 'teaching',
          url: '/tools/assignment-creator',
          order: 2
        }
      ],
      'admin': [
        {
          id: 'system-monitor',
          name: 'system-monitor',
          title: '系统监控',
          description: '系统性能和状态监控',
          icon: '📈',
          enabled: true,
          category: 'system',
          url: '/tools/system-monitor',
          order: 1
        },
        {
          id: 'user-analytics',
          name: 'user-analytics',
          title: '用户分析',
          description: '用户行为和数据分析',
          icon: '📊',
          enabled: true,
          category: 'analytics',
          url: '/tools/user-analytics',
          order: 2
        }
      ]
    }

    return defaultTools[role] || defaultTools['student']
  }
}

// 导出单例实例
export const menuAdapter = MenuAdapter.getInstance()