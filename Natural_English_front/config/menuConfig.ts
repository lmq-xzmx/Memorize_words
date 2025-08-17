/**
 * 菜单配置文件
 * 定义应用程序的菜单结构、权限和显示逻辑
 */

// 菜单项接口
interface MenuItem {
  id: string
  name: string
  icon?: string
  path?: string
  component?: string
  permission?: string
  roles?: string[]
  children?: MenuItem[]
  meta?: {
    requiresAuth?: boolean
    title?: string
    description?: string
  }
}

// 权限映射接口
interface PermissionMap {
  [key: string]: string
}

// 角色显示名称接口
interface RoleDisplayNames {
  [key: string]: string
}

// 底部导航菜单
export const bottomNavMenus: MenuItem[] = [
  {
    id: 'home',
    name: '首页',
    icon: 'home',
    path: '/home',
    component: 'Home'
  },
  {
    id: 'words',
    name: '单词',
    icon: 'book',
    path: '/words',
    component: 'Words'
  },
  {
    id: 'practice',
    name: '练习',
    icon: 'edit',
    path: '/practice',
    component: 'Practice'
  },
  {
    id: 'profile',
    name: '我的',
    icon: 'user',
    path: '/profile',
    component: 'Profile'
  }
]

// 工具菜单
export const toolMenus: MenuItem[] = [
  {
    id: 'dictionary',
    name: '词典',
    icon: 'dictionary',
    path: '/dictionary',
    component: 'Dictionary'
  },
  {
    id: 'translator',
    name: '翻译',
    icon: 'translate',
    path: '/translator',
    component: 'Translator'
  },
  {
    id: 'grammar',
    name: '语法',
    icon: 'grammar',
    path: '/grammar',
    component: 'Grammar'
  }
]

// 时尚菜单
export const fashionMenus: MenuItem[] = [
  {
    id: 'trends',
    name: '趋势',
    icon: 'trending',
    path: '/trends',
    component: 'Trends'
  },
  {
    id: 'style',
    name: '风格',
    icon: 'style',
    path: '/style',
    component: 'Style'
  },
  {
    id: 'fashion-news',
    name: '时尚资讯',
    icon: 'news',
    path: '/fashion-news',
    component: 'FashionNews'
  }
]

// 管理菜单
export const adminMenus: MenuItem[] = [
  {
    id: 'user-management',
    name: '用户管理',
    icon: 'users',
    path: '/admin/users',
    component: 'UserManagement',
    permission: 'admin.users.view',
    roles: ['admin', 'super_admin']
  },
  {
    id: 'content-management',
    name: '内容管理',
    icon: 'content',
    path: '/admin/content',
    component: 'ContentManagement',
    permission: 'admin.content.view',
    roles: ['admin', 'super_admin', 'editor']
  },
  {
    id: 'system-settings',
    name: '系统设置',
    icon: 'settings',
    path: '/admin/settings',
    component: 'SystemSettings',
    permission: 'admin.settings.view',
    roles: ['super_admin']
  }
]

// 菜单权限映射
export const menuPermissions: PermissionMap = {
  'home': 'menu.home.view',
  'words': 'menu.words.view',
  'practice': 'menu.practice.view',
  'profile': 'menu.profile.view',
  'dictionary': 'menu.dictionary.view',
  'translator': 'menu.translator.view',
  'grammar': 'menu.grammar.view',
  'trends': 'menu.trends.view',
  'style': 'menu.style.view',
  'fashion-news': 'menu.fashion-news.view',
  'user-management': 'admin.users.view',
  'content-management': 'admin.content.view',
  'system-settings': 'admin.settings.view'
}

// 角色显示名称
export const roleDisplayNames: RoleDisplayNames = {
  'user': '普通用户',
  'vip': 'VIP用户',
  'editor': '编辑',
  'admin': '管理员',
  'super_admin': '超级管理员',
  'teacher': '教师',
  'student': '学生'
}

// 获取用户可访问的菜单项
export function getAccessibleMenuItems(
  menus: MenuItem[], 
  userRoles: string[] = [], 
  userPermissions: string[] = []
): MenuItem[] {
  return menus.filter(menu => {
    // 如果没有权限要求，则所有用户都可以访问
    if (!menu.permission && (!menu.roles || menu.roles.length === 0)) {
      return true
    }
    
    // 检查角色权限
    if (menu.roles && menu.roles.length > 0) {
      const hasRole = menu.roles.some(role => userRoles.includes(role))
      if (!hasRole) return false
    }
    
    // 检查具体权限
    if (menu.permission) {
      return userPermissions.includes(menu.permission)
    }
    
    return true
  }).map(menu => {
    // 递归处理子菜单
    if (menu.children && menu.children.length > 0) {
      return {
        ...menu,
        children: getAccessibleMenuItems(menu.children, userRoles, userPermissions)
      }
    }
    return menu
  })
}

// 检查菜单权限
export function checkMenuPermission(
  menuId: string, 
  userRoles: string[] = [], 
  userPermissions: string[] = []
): boolean {
  const permission = menuPermissions[menuId]
  if (!permission) return true // 没有权限要求的菜单默认可访问
  
  return userPermissions.includes(permission)
}

// 根据角色获取菜单
export function getMenusByRole(role: string): MenuItem[] {
  const allMenus = [...bottomNavMenus, ...toolMenus, ...fashionMenus, ...adminMenus]
  
  return allMenus.filter(menu => {
    if (!menu.roles || menu.roles.length === 0) return true
    return menu.roles.includes(role)
  })
}

// 获取角色显示名称
export function getRoleDisplayName(role: string): string {
  return roleDisplayNames[role] || role
}

// 默认导出
const menuConfig = {
  bottomNavMenus,
  toolMenus,
  fashionMenus,
  adminMenus,
  menuPermissions,
  roleDisplayNames,
  getAccessibleMenuItems,
  checkMenuPermission,
  getMenusByRole,
  getRoleDisplayName
}

export default menuConfig

// 导出类型
export type { MenuItem, PermissionMap, RoleDisplayNames }