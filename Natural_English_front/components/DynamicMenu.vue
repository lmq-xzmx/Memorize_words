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
  background: #f8f9fa;
  border-right: 1px solid #e9ecef;
}

.main-menu {
  flex: 1;
  padding: 1rem 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  margin: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.menu-item:hover {
  background: #e9ecef;
  transform: translateX(2px);
}

.menu-item.active {
  background: #007bff;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
}

.menu-icon {
  font-size: 1.2rem;
  margin-right: 0.75rem;
  width: 1.5rem;
  text-align: center;
}

.menu-title {
  flex: 1;
  font-weight: 500;
}

.menu-badge {
  background: #dc3545;
  color: white;
  font-size: 0.75rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.75rem;
  margin-left: 0.5rem;
}

.role-info {
  padding: 1rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  background: white;
}

.user-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  margin-right: 0.75rem;
  overflow: hidden;
  background: #007bff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-avatar {
  color: white;
  font-weight: bold;
  font-size: 1.1rem;
}

.user-details {
  flex: 1;
}

.username {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.125rem;
}

.user-role {
  font-size: 0.875rem;
  color: #6c757d;
}

.quick-actions {
  padding: 0.5rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: space-around;
  background: white;
}

.quick-btn {
  width: 2.5rem;
  height: 2.5rem;
  border: none;
  border-radius: 50%;
  background: #f8f9fa;
  cursor: pointer;
  font-size: 1.1rem;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quick-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.analytics-btn:hover {
  background: #e3f2fd;
}

.resource-btn:hover {
  background: #fff3e0;
}

.admin-btn:hover {
  background: #f3e5f5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dynamic-menu {
    width: 100%;
    height: auto;
    flex-direction: row;
    border-right: none;
    border-top: 1px solid #e9ecef;
  }
  
  .main-menu {
    display: flex;
    flex: 1;
    padding: 0.5rem;
    overflow-x: auto;
  }
  
  .menu-item {
    flex-direction: column;
    min-width: 4rem;
    margin: 0 0.25rem;
    padding: 0.5rem;
    text-align: center;
  }
  
  .menu-icon {
    margin-right: 0;
    margin-bottom: 0.25rem;
  }
  
  .menu-title {
    font-size: 0.75rem;
  }
  
  .role-info {
    display: none;
  }
  
  .quick-actions {
    flex-direction: column;
    padding: 0.25rem;
  }
  
  .quick-btn {
    margin: 0.125rem 0;
    width: 2rem;
    height: 2rem;
    font-size: 0.9rem;
  }
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .dynamic-menu {
    background: #2d3748;
    border-right-color: #4a5568;
  }
  
  .menu-item:hover {
    background: #4a5568;
  }
  
  .role-info,
  .quick-actions {
    background: #2d3748;
    border-top-color: #4a5568;
  }
  
  .username {
    color: #e2e8f0;
  }
  
  .user-role {
    color: #a0aec0;
  }
  
  .quick-btn {
    background: #4a5568;
    color: #e2e8f0;
  }
}
</style>