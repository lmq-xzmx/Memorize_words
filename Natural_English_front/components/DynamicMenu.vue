<template>
  <div class="dynamic-menu">
    <!-- 主菜单 -->
    <div class="main-menu">
      <div 
        v-for="menu in accessibleMenus" 
        :key="menu.id"
        class="menu-item"
        :class="{ active: isActiveMenu(menu.path) }"
        @click="navigateToMenu(menu)"
      >
        <span class="menu-icon">{{ menu.icon }}</span>
        <span class="menu-title">{{ menu.title }}</span>
        <span v-if="menu.badge" class="menu-badge">{{ menu.badge }}</span>
      </div>
    </div>
    
    <!-- 角色信息显示 -->
    <div class="role-info" v-if="currentUser">
      <div class="user-avatar">
        <img v-if="currentUser.avatar" :src="currentUser.avatar" :alt="currentUser.username" />
        <div v-else class="default-avatar">{{ currentUser.username?.charAt(0)?.toUpperCase() }}</div>
      </div>
      <div class="user-details">
        <div class="username">{{ currentUser.username }}</div>
        <div class="user-role">{{ roleDisplayName }}</div>
      </div>
    </div>
    
    <!-- 快速操作按钮 -->
    <div class="quick-actions">
      <button 
        v-permission="'view_analytics'"
        class="quick-btn analytics-btn"
        @click="$navigateWithPermission('/analytics')"
        title="数据分析"
      >
        📊
      </button>
      
      <button 
        v-permission="'manage_resource_auth'"
        class="quick-btn resource-btn"
        @click="$navigateWithPermission('/resource-auth')"
        title="资源管理"
      >
        🔐
      </button>
      
      <button 
        v-role="['admin', 'dean']"
        class="quick-btn admin-btn"
        @click="$navigateWithPermission('/admin/dev-index')"
        title="管理面板"
      >
        ⚙️
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DynamicMenu',
  
  data() {
    return {
      // 这些数据会通过权限混入自动注入
    }
  },
  
  computed: {
    /**
     * 根据用户角色过滤菜单项
     */
    filteredMenus() {
      return this.accessibleMenus.map(menu => {
        // 为某些菜单添加徽章
        if (menu.id === 'word-challenge' && this.isStudent) {
          menu.badge = '新'
        }
        if (menu.id === 'analytics' && this.isTeacher) {
          menu.badge = '📈'
        }
        return menu
      })
    }
  },
  
  methods: {
    /**
     * 检查菜单是否为当前激活状态
     * @param {string} path - 菜单路径
     * @returns {boolean} 是否激活
     */
    isActiveMenu(path) {
      return this.$route.path === path || this.$route.path.startsWith(path + '/')
    },
    
    /**
     * 导航到菜单页面
     * @param {Object} menu - 菜单对象
     */
    navigateToMenu(menu) {
      if (this.$canAccessPage(menu.path)) {
        this.$router.push(menu.path)
      } else {
        this.$showError(`您没有权限访问 ${menu.title}`)
      }
    },
    
    /**
     * 处理权限变更
     * @param {Object} user - 用户信息
     */
    $onPermissionChange(user) {
      // 重新计算可访问菜单
      this.$updateUserInfo()
      
      // 检查当前页面是否还有权限访问
      if (user && !this.$canAccessPage(this.$route.path)) {
        this.$router.push('/dashboard')
        this.$showError('您的权限已变更，已重定向到仪表板')
      }
    }
  },
  
  watch: {
    /**
     * 监听路由变化，更新菜单状态
     */
    '$route'(to, from) {
      // 检查新路由的权限
      if (!this.$canAccessPage(to.path)) {
        this.$router.push('/dashboard')
        this.$showError('您没有权限访问该页面')
      }
    }
  }
}
</script>

<style scoped>
.dynamic-menu {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 主菜单样式 */
.main-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.menu-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.menu-item:hover::before {
  left: 100%;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.menu-item.active {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
}

.menu-icon {
  font-size: 20px;
  margin-right: 12px;
  min-width: 24px;
  text-align: center;
}

.menu-title {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.menu-badge {
  background: linear-gradient(45deg, #ff6b6b, #ee5a24);
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
  min-width: 16px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* 角色信息样式 */
.role-info {
  display: flex;
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  margin-right: 12px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-avatar {
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.user-details {
  flex: 1;
}

.username {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin-bottom: 4px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.user-role {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 8px;
  display: inline-block;
}

/* 快速操作按钮样式 */
.quick-actions {
  display: flex;
  gap: 8px;
  justify-content: space-between;
}

.quick-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.quick-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: all 0.3s ease;
}

.quick-btn:hover::before {
  width: 100px;
  height: 100px;
}

.quick-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.quick-btn:active {
  transform: translateY(0);
}

.analytics-btn:hover {
  background: rgba(52, 152, 219, 0.3);
}

.resource-btn:hover {
  background: rgba(46, 204, 113, 0.3);
}

.admin-btn:hover {
  background: rgba(231, 76, 60, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dynamic-menu {
    padding: 12px;
  }
  
  .menu-item {
    padding: 10px 12px;
  }
  
  .menu-icon {
    font-size: 18px;
    margin-right: 10px;
  }
  
  .menu-title {
    font-size: 13px;
  }
  
  .role-info {
    padding: 12px;
  }
  
  .user-avatar {
    width: 40px;
    height: 40px;
  }
  
  .username {
    font-size: 14px;
  }
  
  .quick-btn {
    padding: 10px;
    font-size: 16px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .dynamic-menu {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  }
  
  .menu-item {
    background: rgba(255, 255, 255, 0.05);
  }
  
  .menu-item:hover {
    background: rgba(255, 255, 255, 0.1);
  }
  
  .role-info {
    background: rgba(255, 255, 255, 0.05);
  }
  
  .quick-btn {
    background: rgba(255, 255, 255, 0.05);
  }
}

/* 无障碍支持 */
@media (prefers-reduced-motion: reduce) {
  .menu-item,
  .quick-btn {
    transition: none;
  }
  
  .menu-item::before,
  .quick-btn::before {
    display: none;
  }
  
  .menu-badge {
    animation: none;
  }
}

/* 加载状态 */
.dynamic-menu.loading {
  opacity: 0.7;
  pointer-events: none;
}

.dynamic-menu.loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 24px;
  height: 24px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: translate(-50%, -50%) rotate(0deg); }
  100% { transform: translate(-50%, -50%) rotate(360deg); }
}
</style>

