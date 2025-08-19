<template>
  <div class="permission-system-panel">
    <!-- 页面标题 -->
    <div class="panel-header">
      <h1 class="panel-title">
        <el-icon><Setting /></el-icon>
        权限系统管理面板
      </h1>
      <p class="panel-description">统一管理权限系统的各项功能和配置</p>
    </div>

    <!-- 系统状态概览 -->
    <el-row :gutter="20" class="status-overview">
      <el-col :span="6">
        <el-card class="status-card">
          <div class="status-item">
            <el-icon class="status-icon" :class="systemStatus.overall ? 'status-success' : 'status-error'">
              <CircleCheck v-if="systemStatus.overall" />
              <CircleClose v-else />
            </el-icon>
            <div class="status-content">
              <h3>系统状态</h3>
              <p>{{ systemStatus.overall ? '正常运行' : '异常' }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card">
          <div class="status-item">
            <el-icon class="status-icon" :class="systemStatus.cache ? 'status-success' : 'status-warning'">
              <DataBoard />
            </el-icon>
            <div class="status-content">
              <h3>缓存状态</h3>
              <p>{{ systemStatus.cache ? '正常' : '异常' }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card">
          <div class="status-item">
            <el-icon class="status-icon" :class="systemStatus.websocket ? 'status-success' : 'status-warning'">
              <Connection />
            </el-icon>
            <div class="status-content">
              <h3>实时同步</h3>
              <p>{{ systemStatus.websocket ? '已连接' : '断开' }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card">
          <div class="status-item">
            <el-icon class="status-icon" :class="systemStatus.security ? 'status-success' : 'status-error'">
              <Lock />
            </el-icon>
            <div class="status-content">
              <h3>安全状态</h3>
              <p>{{ systemStatus.security ? '安全' : '风险' }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 功能模块 -->
    <el-row :gutter="20" class="function-modules">
      <!-- 权限管理 -->
      <el-col :span="8">
        <el-card class="module-card">
          <template #header>
            <div class="card-header">
              <el-icon><User /></el-icon>
              <span>权限管理</span>
            </div>
          </template>
          <div class="module-content">
            <p class="module-description">管理用户权限、角色分配和权限测试</p>
            <div class="module-actions">
              <el-button type="primary" @click="navigateTo('/admin/user-management')">
                用户管理
              </el-button>
              <el-button @click="navigateTo('/admin/role-management')">
                角色管理
              </el-button>
              <el-button @click="navigateTo('/admin/permission-test')">
                权限测试
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 审计日志 -->
      <el-col :span="8">
        <el-card class="module-card">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>审计日志</span>
            </div>
          </template>
          <div class="module-content">
            <p class="module-description">查看和分析权限操作的审计记录</p>
            <div class="module-stats">
              <div class="stat-item">
                <span class="stat-label">今日操作:</span>
                <span class="stat-value">{{ auditStats.today }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">异常操作:</span>
                <span class="stat-value text-warning">{{ auditStats.suspicious }}</span>
              </div>
            </div>
            <div class="module-actions">
              <el-button type="primary" @click="navigateTo('/admin/audit-logs')">
                查看日志
              </el-button>
              <el-button @click="exportAuditLogs">
                导出报告
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 安全设置 -->
      <el-col :span="8">
        <el-card class="module-card">
          <template #header>
            <div class="card-header">
              <el-icon><Lock /></el-icon>
              <span>安全设置</span>
            </div>
          </template>
          <div class="module-content">
            <p class="module-description">配置安全策略和二次验证</p>
            <div class="security-options">
              <el-switch
                v-model="securityConfig.enableTwoFactor"
                @change="updateSecurityConfig"
                active-text="二次验证"
                inactive-text="已禁用"
              />
              <el-switch
                v-model="securityConfig.enableAutoRecovery"
                @change="updateSecurityConfig"
                active-text="自动恢复"
                inactive-text="已禁用"
              />
            </div>
            <div class="module-actions">
              <el-button type="primary" @click="showSecuritySettings">
                安全配置
              </el-button>
              <el-button @click="testSecondaryVerification">
                测试验证
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统监控 -->
    <el-card class="monitoring-card">
      <template #header>
        <div class="card-header">
          <el-icon><Monitor /></el-icon>
          <span>系统监控</span>
          <el-button type="text" @click="refreshMonitoring" :loading="monitoringLoading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeMonitoringTab">
        <!-- 异常监控 -->
        <el-tab-pane label="异常监控" name="exceptions">
          <div class="exception-monitoring">
            <div class="exception-stats">
              <el-row :gutter="16">
                <el-col :span="6" v-for="(stat, type) in exceptionStats.byType" :key="type">
                  <div class="exception-stat-item">
                    <div class="stat-number">{{ stat }}</div>
                    <div class="stat-label">{{ getExceptionTypeLabel(type) }}</div>
                  </div>
                </el-col>
              </el-row>
            </div>
            
            <div class="recent-exceptions">
              <h4>最近异常</h4>
              <el-table :data="recentExceptions" size="small">
                <el-table-column prop="timestamp" label="时间" width="160">
                  <template #default="{ row }">
                    {{ formatTime(row.timestamp) }}
                  </template>
                </el-table-column>
                <el-table-column prop="type" label="类型" width="120">
                  <template #default="{ row }">
                    <el-tag :type="getExceptionTagType(row.type)" size="small">
                      {{ getExceptionTypeLabel(row.type) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="severity" label="严重程度" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getSeverityTagType(row.severity)" size="small">
                      {{ row.severity }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="message" label="消息" show-overflow-tooltip />
                <el-table-column label="操作" width="120">
                  <template #default="{ row }">
                    <el-button type="text" size="small" @click="triggerRecovery(row.type)">
                      恢复
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-tab-pane>

        <!-- 性能监控 -->
        <el-tab-pane label="性能监控" name="performance">
          <div class="performance-monitoring">
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="performance-chart">
                  <h4>权限检查响应时间</h4>
                  <div class="chart-placeholder">
                    <el-icon><TrendCharts /></el-icon>
                    <p>图表数据加载中...</p>
                  </div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="performance-metrics">
                  <h4>性能指标</h4>
                  <div class="metric-item">
                    <span class="metric-label">平均响应时间:</span>
                    <span class="metric-value">{{ performanceMetrics.avgResponseTime }}ms</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">缓存命中率:</span>
                    <span class="metric-value">{{ performanceMetrics.cacheHitRate }}%</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">并发用户数:</span>
                    <span class="metric-value">{{ performanceMetrics.concurrentUsers }}</span>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <!-- 系统配置 -->
        <el-tab-pane label="系统配置" name="config">
          <div class="system-config">
            <el-form :model="systemConfig" label-width="150px">
              <el-form-item label="缓存过期时间">
                <el-input-number
                  v-model="systemConfig.cacheExpiration"
                  :min="60"
                  :max="3600"
                  :step="60"
                  controls-position="right"
                />
                <span class="form-help">秒</span>
              </el-form-item>
              
              <el-form-item label="最大重试次数">
                <el-input-number
                  v-model="systemConfig.maxRetries"
                  :min="1"
                  :max="10"
                  controls-position="right"
                />
              </el-form-item>
              
              <el-form-item label="监控间隔">
                <el-input-number
                  v-model="systemConfig.monitoringInterval"
                  :min="5000"
                  :max="60000"
                  :step="5000"
                  controls-position="right"
                />
                <span class="form-help">毫秒</span>
              </el-form-item>
              
              <el-form-item label="通知级别">
                <el-select v-model="systemConfig.notificationLevel">
                  <el-option label="无通知" value="none" />
                  <el-option label="仅错误" value="errors" />
                  <el-option label="全部" value="all" />
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveSystemConfig" :loading="configSaving">
                  保存配置
                </el-button>
                <el-button @click="resetSystemConfig">
                  重置
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 二次验证对话框 -->
    <SecondaryVerification
      v-model="showVerificationDialog"
      :operation="currentOperation"
      @verified="handleVerificationSuccess"
      @cancelled="handleVerificationCancel"
    />

    <!-- 安全设置对话框 -->
    <el-dialog
      v-model="showSecurityDialog"
      title="安全设置"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="detailedSecurityConfig" label-width="120px">
        <el-form-item label="密码策略">
          <el-checkbox-group v-model="detailedSecurityConfig.passwordPolicy">
            <el-checkbox label="requireUppercase">要求大写字母</el-checkbox>
            <el-checkbox label="requireNumbers">要求数字</el-checkbox>
            <el-checkbox label="requireSpecialChars">要求特殊字符</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="会话超时">
          <el-input-number
            v-model="detailedSecurityConfig.sessionTimeout"
            :min="300"
            :max="86400"
            :step="300"
            controls-position="right"
          />
          <span class="form-help">秒</span>
        </el-form-item>
        
        <el-form-item label="登录失败限制">
          <el-input-number
            v-model="detailedSecurityConfig.maxLoginAttempts"
            :min="3"
            :max="10"
            controls-position="right"
          />
        </el-form-item>
        
        <el-form-item label="IP白名单">
          <el-input
            v-model="detailedSecurityConfig.ipWhitelist"
            type="textarea"
            :rows="3"
            placeholder="每行一个IP地址或CIDR块"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showSecurityDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSecurityConfig" :loading="securityConfigSaving">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
// @ts-ignore
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import {
  Setting, CircleCheck, CircleClose, DataBoard, Connection, Lock,
  User, Document, Monitor, Refresh, TrendCharts
} from '@element-plus/icons-vue'
// Shield 图标暂时用 Lock 替代
import SecondaryVerification from '@/components/SecondaryVerification.vue'
import { permissionRecoveryService } from '@/services/permissionRecoveryService'

const router = useRouter()

// 系统状态
const systemStatus = reactive({
  overall: true,
  cache: true,
  websocket: true,
  security: true
})

// 审计统计
const auditStats = reactive({
  today: 156,
  suspicious: 3
})

// 安全配置
const securityConfig = reactive({
  enableTwoFactor: true,
  enableAutoRecovery: true
})

// 监控相关
const activeMonitoringTab = ref('exceptions')
const monitoringLoading = ref(false)

// 异常统计
const exceptionStats = ref({
  total: 0,
  byType: {} as Record<string, number>,
  bySeverity: {} as Record<string, number>
})

// 最近异常
const recentExceptions = ref<any[]>([])

// 性能指标
const performanceMetrics = reactive({
  avgResponseTime: 45,
  cacheHitRate: 94.5,
  concurrentUsers: 128
})

// 系统配置
const systemConfig = reactive({
  cacheExpiration: 1800,
  maxRetries: 3,
  monitoringInterval: 30000,
  notificationLevel: 'errors'
})

const configSaving = ref(false)

// 二次验证
const showVerificationDialog = ref(false)
const currentOperation = ref('')

// 安全设置对话框
const showSecurityDialog = ref(false)
const securityConfigSaving = ref(false)
const detailedSecurityConfig = reactive({
  passwordPolicy: ['requireUppercase', 'requireNumbers'],
  sessionTimeout: 3600,
  maxLoginAttempts: 5,
  ipWhitelist: ''
})

/**
 * 页面初始化
 */
onMounted(() => {
  loadSystemStatus()
  loadMonitoringData()
})

/**
 * 加载系统状态
 */
const loadSystemStatus = async () => {
  try {
    // 模拟加载系统状态
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 这里应该调用实际的API获取系统状态
    systemStatus.overall = true
    systemStatus.cache = true
    systemStatus.websocket = Math.random() > 0.3 // 模拟偶尔断开
    systemStatus.security = true
  } catch (error) {
    console.error('加载系统状态失败:', error)
    ElMessage.error('加载系统状态失败')
  }
}

/**
 * 加载监控数据
 */
const loadMonitoringData = async () => {
  try {
    // 获取异常统计
    const stats = permissionRecoveryService.getExceptionStats()
    exceptionStats.value = stats
    recentExceptions.value = stats.recent
  } catch (error) {
    console.error('加载监控数据失败:', error)
  }
}

/**
 * 导航到指定页面
 */
const navigateTo = (path: string) => {
  router.push(path)
}

/**
 * 更新安全配置
 */
const updateSecurityConfig = () => {
  // 更新权限恢复服务配置
  permissionRecoveryService.updateConfig({
    enableAutoRecovery: securityConfig.enableAutoRecovery
  })
  
  ElMessage.success('安全配置已更新')
}

/**
 * 显示安全设置对话框
 */
const showSecuritySettings = () => {
  showSecurityDialog.value = true
}

/**
 * 测试二次验证
 */
const testSecondaryVerification = () => {
  currentOperation.value = '测试二次验证功能'
  showVerificationDialog.value = true
}

/**
 * 处理验证成功
 */
const handleVerificationSuccess = () => {
  ElMessage.success('二次验证测试成功')
  showVerificationDialog.value = false
}

/**
 * 处理验证取消
 */
const handleVerificationCancel = () => {
  ElMessage.info('二次验证已取消')
  showVerificationDialog.value = false
}

/**
 * 刷新监控数据
 */
const refreshMonitoring = async () => {
  monitoringLoading.value = true
  try {
    await loadMonitoringData()
    await loadSystemStatus()
    ElMessage.success('监控数据已刷新')
  } catch (error) {
    ElMessage.error('刷新监控数据失败')
  } finally {
    monitoringLoading.value = false
  }
}

/**
 * 触发恢复
 */
const triggerRecovery = async (exceptionType: string) => {
  try {
    const success = await permissionRecoveryService.manualRecovery(exceptionType)
    if (success) {
      ElMessage.success('恢复操作已触发')
      await loadMonitoringData()
    }
  } catch (error) {
    ElMessage.error('触发恢复失败')
  }
}

/**
 * 导出审计日志
 */
const exportAuditLogs = async () => {
  try {
    ElMessage.info('正在生成审计报告...')
    // 模拟导出过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('审计报告已生成并下载')
  } catch (error) {
    ElMessage.error('导出审计报告失败')
  }
}

/**
 * 保存系统配置
 */
const saveSystemConfig = async () => {
  configSaving.value = true
  try {
    // 模拟保存配置
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新权限恢复服务配置
    permissionRecoveryService.updateConfig({
      maxRecoveryAttempts: systemConfig.maxRetries,
      recoveryInterval: systemConfig.monitoringInterval,
      notificationLevel: systemConfig.notificationLevel as any
    })
    
    ElMessage.success('系统配置已保存')
  } catch (error) {
    ElMessage.error('保存系统配置失败')
  } finally {
    configSaving.value = false
  }
}

/**
 * 重置系统配置
 */
const resetSystemConfig = () => {
  systemConfig.cacheExpiration = 1800
  systemConfig.maxRetries = 3
  systemConfig.monitoringInterval = 30000
  systemConfig.notificationLevel = 'errors'
  ElMessage.info('系统配置已重置')
}

/**
 * 保存安全配置
 */
const saveSecurityConfig = async () => {
  securityConfigSaving.value = true
  try {
    // 模拟保存配置
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('安全配置已保存')
    showSecurityDialog.value = false
  } catch (error) {
    ElMessage.error('保存安全配置失败')
  } finally {
    securityConfigSaving.value = false
  }
}

/**
 * 格式化时间
 */
const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleString()
}

/**
 * 获取异常类型标签
 */
const getExceptionTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    cache_corruption: '缓存损坏',
    sync_failure: '同步失败',
    token_expired: 'Token过期',
    network_error: '网络错误',
    server_error: '服务器错误'
  }
  return labels[type] || type
}

/**
 * 获取异常类型标签颜色
 */
const getExceptionTagType = (type: string) => {
  const types: Record<string, string> = {
    cache_corruption: 'warning',
    sync_failure: 'danger',
    token_expired: 'info',
    network_error: 'warning',
    server_error: 'danger'
  }
  return types[type] || 'info'
}

/**
 * 获取严重程度标签颜色
 */
const getSeverityTagType = (severity: string) => {
  const types: Record<string, string> = {
    low: 'info',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return types[severity] || 'info'
}
</script>

<style scoped>
.permission-system-panel {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.panel-header {
  margin-bottom: 30px;
  text-align: center;
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 10px 0;
}

.panel-description {
  font-size: 16px;
  color: #606266;
  margin: 0;
}

.status-overview {
  margin-bottom: 30px;
}

.status-card {
  height: 100px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 15px;
  height: 100%;
}

.status-icon {
  font-size: 32px;
}

.status-success {
  color: #67c23a;
}

.status-warning {
  color: #e6a23c;
}

.status-error {
  color: #f56c6c;
}

.status-content h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.status-content p {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.function-modules {
  margin-bottom: 30px;
}

.module-card {
  height: 280px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.module-content {
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.module-description {
  color: #606266;
  margin-bottom: 20px;
}

.module-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.module-stats {
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.stat-label {
  color: #606266;
}

.stat-value {
  font-weight: 600;
}

.text-warning {
  color: #e6a23c;
}

.security-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.monitoring-card {
  margin-bottom: 20px;
}

.exception-monitoring {
  padding: 20px 0;
}

.exception-stats {
  margin-bottom: 30px;
}

.exception-stat-item {
  text-align: center;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.recent-exceptions h4 {
  margin-bottom: 15px;
  color: #303133;
}

.performance-monitoring {
  padding: 20px 0;
}

.performance-chart {
  text-align: center;
  padding: 40px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: #909399;
}

.chart-placeholder .el-icon {
  font-size: 48px;
}

.performance-metrics {
  padding: 20px;
}

.performance-metrics h4 {
  margin-bottom: 20px;
  color: #303133;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.metric-label {
  color: #606266;
}

.metric-value {
  font-weight: 600;
  color: #303133;
}

.system-config {
  padding: 20px 0;
}

.form-help {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

@media (max-width: 768px) {
  .permission-system-panel {
    padding: 10px;
  }
  
  .status-overview .el-col,
  .function-modules .el-col {
    margin-bottom: 20px;
  }
  
  .module-card {
    height: auto;
  }
  
  .module-content {
    height: auto;
  }
}
</style>