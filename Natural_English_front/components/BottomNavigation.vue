<template>
  <div class="tab-bar-container">
    <!-- 底部导航栏 -->
    <div class="bottom-navigation">
      <!-- 斩词 -->
      <div 
        class="nav-item"
        :class="{ active: activeMenu === 'word' }"
        @click="handleWordClick"
      >
        <div class="nav-icon">
          <span class="icon chinese-icon">斩</span>
        </div>
        <div class="nav-text">斩词</div>
      </div>

      <!-- 工具 -->
      <div 
        class="nav-item"
        :class="{ active: activeMenu === 'tools' }"
        @click="handleToolsClick"
        ref="toolsTab"
      >
        <div class="nav-icon">
          <span class="icon chinese-icon">新</span>
        </div>
        <div class="nav-text">工具</div>
      </div>

      <!-- 时尚 -->
      <div 
        class="nav-item"
        :class="{ active: activeMenu === 'fashion' }"
        @click="toggleMenu('fashion')"
        ref="fashionTab"
      >
        <div class="nav-icon">
          <span class="icon chinese-icon">榜</span>
        </div>
        <div class="nav-text">时尚</div>
      </div>

      <!-- 我的 -->
      <div 
        class="nav-item"
        :class="{ active: currentPath === '/profile' }"
        @click="navigateTo('/profile')"
      >
        <div class="nav-icon">
          <span class="icon">👤</span>
        </div>
        <div class="nav-text">我的</div>
      </div>
    </div>

    <!-- 弹出层容器 -->
    <div class="popup-container">
      <!-- 时尚弹出菜单 -->
      <transition name="popup-fade">
        <div v-if="activeMenu === 'fashion'" class="popup-menu fashion-menu" :style="fashionMenuPosition">
          <!-- 听说训练中心菜单项 -->
          <div class="menu-item" @click="navigateTo('/listening')">
            <span class="menu-icon">🎧</span>
            <span class="menu-text">听说训练中心</span>
          </div>
          
          <div class="menu-item" @click="navigateTo('/community')">
            <span class="menu-icon">👥</span>
            <span class="menu-text">社区互动</span>
          </div>
          
          <!-- 词汇阅读中心菜单项 -->
          <div class="menu-item" @click="navigateTo('/learning-modes')">
            <span class="menu-icon">📚</span>
            <span class="menu-text">词汇阅读中心</span>
          </div>
          
          <div class="menu-item" @click="navigateTo('/fashion')">
            <span class="menu-icon">🌟</span>
            <span class="menu-text">时尚趋势</span>
          </div>
          <div class="menu-item" @click="navigateTo('/dev-index')">
            <span class="menu-icon">🔍</span>
            <span class="menu-text">发现</span>
          </div>
        </div>
      </transition>

      <!-- 工具一级菜单（开发中心） -->
      <transition name="popup-fade">
        <div v-if="activeMenu === 'tools'" class="popup-menu tools-menu level-1" :style="toolsMenuPosition" @click.stop>
          <!-- 开发中心菜单项 -->
          <div class="menu-item dev-center-item" @click.stop="toggleDevCenter">
            <span class="menu-icon">🛠️</span>
            <span class="menu-text">开发中心</span>
            <span class="menu-arrow">{{ showDevCenter ? '▼' : '▶' }}</span>
          </div>
          
          <!-- 管理开发期首页菜单项（仅管理员可见） -->
          <div v-if="userInfo && userInfo.role === 'admin'" class="menu-item" @click="navigateTo('/admin/dev-index')">
            <span class="menu-icon">⚙️</span>
            <span class="menu-text">管理开发期首页</span>
          </div>
          
          <!-- 启用的功能菜单项（单选框模式） -->
          <div v-if="enabledMenuItems.length > 0" class="enabled-tools">
            <div class="menu-divider"></div>
            <div v-for="item in enabledMenuItems" :key="item.id" class="tool-menu-item" @click.stop>
              <input 
                type="radio" 
                :id="'radio-' + item.id"
                :value="item.id"
                v-model="selectedTool"
                @change.stop="selectTool(item)"
                class="tool-radio"
              >
              <label :for="'radio-' + item.id" class="tool-label" @click.stop>
                <span class="tool-name">{{ item.name }}</span>
              </label>
            </div>
          </div>
          
          <!-- 无启用功能时的提示 -->
          <div v-else class="no-tools-tip">
            <div class="menu-divider"></div>
            <div class="tip-text">请在开发中心启用功能</div>
          </div>
        </div>
      </transition>



      <!-- 开发中心二级菜单 -->
      <transition name="popup-fade">
        <div v-if="showDevCenter && activeMenu === 'tools'" class="popup-menu dev-center-menu level-2" :style="devCenterMenuPosition" @click.stop>
          <div class="dev-center-header">
            <h3>开发中心 ({{ enabledMenuItems.length }}/{{ allDevTools.length }})</h3>
          </div>
          <div class="dev-tool-list">
            <div v-for="tool in allDevTools" :key="tool.id" class="dev-tool-item">
              <div class="tool-info">
                <span class="tool-icon">{{ tool.icon }}</span>
                <div class="tool-details">
                  <span class="tool-name">{{ tool.title }}</span>
                  <span class="tool-desc">{{ tool.description }}</span>
                </div>
              </div>
              <div class="tool-switch" @click.stop>
                <input 
                  type="checkbox" 
                  :id="'dev-switch-' + tool.id"
                  v-model="tool.enabled"
                  @change.stop="toggleDevTool(tool)"
                >
                <label :for="'dev-switch-' + tool.id" class="switch-label" @click.stop></label>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <!-- 遮罩层 -->
      <transition name="overlay-fade">
        <div v-if="activeMenu || showDevCenter" class="overlay" @click="handleOverlayClick"></div>
      </transition>
    </div>
  </div>
</template>

<script>
import permissionMixin from '../mixins/permissionMixin.js'
import { getCurrentUser, isAuthenticated, permissionWatcher } from '../utils/permission.js'
import { manualSyncAuth } from '../utils/authSync.js'
import permissionSyncManager, { 
  syncUserPermissions, 
  startAutoSync, 
  addPermissionListener,
  removePermissionListener 
} from '../utils/permissionSync.js'
// 引入动态权限系统
import {
  getAccessibleMenus as getDynamicMenus,
  hasPermission as hasDynamicPermission,
  fetchUserMenuPermissions,
  checkMenuPermission
} from '../utils/dynamicPermission.js'

export default {
  name: 'BottomNavigation',
  mixins: [permissionMixin],
  data() {
    return {
      userAuthState: false, // 用户认证状态
      userInfo: null, // 用户信息
      activeMenu: null, // 当前激活的菜单
      showDevCenter: false, // 显示开发中心二级页面
      selectedTool: null, // 当前选中的工具
      enabledMenuItems: [], // 启用的菜单项
      toolsMenuPosition: {}, // 工具菜单位置
      fashionMenuPosition: {}, // 时尚菜单位置
      devCenterMenuPosition: {}, // 开发中心菜单位置
      userId: null, // 当前用户ID
      allDevTools: [
        {
          id: 'word-reading',
          title: '单词阅读',
          description: 'H5版单词阅读页面，支持音频播放和进度跟踪',
          path: '/word-reading',
          icon: '📖',
          enabled: false
        },
        {
          id: 'word-learning',
          title: '单词学习',
          description: 'H5版单词学习页面，展示单词详情和多种释义',
          path: '/word-learning',
          icon: '📚',
          enabled: false
        },
        {
          id: 'word-spelling',
          title: '拼写练习',
          description: '听音拼写练习页面，提升单词记忆',
          path: '/word-learning/spelling',
          icon: '✍️',
          enabled: false
        },
        {
          id: 'word-flashcard',
          title: '闪卡学习',
          description: '翻转卡片学习单词页面',
          path: '/word-learning/flashcard',
          icon: '🃏',
          enabled: false
        },
        {
          id: 'word-detail',
          title: '单词详情',
          description: '单词详情页面，包含音标、释义、例句、词根词缀等完整信息',
          path: '/word-detail/institution',
          icon: '📝',
          enabled: false
        },
        {
          id: 'word-root-analysis',
          title: '词根分解',
          description: '词根拆解展示页面，支持词根分析和学习进度管理',
          path: '/word-root-analysis',
          icon: '🌱',
          enabled: false
        },
        {
          id: 'pattern-memory',
          title: '模式匹配记忆',
          description: '三级学习模式：图片选择、选择题、单词补全，支持多种记忆方式',
          path: '/pattern-memory',
          icon: '🧠',
          enabled: false
        },
        {
          id: 'story-reading',
          title: '故事阅读',
          description: '交互式故事阅读页面，支持词性标注和生词收集功能',
          path: '/story-reading',
          icon: '📚',
          enabled: false
        },
        {
          id: 'word-challenge',
          title: '单词挑战',
          description: '单词挑战游戏页面',
          path: '/word-challenge',
          icon: '⚔️',
          enabled: false
        }
      ]
    }
  },
  computed: {
    // 检查用户是否已登录
    isUserLoggedIn() {
      return this.userAuthState && this.userInfo
    },
    // 检查是否有权限使用工具
    canUseTools() {
      // 检查用户是否已登录
      if (!this.isUserLoggedIn || !this.userInfo || !this.userInfo.role) {
        return false
      }
      
      // 使用权限系统检查是否有访问开发工具的权限
      return this.$hasPermission('access_dev_tools')
    }
  },
  props: {
    currentPath: {
      type: String,
      default: '/'
    }
  },
  mounted() {
    // 初始化用户状态
    this.updateUserState()
    
    // 监听权限变更
    if (window.permissionWatcher) {
      window.permissionWatcher.addListener(this.handlePermissionChange)
    }
    
    // 监听localStorage变化
    window.addEventListener('storage', this.handleStorageChange)
    
    // 初始化用户偏好设置
    this.initializeUserPreferences()
  },
  beforeUnmount() {
    // 移除监听器
    if (window.permissionWatcher) {
      window.permissionWatcher.removeListener(this.handlePermissionChange)
    }
    window.removeEventListener('storage', this.handleStorageChange)
    
    // 保存用户偏好
    if (this.userId && this.userId !== 'default') {
      this.saveUserMenuPreferences()
    }
  },
  watch: {
    currentPath(newVal) {
      // 监听路径变化
    },
    '$route.path'(newPath) {
      // 监听路由变化
    },
    // 监听用户变化，重新初始化偏好设置
    userId(newUserId, oldUserId) {
      if (newUserId && newUserId !== oldUserId) {
        this.restoreUserMenuPreferences()
      }
    }
  },
  methods: {
    // 更新用户状态
    async updateUserState() {
      try {
        this.userInfo = getCurrentUser()
        this.userAuthState = isAuthenticated()
        
        if (this.userInfo && this.userAuthState) {
          this.userId = this.userInfo.id || this.userInfo.user_id
          
          // 只有在用户已登录时才获取动态菜单权限
          await this.loadDynamicMenuPermissions()
        } else {
          this.userId = null
          this.enabledMenuItems = []
          console.log('用户未登录，跳过权限加载')
        }
        
        // console.log('用户状态更新:', {
        //   userInfo: this.userInfo,
        //   userAuthState: this.userAuthState,
        //   userId: this.userId
        // })
      } catch (error) {
        console.error('更新用户状态失败:', error)
        this.userInfo = null
        this.userAuthState = false
        this.userId = null
        this.enabledMenuItems = []
      }
    },
    
    // 加载动态菜单权限
    async loadDynamicMenuPermissions() {
      try {
        // console.log('开始加载动态菜单权限...')
        const permissionData = await fetchUserMenuPermissions()
        
        if (permissionData && permissionData.success) {
          // console.log('动态菜单权限加载成功:', permissionData)
          
          // 可以在这里根据权限数据更新UI状态
          // 例如：显示/隐藏某些菜单项
          this.updateMenuVisibility(permissionData)
        } else {
          // console.warn('动态菜单权限加载失败:', permissionData)
        }
      } catch (error) {
        console.error('加载动态菜单权限失败:', error)
      }
    },
    
    // 根据权限数据更新菜单可见性
    updateMenuVisibility(permissionData) {
      // 这里可以根据后端返回的权限数据来控制菜单的显示
      // 例如：根据权限隐藏某些底部导航项
      // console.log('更新菜单可见性:', permissionData)
    },
    
    // 处理权限变更
    handlePermissionChange(user) {
      // console.log('权限变更事件:', user)
      this.updateUserState()
    },
    
    // 处理localStorage变化
    handleStorageChange(event) {
      if (event.key === 'user' || event.key === 'token') {
        // console.log('localStorage变化:', event.key)
        this.updateUserState()
      }
    },
    
    // 处理斩词点击
    handleWordClick() {
      this.navigateTo('/index')
    },
    
    // 处理工具点击
    async handleToolsClick() {
      // 使用动态权限系统检查工具菜单权限
      await this.checkToolsPermissionDynamic()
    },
    
    // 动态检查工具权限
    async checkToolsPermissionDynamic() {
      try {
        // 检查前端登录状态
        if (!this.isUserLoggedIn) {
          this.$showError('请先登录后再使用工具功能')
          this.$router.push('/login')
          return
        }
        
        // 使用动态权限检查工具菜单权限
        const hasToolsPermission = await hasDynamicPermission('access_dev_tools')
        
        if (!hasToolsPermission) {
          const roleDisplay = this.userInfo?.role ? this.getRoleDisplayName(this.userInfo.role) : '当前角色'
          this.$showError(`${roleDisplay}暂无权限使用开发工具功能`)
          return
        }
        
        // 权限检查通过，打开工具菜单
        this.toggleMenu('tools')
        
      } catch (error) {
        console.error('检查工具权限失败:', error)
        this.$showError('权限检查失败，请稍后重试')
      }
    },
    
    // 计算菜单位置
    calculateMenuPosition(menuType) {
      this.$nextTick(() => {
        const tabRef = menuType === 'tools' ? this.$refs.toolsTab : this.$refs.fashionTab
        if (tabRef) {
          const rect = tabRef.getBoundingClientRect()
          const position = {
            left: rect.left + rect.width / 2 + 'px',
            transform: 'translateX(-50%)'
          }
          
          if (menuType === 'tools') {
            this.toolsMenuPosition = position
          } else {
            this.fashionMenuPosition = position
          }
        }
      })
    },
    
    // 计算开发中心二级菜单位置
    calculateDevCenterPosition() {
      this.$nextTick(() => {
        const toolsMenu = document.querySelector('.tools-menu.level-1')
        if (toolsMenu) {
          const rect = toolsMenu.getBoundingClientRect()
          const windowWidth = window.innerWidth
          const menuWidth = 320 // 二级菜单的最大宽度
          
          let leftPosition = rect.right + 8
          
          // 如果右侧空间不够，则显示在左侧
          if (leftPosition + menuWidth > windowWidth) {
            leftPosition = rect.left - menuWidth - 8
          }
          
          // 确保不超出屏幕左边界
          if (leftPosition < 8) {
            leftPosition = 8
          }
          
          this.devCenterMenuPosition = {
            left: leftPosition + 'px',
            bottom: '68px'
          }
        }
      })
    },
    
    // 切换菜单显示状态
    toggleMenu(menuType) {
      console.log('toggleMenu called with:', menuType, 'current activeMenu:', this.activeMenu)
      
      // 如果当前菜单已经是要切换的菜单，则关闭
      if (this.activeMenu === menuType) {
        this.activeMenu = null
        this.showDevCenter = false
        console.log('Menu closed:', menuType)
        return
      }
      
      // 关闭其他菜单，打开新菜单
      this.activeMenu = menuType
      
      // 根据菜单类型进行特殊处理
      if (menuType === 'tools') {
        // 工具菜单保持开发中心状态不变
        this.calculateMenuPosition('tools')
      } else {
        // 非工具菜单关闭开发中心
        this.showDevCenter = false
        if (menuType === 'fashion') {
          this.calculateMenuPosition('fashion')
        }
      }
      
      console.log('Menu opened:', menuType)
    },
    
    // 关闭菜单
    closeMenu() {
      this.activeMenu = null
      this.showDevCenter = false
    },
    
    // 处理遮罩层点击
    handleOverlayClick() {
      // 关闭所有菜单状态
      this.activeMenu = null
      this.showDevCenter = false
    },
    
    // 导航到指定页面
    async navigateTo(path) {
      // 检查是否需要认证
      if (this.requiresAuth(path)) {
        // 只检查前端登录状态，避免过度同步
        if (!this.isUserLoggedIn) {
          this.$showError('请先登录后再访问此功能')
          this.$router.push('/login')
          return
        }
      }
      
      // 使用权限检查的导航方法
      if (this.$navigateWithPermission) {
        this.$navigateWithPermission(path)
      } else {
        this.$router.push(path)
      }
      this.closeMenu()
    },
    
    // 检查页面是否需要认证
    requiresAuth(path) {
      const authRequiredPaths = [
        '/dashboard', '/profile', '/settings', '/word-learning',
        '/word-detail', '/word-root-analysis', '/story-reading',
        '/pattern-memory', '/resource-auth', '/subscription-management'
      ]
      return authRequiredPaths.some(authPath => path.startsWith(authPath))
    },
    
    // 切换开发中心显示
    toggleDevCenter() {
      console.log('toggleDevCenter called, current showDevCenter:', this.showDevCenter)
      this.showDevCenter = !this.showDevCenter
      if (this.showDevCenter) {
        this.calculateDevCenterPosition()
        console.log('Dev center opened')
      } else {
        console.log('Dev center closed')
      }
    },
    
    // 切换开发工具开关
    toggleDevTool(tool) {
      if (tool.enabled) {
        // 添加到启用列表
        if (!this.enabledMenuItems.find(item => item.id === tool.id)) {
          this.enabledMenuItems.push({
            id: tool.id,
            name: tool.title,
            path: tool.path
          })
        }
      } else {
        // 从启用列表移除
        this.enabledMenuItems = this.enabledMenuItems.filter(item => item.id !== tool.id)
        // 如果当前选中的工具被禁用，清除选择
        if (this.selectedTool === tool.id) {
          this.selectedTool = null
        }
      }
      
      // 保存用户菜单偏好
      this.saveUserMenuPreferences()
    },
    
    // 选择工具
    async selectTool(item) {
      // 同步登录状态
      const syncResult = await manualSyncAuth()
      this.updateUserState()
      
      // 检查用户认证状态
      if (!this.isUserLoggedIn) {
        this.$showError('请先登录后再使用该工具')
        this.$router.push('/login')
        return
      }
      
      // 检查工具访问权限
      if (!this.$canAccessPage(item.path)) {
        this.$showError('您没有权限使用该工具')
        return
      }
      
      this.selectedTool = item.id
      // 立即跳转到对应页面
      this.navigateTo(item.path)
      // 关闭工具菜单
      this.activeMenu = null
      
      // 保存用户菜单偏好
      this.saveUserMenuPreferences()
    },
    
    // 初始化用户偏好设置
    initializeUserPreferences() {
      // 获取用户ID
      this.getUserId()
      
      // 恢复用户菜单偏好
      this.restoreUserMenuPreferences()
    },
    
    // 获取用户ID
    getUserId() {
      try {
        // 从localStorage获取用户信息
        const userInfo = localStorage.getItem('user')
        if (userInfo) {
          const user = JSON.parse(userInfo)
          this.userId = user.id || user.user_id || 'default'
        } else {
          // 如果没有用户信息，使用默认ID
          this.userId = 'default'
        }
      } catch (error) {
        console.error('获取用户ID失败:', error)
        this.userId = 'default'
      }
    },
    
    // 获取角色显示名称
    getRoleDisplayName(role) {
      const roleNames = {
        'admin': '管理员',
        'dean': '教导主任', 
        'academic_director': '教务主任',
        'research_leader': '教研组长',
        'teacher': '自由老师',
        'parent': '家长',
        'student': '学生'
      }
      return roleNames[role] || role
    },
    
    // 恢复用户菜单偏好
    restoreUserMenuPreferences() {
      try {
        const storageKey = `menuPreferences_${this.userId}`
        const savedPreferences = localStorage.getItem(storageKey)
        
        if (savedPreferences) {
          const preferences = JSON.parse(savedPreferences)
          
          // 恢复启用的菜单项
          if (preferences.enabledMenuItems) {
            this.enabledMenuItems = preferences.enabledMenuItems
          }
          
          // 恢复选中的工具
          if (preferences.selectedTool) {
            this.selectedTool = preferences.selectedTool
          }
          
          // 恢复工具启用状态
          if (preferences.toolsEnabled) {
            this.allDevTools.forEach(tool => {
              const savedTool = preferences.toolsEnabled.find(t => t.id === tool.id)
              if (savedTool) {
                tool.enabled = savedTool.enabled
              }
            })
          }
          
          console.log('用户菜单偏好已恢复:', preferences)
        }
      } catch (error) {
        console.error('恢复用户菜单偏好失败:', error)
      }
    },
    
    // 保存用户菜单偏好
    saveUserMenuPreferences() {
      try {
        const preferences = {
          enabledMenuItems: this.enabledMenuItems,
          selectedTool: this.selectedTool,
          toolsEnabled: this.allDevTools.map(tool => ({
            id: tool.id,
            enabled: tool.enabled
          })),
          lastUpdated: new Date().toISOString()
        }
        
        const storageKey = `menuPreferences_${this.userId}`
        localStorage.setItem(storageKey, JSON.stringify(preferences))
        
        console.log('用户菜单偏好已保存:', preferences)
      } catch (error) {
        console.error('保存用户菜单偏好失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.tab-bar-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 9999;
}

.bottom-navigation {
  height: 60px;
  background: #ffffff;
  border-top: 1px solid #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: space-around;
  /* 适配安全区域 */
  padding-bottom: env(safe-area-inset-bottom);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10000;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  height: 100%;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.nav-item:hover {
  background-color: #f5f5f5;
}

.nav-item.active {
  color: #007AFF;
}

.nav-item.active .nav-icon {
  transform: scale(1.1);
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  margin-bottom: 2px;
  transition: transform 0.3s ease;
}

.icon {
  font-size: 18px;
  display: block;
}

.chinese-icon {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-item.active .chinese-icon {
  background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-text {
  font-size: 10px;
  color: #666;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-item.active .nav-text {
  color: #007AFF;
  font-weight: 600;
}

/* 弹出层容器 */
.popup-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  pointer-events: none;
  z-index: 10002;
}

/* 遮罩层 */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 60px; /* 不遮挡底部导航栏 */
  background: rgba(0, 0, 0, 0.3);
  pointer-events: all;
  z-index: 1000; /* 降低z-index，避免遮挡页面重要元素 */
}

/* 弹出菜单基础样式 */
.popup-menu {
  position: absolute;
  bottom: 68px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  min-width: 160px;
  max-width: 280px;
  pointer-events: all;
  z-index: 1001; /* 调整z-index，确保在遮罩层之上但不过度遮挡 */
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

/* 工具菜单样式 */
.tools-menu {
  min-width: 200px;
}

/* 时尚菜单样式 */
.fashion-menu {
  min-width: 160px;
}

/* 菜单项样式 */
.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #f0f0f0;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background-color: #f8f9fa;
}

.menu-icon {
  font-size: 16px;
  margin-right: 12px;
  width: 20px;
  text-align: center;
}

.menu-text {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* 开发中心菜单项特殊样式 */
.dev-center-item {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  justify-content: space-between;
}

.dev-center-item .menu-text {
  color: white;
  flex: 1;
}

.menu-arrow {
  font-size: 12px;
  margin-left: 8px;
  transition: transform 0.3s ease;
}

/* 菜单分割线 */
.menu-divider {
  height: 1px;
  background: #e8e8e8;
  margin: 8px 0;
}

/* 启用的工具列表 */
.enabled-tools {
  padding: 0;
}

.tool-menu-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.tool-menu-item:hover {
  background-color: #f8f9fa;
}

.tool-radio {
  margin-right: 8px;
  cursor: pointer;
}

.tool-label {
  cursor: pointer;
  flex: 1;
}

.tool-name {
  font-size: 13px;
  color: #333;
}

/* 无工具提示 */
.no-tools-tip {
  padding: 0;
}

.tip-text {
  padding: 12px 16px;
  font-size: 12px;
  color: #999;
  text-align: center;
  font-style: italic;
}

/* 开发中心二级菜单 */
.dev-center-menu {
  position: fixed;
  bottom: 68px;
  width: 320px;
  max-height: 400px;
  overflow-y: auto;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  pointer-events: all;
  z-index: 1002; /* 调整z-index，确保在一级菜单之上 */
  border: 1px solid #e0e0e0;
}

.dev-center-header {
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
}

.dev-center-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.dev-tool-list {
  padding: 8px 0;
}

.dev-tool-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s ease;
}

.dev-tool-item:last-child {
  border-bottom: none;
}

.dev-tool-item:hover {
  background-color: #f8f9fa;
}

.tool-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.tool-icon {
  font-size: 18px;
  margin-right: 12px;
  width: 24px;
  text-align: center;
}

.tool-details {
  flex: 1;
}

.tool-name {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 2px;
}

.tool-desc {
  display: block;
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

/* 开关样式 */
.tool-switch {
  position: relative;
  margin-left: 12px;
}

.tool-switch input[type="checkbox"] {
  display: none;
}

.switch-label {
  display: block;
  width: 44px;
  height: 24px;
  background: #ddd;
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.switch-label::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.tool-switch input[type="checkbox"]:checked + .switch-label {
  background: #007AFF;
}

.tool-switch input[type="checkbox"]:checked + .switch-label::after {
  transform: translateX(20px);
}

/* 过渡动画 */
.popup-fade-enter-active,
.popup-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.popup-fade-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.popup-fade-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.3s ease;
}

.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .bottom-navigation {
    height: 55px;
  }
  
  .nav-text {
    font-size: 9px;
  }
  
  .icon {
    font-size: 16px;
  }
  
  .chinese-icon {
    font-size: 14px;
  }
  
  .popup-menu {
    bottom: 63px;
    max-width: calc(100vw - 32px);
  }
  
  .dev-center-menu {
    width: calc(100vw - 32px);
    max-width: 320px;
    bottom: 63px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .bottom-navigation {
    background: #1c1c1e;
    border-top-color: #38383a;
  }
  
  .popup-menu,
  .dev-center-menu {
    background: #2c2c2e;
  }
  
  .menu-item:hover,
  .tool-menu-item:hover,
  .dev-tool-item:hover {
    background-color: #3a3a3c;
  }
  
  .menu-text,
  .tool-name {
    color: #ffffff;
  }
  
  .tool-desc {
    color: #8e8e93;
  }
  
  .menu-divider {
    background: #38383a;
  }
  
  .tip-text {
    color: #8e8e93;
  }
}
</style>