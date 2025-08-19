<template>
  <div class="permission-loader">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner">
        <div class="spinner"></div>
      </div>
      <div class="loading-text">
        <p>{{ loadingText }}</p>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: progress + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- 权限检查通过 -->
    <div v-else-if="hasPermission" class="permission-granted">
      <transition name="fade-in" appear>
        <slot />
      </transition>
    </div>

    <!-- 权限不足 -->
    <div v-else class="permission-denied">
      <div class="no-permission-container">
        <div class="no-permission-icon">
          <svg viewBox="0 0 24 24" width="64" height="64">
            <path fill="#f56565" d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M15.5,17L20.5,12L15.5,7V10.5H9.5V13.5H15.5V17Z"/>
          </svg>
        </div>
        <h3>{{ deniedTitle }}</h3>
        <p>{{ deniedMessage }}</p>
        <div class="permission-actions" v-if="showActions">
          <button class="retry-btn" @click="retryPermissionCheck" :disabled="retrying">
            <span v-if="retrying">重试中...</span>
            <span v-else>重试</span>
          </button>
          <button class="contact-btn" @click="contactAdmin">
            联系管理员
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
// @ts-ignore
import { onMounted } from 'vue'
import { usePermission } from '@/composables/usePermission'
import { ElMessage } from 'element-plus'

interface Props {
  permission?: string | string[]
  role?: string | string[]
  loadingText?: string
  deniedTitle?: string
  deniedMessage?: string
  showActions?: boolean
  autoRetry?: boolean
  retryInterval?: number
  maxRetries?: number
}

const props = withDefaults(defineProps<Props>(), {
  loadingText: '正在验证权限...',
  deniedTitle: '权限不足',
  deniedMessage: '您没有访问此内容的权限，请联系管理员获取相应权限。',
  showActions: true,
  autoRetry: false,
  retryInterval: 3000,
  maxRetries: 3
})

const emit = defineEmits<{
  permissionGranted: []
  permissionDenied: []
  retryAttempt: [attempt: number]
  contactAdmin: []
}>()

const { hasPermission: checkPermission, hasRole, refreshPermissions } = usePermission()

const loading = ref(true)
const hasPermission = ref(false)
const retrying = ref(false)
const progress = ref(0)
const retryCount = ref(0)

// 检查权限
const checkUserPermission = async (): Promise<boolean> => {
  try {
    let permissionGranted = true

    // 检查权限
    if (props.permission) {
      if (Array.isArray(props.permission)) {
        // 检查多个权限（需要全部满足）
        for (const perm of props.permission) {
          if (!await checkPermission(perm)) {
            permissionGranted = false
            break
          }
        }
      } else {
        permissionGranted = await checkPermission(props.permission)
      }
    }

    // 检查角色
    if (permissionGranted && props.role) {
      if (Array.isArray(props.role)) {
        // 检查多个角色（满足其中一个即可）
        permissionGranted = props.role.some((role: string) => hasRole(role))
      } else {
        permissionGranted = hasRole(props.role)
      }
    }

    return permissionGranted
  } catch (error) {
    console.error('权限检查失败:', error)
    return false
  }
}

// 执行权限检查
const performPermissionCheck = async () => {
  loading.value = true
  progress.value = 0

  // 模拟加载进度
  const progressInterval = setInterval(() => {
    if (progress.value < 90) {
      progress.value += Math.random() * 20
    }
  }, 100)

  try {
    const granted = await checkUserPermission()
    hasPermission.value = granted
    
    progress.value = 100
    
    setTimeout(() => {
      loading.value = false
      clearInterval(progressInterval)
      
      if (granted) {
        emit('permissionGranted')
      } else {
        emit('permissionDenied')
        
        // 自动重试机制
        if (props.autoRetry && retryCount.value < props.maxRetries) {
          setTimeout(() => {
            retryPermissionCheck()
          }, props.retryInterval)
        }
      }
    }, 300)
  } catch (error) {
    clearInterval(progressInterval)
    loading.value = false
    hasPermission.value = false
    emit('permissionDenied')
  }
}

// 重试权限检查
const retryPermissionCheck = async () => {
  if (retrying.value) return
  
  retrying.value = true
  retryCount.value++
  
  emit('retryAttempt', retryCount.value)
  
  try {
    // 刷新权限缓存
    await refreshPermissions()
    
    // 重新检查权限
    await performPermissionCheck()
    
    if (hasPermission.value) {
      ElMessage.success('权限验证成功')
      retryCount.value = 0
    } else {
      ElMessage.warning('权限仍然不足')
    }
  } catch (error) {
    ElMessage.error('权限重试失败')
  } finally {
    retrying.value = false
  }
}

// 联系管理员
const contactAdmin = () => {
  emit('contactAdmin')
  ElMessage.info('请联系系统管理员获取相应权限')
}

// 监听权限变化
watch([() => props.permission, () => props.role], () => {
  retryCount.value = 0
  performPermissionCheck()
}, { deep: true })

// 组件挂载时检查权限
onMounted(() => {
  performPermissionCheck()
})
</script>

<style scoped>
.permission-loader {
  width: 100%;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-container {
  text-align: center;
  padding: 2rem;
}

.loading-spinner {
  margin-bottom: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: #666;
}

.loading-text p {
  margin: 0 0 1rem 0;
  font-size: 14px;
}

.loading-progress {
  width: 200px;
  height: 4px;
  background: #f0f0f0;
  border-radius: 2px;
  overflow: hidden;
  margin: 0 auto;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.permission-granted {
  width: 100%;
}

.fade-in-enter-active {
  transition: all 0.3s ease;
}

.fade-in-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.permission-denied {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.no-permission-container {
  text-align: center;
  padding: 2rem;
  max-width: 400px;
}

.no-permission-icon {
  margin-bottom: 1rem;
}

.no-permission-container h3 {
  color: #e53e3e;
  margin: 0 0 1rem 0;
  font-size: 1.5rem;
}

.no-permission-container p {
  color: #666;
  margin: 0 0 2rem 0;
  line-height: 1.5;
}

.permission-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.retry-btn,
.contact-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.retry-btn {
  background: #3498db;
  color: white;
}

.retry-btn:hover:not(:disabled) {
  background: #2980b9;
}

.retry-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.contact-btn {
  background: #95a5a6;
  color: white;
}

.contact-btn:hover {
  background: #7f8c8d;
}
</style>