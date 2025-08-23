<template>
  <teleport to="body">
    <transition name="modal" appear>
      <div 
        v-if="visible" 
        class="modal-overlay" 
        :class="overlayClasses"
        @click="handleOverlayClick"
        @keydown.esc="handleEscKey"
        tabindex="-1"
        ref="overlayRef"
      >
        <div 
          class="modal-container" 
          :class="containerClasses"
          @click.stop
          ref="containerRef"
        >
          <!-- 模态框头部 -->
          <div v-if="showHeader" class="modal-header">
            <div class="modal-title-section">
              <div v-if="icon" class="modal-icon">
                <component v-if="typeof icon === 'object'" :is="icon" />
                <span v-else>{{ icon }}</span>
              </div>
              <h3 v-if="title" class="modal-title">{{ title }}</h3>
              <p v-if="subtitle" class="modal-subtitle">{{ subtitle }}</p>
            </div>
            
            <button 
              v-if="closable" 
              class="modal-close"
              @click="handleClose"
              :title="closeButtonTitle"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          
          <!-- 模态框内容 -->
          <div class="modal-body" :class="bodyClasses">
            <slot>
              <div v-if="message" class="modal-message">
                {{ message }}
              </div>
            </slot>
          </div>
          
          <!-- 模态框底部 -->
          <div v-if="showFooter" class="modal-footer">
            <slot name="footer">
              <div class="modal-actions">
                <button 
                  v-if="showCancelButton"
                  class="modal-btn modal-btn-secondary"
                  @click="handleCancel"
                  :disabled="loading"
                >
                  {{ cancelText }}
                </button>
                
                <button 
                  v-if="showConfirmButton"
                  class="modal-btn modal-btn-primary"
                  :class="confirmButtonClass"
                  @click="handleConfirm"
                  :disabled="loading || confirmDisabled"
                >
                  <span v-if="loading" class="btn-spinner"></span>
                  {{ confirmText }}
                </button>
              </div>
            </slot>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script>
import { computed, ref, watch, nextTick, onMounted, onUnmounted } from 'vue'

export default {
  name: 'ModalComponent',
  
  props: {
    // 是否显示模态框
    visible: {
      type: Boolean,
      default: false
    },
    
    // 模态框标题
    title: {
      type: String,
      default: ''
    },
    
    // 模态框副标题
    subtitle: {
      type: String,
      default: ''
    },
    
    // 模态框图标
    icon: {
      type: [String, Object],
      default: null
    },
    
    // 模态框消息（当没有插槽内容时显示）
    message: {
      type: String,
      default: ''
    },
    
    // 模态框大小
    size: {
      type: String,
      default: 'medium',
      validator: (value) => {
        return ['small', 'medium', 'large', 'xlarge', 'fullscreen'].includes(value)
      }
    },
    
    // 模态框类型
    type: {
      type: String,
      default: 'default',
      validator: (value) => {
        return ['default', 'info', 'success', 'warning', 'error', 'confirm'].includes(value)
      }
    },
    
    // 是否可关闭
    closable: {
      type: Boolean,
      default: true
    },
    
    // 是否点击遮罩关闭
    closeOnOverlay: {
      type: Boolean,
      default: true
    },
    
    // 是否按ESC关闭
    closeOnEsc: {
      type: Boolean,
      default: true
    },
    
    // 是否显示头部
    showHeader: {
      type: Boolean,
      default: true
    },
    
    // 是否显示底部
    showFooter: {
      type: Boolean,
      default: true
    },
    
    // 是否显示确认按钮
    showConfirmButton: {
      type: Boolean,
      default: true
    },
    
    // 是否显示取消按钮
    showCancelButton: {
      type: Boolean,
      default: true
    },
    
    // 确认按钮文本
    confirmText: {
      type: String,
      default: '确认'
    },
    
    // 取消按钮文本
    cancelText: {
      type: String,
      default: '取消'
    },
    
    // 确认按钮是否禁用
    confirmDisabled: {
      type: Boolean,
      default: false
    },
    
    // 是否加载中
    loading: {
      type: Boolean,
      default: false
    },
    
    // 关闭按钮标题
    closeButtonTitle: {
      type: String,
      default: '关闭'
    },
    
    // 是否锁定滚动
    lockScroll: {
      type: Boolean,
      default: true
    },
    
    // 是否居中显示
    centered: {
      type: Boolean,
      default: true
    },
    
    // 自定义类名
    customClass: {
      type: String,
      default: ''
    },
    
    // 层级
    zIndex: {
      type: Number,
      default: 1000
    },
    
    // 是否可拖拽
    draggable: {
      type: Boolean,
      default: false
    },
    
    // 是否可调整大小
    resizable: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['update:visible', 'confirm', 'cancel', 'close', 'open', 'opened', 'closed'],
  
  setup(props, { emit }) {
    // 响应式引用
    const overlayRef = ref(null)
    const containerRef = ref(null)
    const isDragging = ref(false)
    const isResizing = ref(false)
    const dragOffset = ref({ x: 0, y: 0 })
    const originalBodyOverflow = ref('')
    
    // 计算属性
    const overlayClasses = computed(() => {
      return {
        'modal-centered': props.centered,
        'modal-dragging': isDragging.value,
        [props.customClass]: props.customClass
      }
    })
    
    const containerClasses = computed(() => {
      return {
        [`modal-${props.size}`]: true,
        [`modal-${props.type}`]: true,
        'modal-draggable': props.draggable,
        'modal-resizable': props.resizable,
        'modal-loading': props.loading
      }
    })
    
    const bodyClasses = computed(() => {
      return {
        'modal-body-no-header': !props.showHeader,
        'modal-body-no-footer': !props.showFooter
      }
    })
    
    const confirmButtonClass = computed(() => {
      const typeMap = {
        success: 'modal-btn-success',
        warning: 'modal-btn-warning',
        error: 'modal-btn-error',
        confirm: 'modal-btn-primary'
      }
      return typeMap[props.type] || 'modal-btn-primary'
    })
    
    // 方法
    const handleOverlayClick = () => {
      if (props.closeOnOverlay && props.closable && !isDragging.value) {
        handleClose()
      }
    }
    
    const handleEscKey = () => {
      if (props.closeOnEsc && props.closable) {
        handleClose()
      }
    }
    
    const handleClose = () => {
      emit('update:visible', false)
      emit('close')
    }
    
    const handleConfirm = () => {
      emit('confirm')
    }
    
    const handleCancel = () => {
      emit('cancel')
      handleClose()
    }
    
    const lockBodyScroll = () => {
      if (props.lockScroll) {
        originalBodyOverflow.value = document.body.style.overflow
        document.body.style.overflow = 'hidden'
      }
    }
    
    const unlockBodyScroll = () => {
      if (props.lockScroll) {
        document.body.style.overflow = originalBodyOverflow.value
      }
    }
    
    const focusModal = () => {
      nextTick(() => {
        if (overlayRef.value) {
          overlayRef.value.focus()
        }
      })
    }
    
    // 拖拽功能
    const setupDragging = () => {
      if (!props.draggable) return
      
      const handleMouseDown = (event) => {
        if (event.target.closest('.modal-header')) {
          isDragging.value = true
          const rect = containerRef.value.getBoundingClientRect()
          dragOffset.value = {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
          }
          
          document.addEventListener('mousemove', handleMouseMove)
          document.addEventListener('mouseup', handleMouseUp)
          event.preventDefault()
        }
      }
      
      const handleMouseMove = (event) => {
        if (!isDragging.value) return
        
        const x = event.clientX - dragOffset.value.x
        const y = event.clientY - dragOffset.value.y
        
        containerRef.value.style.transform = `translate(${x}px, ${y}px)`
      }
      
      const handleMouseUp = () => {
        isDragging.value = false
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
      
      if (containerRef.value) {
        containerRef.value.addEventListener('mousedown', handleMouseDown)
      }
    }
    
    // 调整大小功能
    const setupResizing = () => {
      if (!props.resizable) return
      
      // 这里可以添加调整大小的逻辑
      // 为了简化，暂时省略具体实现
    }
    
    // 监听visible变化
    watch(
      () => props.visible,
      (newVisible) => {
        if (newVisible) {
          emit('open')
          lockBodyScroll()
          focusModal()
          
          nextTick(() => {
            setupDragging()
            setupResizing()
            emit('opened')
          })
        } else {
          unlockBodyScroll()
          emit('closed')
        }
      },
      { immediate: true }
    )
    
    // 设置z-index
    watch(
      () => props.zIndex,
      (newZIndex) => {
        if (overlayRef.value) {
          overlayRef.value.style.zIndex = newZIndex
        }
      }
    )
    
    // 生命周期
    onMounted(() => {
      if (props.visible) {
        lockBodyScroll()
        focusModal()
      }
    })
    
    onUnmounted(() => {
      unlockBodyScroll()
    })
    
    return {
      // 响应式引用
      overlayRef,
      containerRef,
      isDragging,
      isResizing,
      
      // 计算属性
      overlayClasses,
      containerClasses,
      bodyClasses,
      confirmButtonClass,
      
      // 方法
      handleOverlayClick,
      handleEscKey,
      handleClose,
      handleConfirm,
      handleCancel
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: var(--space-4);
  overflow-y: auto;
  z-index: var(--z-modal);
}

.modal-centered {
  align-items: center;
}

.modal-dragging {
  user-select: none;
}

.modal-container {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  max-width: 100%;
  max-height: calc(100vh - var(--space-8));
  display: flex;
  flex-direction: column;
  position: relative;
  margin: auto 0;
}

/* 模态框大小 */
.modal-small {
  width: 400px;
}

.modal-medium {
  width: 500px;
}

.modal-large {
  width: 700px;
}

.modal-xlarge {
  width: 900px;
}

.modal-fullscreen {
  width: calc(100vw - var(--space-8));
  height: calc(100vh - var(--space-8));
  max-height: calc(100vh - var(--space-8));
}

/* 模态框类型 */
.modal-info {
  border-top: 4px solid var(--color-info, #3b82f6);
}

.modal-success {
  border-top: 4px solid var(--color-success);
}

.modal-warning {
  border-top: 4px solid var(--color-warning);
}

.modal-error {
  border-top: 4px solid var(--color-error);
}

.modal-confirm {
  border-top: 4px solid var(--color-primary);
}

/* 拖拽和调整大小 */
.modal-draggable .modal-header {
  cursor: move;
}

.modal-resizable {
  resize: both;
  overflow: auto;
}

.modal-loading {
  pointer-events: none;
  opacity: 0.8;
}

/* 模态框头部 */
.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: var(--space-6) var(--space-6) var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.modal-title-section {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.modal-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background: var(--color-bg-secondary);
  color: var(--color-primary);
  font-size: var(--font-size-lg);
  flex-shrink: 0;
}

.modal-info .modal-icon {
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-info, #3b82f6);
}

.modal-success .modal-icon {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.modal-warning .modal-icon {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.modal-error .modal-icon {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}

.modal-title {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  line-height: var(--line-height-tight);
}

.modal-subtitle {
  margin: var(--space-1) 0 0 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  flex-shrink: 0;
}

.modal-close:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text);
}

/* 模态框内容 */
.modal-body {
  flex: 1;
  padding: var(--space-6);
  overflow-y: auto;
  min-height: 0;
}

.modal-body-no-header {
  padding-top: var(--space-6);
}

.modal-body-no-footer {
  padding-bottom: var(--space-6);
}

.modal-message {
  font-size: var(--font-size-base);
  color: var(--color-text);
  line-height: var(--line-height-relaxed);
}

/* 模态框底部 */
.modal-footer {
  padding: var(--space-4) var(--space-6) var(--space-6) var(--space-6);
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

.modal-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  text-decoration: none;
  min-width: 80px;
}

.modal-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-btn-primary {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.modal-btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

.modal-btn-secondary {
  background: transparent;
  color: var(--color-text);
  border-color: var(--color-border);
}

.modal-btn-secondary:hover:not(:disabled) {
  background: var(--color-bg-secondary);
  border-color: var(--color-border-hover);
}

.modal-btn-success {
  background: var(--color-success);
  color: white;
  border-color: var(--color-success);
}

.modal-btn-success:hover:not(:disabled) {
  background: var(--color-success-dark);
  border-color: var(--color-success-dark);
}

.modal-btn-warning {
  background: var(--color-warning);
  color: white;
  border-color: var(--color-warning);
}

.modal-btn-warning:hover:not(:disabled) {
  background: var(--color-warning-dark);
  border-color: var(--color-warning-dark);
}

.modal-btn-error {
  background: var(--color-error);
  color: white;
  border-color: var(--color-error);
}

.modal-btn-error:hover:not(:disabled) {
  background: var(--color-error-dark);
  border-color: var(--color-error-dark);
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 过渡动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all var(--duration-normal) var(--ease-out);
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: all var(--duration-normal) var(--ease-out);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  opacity: 0;
  transform: scale(0.9) translateY(-20px);
}

/* 响应式适配 */
@media (max-width: 768px) {
  .modal-overlay {
    padding: var(--space-2);
  }
  
  .modal-container {
    width: 100% !important;
    max-height: calc(100vh - var(--space-4));
    margin: 0;
  }
  
  .modal-fullscreen {
    width: 100% !important;
    height: calc(100vh - var(--space-4));
  }
  
  .modal-header {
    padding: var(--space-4);
  }
  
  .modal-body {
    padding: var(--space-4);
  }
  
  .modal-footer {
    padding: var(--space-3) var(--space-4) var(--space-4) var(--space-4);
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .modal-btn {
    width: 100%;
  }
  
  .modal-title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-2);
  }
  
  .modal-icon {
    width: 32px;
    height: 32px;
    font-size: var(--font-size-base);
  }
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
  .modal-overlay {
    background: rgba(0, 0, 0, 0.7);
  }
  
  .modal-container {
    background: var(--color-bg-dark, #1a1a1a);
    border: 1px solid var(--color-border-dark, #333);
  }
  
  .modal-header {
    border-color: var(--color-border-dark, #333);
  }
  
  .modal-footer {
    border-color: var(--color-border-dark, #333);
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  .modal-enter-active,
  .modal-leave-active,
  .modal-container,
  .btn-spinner {
    transition: none;
    animation: none;
  }
}

/* 打印样式 */
@media print {
  .modal-overlay {
    position: static;
    background: none;
    backdrop-filter: none;
  }
  
  .modal-container {
    box-shadow: none;
    border: 1px solid #ccc;
  }
  
  .modal-close,
  .modal-actions {
    display: none;
  }
}
</style>