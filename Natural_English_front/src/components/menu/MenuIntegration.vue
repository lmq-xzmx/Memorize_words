<template>
  <div class="menu-integration">
    <!-- 移动端底部导航 -->
    <MobileTabBar 
      v-if="isMobile" 
      :menu-items="mobileMenuItems"
      :tools-config="toolsConfig"
      @menu-click="handleMenuClick"
      @tool-select="handleToolSelect"
    />
    
    <!-- 桌面端侧边栏菜单 -->
    <BaseMenu 
      v-else
      :title="menuTitle"
      :menu-items="desktopMenuItems"
      @menu-click="handleMenuClick"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import MobileTabBar from '../MobileTabBar.vue'
import BaseMenu from './BaseMenu.vue'
import { useMenuManager } from '@/composables/useMenuManager'
import { usePermission } from '@/composables/usePermission'
import type { MenuItem, ToolItem } from '@/composables/useMenuManager'

interface Props {
  title?: string
  forceMode?: 'mobile' | 'desktop' | 'auto'
}

const props = withDefaults(defineProps<Props>(), {
  title: '英语学习平台',
  forceMode: 'auto'
})

const emit = defineEmits<{
  menuClick: [item: MenuItem]
  toolSelect: [tool: ToolItem]
}>()

const store = useStore()
const router = useRouter()
const { 
  filteredMenus, 
  toolsConfig, 
  loadMenuConfig, 
  loadToolsConfig,
  setActiveMenu,
  toggleTool
} = useMenuManager()
const { hasPermission, hasRole } = usePermission()

// 响应式检测
const screenWidth = ref(window.innerWidth)
const isMobile = computed(() => {
  if (props.forceMode === 'mobile') return true
  if (props.forceMode === 'desktop') return false
  return screenWidth.value <= 768
})

// 菜单标题
const menuTitle = computed(() => {
  const userRole = store.getters['user/role']
  const roleNames = {
    'admin': '管理员控制台',
    'teacher': '教师工作台',
    'student': '学习中心'
  }
  return roleNames[userRole] || props.title
})

// 移动端菜单项（底部导航格式）
const mobileMenuItems = computed(() => {
  return filteredMenus.value
    .filter(item => {
      // 权限检查
      if (item.meta?.permissions?.length) {
        return item.meta.permissions.some(permission => hasPermission(permission))
      }
      if (item.meta?.roles?.length) {
        return item.meta.roles.some(role => hasRole(role))
      }
      return !item.meta?.hideInMenu
    })
    .map(item => ({
      id: item.id,
      title: item.meta?.title || item.name,
      path: item.path,
      icon: item.icon,
      permission: item.meta?.permissions?.[0],
      children: item.children?.map(child => ({
        id: child.id,
        title: child.meta?.title || child.name,
        path: child.path,
        icon: child.icon,
        permission: child.meta?.permissions?.[0]
      }))
    }))
    .sort((a, b) => (a.meta?.order || 0) - (b.meta?.order || 0))
})

// 桌面端菜单项（侧边栏格式）
const desktopMenuItems = computed(() => {
  return filteredMenus.value
    .filter(item => {
      // 权限检查
      if (item.meta?.permissions?.length) {
        return item.meta.permissions.some(permission => hasPermission(permission))
      }
      if (item.meta?.roles?.length) {
        return item.meta.roles.some(role => hasRole(role))
      }
      return !item.meta?.hideInMenu
    })
    .map(item => ({
      id: item.id,
      title: item.meta?.title || item.name,
      path: item.path,
      icon: item.icon,
      permission: item.meta?.permissions?.[0],
      children: item.children?.map(child => ({
        id: child.id,
        title: child.meta?.title || child.name,
        path: child.path,
        icon: child.icon,
        permission: child.meta?.permissions?.[0]
      }))
    }))
    .sort((a, b) => (a.meta?.order || 0) - (b.meta?.order || 0))
})

// 处理菜单点击
const handleMenuClick = (item: MenuItem) => {
  setActiveMenu(item.id)
  
  // 路由跳转
  if (item.path && item.path !== router.currentRoute.value.path) {
    router.push(item.path)
  }
  
  // 记录菜单使用统计
  store.dispatch('menu/recordMenuUsage', {
    menuId: item.id,
    timestamp: Date.now(),
    userAgent: navigator.userAgent
  })
  
  emit('menuClick', item)
}

// 处理工具选择
const handleToolSelect = (tool: ToolItem) => {
  toggleTool(tool.id)
  
  // 路由跳转
  if (tool.path && tool.path !== router.currentRoute.value.path) {
    router.push(tool.path)
  }
  
  // 更新工具状态
  store.dispatch('menu/updateToolStatus', {
    toolId: tool.id,
    enabled: !tool.enabled
  })
  
  emit('toolSelect', tool)
}

// 窗口大小变化监听
const handleResize = () => {
  screenWidth.value = window.innerWidth
}

// 初始化
onMounted(async () => {
  window.addEventListener('resize', handleResize)
  
  // 加载菜单和工具配置
  await Promise.all([
    loadMenuConfig(),
    loadToolsConfig()
  ])
  
  // 获取当前用户ID并初始化WebSocket连接
  const currentUser = store.getters['user/currentUser']
  const userId = currentUser?.id || currentUser?.user_id
  store.dispatch('menu/initializeWebSocket', userId)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.menu-integration {
  position: relative;
  width: 100%;
  height: 100%;
}

.desktop-menu {
  display: block;
  width: 100%;
  height: 100%;
}

.mobile-menu {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: white;
  border-top: 1px solid var(--color-border-light);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .desktop-menu {
    display: none;
  }
  
  .mobile-menu {
    display: block;
  }
  
  .menu-integration {
    position: static;
  }
}

/* 平板适配 */
@media (min-width: 769px) and (max-width: 1024px) {
  .desktop-menu {
    width: 240px;
  }
}

/* 桌面端适配 */
@media (min-width: 1025px) {
  .desktop-menu {
    width: 260px;
  }
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .mobile-menu {
    padding-bottom: env(safe-area-inset-bottom);
  }
}

/* 横屏适配 */
@media (orientation: landscape) and (max-height: 500px) {
  .mobile-menu {
    height: 48px;
  }
}

/* 高分辨率屏幕适配 */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .mobile-menu {
    border-top-width: 0.5px;
  }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .mobile-menu {
    background: #2a2a2a;
    border-top-color: #333333;
  }
}

/* 减少动画偏好适配 */
@media (prefers-reduced-motion: reduce) {
  .mobile-menu {
    transition: none;
  }
}
</style>