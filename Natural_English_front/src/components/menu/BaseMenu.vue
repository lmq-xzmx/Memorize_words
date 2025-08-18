<template>
  <div class="base-menu">
    <div class="menu-header">
      <h2 class="menu-title">{{ title }}</h2>
    </div>
    <nav class="menu-nav">
      <ul class="menu-list">
        <li 
          v-for="item in filteredMenuItems" 
          :key="item.id"
          class="menu-item"
          :class="{ 'active': isActive(item.path) }"
        >
          <router-link 
            :to="item.path" 
            class="menu-link"
            @click="handleMenuClick(item)"
          >
            <i v-if="item.icon" :class="item.icon" class="menu-icon"></i>
            <span class="menu-text">{{ item.title }}</span>
          </router-link>
          
          <!-- 子菜单 -->
          <ul v-if="item.children && item.children.length" class="submenu">
            <li 
              v-for="child in item.children" 
              :key="child.id"
              class="submenu-item"
              :class="{ 'active': isActive(child.path) }"
            >
              <router-link 
                :to="child.path" 
                class="submenu-link"
                @click="handleMenuClick(child)"
              >
                <i v-if="child.icon" :class="child.icon" class="submenu-icon"></i>
                <span class="submenu-text">{{ child.title }}</span>
              </router-link>
            </li>
          </ul>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'

interface MenuItem {
  id: string
  title: string
  path: string
  icon?: string
  permission?: string
  children?: MenuItem[]
}

interface Props {
  title?: string
  menuItems: MenuItem[]
}

const props = withDefaults(defineProps<Props>(), {
  title: '菜单',
  menuItems: () => []
})

const route = useRoute()
const store = useStore()

// 检查权限
const hasPermission = (permission?: string): boolean => {
  if (!permission) return true
  return store.getters['user/hasPermission'](permission)
}

// 过滤有权限的菜单项
const filteredMenuItems = computed(() => {
  const filterItems = (items: MenuItem[]): MenuItem[] => {
    return items.filter(item => {
      if (!hasPermission(item.permission)) return false
      
      if (item.children) {
        item.children = filterItems(item.children)
      }
      
      return true
    })
  }
  
  return filterItems(props.menuItems)
})

// 检查菜单项是否激活
const isActive = (path: string): boolean => {
  return route.path === path || route.path.startsWith(path + '/')
}

// 处理菜单点击
const handleMenuClick = (item: MenuItem) => {
  // 可以在这里添加菜单点击的额外逻辑
  console.log('Menu clicked:', item.title)
}
</script>

<style lang="scss" scoped>
.base-menu {
  background: var(--bg-color-secondary);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-light);
  overflow: hidden;
}

.menu-header {
  padding: 1rem;
  background: var(--primary-color);
  color: white;
  
  .menu-title {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
  }
}

.menu-nav {
  padding: 0.5rem 0;
}

.menu-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.menu-item {
  margin: 0;
  
  &.active > .menu-link {
    background: var(--primary-color);
    color: white;
  }
}

.menu-link {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  color: var(--text-color);
  text-decoration: none;
  transition: var(--transition);
  
  &:hover {
    background: var(--bg-color-hover);
    color: var(--primary-color);
  }
  
  .menu-icon {
    margin-right: 0.5rem;
    font-size: 1.1rem;
  }
  
  .menu-text {
    flex: 1;
  }
}

.submenu {
  list-style: none;
  margin: 0;
  padding: 0;
  background: var(--bg-color);
}

.submenu-item {
  &.active > .submenu-link {
    background: var(--primary-color);
    color: white;
  }
}

.submenu-link {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  color: var(--text-color-secondary);
  text-decoration: none;
  transition: var(--transition);
  font-size: 0.9rem;
  
  &:hover {
    background: var(--bg-color-hover);
    color: var(--primary-color);
  }
  
  .submenu-icon {
    margin-right: 0.5rem;
    font-size: 1rem;
  }
  
  .submenu-text {
    flex: 1;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .menu-link {
    padding: 0.6rem 0.8rem;
    
    .menu-text {
      font-size: 0.9rem;
    }
  }
  
  .submenu-link {
    padding: 0.4rem 0.8rem 0.4rem 2rem;
    font-size: 0.85rem;
  }
}
</style>