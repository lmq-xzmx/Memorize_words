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

<style lang="scss" scoped>
@use '../styles/index.scss';
@include bem-block('dynamic-menu') {
  @include flex-column;
  height: 100%;
  background: linear-gradient(135deg, var(--color-primary-500) 0%, var(--color-purple-600) 100%);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-4);
  box-shadow: var(--shadow-2xl);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(var(--color-white), 0.1);

  @include bem-modifier('loading') {
    opacity: 0.7;
    pointer-events: none;

    &::after {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      width: 24px;
      height: 24px;
      border: 2px solid rgba(var(--color-white), 0.3);
      border-top: 2px solid var(--color-white);
      border-radius: var(--border-radius-full);
      transform: translate(-50%, -50%);
      animation: spin 1s linear infinite;
    }
  }
}

@include bem-element('main-menu') {
  flex: 1;
  @include flex-column;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-4);
}

@include bem-element('menu-item') {
  @include flex-center;
  padding: var(--spacing-3) var(--spacing-4);
  border-radius: var(--border-radius-lg);
  background: rgba(var(--color-white), 0.1);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(var(--color-white), 0.1);
  cursor: pointer;
  @include transition;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba($color-white, 0.2), transparent);
    @include transition('left', 0.5s);
  }

  &:hover {
    background: rgba(var(--color-white), 0.2);
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);

    &::before {
      left: 100%;
    }
  }

  @include bem-modifier('active') {
    background: rgba($color-white, 0.25);
    border-color: rgba($color-white, 0.3);
    box-shadow: 0 0 20px rgba($color-white, 0.3);
  }
}

@include bem-element('menu-icon') {
  @include text-style('lg');
  margin-right: var(--spacing-3);
  min-width: 24px;
  text-align: center;
}

@include bem-element('menu-title') {
  flex: 1;
  @include text-style('sm', 'medium');
  color: var(--color-white);
  text-shadow: 0 1px 2px rgba(var(--color-black), 0.3);
}

@include bem-element('menu-badge') {
  background: linear-gradient(45deg, $color-red-500, $color-orange-600);
  color: $color-white;
  @include text-style('xs', 'semibold');
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--border-radius-xl);
  min-width: 16px;
  text-align: center;
  box-shadow: 0 2px 8px rgba($color-red-500, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@include bem-element('role-info') {
  @include flex-center;
  padding: var(--spacing-4);
  background: rgba(var(--color-white), 0.1);
  border-radius: var(--border-radius-xl);
  margin-bottom: var(--spacing-4);
  border: 1px solid rgba(var(--color-white), 0.1);
}

@include bem-element('user-avatar') {
  width: 48px;
  height: 48px;
  border-radius: var(--border-radius-full);
  margin-right: var(--spacing-3);
  overflow: hidden;
  border: 2px solid rgba(var(--color-white), 0.3);
  box-shadow: var(--shadow-lg);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

@include bem-element('default-avatar') {
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, var(--color-primary-500), var(--color-purple-600));
  @include flex-center;
  color: var(--color-white);
  @include text-style('lg', 'semibold');
  text-shadow: 0 1px 2px rgba(var(--color-black), 0.3);
}

@include bem-element('user-details') {
  flex: 1;
}

@include bem-element('username') {
  @include text-style('base', 'semibold');
  color: var(--color-white);
  margin-bottom: var(--spacing-1);
  text-shadow: 0 1px 2px rgba(var(--color-black), 0.3);
}

@include bem-element('user-role') {
  @include text-style('xs');
  color: rgba(var(--color-white), 0.8);
  background: rgba(var(--color-white), 0.1);
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--border-radius-lg);
  display: inline-block;
}

@include bem-element('quick-actions') {
  display: flex;
  gap: var(--spacing-2);
  justify-content: space-between;
}

@include bem-element('quick-btn') {
  flex: 1;
  padding: var(--spacing-3);
  border: none;
  border-radius: var(--border-radius-lg);
  background: rgba(var(--color-white), 0.1);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(var(--color-white), 0.1);
  color: var(--color-white);
  @include text-style('lg');
  cursor: pointer;
  @include transition;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: rgba(var(--color-white), 0.2);
    border-radius: var(--border-radius-full);
    transform: translate(-50%, -50%);
    @include transition;
  }

  &:hover {
    background: rgba($color-white, 0.2);
    transform: translateY(-2px);
    box-shadow: $shadow-lg;

    &::before {
      width: 100px;
      height: 100px;
    }
  }

  &:active {
    transform: translateY(0);
  }

  @include bem-modifier('analytics') {
    &:hover {
      background: rgba($color-blue-500, 0.3);
    }
  }

  @include bem-modifier('resource') {
    &:hover {
      background: rgba($color-green-500, 0.3);
    }
  }

  @include bem-modifier('admin') {
    &:hover {
      background: rgba($color-red-500, 0.3);
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .dynamic-menu {
    padding: var(--spacing-3);
  }
  
  .dynamic-menu__menu-item {
    padding: var(--spacing-2) var(--spacing-3);
  }
  
  .dynamic-menu__menu-icon {
    @include text-style('base');
    margin-right: var(--spacing-2);
  }
  
  .dynamic-menu__menu-title {
    @include text-style('xs', 'medium');
  }
  
  .dynamic-menu__role-info {
    padding: var(--spacing-3);
  }
  
  .dynamic-menu__user-avatar {
    width: 40px;
    height: 40px;
  }
  
  .dynamic-menu__username {
    @include text-style('sm', 'semibold');
  }
  
  .dynamic-menu__quick-btn {
    padding: var(--spacing-2);
    @include text-style('base');
  }
}

// 深色模式支持
@media (prefers-color-scheme: dark) {
  .dynamic-menu {
    background: linear-gradient(135deg, $color-gray-800 0%, $color-gray-700 100%);
  }
  
  .dynamic-menu__menu-item {
    background: rgba(var(--color-white), 0.05);

    &:hover {
      background: rgba(var(--color-white), 0.1);
    }
  }
  
  .dynamic-menu__role-info {
    background: rgba($color-white, 0.05);
  }
  
  .dynamic-menu__quick-btn {
    background: rgba($color-white, 0.05);
  }
}

// 无障碍支持
@media (prefers-reduced-motion: reduce) {
  .dynamic-menu__menu-item {
    transition: none;
    
    &::before {
      display: none;
    }
  }
  
  .dynamic-menu__quick-btn {
    transition: none;
    
    &::before {
      display: none;
    }
  }
  
  .dynamic-menu__menu-badge {
    animation: none;
  }
}

@keyframes spin {
  0% { transform: translate(-50%, -50%) rotate(0deg); }
  100% { transform: translate(-50%, -50%) rotate(360deg); }
}
</style>

