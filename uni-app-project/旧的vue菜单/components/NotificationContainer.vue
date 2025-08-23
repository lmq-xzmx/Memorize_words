<template>
  <Teleport to="body">
    <div class="notification-container">
      <TransitionGroup name="notification" tag="div" class="notification-list">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          :class="getNotificationClasses(notification)"
          class="notification"
          @click="handleNotificationClick(notification)"
        >
          <!-- 图标 -->
          <div class="notification-icon">
            <component :is="getNotificationIcon(notification.type)" />
          </div>
          
          <!-- 内容 -->
          <div class="notification-content">
            <h4 v-if="notification.title" class="notification-title">
              {{ notification.title }}
            </h4>
            <p class="notification-message">
              {{ notification.message }}
            </p>
            
            <!-- 操作按钮 -->
            <div v-if="notification.actions" class="notification-actions">
              <button
                v-for="action in notification.actions"
                :key="action.label"
                :class="getActionClasses(action)"
                class="notification-action"
                @click.stop="handleActionClick(action, notification)"
              >
                {{ action.label }}
              </button>
            </div>
          </div>
          
          <!-- 关闭按钮 -->
          <button
            v-if="notification.closable !== false"
            class="notification-close"
            @click.stop="removeNotification(notification.id)"
            :aria-label="'关闭通知'"
          >
            <CloseIcon />
          </button>
          
          <!-- 进度条 -->
          <div
            v-if="notification.duration > 0"
            class="notification-progress"
            :style="getProgressStyle(notification)"
          ></div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useStore } from 'vuex'

// 图标组件
const SuccessIcon = {
  template: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
    </svg>
  `
}

const ErrorIcon = {
  template: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
    </svg>
  `
}

const WarningIcon = {
  template: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
    </svg>
  `
}

const InfoIcon = {
  template: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
    </svg>
  `
}

const CloseIcon = {
  template: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
    </svg>
  `
}

export default {
  name: 'NotificationContainer',
  
  components: {
    SuccessIcon,
    ErrorIcon,
    WarningIcon,
    InfoIcon,
    CloseIcon
  },
  
  setup() {
    const store = useStore()
    
    // 响应式状态
    const timers = ref(new Map())
    
    // 计算属性
    const notifications = computed(() => store.getters['ui/notifications'])
    
    // 获取通知样式类
    const getNotificationClasses = (notification) => {
      return {
        [`notification-${notification.type}`]: true,
        'notification-clickable': notification.clickable || notification.actions,
        'notification-persistent': notification.duration === 0
      }
    }
    
    // 获取通知图标
    const getNotificationIcon = (type) => {
      const iconMap = {
        success: 'SuccessIcon',
        error: 'ErrorIcon',
        warning: 'WarningIcon',
        info: 'InfoIcon'
      }
      return iconMap[type] || 'InfoIcon'
    }
    
    // 获取操作按钮样式类
    const getActionClasses = (action) => {
      return {
        'btn': true,
        'btn-sm': true,
        [`btn-${action.type || 'secondary'}`]: true
      }
    }
    
    // 获取进度条样式
    const getProgressStyle = (notification) => {
      if (!notification.duration || notification.duration === 0) {
        return { display: 'none' }
      }
      
      const timer = timers.value.get(notification.id)
      if (!timer) {
        return { width: '100%' }
      }
      
      const elapsed = Date.now() - timer.startTime
      const progress = Math.max(0, 100 - (elapsed / notification.duration) * 100)
      
      return {
        width: `${progress}%`,
        transition: 'width 100ms linear'
      }
    }
    
    // 移除通知
    const removeNotification = (id) => {
      // 清除定时器
      const timer = timers.value.get(id)
      if (timer) {
        clearTimeout(timer.timeoutId)
        timers.value.delete(id)
      }
      
      // 从store中移除
      store.dispatch('ui/removeNotification', id)
    }
    
    // 处理通知点击
    const handleNotificationClick = (notification) => {
      if (notification.clickable && notification.onClick) {
        notification.onClick(notification)
      }
      
      // 如果设置了点击关闭，则关闭通知
      if (notification.clickToClose !== false) {
        removeNotification(notification.id)
      }
    }
    
    // 处理操作按钮点击
    const handleActionClick = (action, notification) => {
      if (action.onClick) {
        action.onClick(notification)
      }
      
      // 如果操作设置了关闭通知，则关闭
      if (action.closeNotification !== false) {
        removeNotification(notification.id)
      }
    }
    
    // 设置自动关闭定时器
    const setupAutoClose = (notification) => {
      if (notification.duration > 0) {
        const startTime = Date.now()
        const timeoutId = setTimeout(() => {
          removeNotification(notification.id)
        }, notification.duration)
        
        timers.value.set(notification.id, {
          timeoutId,
          startTime
        })
      }
    }
    
    // 监听通知变化
    const unwatchNotifications = computed(() => notifications.value).effect(() => {
      notifications.value.forEach(notification => {
        if (!timers.value.has(notification.id)) {
          setupAutoClose(notification)
        }
      })
    })
    
    // 键盘事件处理
    const handleKeydown = (event) => {
      // Esc键关闭所有可关闭的通知
      if (event.key === 'Escape') {
        notifications.value.forEach(notification => {
          if (notification.closable !== false) {
            removeNotification(notification.id)
          }
        })
      }
    }
    
    // 生命周期
    onMounted(() => {
      document.addEventListener('keydown', handleKeydown)
    })
    
    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeydown)
      
      // 清除所有定时器
      timers.value.forEach(timer => {
        clearTimeout(timer.timeoutId)
      })
      timers.value.clear()
      
      // 停止监听
      if (unwatchNotifications) {
        unwatchNotifications()
      }
    })
    
    return {
      notifications,
      getNotificationClasses,
      getNotificationIcon,
      getActionClasses,
      getProgressStyle,
      removeNotification,
      handleNotificationClick,
      handleActionClick
    }
  }
}
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: var(--space-4);
  right: var(--space-4);
  z-index: var(--z-toast);
  pointer-events: none;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  max-width: 400px;
  width: 100vw;
  max-height: calc(100vh - var(--space-8));
  overflow-y: auto;
}

.notification {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  pointer-events: auto;
  transition: all var(--duration-normal) var(--ease-out);
  overflow: hidden;
}

.notification:hover {
  box-shadow: var(--shadow-xl);
  transform: translateY(-2px);
}

.notification-clickable {
  cursor: pointer;
}

.notification-clickable:hover {
  border-color: var(--color-border-hover);
}

/* 通知类型样式 */
.notification-success {
  border-left: 4px solid var(--color-success);
}

.notification-error {
  border-left: 4px solid var(--color-error);
}

.notification-warning {
  border-left: 4px solid var(--color-warning);
}

.notification-info {
  border-left: 4px solid var(--color-primary);
}

/* 图标样式 */
.notification-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  margin-top: 2px;
}

.notification-success .notification-icon {
  color: var(--color-success);
}

.notification-error .notification-icon {
  color: var(--color-error);
}

.notification-warning .notification-icon {
  color: var(--color-warning);
}

.notification-info .notification-icon {
  color: var(--color-primary);
}

.notification-icon svg {
  width: 100%;
  height: 100%;
}

/* 内容样式 */
.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  margin: 0 0 var(--space-1) 0;
  line-height: var(--line-height-tight);
}

.notification-message {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: var(--line-height-normal);
  word-wrap: break-word;
}

/* 操作按钮样式 */
.notification-actions {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-3);
}

.notification-action {
  font-size: var(--font-size-xs);
  padding: var(--space-1) var(--space-3);
}

/* 关闭按钮样式 */
.notification-close {
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.notification-close:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text);
}

.notification-close svg {
  width: 16px;
  height: 16px;
}

/* 进度条样式 */
.notification-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: var(--color-primary);
  transition: width 100ms linear;
}

.notification-success .notification-progress {
  background: var(--color-success);
}

.notification-error .notification-progress {
  background: var(--color-error);
}

.notification-warning .notification-progress {
  background: var(--color-warning);
}

/* 过渡动画 */
.notification-enter-active {
  transition: all var(--duration-normal) var(--ease-out);
}

.notification-leave-active {
  transition: all var(--duration-normal) var(--ease-in);
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
}

.notification-move {
  transition: transform var(--duration-normal) var(--ease-out);
}

/* 响应式适配 */
@media (max-width: 640px) {
  .notification-container {
    top: var(--space-2);
    right: var(--space-2);
    left: var(--space-2);
  }
  
  .notification-list {
    max-width: none;
  }
  
  .notification {
    padding: var(--space-3);
  }
  
  .notification-title {
    font-size: var(--font-size-xs);
  }
  
  .notification-message {
    font-size: var(--font-size-xs);
  }
}

/* 深色主题适配 */
[data-theme="dark"] .notification {
  background: var(--color-bg-secondary);
  border-color: var(--color-border);
}

[data-theme="dark"] .notification:hover {
  border-color: var(--color-border-hover);
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .notification {
    border-width: 2px;
  }
  
  .notification-close {
    border: 1px solid var(--color-border);
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  .notification-enter-active,
  .notification-leave-active,
  .notification-move {
    transition: none !important;
  }
  
  .notification:hover {
    transform: none !important;
  }
  
  .notification-progress {
    transition: none !important;
  }
}

/* 打印样式 */
@media print {
  .notification-container {
    display: none !important;
  }
}
</style>