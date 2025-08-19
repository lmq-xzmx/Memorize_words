<template>
  <div class="permission-transition">
    <transition
      :name="transitionName"
      :mode="mode"
      :duration="duration"
      @before-enter="onBeforeEnter"
      @enter="onEnter"
      @after-enter="onAfterEnter"
      @before-leave="onBeforeLeave"
      @leave="onLeave"
      @after-leave="onAfterLeave"
    >
      <div v-if="show" :key="permissionKey" class="permission-content">
        <slot :permission-status="permissionStatus" />
      </div>
    </transition>

    <!-- 权限变更通知 -->
    <transition name="notification-slide">
      <div v-if="showNotification" class="permission-notification" :class="notificationClass">
        <div class="notification-icon">
          <svg v-if="notificationType === 'granted'" viewBox="0 0 24 24" width="20" height="20">
            <path fill="#48bb78" d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M11,16.5L18,9.5L16.59,8.09L11,13.67L7.91,10.59L6.5,12L11,16.5Z"/>
          </svg>
          <svg v-else-if="notificationType === 'denied'" viewBox="0 0 24 24" width="20" height="20">
            <path fill="#f56565" d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,7A5,5 0 0,0 7,12A5,5 0 0,0 12,17A5,5 0 0,0 17,12A5,5 0 0,0 12,7M12,9A3,3 0 0,1 15,12A3,3 0 0,1 12,15A3,3 0 0,1 9,12A3,3 0 0,1 12,9Z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" width="20" height="20">
            <path fill="#ed8936" d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,7A5,5 0 0,0 7,12A5,5 0 0,0 12,17A5,5 0 0,0 17,12A5,5 0 0,0 12,7Z"/>
          </svg>
        </div>
        <span class="notification-text">{{ notificationMessage }}</span>
        <button class="notification-close" @click="hideNotification">
          <svg viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
          </svg>
        </button>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
// @ts-ignore
import { onMounted, onUnmounted, nextTick } from 'vue'

interface Props {
  show?: boolean
  permission?: string | string[]
  transitionName?: string
  mode?: 'out-in' | 'in-out' | undefined
  duration?: number | { enter: number; leave: number }
  showNotifications?: boolean
  notificationDuration?: number
}

const props = withDefaults(defineProps<Props>(), {
  show: true,
  transitionName: 'permission-fade',
  mode: 'out-in',
  duration: 300,
  showNotifications: true,
  notificationDuration: 3000
})

const emit = defineEmits<{
  beforeEnter: [el: Element]
  enter: [el: Element]
  afterEnter: [el: Element]
  beforeLeave: [el: Element]
  leave: [el: Element]
  afterLeave: [el: Element]
  permissionChange: [status: 'granted' | 'denied' | 'loading']
}>()

const permissionStatus = ref<'granted' | 'denied' | 'loading'>('loading')
const showNotification = ref(false)
const notificationType = ref<'granted' | 'denied' | 'loading'>('loading')
const notificationMessage = ref('')
const notificationTimer = ref<number | null>(null)

// 生成唯一的权限键，用于强制重新渲染
const permissionKey = computed(() => {
  if (Array.isArray(props.permission)) {
    return props.permission.join(',')
  }
  return props.permission || 'default'
})

// 通知样式类
const notificationClass = computed(() => {
  return {
    'notification-granted': notificationType.value === 'granted',
    'notification-denied': notificationType.value === 'denied',
    'notification-loading': notificationType.value === 'loading'
  }
})

// 过渡事件处理
const onBeforeEnter = (el: Element) => {
  emit('beforeEnter', el)
}

const onEnter = (el: Element) => {
  emit('enter', el)
}

const onAfterEnter = (el: Element) => {
  emit('afterEnter', el)
}

const onBeforeLeave = (el: Element) => {
  emit('beforeLeave', el)
}

const onLeave = (el: Element) => {
  emit('leave', el)
}

const onAfterLeave = (el: Element) => {
  emit('afterLeave', el)
}

// 显示权限变更通知
const showPermissionNotification = (type: 'granted' | 'denied' | 'loading', message: string) => {
  if (!props.showNotifications) return

  notificationType.value = type
  notificationMessage.value = message
  showNotification.value = true

  // 清除之前的定时器
  if (notificationTimer.value) {
    clearTimeout(notificationTimer.value)
  }

  // 设置自动隐藏
  notificationTimer.value = window.setTimeout(() => {
    hideNotification()
  }, props.notificationDuration)
}

// 隐藏通知
const hideNotification = () => {
  showNotification.value = false
  if (notificationTimer.value) {
    clearTimeout(notificationTimer.value)
    notificationTimer.value = null
  }
}

// 更新权限状态
const updatePermissionStatus = (status: 'granted' | 'denied' | 'loading') => {
  const oldStatus = permissionStatus.value
  permissionStatus.value = status
  
  emit('permissionChange', status)
  
  // 显示状态变更通知
  if (oldStatus !== status) {
    let message = ''
    switch (status) {
      case 'granted':
        message = '权限验证通过'
        break
      case 'denied':
        message = '权限验证失败'
        break
      case 'loading':
        message = '正在验证权限...'
        break
    }
    showPermissionNotification(status, message)
  }
}

// 监听权限变化
watch(() => props.permission, () => {
  updatePermissionStatus('loading')
  
  // 模拟权限检查过程
  nextTick(() => {
    // 这里应该调用实际的权限检查逻辑
    // 暂时使用随机结果进行演示
    setTimeout(() => {
      const hasPermission = Math.random() > 0.3 // 70% 概率有权限
      updatePermissionStatus(hasPermission ? 'granted' : 'denied')
    }, 500)
  })
}, { immediate: true })

// 组件卸载时清理定时器
onUnmounted(() => {
  if (notificationTimer.value) {
    clearTimeout(notificationTimer.value)
  }
})

// 暴露方法给父组件
defineExpose({
  updatePermissionStatus,
  showPermissionNotification,
  hideNotification
})
</script>

<style scoped>
.permission-transition {
  position: relative;
  width: 100%;
}

.permission-content {
  width: 100%;
}

/* 默认淡入淡出过渡 */
.permission-fade-enter-active,
.permission-fade-leave-active {
  transition: all 0.3s ease;
}

.permission-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.permission-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 滑动过渡 */
.permission-slide-enter-active,
.permission-slide-leave-active {
  transition: all 0.4s ease;
}

.permission-slide-enter-from {
  opacity: 0;
  transform: translateX(-100%);
}

.permission-slide-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* 缩放过渡 */
.permission-scale-enter-active,
.permission-scale-leave-active {
  transition: all 0.3s ease;
}

.permission-scale-enter-from {
  opacity: 0;
  transform: scale(0.8);
}

.permission-scale-leave-to {
  opacity: 0;
  transform: scale(1.2);
}

/* 旋转过渡 */
.permission-rotate-enter-active,
.permission-rotate-leave-active {
  transition: all 0.5s ease;
}

.permission-rotate-enter-from {
  opacity: 0;
  transform: rotate(-180deg) scale(0.5);
}

.permission-rotate-leave-to {
  opacity: 0;
  transform: rotate(180deg) scale(0.5);
}

/* 权限变更通知 */
.permission-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  font-size: 14px;
  max-width: 300px;
}

.notification-granted {
  background: rgba(72, 187, 120, 0.9);
  color: white;
  border: 1px solid rgba(72, 187, 120, 0.3);
}

.notification-denied {
  background: rgba(245, 101, 101, 0.9);
  color: white;
  border: 1px solid rgba(245, 101, 101, 0.3);
}

.notification-loading {
  background: rgba(237, 137, 54, 0.9);
  color: white;
  border: 1px solid rgba(237, 137, 54, 0.3);
}

.notification-icon {
  flex-shrink: 0;
}

.notification-text {
  flex: 1;
  margin: 0;
}

.notification-close {
  background: none;
  border: none;
  color: currentColor;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.notification-close:hover {
  opacity: 1;
}

/* 通知滑入动画 */
.notification-slide-enter-active,
.notification-slide-leave-active {
  transition: all 0.3s ease;
}

.notification-slide-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-slide-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .permission-notification {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }
}
</style>