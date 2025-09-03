import { getMenuHierarchy, getUserMenuPermissions, checkMenuPermission } from '@/services/permissionService'

const state = {
  // 槽位配置
  slotConfig: uni.getStorageSync('slotConfig') || [],
  // 菜单模块配置
  menuConfig: uni.getStorageSync('menuConfig') || [],
  // 菜单有效性配置
  menuValidity: uni.getStorageSync('menuValidity') || [],
  // 用户菜单权限
  userMenuPermissions: uni.getStorageSync('userMenuPermissions') || [],
  // 动态生成的菜单树
  menuTree: uni.getStorageSync('menuTree') || [],
  // 底部导航菜单
  tabBarMenus: uni.getStorageSync('tabBarMenus') || [],
  // 当前用户角色
  currentRole: uni.getStorageSync('currentRole') || 'student',
  // 权限加载状态
  permissionLoaded: false
}

const mutations = {
  SET_SLOT_CONFIG(state, config) {
    state.slotConfig = config
    uni.setStorageSync('slotConfig', config)
  },
  
  SET_MENU_CONFIG(state, config) {
    state.menuConfig = config
    uni.setStorageSync('menuConfig', config)
  },
  
  SET_MENU_VALIDITY(state, validity) {
    state.menuValidity = validity
    uni.setStorageSync('menuValidity', validity)
  },
  
  SET_USER_MENU_PERMISSIONS(state, permissions) {
    state.userMenuPermissions = permissions
    uni.setStorageSync('userMenuPermissions', permissions)
  },
  
  SET_MENU_TREE(state, tree) {
    state.menuTree = tree
    uni.setStorageSync('menuTree', tree)
  },
  
  SET_TAB_BAR_MENUS(state, menus) {
    state.tabBarMenus = menus
    uni.setStorageSync('tabBarMenus', menus)
  },
  
  SET_CURRENT_ROLE(state, role) {
    state.currentRole = role
    uni.setStorageSync('currentRole', role)
  },
  
  SET_PERMISSION_LOADED(state, loaded) {
    state.permissionLoaded = loaded
  },
  
  CLEAR_PERMISSION_DATA(state) {
    state.slotConfig = []
    state.menuConfig = []
    state.menuValidity = []
    state.userMenuPermissions = []
    state.menuTree = []
    state.tabBarMenus = []
    state.currentRole = 'student'
    state.permissionLoaded = false
    
    // 清除本地存储
    uni.removeStorageSync('slotConfig')
    uni.removeStorageSync('menuConfig')
    uni.removeStorageSync('menuValidity')
    uni.removeStorageSync('userMenuPermissions')
    uni.removeStorageSync('menuTree')
    uni.removeStorageSync('tabBarMenus')
    uni.removeStorageSync('currentRole')
  }
}

const actions = {
  // 加载权限数据
  async loadPermissionData({ commit, state, rootState }) {
    try {
      // 获取菜单层次结构
      const menuHierarchy = await getMenuHierarchy()
      
      commit('SET_SLOT_CONFIG', menuHierarchy.slotConfig || [])
      commit('SET_MENU_CONFIG', menuHierarchy.menuConfig || [])
      commit('SET_MENU_VALIDITY', menuHierarchy.menuValidity || [])
      
      // 如果用户已登录，获取用户菜单权限
      if (rootState.user && rootState.user.isLoggedIn) {
        const userPermissions = await getUserMenuPermissions()
        commit('SET_USER_MENU_PERMISSIONS', userPermissions || [])
      }
      
      commit('SET_PERMISSION_LOADED', true)
      
      return true
    } catch (error) {
      console.error('加载权限数据失败:', error)
      commit('SET_PERMISSION_LOADED', false)
      throw error
    }
  },
  
  // 构建菜单树
  async buildMenuTree({ commit, state, dispatch }) {
    try {
      const currentRole = state.currentRole || 'student'
      const { slotConfig, menuConfig, menuValidity } = state
      
      // 过滤当前角色的有效菜单
      const validMenus = menuValidity.filter(menu => 
        menu.role === currentRole && menu.is_valid
      )
      
      // 构建菜单树
      const menuTree = await dispatch('generateMenuTree', { slotConfig, menuConfig, validMenus, currentRole })
      
      commit('SET_MENU_TREE', menuTree)
      
      // 生成底部导航菜单
      const tabBarMenus = menuTree.filter(menu => 
        menu.level === 'root' && dispatch('isTabBarMenu', menu.name)
      ).slice(0, 5)
      
      commit('SET_TAB_BAR_MENUS', tabBarMenus)
      
      return menuTree
    } catch (error) {
      console.error('构建菜单树失败:', error)
      throw error
    }
  },
  
  // 生成菜单树
  generateMenuTree({ dispatch }, { slotConfig, menuConfig, validMenus, currentRole }) {
    const menuTree = []
    
    // 获取当前角色的槽位配置
    const roleSlots = slotConfig.filter(slot => slot.role === currentRole)
    
    // 为每个槽位构建菜单
    roleSlots.forEach(slot => {
      // 查找对应的菜单配置
      const menuItem = menuConfig.find(menu => 
        menu.slot_name === slot.slot_name && 
        menu.menu_level === slot.menu_level
      )
      
      if (menuItem) {
        // 检查菜单是否有效
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
            icon: menuItem.icon || dispatch('getDefaultIcon', menuItem.menu_name),
            path: dispatch('getMenuPath', { menuName: menuItem.menu_name, menuLevel: menuItem.menu_level }),
            children: []
          }
          
          // 如果是根菜单或一级菜单，查找子菜单
          if (menu.level === 'root' || menu.level === 'level1') {
            menu.children = dispatch('findChildMenus', { menuConfig, validMenus, parentName: menu.name, currentRole })
          }
          
          menuTree.push(menu)
        }
      }
    })
    
    return menuTree
  },
  
  // 查找子菜单
  findChildMenus({ dispatch }, { menuConfig, validMenus, parentName, currentRole }) {
    const children = []
    
    // 查找子菜单
    const childMenus = menuConfig.filter(menu => {
      if (menu.menu_level === 'level1' && parentName) {
        // 一级菜单的父菜单是根菜单
        return menu.parent_menu === parentName
      } else if (menu.menu_level === 'level2' && parentName) {
        // 二级菜单的父菜单是一级菜单
        return menu.parent_menu === parentName
      }
      return false
    })
    
    childMenus.forEach(childMenu => {
      // 检查子菜单是否有效
      const isValid = validMenus.some(valid => 
        valid.menu_name === childMenu.menu_name &&
        valid.menu_level === childMenu.menu_level &&
        valid.role === currentRole
      )
      
      if (isValid) {
        const child = {
          id: childMenu.id,
          name: childMenu.menu_name,
          title: childMenu.display_name,
          level: childMenu.menu_level,
          icon: childMenu.icon || dispatch('getDefaultIcon', childMenu.menu_name),
          path: dispatch('getMenuPath', { menuName: childMenu.menu_name, menuLevel: childMenu.menu_level }),
          children: []
        }
        
        // 递归查找子菜单
        if (child.level === 'level1') {
          child.children = dispatch('findChildMenus', { menuConfig, validMenus, parentName: child.name, currentRole })
        }
        
        children.push(child)
      }
    })
    
    return children
  },
  
  // 获取菜单路径
  getMenuPath({ state }, { menuName, menuLevel }) {
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
    
    return pathMap[menuName] || `/pages/${menuName.toLowerCase()}/${menuName.toLowerCase()}`
  },
  
  // 获取默认图标
  getDefaultIcon({ state }, menuName) {
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
  },
  
  // 检查菜单权限
  async checkMenuPermission({ state }, { menuName, menuLevel, userId }) {
    try {
      return await checkMenuPermission(menuName, menuLevel, userId)
    } catch (error) {
      console.error('检查菜单权限失败:', error)
      return false
    }
  },
  
  // 设置当前角色
  async setCurrentRole({ commit }, role) {
    commit('SET_CURRENT_ROLE', role)
  },
  
  // 切换角色
  async switchRole({ commit, dispatch }, role) {
    commit('SET_CURRENT_ROLE', role)
    await dispatch('buildMenuTree')
  },
  
  // 清除权限数据
  async clearPermissionData({ commit }) {
    commit('CLEAR_PERMISSION_DATA')
  },
  
  // 判断是否为TabBar菜单
  isTabBarMenu({ state }, menuName) {
    const tabBarMenus = ['斩词', '学习工具', '个人中心', '时尚内容']
    return tabBarMenus.includes(menuName)
  },
  
  // 刷新菜单数据
  async refreshMenuData({ dispatch }) {
    await dispatch('clearPermissionData')
    await dispatch('loadPermissionData')
    await dispatch('buildMenuTree')
  }
}

const getters = {
  slotConfig: state => state.slotConfig,
  menuConfig: state => state.menuConfig,
  menuValidity: state => state.menuValidity,
  userMenuPermissions: state => state.userMenuPermissions,
  menuTree: state => state.menuTree,
  tabBarMenus: state => state.tabBarMenus,
  currentRole: state => state.currentRole,
  permissionLoaded: state => state.permissionLoaded,
  
  // 根据菜单名称查找菜单
  getMenuByName: (state) => (name) => {
    const findMenu = (menus) => {
      for (const menu of menus) {
        if (menu.name === name) {
          return menu
        }
        if (menu.children && menu.children.length > 0) {
          const found = findMenu(menu.children)
          if (found) return found
        }
      }
      return null
    }
    return findMenu(state.menuTree)
  },
  
  // 获取指定级别的菜单
  getMenusByLevel: (state) => (level) => {
    const result = []
    const findMenus = (menus) => {
      menus.forEach(menu => {
        if (menu.level === level) {
          result.push(menu)
        }
        if (menu.children && menu.children.length > 0) {
          findMenus(menu.children)
        }
      })
    }
    findMenus(state.menuTree)
    return result
  },
  
  // 检查是否有菜单权限
  hasMenuPermission: (state) => (menuName, menuLevel) => {
    return state.userMenuPermissions.some(permission => 
      permission.menu_name === menuName && 
      permission.menu_level === menuLevel
    )
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}