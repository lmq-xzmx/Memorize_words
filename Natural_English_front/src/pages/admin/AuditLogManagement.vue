<template>
  <div class="audit-log-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>权限审计日志</h1>
      <p class="page-description">查看和分析系统权限操作记录</p>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-section">
      <div class="filter-row">
        <div class="filter-item">
          <label>操作类型:</label>
          <select v-model="filters.actionType" @change="loadAuditLogs">
            <option value="">全部</option>
            <option value="permission_grant">权限授予</option>
            <option value="permission_revoke">权限撤销</option>
            <option value="role_assign">角色分配</option>
            <option value="role_remove">角色移除</option>
            <option value="login_success">登录成功</option>
            <option value="login_failure">登录失败</option>
            <option value="security_violation">安全违规</option>
          </select>
        </div>
        
        <div class="filter-item">
          <label>风险等级:</label>
          <select v-model="filters.riskLevel" @change="loadAuditLogs">
            <option value="">全部</option>
            <option value="low">低风险</option>
            <option value="medium">中风险</option>
            <option value="high">高风险</option>
            <option value="critical">严重风险</option>
          </select>
        </div>
        
        <div class="filter-item">
          <label>开始日期:</label>
          <input 
            type="date" 
            v-model="filters.startDate" 
            @change="loadAuditLogs"
          >
        </div>
        
        <div class="filter-item">
          <label>结束日期:</label>
          <input 
            type="date" 
            v-model="filters.endDate" 
            @change="loadAuditLogs"
          >
        </div>
        
        <div class="filter-item">
          <button @click="resetFilters" class="btn btn-secondary">
            重置筛选
          </button>
          <button @click="exportLogs" class="btn btn-primary">
            导出日志
          </button>
        </div>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-number">{{ totalLogs }}</div>
        <div class="stat-label">总日志数</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ suspiciousCount }}</div>
        <div class="stat-label">可疑操作</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ highRiskCount }}</div>
        <div class="stat-label">高风险操作</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ todayCount }}</div>
        <div class="stat-label">今日操作</div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载审计日志中...</p>
    </div>

    <!-- 审计日志表格 -->
    <div v-else class="logs-table-container">
      <table class="logs-table">
        <thead>
          <tr>
            <th>时间</th>
            <th>操作类型</th>
            <th>操作用户</th>
            <th>目标用户</th>
            <th>资源</th>
            <th>结果</th>
            <th>风险等级</th>
            <th>IP地址</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in auditLogs" :key="log.id" :class="getRowClass(log)">
            <td>{{ formatDateTime(log.timestamp) }}</td>
            <td>
              <span :class="`action-type ${log.action_type}`">
                {{ getActionTypeLabel(log.action_type) }}
              </span>
            </td>
            <td>{{ log.user?.username || '系统' }}</td>
            <td>{{ log.target_user?.username || '-' }}</td>
            <td>{{ log.resource || '-' }}</td>
            <td>
              <span :class="`result ${log.result}`">
                {{ getResultLabel(log.result) }}
              </span>
            </td>
            <td>
              <span :class="`risk-level ${log.risk_level}`">
                {{ getRiskLevelLabel(log.risk_level) }}
              </span>
            </td>
            <td>{{ log.ip_address || '-' }}</td>
            <td>
              <button 
                @click="viewLogDetails(log)" 
                class="btn btn-sm btn-info"
              >
                详情
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- 空状态 -->
      <div v-if="auditLogs.length === 0" class="empty-state">
        <p>暂无审计日志数据</p>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-container">
      <div class="pagination-info">
        显示第 {{ (currentPage - 1) * pageSize + 1 }} - 
        {{ Math.min(currentPage * pageSize, totalLogs) }} 条，
        共 {{ totalLogs }} 条记录
      </div>
      <div class="pagination">
        <button 
          @click="changePage(currentPage - 1)" 
          :disabled="currentPage <= 1"
          class="btn btn-sm"
        >
          上一页
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button 
          @click="changePage(currentPage + 1)" 
          :disabled="currentPage >= totalPages"
          class="btn btn-sm"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 日志详情模态框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>审计日志详情</h3>
          <button @click="closeDetailModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedLog" class="log-details">
            <div class="detail-row">
              <label>操作时间:</label>
              <span>{{ formatDateTime(selectedLog.timestamp) }}</span>
            </div>
            <div class="detail-row">
              <label>操作类型:</label>
              <span>{{ getActionTypeLabel(selectedLog.action_type) }}</span>
            </div>
            <div class="detail-row">
              <label>操作用户:</label>
              <span>{{ selectedLog.user?.username || '系统' }}</span>
            </div>
            <div class="detail-row">
              <label>目标用户:</label>
              <span>{{ selectedLog.target_user?.username || '-' }}</span>
            </div>
            <div class="detail-row">
              <label>资源:</label>
              <span>{{ selectedLog.resource || '-' }}</span>
            </div>
            <div class="detail-row">
              <label>操作:</label>
              <span>{{ selectedLog.action || '-' }}</span>
            </div>
            <div class="detail-row">
              <label>权限:</label>
              <span>{{ selectedLog.permission || '-' }}</span>
            </div>
            <div class="detail-row">
              <label>角色:</label>
              <span>{{ selectedLog.role || '-' }}</span>
            </div>
            <div class="detail-row">
              <label>结果:</label>
              <span :class="`result ${selectedLog.result}`">
                {{ getResultLabel(selectedLog.result) }}
              </span>
            </div>
            <div class="detail-row">
              <label>风险等级:</label>
              <span :class="`risk-level ${selectedLog.risk_level}`">
                {{ getRiskLevelLabel(selectedLog.risk_level) }}
              </span>
            </div>
            <div class="detail-row">
              <label>IP地址:</label>
              <span>{{ selectedLog.ip_address || '-' }}</span>
            </div>
            <div class="detail-row">
              <label>用户代理:</label>
              <span class="user-agent">{{ selectedLog.user_agent || '-' }}</span>
            </div>
            <div class="detail-row">
              <label>描述:</label>
              <span>{{ selectedLog.description || '-' }}</span>
            </div>
            <div v-if="selectedLog.details" class="detail-row">
              <label>详细信息:</label>
              <pre class="details-json">{{ JSON.stringify(selectedLog.details, null, 2) }}</pre>
            </div>
            <div v-if="selectedLog.is_suspicious" class="detail-row">
              <label>可疑标记:</label>
              <span class="suspicious-flag">是</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
// @ts-ignore
import { onMounted } from 'vue'
import roleService from '@/services/roleService'
import type { PermissionAuditLog } from '@/services/roleService'

// 定义审计日志显示接口（基于实际的PermissionAuditLog）
interface AuditLogData {
  id: number
  action_type: string
  result: string
  risk_level: string
  user: string
  target_user?: string
  resource?: string
  permission?: string
  role?: string
  description: string
  ip_address: string
  created_at: string
  // 扩展字段用于UI显示
  timestamp: string
  is_suspicious: boolean
}

// 响应式数据
const loading = ref(false)
const auditLogs = ref<AuditLogData[]>([])
const totalLogs = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const showDetailModal = ref(false)
const selectedLog = ref<AuditLogData | null>(null)

// 筛选条件
const filters = reactive({
  actionType: '',
  riskLevel: '',
  startDate: '',
  endDate: ''
})

// 计算属性
const totalPages = computed(() => Math.ceil(totalLogs.value / pageSize.value))

const suspiciousCount = computed(() => 
  auditLogs.value.filter(log => log.is_suspicious).length
)

const highRiskCount = computed(() => 
  auditLogs.value.filter(log => log.risk_level === 'high' || log.risk_level === 'critical').length
)

const todayCount = computed(() => {
  const today = new Date().toDateString()
  return auditLogs.value.filter(log => 
    new Date(log.timestamp).toDateString() === today
  ).length
})

// 方法
const loadAuditLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      pageSize: pageSize.value,
      ...filters
    }
    
    const result = await roleService.getAuditLogs(params)
    
    // 转换数据格式以匹配AuditLogData接口
    auditLogs.value = result.logs.map((log: PermissionAuditLog) => ({
      id: log.id,
      action_type: log.action_type,
      result: log.result,
      risk_level: log.risk_level,
      user: log.user,
      target_user: log.target_user,
      resource: log.resource,
      permission: log.permission,
      role: log.role,
      description: log.description,
      ip_address: log.ip_address,
      created_at: log.created_at,
      timestamp: log.created_at,
      is_suspicious: false // 默认值，因为原接口没有此字段
    }))
    
    totalLogs.value = result.total
  } catch (error) {
    console.error('加载审计日志失败:', error)
  } finally {
    loading.value = false
  }
}

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadAuditLogs()
  }
}

const resetFilters = () => {
  Object.assign(filters, {
    actionType: '',
    riskLevel: '',
    startDate: '',
    endDate: ''
  })
  currentPage.value = 1
  loadAuditLogs()
}

const exportLogs = async () => {
  try {
    // 这里可以调用导出API
    console.log('导出审计日志')
  } catch (error) {
    console.error('导出失败:', error)
  }
}

const viewLogDetails = (log: AuditLogData) => {
  selectedLog.value = log
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedLog.value = null
}

const formatDateTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

const getActionTypeLabel = (actionType: string) => {
  const labels: Record<string, string> = {
    'permission_grant': '权限授予',
    'permission_revoke': '权限撤销',
    'role_assign': '角色分配',
    'role_remove': '角色移除',
    'role_create': '角色创建',
    'role_update': '角色更新',
    'role_delete': '角色删除',
    'login_success': '登录成功',
    'login_failure': '登录失败',
    'logout': '登出',
    'security_violation': '安全违规',
    'permission_check': '权限检查'
  }
  return labels[actionType] || actionType
}

const getResultLabel = (result: string) => {
  const labels: Record<string, string> = {
    'success': '成功',
    'failure': '失败',
    'denied': '拒绝',
    'error': '错误'
  }
  return labels[result] || result
}

const getRiskLevelLabel = (riskLevel: string) => {
  const labels: Record<string, string> = {
    'low': '低风险',
    'medium': '中风险',
    'high': '高风险',
    'critical': '严重风险'
  }
  return labels[riskLevel] || riskLevel
}

const getRowClass = (log: AuditLogData) => {
  const classes = []
  if (log.is_suspicious) classes.push('suspicious')
  if (log.risk_level === 'high' || log.risk_level === 'critical') {
    classes.push('high-risk')
  }
  return classes.join(' ')
}

// 生命周期
onMounted(() => {
  loadAuditLogs()
})
</script>

<style scoped>
.audit-log-management {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  color: #2c3e50;
  margin-bottom: 8px;
}

.page-description {
  color: #7f8c8d;
  margin: 0;
}

.filter-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  gap: 20px;
  align-items: end;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-item label {
  font-weight: 500;
  color: #495057;
}

.filter-item select,
.filter-item input {
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-number {
  font-size: 2em;
  font-weight: bold;
  color: #3498db;
  margin-bottom: 5px;
}

.stat-label {
  color: #7f8c8d;
  font-size: 14px;
}

.loading-container {
  text-align: center;
  padding: 40px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.logs-table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
}

.logs-table th {
  background: #f8f9fa;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
}

.logs-table td {
  padding: 12px;
  border-bottom: 1px solid #dee2e6;
}

.logs-table tr:hover {
  background: #f8f9fa;
}

.logs-table tr.suspicious {
  background: #fff3cd;
}

.logs-table tr.high-risk {
  background: #f8d7da;
}

.action-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.action-type.permission_grant {
  background: #d4edda;
  color: #155724;
}

.action-type.permission_revoke {
  background: #f8d7da;
  color: #721c24;
}

.action-type.login_success {
  background: #d1ecf1;
  color: #0c5460;
}

.action-type.login_failure {
  background: #f5c6cb;
  color: #721c24;
}

.action-type.security_violation {
  background: #f8d7da;
  color: #721c24;
}

.result {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.result.success {
  background: #d4edda;
  color: #155724;
}

.result.failure,
.result.denied,
.result.error {
  background: #f8d7da;
  color: #721c24;
}

.risk-level {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.risk-level.low {
  background: #d4edda;
  color: #155724;
}

.risk-level.medium {
  background: #fff3cd;
  color: #856404;
}

.risk-level.high,
.risk-level.critical {
  background: #f8d7da;
  color: #721c24;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.pagination {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-info {
  padding: 0 15px;
  color: #6c757d;
}

.btn {
  padding: 8px 16px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background: white;
  color: #495057;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn:hover:not(:disabled) {
  background: #e9ecef;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border-color: #6c757d;
}

.btn-secondary:hover {
  background: #545b62;
}

.btn-info {
  background: #17a2b8;
  color: white;
  border-color: #17a2b8;
}

.btn-info:hover {
  background: #138496;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #dee2e6;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6c757d;
}

.close-btn:hover {
  color: #495057;
}

.modal-body {
  padding: 20px;
}

.log-details {
  display: grid;
  gap: 15px;
}

.detail-row {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 10px;
  align-items: start;
}

.detail-row label {
  font-weight: 600;
  color: #495057;
}

.user-agent {
  word-break: break-all;
  font-size: 12px;
  color: #6c757d;
}

.details-json {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
}

.suspicious-flag {
  color: #dc3545;
  font-weight: 600;
}

@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .logs-table-container {
    overflow-x: auto;
  }
  
  .pagination-container {
    flex-direction: column;
    gap: 10px;
  }
  
  .modal-content {
    margin: 20px;
    max-width: calc(100vw - 40px);
  }
  
  .detail-row {
    grid-template-columns: 1fr;
  }
}
</style>