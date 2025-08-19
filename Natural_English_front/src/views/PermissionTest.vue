<template>
  <div class="permission-test">
    <!-- 权限加载器包装整个页面 -->
    <PermissionLoader
      :permission="['admin:permission:test']"
      :role="['admin', 'super_admin']"
      :show-retry="true"
      :auto-retry="true"
    >
      <template #default>
        <PermissionTransition
          :show="true"
          transition-name="permission-fade"
          :show-notifications="true"
        >
          <el-card class="test-card">
            <template #header>
              <div class="card-header">
                <span>权限同步测试</span>
                <el-button type="primary" @click="refreshAllCache">刷新所有缓存</el-button>
              </div>
            </template>
      
      <div class="test-section">
        <h3>用户权限测试</h3>
        <el-form :model="testForm" label-width="120px">
          <el-form-item label="用户ID:">
            <el-input v-model="testForm.userId" placeholder="输入用户ID" style="width: 200px" />
            <el-button @click="getUserPermissions" :loading="loading.user">获取权限</el-button>
            <el-button @click="refreshUserCache" :loading="loading.userRefresh">刷新用户缓存</el-button>
          </el-form-item>
        </el-form>
        
        <PermissionTransition
          :show="!!userPermissions"
          transition-name="permission-slide"
          :show-notifications="false"
        >
          <div v-if="userPermissions" class="result-box">
            <h4>用户权限结果:</h4>
            <pre>{{ JSON.stringify(userPermissions, null, 2) }}</pre>
          </div>
        </PermissionTransition>
      </div>
      
      <div class="test-section">
        <h3>角色权限测试</h3>
        <el-form :model="testForm" label-width="120px">
          <el-form-item label="角色ID:">
            <el-input v-model="testForm.roleId" placeholder="输入角色ID" style="width: 200px" />
            <el-button @click="getRolePermissions" :loading="loading.role">获取权限</el-button>
            <el-button @click="refreshRoleCache" :loading="loading.roleRefresh">刷新角色缓存</el-button>
          </el-form-item>
        </el-form>
        
        <PermissionTransition
          :show="!!rolePermissions"
          transition-name="permission-slide"
          :show-notifications="false"
        >
          <div v-if="rolePermissions" class="result-box">
            <h4>角色权限结果:</h4>
            <pre>{{ JSON.stringify(rolePermissions, null, 2) }}</pre>
          </div>
        </PermissionTransition>
      </div>
      
      <div class="test-section">
        <h3>权限检查测试</h3>
        <el-form :model="testForm" label-width="120px">
          <el-form-item label="路由权限:">
            <el-input v-model="testForm.route" placeholder="输入路由名称" style="width: 200px" />
            <el-button @click="checkRoutePermission" :loading="loading.route">检查权限</el-button>
          </el-form-item>
          <el-form-item label="组件权限:">
            <el-input v-model="testForm.component" placeholder="输入组件名称" style="width: 200px" />
            <el-button @click="checkComponentPermission" :loading="loading.component">检查权限</el-button>
          </el-form-item>
        </el-form>
        
        <PermissionTransition
          :show="permissionResults.length > 0"
          transition-name="permission-scale"
          :show-notifications="false"
        >
          <div v-if="permissionResults.length > 0" class="result-box">
            <h4>权限检查结果:</h4>
            <div v-for="(result, index) in permissionResults" :key="index" class="permission-result">
              <el-tag :type="result.hasPermission ? 'success' : 'danger'">
                {{ result.type }}: {{ result.name }} - {{ result.hasPermission ? '有权限' : '无权限' }}
              </el-tag>
            </div>
          </div>
        </PermissionTransition>
      </div>
      
      <div class="test-section">
        <h3>缓存统计信息</h3>
        <el-button @click="getCacheStats" :loading="loading.stats">获取统计</el-button>
        <el-button @click="showCacheStats">显示缓存统计</el-button>
        
        <PermissionTransition
          :show="!!cacheStats"
          transition-name="permission-fade"
          :show-notifications="false"
        >
          <div v-if="cacheStats" class="result-box">
            <h4>缓存统计:</h4>
            <pre>{{ JSON.stringify(cacheStats, null, 2) }}</pre>
          </div>
        </PermissionTransition>
      </div>
          </el-card>
        </PermissionTransition>
      </template>
      
      <!-- 权限不足时显示的内容 -->
      <template #denied>
        <PermissionDenied
          title="权限测试访问被拒绝"
          description="您需要管理员权限才能访问权限测试功能。请联系系统管理员获取相应权限。"
          required-permission="admin:permission:test"
          :current-role="currentUserRole"
          error-code="PERM_TEST_ACCESS_DENIED"
          :show-details="true"
          :show-retry="true"
          :show-contact="true"
          :show-go-back="true"
          :custom-suggestions="testPageSuggestions"
        />
      </template>
    </PermissionLoader>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { PermissionCache } from '@/services/permissionCacheService'
import PermissionLoader from '@/components/PermissionLoader.vue'
import PermissionTransition from '@/components/PermissionTransition.vue'
import PermissionDenied from '@/components/PermissionDenied.vue'
// import { useUserStore } from '@/stores/user' // 暂时注释，如果没有用户store

// 类型定义
interface UserPermissions {
  permissions: string[]
  roles: string[]
  menus: any[]
  lastUpdate: number
}

interface RolePermissions {
  permissions: string[]
  menus: string[]
  actions: string[]
  lastUpdate: number
}

interface PermissionResult {
  type: string
  name: string
  hasPermission: boolean
}

// 响应式数据
const testForm = reactive({
  userId: '1',
  roleId: '1',
  route: '/admin/users',
  component: 'UserManagement'
})

const loading = reactive({
  user: false,
  role: false,
  route: false,
  component: false,
  userRefresh: false,
  roleRefresh: false,
  stats: false
})

const userPermissions = ref<UserPermissions | null>(null)
const rolePermissions = ref<RolePermissions | null>(null)
const permissionResults = ref<PermissionResult[]>([])

// 当前用户角色（模拟数据）
const currentUserRole = ref('user')

// 权限测试页面的自定义建议
const testPageSuggestions = ref([
  {
    id: 'contact-admin',
    text: '联系系统管理员申请权限测试访问权限',
    buttonText: '联系管理员',
    buttonClass: 'primary'
  },
  {
    id: 'view-docs',
    text: '查看权限系统文档了解更多信息',
    buttonText: '查看文档',
    buttonClass: 'outline'
  },
  {
    id: 'return-dashboard',
    text: '返回仪表盘继续其他操作',
    action: () => {
      // 这里可以添加路由跳转逻辑
      console.log('返回仪表盘')
    },
    buttonText: '返回仪表盘',
    buttonClass: 'outline'
  }
])
const cacheStats = ref<any>(null)

// 获取用户权限
const getUserPermissions = async () => {
  if (!testForm.userId) {
    ElMessage.warning('请输入用户ID')
    return
  }
  
  loading.user = true
  try {
    const result = await PermissionCache.getUserPermissions(testForm.userId)
    userPermissions.value = result
    ElMessage.success('获取用户权限成功')
  } catch (error) {
    ElMessage.error('获取用户权限失败')
    console.error(error)
  } finally {
    loading.user = false
  }
}

// 获取角色权限
const getRolePermissions = async () => {
  if (!testForm.roleId) {
    ElMessage.warning('请输入角色ID')
    return
  }
  
  loading.role = true
  try {
    // 注意：这里需要使用 permissionCacheService 的 getRolePermissions 方法
    const { permissionCacheService } = await import('@/services/permissionCacheService')
    const result = await permissionCacheService.getRolePermissions(testForm.roleId)
    rolePermissions.value = result
    ElMessage.success('获取角色权限成功')
  } catch (error) {
    ElMessage.error('获取角色权限失败')
    console.error(error)
  } finally {
    loading.role = false
  }
}

// 检查路由权限
const checkRoutePermission = async () => {
  if (!testForm.route || !testForm.userId) {
    ElMessage.warning('请输入路由名称和用户ID')
    return
  }
  
  loading.route = true
  try {
    const hasPermission = await PermissionCache.checkRoute(testForm.route, testForm.userId)
    permissionResults.value.push({
      type: '路由',
      name: testForm.route,
      hasPermission
    })
    ElMessage.success('路由权限检查完成')
  } catch (error) {
    ElMessage.error('路由权限检查失败')
    console.error(error)
  } finally {
    loading.route = false
  }
}

// 检查组件权限
const checkComponentPermission = async () => {
  if (!testForm.component || !testForm.userId) {
    ElMessage.warning('请输入组件名称和用户ID')
    return
  }
  
  loading.component = true
  try {
    const hasPermission = await PermissionCache.checkComponent(testForm.component, testForm.userId)
    permissionResults.value.push({
      type: '组件',
      name: testForm.component,
      hasPermission
    })
    ElMessage.success('组件权限检查完成')
  } catch (error) {
    ElMessage.error('组件权限检查失败')
    console.error(error)
  } finally {
    loading.component = false
  }
}

// 刷新用户缓存
const refreshUserCache = async () => {
  if (!testForm.userId) {
    ElMessage.warning('请输入用户ID')
    return
  }
  
  loading.userRefresh = true
  try {
    await PermissionCache.refreshUser(testForm.userId)
    ElMessage.success('用户缓存刷新成功')
  } catch (error) {
    ElMessage.error('用户缓存刷新失败')
    console.error(error)
  } finally {
    loading.userRefresh = false
  }
}

// 刷新角色缓存
const refreshRoleCache = async () => {
  if (!testForm.roleId) {
    ElMessage.warning('请输入角色ID')
    return
  }
  
  loading.roleRefresh = true
  try {
    const { permissionCacheService } = await import('@/services/permissionCacheService')
    await permissionCacheService.refreshRoleCache(testForm.roleId)
    ElMessage.success('角色缓存刷新成功')
  } catch (error) {
    ElMessage.error('角色缓存刷新失败')
    console.error(error)
  } finally {
    loading.roleRefresh = false
  }
}

// 刷新所有缓存
const refreshAllCache = () => {
  PermissionCache.clear()
  userPermissions.value = null
  rolePermissions.value = null
  permissionResults.value = []
  cacheStats.value = null
  ElMessage.success('所有缓存已清除')
}

// 获取缓存统计
const getCacheStats = async () => {
  loading.stats = true
  try {
    const { permissionCacheService } = await import('@/services/permissionCacheService')
    const stats = permissionCacheService.getCacheStats()
    cacheStats.value = stats
    ElMessage.success('获取缓存统计成功')
  } catch (error) {
    ElMessage.error('获取缓存统计失败')
    console.error(error)
  } finally {
    loading.stats = false
  }
}

// 显示缓存统计（开发环境）
const showCacheStats = () => {
  const { permissionCacheService } = require('@/services/permissionCacheService')
  permissionCacheService.showCacheStats()
  ElMessage.info('缓存统计已输出到控制台')
}
</script>

<style scoped>
.permission-test {
  padding: 20px;
}

.test-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.test-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.test-section h3 {
  margin-top: 0;
  color: #303133;
}

.result-box {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.result-box h4 {
  margin-top: 0;
  color: #606266;
}

.result-box pre {
  background-color: #fff;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  overflow-x: auto;
  font-size: 12px;
  line-height: 1.4;
}

.permission-result {
  margin-bottom: 10px;
}

.el-form-item {
  margin-bottom: 15px;
}

.el-button {
  margin-left: 10px;
}
</style>