import request from '@/utils/request'

/**
 * 权限服务类
 */
class PermissionService {
  constructor() {
    this.initialized = false
    this.menuHierarchy = null
    this.userPermissions = null
  }
  
  /**
   * 初始化权限服务
   */
  async init() {
    try {
      if (!this.initialized) {
        await this.loadMenuHierarchy()
        this.initialized = true
      }
    } catch (error) {
      console.error('权限服务初始化失败:', error)
      throw error
    }
  }
  
  /**
   * 获取菜单层次结构
   */
  async getMenuHierarchy() {
    try {
      const response = await request.get('/permissions/api/permissions/menu-hierarchy/')
      return response.data
    } catch (error) {
      console.error('获取菜单层次结构失败:', error)
      throw error
    }
  }
  
  /**
   * 加载菜单层次结构
   */
  async loadMenuHierarchy() {
    try {
      this.menuHierarchy = await this.getMenuHierarchy()
      return this.menuHierarchy
    } catch (error) {
      console.error('加载菜单层次结构失败:', error)
      // 如果网络请求失败，使用本地缓存的数据
      const cachedData = uni.getStorageSync('menuHierarchy')
      if (cachedData) {
        this.menuHierarchy = cachedData
        return this.menuHierarchy
      }
      throw error
    }
  }
  
  /**
   * 获取用户菜单权限
   */
  async getUserMenuPermissions(userId) {
    try {
      const params = userId ? { user_id: userId } : {}
      const response = await request.get('/permissions/api/permissions/user-menu-permissions/', params)
      return response.data
    } catch (error) {
      console.error('获取用户菜单权限失败:', error)
      throw error
    }
  }
  
  /**
   * 检查菜单权限
   */
  async checkMenuPermission(menuName, menuLevel, userId) {
    try {
      const data = {
        menu_name: menuName,
        menu_level: menuLevel
      }
      
      if (userId) {
        data.user_id = userId
      }
      
      const response = await request.post('/permissions/api/permissions/check-menu-permission/', data)
      return response.data
    } catch (error) {
      console.error('检查菜单权限失败:', error)
      throw error
    }
  }
  
  /**
   * 获取角色显示名称
   */
  async getRoleDisplayName(role) {
    try {
      const response = await request.get('/permissions/api/permissions/role-display-name/', { role })
      return response.data
    } catch (error) {
      console.error('获取角色显示名称失败:', error)
      throw error
    }
  }
  
  /**
   * 根据角色生成菜单树
   */
  generateMenuTree(role = 'student') {
    if (!this.menuHierarchy) {
      console.warn('菜单层次结构未加载')
      return []
    }
    
    const { slotConfig, menuConfig, menuValidity } = this.menuHierarchy
    
    // 过滤当前角色的有效菜单
    const validMenus = menuValidity.filter(menu => 
      menu.role === role && menu.is_valid
    )
    
    // 获取当前角色的槽位配置
    const roleSlots = slotConfig.filter(slot => slot.role === role)
    
    const menuTree = []
    
    // 为每个槽位构建菜单
    roleSlots.forEach(slot => {
      const menuItem = menuConfig.find(menu => 
        menu.slot_name === slot.slot_name && 
        menu.menu_level === slot.menu_level
      )
      
      if (menuItem) {
        const isValid = validMenus.some(valid => 
          valid.menu_name === menuItem.menu_name &&
          valid.menu_level === menuItem.menu_level
        )
        
        if (isValid) {
          const menu = {
            id: menuItem.id,
            name: menuItem.menu_name,
            title: menuItem.display_name,
            level: menuItem.menu_level,
            slot: slot.slot_name,
            icon: menuItem.icon || this.getDefaultIcon(menuItem.menu_name),
            path: this.getMenuPath(menuItem.menu_name, menuItem.menu_level),
            children: []
          }
          
          // 查找子菜单
          if (menu.level === 'root' || menu.level === 'level1') {
            menu.children = this.findChildMenus(menuConfig, validMenus, menu.name, role)
          }
          
          menuTree.push(menu)
        }
      }
    })
    
    return menuTree
  }
  
  /**
   * 查找子菜单
   */
  findChildMenus(menuConfig, validMenus, parentName, role) {
    const children = []
    
    const childMenus = menuConfig.filter(menu => {
      if (menu.menu_level === 'level1' && parentName) {
        return menu.parent_menu === parentName
      } else if (menu.menu_level === 'level2' && parentName) {
        return menu.parent_menu === parentName
      }
      return false
    })
    
    childMenus.forEach(childMenu => {
      const isValid = validMenus.some(valid => 
        valid.menu_name === childMenu.menu_name &&
        valid.menu_level === childMenu.menu_level &&
        valid.role === role
      )
      
      if (isValid) {
        const child = {
          id: childMenu.id,
          name: childMenu.menu_name,
          title: childMenu.display_name,
          level: childMenu.menu_level,
          icon: childMenu.icon || this.getDefaultIcon(childMenu.menu_name),
          path: this.getMenuPath(childMenu.menu_name, childMenu.menu_level),
          children: []
        }
        
        if (child.level === 'level1') {
          child.children = this.findChildMenus(menuConfig, validMenus, child.name, role)
        }
        
        children.push(child)
      }
    })
    
    return children
  }
  
  /**
   * 获取菜单路径
   */
  getMenuPath(menuName, menuLevel) {
    const pathMap = {
      // 根菜单路径
      '斩词': '/pages/word/word',
      '学习工具': '/pages/tools/tools',
      '时尚内容': '/pages/fashion/fashion',
      '个人中心': '/pages/profile/profile',
      
      // 一级菜单路径
      '学习练习': '/pages/learning/practice',
      '单词测试': '/pages/learning/test',
      '语法练习': '/pages/learning/grammar',
      '听力训练': '/pages/learning/listening',
      
      // 二级菜单路径
      '基础练习': '/pages/learning/basic',
      '进阶练习': '/pages/learning/advanced',
      '专项练习': '/pages/learning/special'
    }
    
    return pathMap[menuName] || `/pages/${menuName.toLowerCase().replace(/\s+/g, '')}/${menuName.toLowerCase().replace(/\s+/g, '')}`
  }
  
  /**
   * 获取默认图标
   */
  getDefaultIcon(menuName) {
    const iconMap = {
      '斩词': 'word',
      '学习工具': 'tools',
      '时尚内容': 'fashion',
      '个人中心': 'profile',
      '学习练习': 'practice',
      '单词测试': 'test',
      '语法练习': 'grammar',
      '听力训练': 'listening'
    }
    
    return iconMap[menuName] || 'default'
  }
  
  /**
   * 检查本地菜单权限
   */
  hasMenuPermission(menuName, menuLevel, role = 'student') {
    if (!this.menuHierarchy) {
      return false
    }
    
    const { menuValidity } = this.menuHierarchy
    return menuValidity.some(menu => 
      menu.menu_name === menuName &&
      menu.menu_level === menuLevel &&
      menu.role === role &&
      menu.is_valid
    )
  }
  
  /**
   * 获取角色的所有有效菜单
   */
  getRoleMenus(role = 'student') {
    if (!this.menuHierarchy) {
      return []
    }
    
    const { menuValidity } = this.menuHierarchy
    return menuValidity.filter(menu => 
      menu.role === role && menu.is_valid
    )
  }
  
  /**
   * 获取菜单配置
   */
  getMenuConfig() {
    return this.menuHierarchy?.menuConfig || []
  }
  
  /**
   * 获取槽位配置
   */
  getSlotConfig() {
    return this.menuHierarchy?.slotConfig || []
  }
  
  /**
   * 获取菜单有效性配置
   */
  getMenuValidity() {
    return this.menuHierarchy?.menuValidity || []
  }
}

// 创建权限服务实例
const permissionService = new PermissionService()

// 导出服务实例和方法
export default permissionService

export const {
  getMenuHierarchy,
  getUserMenuPermissions,
  checkMenuPermission,
  getRoleDisplayName
} = permissionService