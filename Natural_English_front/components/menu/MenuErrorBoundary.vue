<template>
  <ErrorBoundary
    :show-details="isDevelopment"
    :max-retries="3"
    @error="handleMenuError"
    @retry="handleRetry"
    @reset="handleReset"
  >
    <template #default>
      <slot></slot>
    </template>
  </ErrorBoundary>
</template>

<script setup>
import { computed } from 'vue'
import ErrorBoundary from '@/components/common/ErrorBoundary.vue'
import { useMenuManager } from '@/composables/useMenuManager'

const props = defineProps({
  menuType: {
    type: String,
    default: 'unknown'
  },
  fallbackMessage: {
    type: String,
    default: '菜单加载失败，请重试'
  }
})

const emit = defineEmits(['menu-error', 'menu-retry', 'menu-reset'])

const { closeAllMenus } = useMenuManager()

// 判断是否为开发环境
const isDevelopment = computed(() => {
  return import.meta.env.DEV || import.meta.env.MODE === 'development'
})

// 处理菜单错误
const handleMenuError = (errorInfo) => {
  try {
    console.error(`菜单错误 [${props.menuType}]:`, errorInfo)
    
    // 关闭所有菜单以防止状态混乱
    closeAllMenus()
    
    // 记录错误到监控系统（如果有的话）
    if (window.errorTracker) {
      window.errorTracker.captureException(errorInfo.error, {
        tags: {
          component: 'menu',
          menuType: props.menuType
        },
        extra: {
          componentInfo: errorInfo.info,
          instance: errorInfo.instance
        }
      })
    }
    
    emit('menu-error', {
      ...errorInfo,
      menuType: props.menuType
    })
  } catch (handlerError) {
    console.error('处理菜单错误时出现异常:', handlerError)
  }
}

// 处理重试
const handleRetry = (retryCount) => {
  try {
    console.log(`菜单重试 [${props.menuType}] 第${retryCount}次`)
    
    // 重试前先关闭所有菜单
    closeAllMenus()
    
    emit('menu-retry', {
      menuType: props.menuType,
      retryCount
    })
  } catch (error) {
    console.error('处理菜单重试时出现异常:', error)
  }
}

// 处理重置
const handleReset = () => {
  try {
    console.log(`菜单重置 [${props.menuType}]`)
    
    // 重置时关闭所有菜单
    closeAllMenus()
    
    emit('menu-reset', {
      menuType: props.menuType
    })
  } catch (error) {
    console.error('处理菜单重置时出现异常:', error)
  }
}
</script>

<style scoped>
/* 菜单错误边界不需要额外样式，继承ErrorBoundary的样式 */
</style>