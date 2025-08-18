<template>
  <div class="user-list" v-permission="['admin']">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>用户列表</h1>
      <p>管理系统中的所有用户</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="search-section">
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索用户名、邮箱或手机号"
            @input="handleSearch"
          >
          <span class="search-icon">🔍</span>
        </div>
        
        <select v-model="roleFilter" @change="handleFilter" class="filter-select">
          <option value="">全部角色</option>
          <option value="admin">管理员</option>
          <option value="teacher">教师</option>
          <option value="student">学生</option>
        </select>
        
        <select v-model="statusFilter" @change="handleFilter" class="filter-select">
          <option value="">全部状态</option>
          <option value="active">活跃</option>
          <option value="inactive">非活跃</option>
          <option value="banned">已封禁</option>
        </select>
        
        <select v-model="timeFilter" @change="handleFilter" class="filter-select">
          <option value="all">全部时间</option>
          <option value="today">今天注册</option>
          <option value="week">本周注册</option>
          <option value="month">本月注册</option>
        </select>
      </div>
      
      <div class="action-buttons">
        <button @click="showAddModal = true" class="add-btn">
          ➕ 添加用户
        </button>
        <button @click="showBatchModal = true" class="batch-btn">
          📝 批量操作
        </button>
        <button @click="exportUsers" class="export-btn">
          📊 导出数据
        </button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-icon total">👥</div>
        <div class="stat-content">
          <h3>{{ filteredUsers.length }}</h3>
          <p>总用户数</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon active">🟢</div>
        <div class="stat-content">
          <h3>{{ activeUsers }}</h3>
          <p>活跃用户</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon new">🆕</div>
        <div class="stat-content">
          <h3>{{ newUsers }}</h3>
          <p>新用户(本月)</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon banned">🚫</div>
        <div class="stat-content">
          <h3>{{ bannedUsers }}</h3>
          <p>已封禁</p>
        </div>
      </div>
    </div>

    <!-- 用户表格 -->
    <div class="users-table-container">
      <div class="table-header">
        <h2>用户详情</h2>
        <div class="table-controls">
          <select v-model="pageSize" @change="handlePageSizeChange" class="page-size-select">
            <option value="10">10条/页</option>
            <option value="20">20条/页</option>
            <option value="50">50条/页</option>
            <option value="100">100条/页</option>
          </select>
          
          <div class="view-toggle">
            <button 
              @click="viewMode = 'table'" 
              :class="{ active: viewMode === 'table' }"
              class="view-btn"
            >
              📋 表格
            </button>
            <button 
              @click="viewMode = 'card'" 
              :class="{ active: viewMode === 'card' }"
              class="view-btn"
            >
              🗃️ 卡片
            </button>
          </div>
        </div>
      </div>
      
      <!-- 表格视图 -->
      <div v-if="viewMode === 'table'" class="table-view">
        <table class="users-table">
          <thead>
            <tr>
              <th>
                <input 
                  type="checkbox" 
                  @change="selectAllUsers" 
                  :checked="allSelected"
                >
              </th>
              <th @click="sortBy('username')" class="sortable">
                用户名 
                <span class="sort-icon">{{ getSortIcon('username') }}</span>
              </th>
              <th @click="sortBy('email')" class="sortable">
                邮箱 
                <span class="sort-icon">{{ getSortIcon('email') }}</span>
              </th>
              <th @click="sortBy('role')" class="sortable">
                角色 
                <span class="sort-icon">{{ getSortIcon('role') }}</span>
              </th>
              <th @click="sortBy('status')" class="sortable">
                状态 
                <span class="sort-icon">{{ getSortIcon('status') }}</span>
              </th>
              <th @click="sortBy('lastLogin')" class="sortable">
                最后登录 
                <span class="sort-icon">{{ getSortIcon('lastLogin') }}</span>
              </th>
              <th @click="sortBy('createdAt')" class="sortable">
                注册时间 
                <span class="sort-icon">{{ getSortIcon('createdAt') }}</span>
              </th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="user in paginatedUsers" 
              :key="user.id" 
              :class="{ selected: selectedUserIds.includes(user.id) }"
            >
              <td>
                <input 
                  type="checkbox" 
                  :value="user.id" 
                  v-model="selectedUserIds"
                >
              </td>
              <td>
                <div class="user-info">
                  <div class="user-avatar">
                    {{ user.username.charAt(0).toUpperCase() }}
                  </div>
                  <div class="user-details">
                    <div class="username">{{ user.username }}</div>
                    <div class="user-id">ID: {{ user.id }}</div>
                  </div>
                </div>
              </td>
              <td>{{ user.email }}</td>
              <td>
                <span :class="`role-badge ${user.role}`">
                  {{ getRoleText(user.role) }}
                </span>
              </td>
              <td>
                <span :class="`status-badge ${user.status}`">
                  {{ getStatusText(user.status) }}
                </span>
              </td>
              <td>{{ formatDateTime(user.lastLogin) }}</td>
              <td>{{ formatDate(user.createdAt) }}</td>
              <td>
                <div class="action-buttons">
                  <button @click="viewUser(user)" class="action-btn view" title="查看详情">
                    👁️
                  </button>
                  <button @click="editUser(user)" class="action-btn edit" title="编辑">
                    ✏️
                  </button>
                  <button 
                    @click="toggleUserStatus(user)" 
                    :class="`action-btn ${user.status === 'banned' ? 'unban' : 'ban'}`"
                    :title="user.status === 'banned' ? '解封' : '封禁'"
                  >
                    {{ user.status === 'banned' ? '🔓' : '🔒' }}
                  </button>
                  <button @click="deleteUser(user)" class="action-btn delete" title="删除">
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 卡片视图 -->
      <div v-else class="card-view">
        <div class="users-grid">
          <div 
            v-for="user in paginatedUsers" 
            :key="user.id" 
            class="user-card"
            :class="{ selected: selectedUserIds.includes(user.id) }"
          >
            <div class="card-header">
              <input 
                type="checkbox" 
                :value="user.id" 
                v-model="selectedUserIds"
                class="card-checkbox"
              >
              <div class="user-avatar large">
                {{ user.username.charAt(0).toUpperCase() }}
              </div>
              <div class="user-basic-info">
                <h4>{{ user.username }}</h4>
                <p>{{ user.email }}</p>
              </div>
            </div>
            
            <div class="card-content">
              <div class="info-row">
                <span class="label">角色:</span>
                <span :class="`role-badge ${user.role}`">
                  {{ getRoleText(user.role) }}
                </span>
              </div>
              
              <div class="info-row">
                <span class="label">状态:</span>
                <span :class="`status-badge ${user.status}`">
                  {{ getStatusText(user.status) }}
                </span>
              </div>
              
              <div class="info-row">
                <span class="label">最后登录:</span>
                <span>{{ formatDateTime(user.lastLogin) }}</span>
              </div>
              
              <div class="info-row">
                <span class="label">注册时间:</span>
                <span>{{ formatDate(user.createdAt) }}</span>
              </div>
              
              <div v-if="user.phone" class="info-row">
                <span class="label">手机号:</span>
                <span>{{ user.phone }}</span>
              </div>
            </div>
            
            <div class="card-actions">
              <button @click="viewUser(user)" class="action-btn view">
                👁️ 查看
              </button>
              <button @click="editUser(user)" class="action-btn edit">
                ✏️ 编辑
              </button>
              <button 
                @click="toggleUserStatus(user)" 
                :class="`action-btn ${user.status === 'banned' ? 'unban' : 'ban'}`"
              >
                {{ user.status === 'banned' ? '🔓 解封' : '🔒 封禁' }}
              </button>
              <button @click="deleteUser(user)" class="action-btn delete">
                🗑️ 删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <div class="pagination-info">
        显示第 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredUsers.length) }} 条，
        共 {{ filteredUsers.length }} 条记录
      </div>
      
      <div class="pagination-controls">
        <button 
          @click="currentPage = 1" 
          :disabled="currentPage === 1"
          class="page-btn"
        >
          首页
        </button>
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="page-btn"
        >
          上一页
        </button>
        
        <span class="page-numbers">
          <button 
            v-for="page in visiblePages" 
            :key="page" 
            @click="currentPage = page"
            :class="{ active: page === currentPage }"
            class="page-number"
          >
            {{ page }}
          </button>
        </span>
        
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="page-btn"
        >
          下一页
        </button>
        <button 
          @click="currentPage = totalPages" 
          :disabled="currentPage === totalPages"
          class="page-btn"
        >
          末页
        </button>
      </div>
    </div>

    <!-- 添加/编辑用户弹窗 -->
    <div v-if="showAddModal || showEditModal" class="modal-overlay" @click="closeUserModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ showAddModal ? '添加用户' : '编辑用户' }}</h2>
          <button @click="closeUserModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveUser" class="user-form">
            <div class="form-row">
              <div class="form-group">
                <label>用户名 *</label>
                <input 
                  v-model="userForm.username" 
                  type="text" 
                  required 
                  placeholder="请输入用户名"
                >
              </div>
              
              <div class="form-group">
                <label>邮箱 *</label>
                <input 
                  v-model="userForm.email" 
                  type="email" 
                  required 
                  placeholder="请输入邮箱"
                >
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>手机号</label>
                <input 
                  v-model="userForm.phone" 
                  type="tel" 
                  placeholder="请输入手机号"
                >
              </div>
              
              <div class="form-group">
                <label>角色 *</label>
                <select v-model="userForm.role" required>
                  <option value="">请选择角色</option>
                  <option value="admin">管理员</option>
                  <option value="teacher">教师</option>
                  <option value="student">学生</option>
                </select>
              </div>
            </div>
            
            <div v-if="showAddModal" class="form-row">
              <div class="form-group">
                <label>密码 *</label>
                <input 
                  v-model="userForm.password" 
                  type="password" 
                  required 
                  placeholder="请输入密码"
                >
              </div>
              
              <div class="form-group">
                <label>确认密码 *</label>
                <input 
                  v-model="userForm.confirmPassword" 
                  type="password" 
                  required 
                  placeholder="请确认密码"
                >
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group full-width">
                <label>状态</label>
                <div class="radio-group">
                  <label class="radio-item">
                    <input type="radio" value="active" v-model="userForm.status">
                    活跃
                  </label>
                  <label class="radio-item">
                    <input type="radio" value="inactive" v-model="userForm.status">
                    非活跃
                  </label>
                  <label class="radio-item">
                    <input type="radio" value="banned" v-model="userForm.status">
                    封禁
                  </label>
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeUserModal" class="cancel-btn">
                取消
              </button>
              <button type="submit" class="submit-btn">
                {{ showAddModal ? '添加' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 用户详情弹窗 -->
    <div v-if="showViewModal" class="modal-overlay" @click="closeViewModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>用户详情</h2>
          <button @click="closeViewModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedUser" class="user-detail">
            <div class="detail-header">
              <div class="user-avatar extra-large">
                {{ selectedUser.username.charAt(0).toUpperCase() }}
              </div>
              <div class="user-info">
                <h3>{{ selectedUser.username }}</h3>
                <p>{{ selectedUser.email }}</p>
                <div class="badges">
                  <span :class="`role-badge ${selectedUser.role}`">
                    {{ getRoleText(selectedUser.role) }}
                  </span>
                  <span :class="`status-badge ${selectedUser.status}`">
                    {{ getStatusText(selectedUser.status) }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="detail-content">
              <div class="detail-section">
                <h4>基本信息</h4>
                <div class="info-grid">
                  <div class="info-item">
                    <label>用户ID:</label>
                    <span>{{ selectedUser.id }}</span>
                  </div>
                  <div class="info-item">
                    <label>用户名:</label>
                    <span>{{ selectedUser.username }}</span>
                  </div>
                  <div class="info-item">
                    <label>邮箱:</label>
                    <span>{{ selectedUser.email }}</span>
                  </div>
                  <div class="info-item">
                    <label>手机号:</label>
                    <span>{{ selectedUser.phone || '未设置' }}</span>
                  </div>
                  <div class="info-item">
                    <label>角色:</label>
                    <span>{{ getRoleText(selectedUser.role) }}</span>
                  </div>
                  <div class="info-item">
                    <label>状态:</label>
                    <span>{{ getStatusText(selectedUser.status) }}</span>
                  </div>
                </div>
              </div>
              
              <div class="detail-section">
                <h4>时间信息</h4>
                <div class="info-grid">
                  <div class="info-item">
                    <label>注册时间:</label>
                    <span>{{ formatDateTime(selectedUser.createdAt) }}</span>
                  </div>
                  <div class="info-item">
                    <label>最后登录:</label>
                    <span>{{ formatDateTime(selectedUser.lastLogin) }}</span>
                  </div>
                  <div class="info-item">
                    <label>最后更新:</label>
                    <span>{{ formatDateTime(selectedUser.updatedAt) }}</span>
                  </div>
                </div>
              </div>
              
              <div v-if="selectedUser.role === 'student'" class="detail-section">
                <h4>学习统计</h4>
                <div class="stats-grid">
                  <div class="stat-item">
                    <div class="stat-value">{{ selectedUser.stats?.wordsLearned || 0 }}</div>
                    <div class="stat-label">已学单词</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">{{ selectedUser.stats?.studyTime || 0 }}h</div>
                    <div class="stat-label">学习时长</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">{{ selectedUser.stats?.averageScore || 0 }}%</div>
                    <div class="stat-label">平均分数</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">{{ selectedUser.stats?.streak || 0 }}</div>
                    <div class="stat-label">连续天数</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 批量操作弹窗 -->
    <div v-if="showBatchModal" class="modal-overlay" @click="closeBatchModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>批量操作</h2>
          <button @click="closeBatchModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="batch-info">
            <p>已选择 <strong>{{ selectedUserIds.length }}</strong> 个用户</p>
          </div>
          
          <div class="batch-actions">
            <div class="action-group">
              <h4>状态操作</h4>
              <div class="action-buttons">
                <button @click="batchUpdateStatus('active')" class="batch-action-btn active">
                  🟢 设为活跃
                </button>
                <button @click="batchUpdateStatus('inactive')" class="batch-action-btn inactive">
                  🟡 设为非活跃
                </button>
                <button @click="batchUpdateStatus('banned')" class="batch-action-btn banned">
                  🔴 批量封禁
                </button>
              </div>
            </div>
            
            <div class="action-group">
              <h4>角色操作</h4>
              <div class="action-buttons">
                <button @click="batchUpdateRole('student')" class="batch-action-btn role">
                  👨‍🎓 设为学生
                </button>
                <button @click="batchUpdateRole('teacher')" class="batch-action-btn role">
                  👨‍🏫 设为教师
                </button>
              </div>
            </div>
            
            <div class="action-group">
              <h4>危险操作</h4>
              <div class="action-buttons">
                <button @click="batchDeleteUsers" class="batch-action-btn danger">
                  🗑️ 批量删除
                </button>
              </div>
            </div>
          </div>
          
          <div class="batch-footer">
            <button @click="closeBatchModal" class="cancel-btn">
              取消
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface User {
  id: string
  username: string
  email: string
  phone?: string
  role: 'admin' | 'teacher' | 'student'
  status: 'active' | 'inactive' | 'banned'
  lastLogin: string
  createdAt: string
  updatedAt: string
  stats?: {
    wordsLearned: number
    studyTime: number
    averageScore: number
    streak: number
  }
}

interface UserForm {
  username: string
  email: string
  phone: string
  role: string
  status: string
  password: string
  confirmPassword: string
}

// 响应式数据
const users = ref<User[]>([
  {
    id: '1',
    username: 'admin',
    email: 'admin@example.com',
    phone: '13800138000',
    role: 'admin',
    status: 'active',
    lastLogin: '2024-01-15T14:30:00Z',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-15T14:30:00Z'
  },
  {
    id: '2',
    username: 'teacher1',
    email: 'teacher1@example.com',
    phone: '13800138001',
    role: 'teacher',
    status: 'active',
    lastLogin: '2024-01-15T13:45:00Z',
    createdAt: '2024-01-02T00:00:00Z',
    updatedAt: '2024-01-15T13:45:00Z'
  },
  {
    id: '3',
    username: 'student1',
    email: 'student1@example.com',
    phone: '13800138002',
    role: 'student',
    status: 'active',
    lastLogin: '2024-01-15T15:20:00Z',
    createdAt: '2024-01-03T00:00:00Z',
    updatedAt: '2024-01-15T15:20:00Z',
    stats: {
      wordsLearned: 1250,
      studyTime: 45,
      averageScore: 92,
      streak: 12
    }
  },
  {
    id: '4',
    username: 'student2',
    email: 'student2@example.com',
    role: 'student',
    status: 'banned',
    lastLogin: '2024-01-10T16:30:00Z',
    createdAt: '2024-01-04T00:00:00Z',
    updatedAt: '2024-01-12T10:00:00Z',
    stats: {
      wordsLearned: 650,
      studyTime: 22,
      averageScore: 68,
      streak: 3
    }
  }
])

const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')
const timeFilter = ref('all')
const sortField = ref('createdAt')
const sortOrder = ref<'asc' | 'desc'>('desc')
const currentPage = ref(1)
const pageSize = ref(20)
const viewMode = ref<'table' | 'card'>('table')

const selectedUserIds = ref<string[]>([])
const showAddModal = ref(false)
const showEditModal = ref(false)
const showViewModal = ref(false)
const showBatchModal = ref(false)
const selectedUser = ref<User | null>(null)

const userForm = ref<UserForm>({
  username: '',
  email: '',
  phone: '',
  role: '',
  status: 'active',
  password: '',
  confirmPassword: ''
})

// 计算属性
const filteredUsers = computed(() => {
  let result = users.value
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(user => 
      user.username.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query) ||
      (user.phone && user.phone.includes(query))
    )
  }
  
  // 角色过滤
  if (roleFilter.value) {
    result = result.filter(user => user.role === roleFilter.value)
  }
  
  // 状态过滤
  if (statusFilter.value) {
    result = result.filter(user => user.status === statusFilter.value)
  }
  
  // 时间过滤
  if (timeFilter.value !== 'all') {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const week = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
    const month = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
    
    result = result.filter(user => {
      const createdAt = new Date(user.createdAt)
      switch (timeFilter.value) {
        case 'today':
          return createdAt >= today
        case 'week':
          return createdAt >= week
        case 'month':
          return createdAt >= month
        default:
          return true
      }
    })
  }
  
  // 排序
  result.sort((a, b) => {
    let aVal: any = a[sortField.value as keyof User]
    let bVal: any = b[sortField.value as keyof User]
    
    if (sortField.value === 'lastLogin' || sortField.value === 'createdAt' || sortField.value === 'updatedAt') {
      aVal = new Date(aVal).getTime()
      bVal = new Date(bVal).getTime()
    }
    
    if (sortOrder.value === 'asc') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })
  
  return result
})

const totalPages = computed(() => {
  return Math.ceil(filteredUsers.value.length / pageSize.value)
})

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredUsers.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...', total)
    } else if (current >= total - 3) {
      pages.push(1, '...')
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1, '...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...', total)
    }
  }
  
  return pages
})

const activeUsers = computed(() => {
  return filteredUsers.value.filter(user => user.status === 'active').length
})

const newUsers = computed(() => {
  const month = new Date()
  month.setMonth(month.getMonth() - 1)
  return filteredUsers.value.filter(user => new Date(user.createdAt) >= month).length
})

const bannedUsers = computed(() => {
  return filteredUsers.value.filter(user => user.status === 'banned').length
})

const allSelected = computed(() => {
  return selectedUserIds.value.length === paginatedUsers.value.length && paginatedUsers.value.length > 0
})

// 方法
const handleSearch = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  currentPage.value = 1
}

const handlePageSizeChange = () => {
  currentPage.value = 1
}

const sortBy = (field: string) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'asc'
  }
}

const getSortIcon = (field: string) => {
  if (sortField.value !== field) return '↕️'
  return sortOrder.value === 'asc' ? '↑' : '↓'
}

const getRoleText = (role: string) => {
  const roleMap = {
    admin: '管理员',
    teacher: '教师',
    student: '学生'
  }
  return roleMap[role as keyof typeof roleMap] || role
}

const getStatusText = (status: string) => {
  const statusMap = {
    active: '活跃',
    inactive: '非活跃',
    banned: '已封禁'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const selectAllUsers = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.checked) {
    selectedUserIds.value = paginatedUsers.value.map(user => user.id)
  } else {
    selectedUserIds.value = []
  }
}

const viewUser = (user: User) => {
  selectedUser.value = user
  showViewModal.value = true
}

const editUser = (user: User) => {
  selectedUser.value = user
  userForm.value = {
    username: user.username,
    email: user.email,
    phone: user.phone || '',
    role: user.role,
    status: user.status,
    password: '',
    confirmPassword: ''
  }
  showEditModal.value = true
}

const deleteUser = (user: User) => {
  if (confirm(`确定要删除用户 "${user.username}" 吗？`)) {
    const index = users.value.findIndex(u => u.id === user.id)
    if (index > -1) {
      users.value.splice(index, 1)
    }
  }
}

const toggleUserStatus = (user: User) => {
  const newStatus = user.status === 'banned' ? 'active' : 'banned'
  const action = newStatus === 'banned' ? '封禁' : '解封'
  
  if (confirm(`确定要${action}用户 "${user.username}" 吗？`)) {
    user.status = newStatus
    user.updatedAt = new Date().toISOString()
  }
}

const closeUserModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  selectedUser.value = null
  resetUserForm()
}

const closeViewModal = () => {
  showViewModal.value = false
  selectedUser.value = null
}

const closeBatchModal = () => {
  showBatchModal.value = false
  selectedUserIds.value = []
}

const resetUserForm = () => {
  userForm.value = {
    username: '',
    email: '',
    phone: '',
    role: '',
    status: 'active',
    password: '',
    confirmPassword: ''
  }
}

const saveUser = () => {
  if (showAddModal.value) {
    // 添加用户
    if (userForm.value.password !== userForm.value.confirmPassword) {
      alert('密码和确认密码不一致')
      return
    }
    
    const newUser: User = {
      id: Date.now().toString(),
      username: userForm.value.username,
      email: userForm.value.email,
      phone: userForm.value.phone,
      role: userForm.value.role as User['role'],
      status: userForm.value.status as User['status'],
      lastLogin: new Date().toISOString(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    users.value.push(newUser)
  } else {
    // 编辑用户
    if (selectedUser.value) {
      const user = users.value.find(u => u.id === selectedUser.value!.id)
      if (user) {
        user.username = userForm.value.username
        user.email = userForm.value.email
        user.phone = userForm.value.phone
        user.role = userForm.value.role as User['role']
        user.status = userForm.value.status as User['status']
        user.updatedAt = new Date().toISOString()
      }
    }
  }
  
  closeUserModal()
}

const exportUsers = () => {
  console.log('导出用户数据')
}

const batchUpdateStatus = (status: User['status']) => {
  if (confirm(`确定要将选中的 ${selectedUserIds.value.length} 个用户状态设为 "${getStatusText(status)}" 吗？`)) {
    selectedUserIds.value.forEach(id => {
      const user = users.value.find(u => u.id === id)
      if (user) {
        user.status = status
        user.updatedAt = new Date().toISOString()
      }
    })
    closeBatchModal()
  }
}

const batchUpdateRole = (role: User['role']) => {
  if (confirm(`确定要将选中的 ${selectedUserIds.value.length} 个用户角色设为 "${getRoleText(role)}" 吗？`)) {
    selectedUserIds.value.forEach(id => {
      const user = users.value.find(u => u.id === id)
      if (user) {
        user.role = role
        user.updatedAt = new Date().toISOString()
      }
    })
    closeBatchModal()
  }
}

const batchDeleteUsers = () => {
  if (confirm(`确定要删除选中的 ${selectedUserIds.value.length} 个用户吗？此操作不可恢复！`)) {
    selectedUserIds.value.forEach(id => {
      const index = users.value.findIndex(u => u.id === id)
      if (index > -1) {
        users.value.splice(index, 1)
      }
    })
    closeBatchModal()
  }
}

// 生命周期
onMounted(() => {
  // 初始化数据
})
</script>

<style scoped lang="scss">
.user-list {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
  
  h1 {
    font-size: 32px;
    color: #333;
    margin-bottom: 8px;
  }
  
  p {
    color: #666;
    font-size: 16px;
  }
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
  
  .search-section {
    display: flex;
    gap: 15px;
    flex: 1;
    
    .search-box {
      position: relative;
      flex: 1;
      max-width: 300px;
      
      input {
        width: 100%;
        padding: 10px 40px 10px 15px;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 14px;
        
        &:focus {
          outline: none;
          border-color: #007bff;
        }
      }
      
      .search-icon {
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
        color: #666;
      }
    }
    
    .filter-select {
      padding: 10px 15px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 14px;
      background: white;
      
      &:focus {
        outline: none;
        border-color: #007bff;
      }
    }
  }
  
  .action-buttons {
    display: flex;
    gap: 10px;
    
    button {
      padding: 10px 20px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.2s;
      
      &.add-btn {
        background: #28a745;
        color: white;
        
        &:hover {
          background: #1e7e34;
        }
      }
      
      &.batch-btn {
        background: #6f42c1;
        color: white;
        
        &:hover {
          background: #5a2d91;
        }
      }
      
      &.export-btn {
        background: #17a2b8;
        color: white;
        
        &:hover {
          background: #117a8b;
        }
      }
    }
  }
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
  
  .stat-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    gap: 15px;
    
    .stat-icon {
      width: 50px;
      height: 50px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      
      &.total {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }
      
      &.active {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }
      
      &.new {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      }
      
      &.banned {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
      }
    }
    
    .stat-content {
      h3 {
        font-size: 24px;
        font-weight: bold;
        color: #333;
        margin-bottom: 4px;
      }
      
      p {
        color: #666;
        font-size: 14px;
      }
    }
  }
}

.users-table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
  
  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h2 {
      color: #333;
      font-size: 20px;
    }
    
    .table-controls {
      display: flex;
      gap: 15px;
      align-items: center;
      
      .page-size-select {
        padding: 8px 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
        
        &:focus {
          outline: none;
          border-color: #007bff;
        }
      }
      
      .view-toggle {
        display: flex;
        border: 1px solid #ddd;
        border-radius: 4px;
        overflow: hidden;
        
        .view-btn {
          padding: 8px 12px;
          border: none;
          background: white;
          cursor: pointer;
          font-size: 12px;
          transition: all 0.2s;
          
          &:hover {
            background: #f8f9fa;
          }
          
          &.active {
            background: #007bff;
            color: white;
          }
        }
      }
    }
  }
}

.table-view {
  overflow-x: auto;
  
  .users-table {
    width: 100%;
    border-collapse: collapse;
    
    th, td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #eee;
    }
    
    th {
      background: #f8f9fa;
      font-weight: 600;
      color: #333;
      
      &.sortable {
        cursor: pointer;
        user-select: none;
        
        &:hover {
          background: #e9ecef;
        }
        
        .sort-icon {
          margin-left: 5px;
          font-size: 12px;
        }
      }
    }
    
    tr {
      &:hover {
        background: #f8f9fa;
      }
      
      &.selected {
        background: #e3f2fd;
      }
    }
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 10px;
      
      .user-avatar {
        width: 32px;
        height: 32px;
        background: #007bff;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 14px;
      }
      
      .user-details {
        .username {
          font-weight: 500;
          color: #333;
        }
        
        .user-id {
          font-size: 12px;
          color: #666;
        }
      }
    }
    
    .role-badge, .status-badge {
      padding: 4px 8px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
      
      &.admin {
        background: #dc3545;
        color: white;
      }
      
      &.teacher {
        background: #007bff;
        color: white;
      }
      
      &.student {
        background: #28a745;
        color: white;
      }
      
      &.active {
        background: #d4edda;
        color: #155724;
      }
      
      &.inactive {
        background: #fff3cd;
        color: #856404;
      }
      
      &.banned {
        background: #f8d7da;
        color: #721c24;
      }
    }
    
    .action-buttons {
      display: flex;
      gap: 5px;
      
      .action-btn {
        width: 28px;
        height: 28px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        transition: all 0.2s;
        
        &.view {
          background: #17a2b8;
          color: white;
          
          &:hover {
            background: #117a8b;
          }
        }
        
        &.edit {
          background: #ffc107;
          color: #212529;
          
          &:hover {
            background: #e0a800;
          }
        }
        
        &.ban {
          background: #dc3545;
          color: white;
          
          &:hover {
            background: #c82333;
          }
        }
        
        &.unban {
          background: #28a745;
          color: white;
          
          &:hover {
            background: #1e7e34;
          }
        }
        
        &.delete {
          background: #6c757d;
          color: white;
          
          &:hover {
            background: #545b62;
          }
        }
      }
    }
  }
}

.card-view {
  .users-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 20px;
    
    .user-card {
      border: 1px solid #eee;
      border-radius: 8px;
      padding: 20px;
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
      
      &.selected {
        border-color: #007bff;
        background: #f8f9fa;
      }
      
      .card-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 15px;
        
        .card-checkbox {
          margin: 0;
        }
        
        .user-avatar {
          &.large {
            width: 50px;
            height: 50px;
            font-size: 18px;
          }
        }
        
        .user-basic-info {
          flex: 1;
          
          h4 {
            color: #333;
            margin-bottom: 4px;
            font-size: 16px;
          }
          
          p {
            color: #666;
            font-size: 14px;
            margin: 0;
          }
        }
      }
      
      .card-content {
        margin-bottom: 15px;
        
        .info-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          
          .label {
            font-weight: 500;
            color: #666;
          }
        }
      }
      
      .card-actions {
        display: flex;
        gap: 8px;
        
        .action-btn {
          flex: 1;
          padding: 8px 12px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: all 0.2s;
          
          &:hover {
            background: #f8f9fa;
          }
          
          &.view {
            border-color: #17a2b8;
            color: #17a2b8;
            
            &:hover {
              background: #17a2b8;
              color: white;
            }
          }
          
          &.edit {
            border-color: #ffc107;
            color: #856404;
            
            &:hover {
              background: #ffc107;
              color: #856404;
            }
          }
          
          &.ban {
            border-color: #dc3545;
            color: #dc3545;
            
            &:hover {
              background: #dc3545;
              color: white;
            }
          }
          
          &.unban {
            border-color: #28a745;
            color: #28a745;
            
            &:hover {
              background: #28a745;
              color: white;
            }
          }
          
          &.delete {
            border-color: #6c757d;
            color: #6c757d;
            
            &:hover {
              background: #6c757d;
              color: white;
            }
          }
        }
      }
    }
  }
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  
  .pagination-info {
    color: #666;
    font-size: 14px;
  }
  
  .pagination-controls {
    display: flex;
    align-items: center;
    gap: 10px;
    
    .page-btn {
      padding: 8px 16px;
      border: 1px solid #ddd;
      background: white;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.2s;
      
      &:hover:not(:disabled) {
        background: #f8f9fa;
        border-color: #007bff;
      }
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
    
    .page-numbers {
      display: flex;
      gap: 5px;
      
      .page-number {
        width: 32px;
        height: 32px;
        border: 1px solid #ddd;
        background: white;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s;
        
        &:hover {
          background: #f8f9fa;
          border-color: #007bff;
        }
        
        &.active {
          background: #007bff;
          color: white;
          border-color: #007bff;
        }
      }
    }
  }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  
  .modal-content {
    background: white;
    border-radius: 12px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    
    &.large {
      max-width: 800px;
    }
    
    .modal-header {
      padding: 20px;
      border-bottom: 1px solid #eee;
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      h2 {
        margin: 0;
        color: #333;
      }
      
      .close-btn {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #666;
        
        &:hover {
          color: #333;
        }
      }
    }
    
    .modal-body {
      padding: 20px;
      
      .user-form {
        .form-row {
          display: flex;
          gap: 20px;
          margin-bottom: 20px;
          
          .form-group {
            flex: 1;
            
            &.full-width {
              flex: none;
              width: 100%;
            }
            
            label {
              display: block;
              margin-bottom: 5px;
              font-weight: 500;
              color: #333;
            }
            
            input, select {
              width: 100%;
              padding: 10px;
              border: 1px solid #ddd;
              border-radius: 4px;
              font-size: 14px;
              
              &:focus {
                outline: none;
                border-color: #007bff;
              }
            }
            
            .radio-group {
              display: flex;
              gap: 20px;
              
              .radio-item {
                display: flex;
                align-items: center;
                gap: 5px;
                
                input[type="radio"] {
                  width: auto;
                }
              }
            }
          }
        }
        
        .form-actions {
          display: flex;
          gap: 10px;
          justify-content: flex-end;
          margin-top: 20px;
          
          button {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            
            &.cancel-btn {
              background: #6c757d;
              color: white;
              
              &:hover {
                background: #545b62;
              }
            }
            
            &.submit-btn {
              background: #007bff;
              color: white;
              
              &:hover {
                background: #0056b3;
              }
            }
          }
        }
      }
      
      .user-detail {
        .detail-header {
          display: flex;
          align-items: center;
          gap: 20px;
          margin-bottom: 30px;
          padding-bottom: 20px;
          border-bottom: 1px solid #eee;
          
          .user-avatar {
            &.extra-large {
              width: 80px;
              height: 80px;
              font-size: 32px;
            }
          }
          
          .user-info {
            h3 {
              color: #333;
              margin-bottom: 5px;
              font-size: 24px;
            }
            
            p {
              color: #666;
              margin-bottom: 10px;
            }
            
            .badges {
              display: flex;
              gap: 10px;
            }
          }
        }
        
        .detail-content {
          .detail-section {
            margin-bottom: 30px;
            
            h4 {
              color: #333;
              margin-bottom: 15px;
              font-size: 18px;
              border-bottom: 2px solid #007bff;
              padding-bottom: 5px;
            }
            
            .info-grid {
              display: grid;
              grid-template-columns: repeat(2, 1fr);
              gap: 15px;
              
              .info-item {
                display: flex;
                
                label {
                  font-weight: 500;
                  color: #666;
                  min-width: 80px;
                }
                
                span {
                  color: #333;
                }
              }
            }
            
            .stats-grid {
              display: grid;
              grid-template-columns: repeat(4, 1fr);
              gap: 20px;
              
              .stat-item {
                text-align: center;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                
                .stat-value {
                  font-size: 24px;
                  font-weight: bold;
                  color: #007bff;
                  margin-bottom: 5px;
                }
                
                .stat-label {
                  font-size: 12px;
                  color: #666;
                }
              }
            }
          }
        }
      }
      
      .batch-info {
        margin-bottom: 20px;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 8px;
        
        p {
          margin: 0;
          color: #333;
        }
      }
      
      .batch-actions {
        .action-group {
          margin-bottom: 25px;
          
          h4 {
            color: #333;
            margin-bottom: 10px;
            font-size: 16px;
          }
          
          .action-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            
            .batch-action-btn {
              padding: 10px 15px;
              border: none;
              border-radius: 4px;
              cursor: pointer;
              font-size: 14px;
              transition: all 0.2s;
              
              &.active {
                background: #28a745;
                color: white;
                
                &:hover {
                  background: #1e7e34;
                }
              }
              
              &.inactive {
                background: #ffc107;
                color: #212529;
                
                &:hover {
                  background: #e0a800;
                }
              }
              
              &.banned {
                background: #dc3545;
                color: white;
                
                &:hover {
                  background: #c82333;
                }
              }
              
              &.role {
                background: #007bff;
                color: white;
                
                &:hover {
                  background: #0056b3;
                }
              }
              
              &.danger {
                background: #6c757d;
                color: white;
                
                &:hover {
                  background: #545b62;
                }
              }
            }
          }
        }
      }
      
      .batch-footer {
        display: flex;
        justify-content: flex-end;
        margin-top: 20px;
        
        .cancel-btn {
          padding: 10px 20px;
          border: none;
          border-radius: 4px;
          background: #6c757d;
          color: white;
          cursor: pointer;
          
          &:hover {
            background: #545b62;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .user-list {
    padding: 15px;
  }
  
  .action-bar {
    flex-direction: column;
    align-items: stretch;
    
    .search-section {
      flex-direction: column;
      
      .search-box {
        max-width: none;
      }
    }
  }
  
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .table-view {
    .users-table {
      font-size: 12px;
      
      th, td {
        padding: 8px;
      }
      
      .action-buttons {
        flex-direction: column;
        gap: 2px;
        
        .action-btn {
          width: 100%;
          height: auto;
          padding: 4px 8px;
        }
      }
    }
  }
  
  .card-view {
    .users-grid {
      grid-template-columns: 1fr;
    }
  }
  
  .pagination {
    flex-direction: column;
    gap: 10px;
    
    .pagination-controls {
      .page-numbers {
        flex-wrap: wrap;
      }
    }
  }
  
  .modal-content {
    .modal-body {
      .user-form {
        .form-row {
          flex-direction: column;
        }
      }
      
      .user-detail {
        .detail-header {
          flex-direction: column;
          text-align: center;
        }
        
        .detail-content {
          .detail-section {
            .info-grid {
              grid-template-columns: 1fr;
            }
            
            .stats-grid {
              grid-template-columns: repeat(2, 1fr);
            }
          }
        }
      }
    }
  }
}
</style>