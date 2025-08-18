import { ref, computed } from 'vue'
import { useAuth } from './useAuth'
import { getMenuByRole, type MenuItem, findMenuItemByPath as findMenuItem, filterMenuByPermissions } from '../config/menu'
import { permissionChecker } from '../utils/permissions'

export const useMenu = () => {
  const { userRole, userPermissions } = useAuth()
  
  // 获取基础菜单项（根据角色）
  const baseMenuItems = ref<MenuItem[]>([])
  const updateBaseMenuItems = () => {
    baseMenuItems.value = getMenuByRole(userRole.value)
  }
  updateBaseMenuItems()

  // 获取过滤后的菜单项（根据权限）
  const userMenuItems = ref<MenuItem[]>([])
  const updateUserMenuItems = () => {
    userMenuItems.value = filterMenuByPermissions(baseMenuItems.value, userPermissions.value)
  }
  updateUserMenuItems()

  // 检查菜单项是否可见
  const isMenuItemVisible = (menuItem: MenuItem): boolean => {
    if (!menuItem.permission) return true
    return permissionChecker.check(menuItem.permission)
  }

  // 获取扁平化的菜单项
  const flatMenuItems = ref<MenuItem[]>([])
  const updateFlatMenuItems = () => {
    const flatten = (items: MenuItem[]): MenuItem[] => {
      const result: MenuItem[] = []
      items.forEach((item: MenuItem) => {
        result.push(item)
        if (item.children) {
          result.push(...flatten(item.children))
        }
      })
      return result
    }
    flatMenuItems.value = flatten(userMenuItems.value)
  }
  updateFlatMenuItems()
  
  // 根据路径查找菜单项
  const findMenuItemByPath = (path: string): MenuItem | undefined => {
    return flatMenuItems.value.find((item: MenuItem) => item.path === path)
  }
  
  // 获取面包屑导航
  const getBreadcrumbs = (currentPath: string): MenuItem[] => {
    const breadcrumbs: MenuItem[] = []
    const findParents = (items: MenuItem[], targetPath: string, parents: MenuItem[] = []): boolean => {
      for (const item of items) {
        const currentParents = [...parents, item]
        if (item.path === targetPath) {
          breadcrumbs.push(...currentParents)
          return true
        }
        if (item.children && findParents(item.children, targetPath, currentParents)) {
          return true
        }
      }
      return false
    }
    findParents(userMenuItems.value, currentPath)
    return breadcrumbs
  }
  
  return {
    menuItems: userMenuItems,
    flatMenuItems,
    isMenuItemVisible,
    findMenuItemByPath,
    getBreadcrumbs,
    updateBaseMenuItems,
    updateUserMenuItems,
    updateFlatMenuItems
  }
}