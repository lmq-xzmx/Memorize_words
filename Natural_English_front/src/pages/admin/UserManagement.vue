<template>
  <div class="user-management" v-permission="'admin.users.view'">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>用户管理</h1>
        <p>管理系统中的所有用户</p>
      </div>
      <div class="header-right">
        <button @click="showCreateModal = true" 
                class="btn-primary"
                v-permission="'admin.users.create'">
          <i class="fas fa-plus"></i>
          添加用户
        </button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filters">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input type="text" 
               v-model="searchQuery" 
               placeholder="搜索用户名、邮箱或手机号"
               class="search-input">
      </div>
      
      <div class="filters">
        <select v-model="filters.role" class="filter-select">
          <option value="">所有角色</option>
          <option value="student">学生</option>
          <option value="teacher">教师</option>
          <option value="admin">管理员</option>
        </select>
        
        <select v-model="filters.status" class="filter-select">
          <option value="">所有状态</option>
          <option value="active">活跃</option>
          <option value="inactive">非活跃</option>
          <option value="banned">已封禁</option>
        </select>
        
        <button @click="resetFilters" class="btn-secondary">
          <i class="fas fa-undo"></i>
          重置
        </button>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="users-table">
      <div class="table-header">
        <div class="table-actions">
          <button @click="selectAll" class="btn-secondary">
            {{ selectedUsers.length === filteredUsers.length ? '取消全选' : '全选' }}
          </button>
          <button @click="batchDelete" 
                  :disabled="selectedUsers.length === 0"
                  class="btn-danger"
                  v-permission="'admin.users.delete'">
            <i class="fas fa-trash"></i>
            批量删除 ({{ selectedUsers.length }})
          </button>
        </div>
        
        <div class="table-info">
          共 {{ filteredUsers.length }} 个用户
        </div>
      </div>
      
      <div class="table-container">
        <table class="users-table-content">
          <thead>
            <tr>
              <th>
                <input type="checkbox" 
                       :checked="selectedUsers.length === filteredUsers.length && filteredUsers.length > 0"
                       @change="selectAll">
              </th>
              <th>用户信息</th>
              <th>角色</th>
              <th>状态</th>
              <th>注册时间</th>
              <th>最后登录</th>
              <th>学习进度</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedUsers" :key="user.id" class="user-row">
              <td>
                <input type="checkbox" 
                       :value="user.id" 
                       v-model="selectedUsers">
              </td>
              <td>
                <div class="user-info">
                  <img :src="user.avatar || '/default-avatar.png'" 
                       :alt="user.username" 
                       class="user-avatar">
                  <div class="user-details">
                    <div class="username">{{ user.username }}</div>
                    <div class="email">{{ user.email }}</div>
                    <div class="phone" v-if="user.phone">{{ user.phone }}</div>
                  </div>
                </div>
              </td>
              <td>
                <span :class="`role-badge role-${user.role}`">
                  {{ getRoleLabel(user.role) }}
                </span>
              </td>
              <td>
                <span :class="`status-badge status-${user.status}`">
                  {{ getStatusLabel(user.status) }}
                </span>
              </td>
              <td>
                <div class="date-info">
                  {{ formatDate(user.createdAt) }}
                </div>
              </td>
              <td>
                <div class="date-info">
                  {{ user.lastLoginAt ? formatDate(user.lastLoginAt) : '从未登录' }}
                </div>
              </td>
              <td>
                <div class="progress-info">
                  <div class="progress-bar">
                    <div class="progress-fill" 
                         :style="{ width: `${user.learningProgress || 0}%` }">
                    </div>
                  </div>
                  <span class="progress-text">{{ user.learningProgress || 0 }}%</span>
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="viewUser(user)" 
                          class="btn-icon" 
                          title="查看详情">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button @click="editUser(user)" 
                          class="btn-icon" 
                          title="编辑"
                          v-permission="'admin.users.edit'">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button @click="toggleUserStatus(user)" 
                          class="btn-icon" 
                          :title="user.status === 'banned' ? '解封' : '封禁'"
                          v-permission="'admin.users.ban'">
                    <i :class="user.status === 'banned' ? 'fas fa-unlock' : 'fas fa-ban'"></i>
                  </button>
                  <button @click="deleteUser(user)" 
                          class="btn-icon btn-danger" 
                          title="删除"
                          v-permission="'admin.users.delete'">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 分页 -->
      <div class="pagination">
        <button @click="currentPage--" 
                :disabled="currentPage === 1" 
                class="btn-secondary">
          上一页
        </button>
        
        <div class="page-numbers">
          <button v-for="page in visiblePages" 
                  :key="page"
                  @click="currentPage = page"
                  :class="{ active: page === currentPage }"
                  class="page-btn">
            {{ page }}
          </button>
        </div>
        
        <button @click="currentPage++" 
                :disabled="currentPage === totalPages" 
                class="btn-secondary">
          下一页
        </button>
        
        <div class="page-info">
          第 {{ currentPage }} 页，共 {{ totalPages }} 页
        </div>
      </div>
    </div>

    <!-- 创建/编辑用户弹窗 -->
    <div class="modal" v-if="showCreateModal || showEditModal" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ showCreateModal ? '添加用户' : '编辑用户' }}</h3>
          <button @click="closeModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveUser">
            <div class="form-row">
              <div class="form-group">
                <label for="username">用户名 *</label>
                <input type="text" 
                       id="username" 
                       v-model="userForm.username" 
                       class="form-input"
                       placeholder="请输入用户名"
                       required>
              </div>
              <div class="form-group">
                <label for="email">邮箱 *</label>
                <input type="email" 
                       id="email" 
                       v-model="userForm.email" 
                       class="form-input"
                       placeholder="请输入邮箱"
                       required>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="phone">手机号</label>
                <input type="tel" 
                       id="phone" 
                       v-model="userForm.phone" 
                       class="form-input"
                       placeholder="请输入手机号">
              </div>
              <div class="form-group">
                <label for="role">角色 *</label>
                <select id="role" v-model="userForm.role" class="form-select" required>
                  <option value="student">学生</option>
                  <option value="teacher">教师</option>
                  <option value="admin">管理员</option>
                </select>
              </div>
            </div>
            
            <div class="form-row" v-if="showCreateModal">
              <div class="form-group">
                <label for="password">密码 *</label>
                <input type="password" 
                       id="password" 
                       v-model="userForm.password" 
                       class="form-input"
                       placeholder="请输入密码"
                       required>
              </div>
              <div class="form-group">
                <label for="confirmPassword">确认密码 *</label>
                <input type="password" 
                       id="confirmPassword" 
                       v-model="userForm.confirmPassword" 
                       class="form-input"
                       placeholder="请再次输入密码"
                       required>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeModal" class="btn-secondary">
                取消
              </button>
              <button type="submit" class="btn-primary">
                {{ showCreateModal ? '创建' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 用户详情弹窗 -->
    <div class="modal" v-if="showDetailModal" @click="showDetailModal = false">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>用户详情</h3>
          <button @click="showDetailModal = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body" v-if="selectedUser">
          <div class="user-detail">
            <div class="detail-section">
              <h4>基本信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>头像</label>
                  <img :src="selectedUser.avatar || '/default-avatar.png'" 
                       :alt="selectedUser.username" 
                       class="detail-avatar">
                </div>
                <div class="detail-item">
                  <label>用户名</label>
                  <span>{{ selectedUser.username }}</span>
                </div>
                <div class="detail-item">
                  <label>邮箱</label>
                  <span>{{ selectedUser.email }}</span>
                </div>
                <div class="detail-item">
                  <label>手机号</label>
                  <span>{{ selectedUser.phone || '未设置' }}</span>
                </div>
                <div class="detail-item">
                  <label>角色</label>
                  <span class="role-badge" :class="`role-${selectedUser.role}`">
                    {{ getRoleLabel(selectedUser.role) }}
                  </span>
                </div>
                <div class="detail-item">
                  <label>状态</label>
                  <span class="status-badge" :class="`status-${selectedUser.status}`">
                    {{ getStatusLabel(selectedUser.status) }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>学习统计</h4>
              <div class="stats-grid">
                <div class="stat-card">
                  <div class="stat-value">{{ selectedUser.totalWords || 0 }}</div>
                  <div class="stat-label">学习单词</div>
                </div>
                <div class="stat-card">
                  <div class="stat-value">{{ selectedUser.studyDays || 0 }}</div>
                  <div class="stat-label">学习天数</div>
                </div>
                <div class="stat-card">
                  <div class="stat-value">{{ selectedUser.studyHours || 0 }}</div>
                  <div class="stat-label">学习时长(小时)</div>
                </div>
                <div class="stat-card">
                  <div class="stat-value">{{ selectedUser.accuracy || 0 }}%</div>
                  <div class="stat-label">正确率</div>
                </div>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>时间信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>注册时间</label>
                  <span>{{ formatDate(selectedUser.createdAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>最后登录</label>
                  <span>{{ selectedUser.lastLoginAt ? formatDate(selectedUser.lastLoginAt) : '从未登录' }}</span>
                </div>
                <div class="detail-item">
                  <label>最后更新</label>
                  <span>{{ formatDate(selectedUser.updatedAt) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'

// 接口定义
interface User {
  id: number
  username: string
  email: string
  phone?: string
  role: 'student' | 'teacher' | 'admin'
  status: 'active' | 'inactive' | 'banned'
  avatar?: string
  createdAt: string
  updatedAt: string
  lastLoginAt?: string
  learningProgress?: number
  totalWords?: number
  studyDays?: number
  studyHours?: number
  accuracy?: number
}

// 响应式数据
const searchQuery = ref('')
const selectedUsers = ref<number[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDetailModal = ref(false)
const selectedUser = ref<User | null>(null)

const filters = reactive({
  role: '',
  status: ''
})

const userForm = reactive({
  id: null as number | null,
  username: '',
  email: '',
  phone: '',
  role: 'student' as User['role'],
  password: '',
  confirmPassword: ''
})

// 模拟用户数据
const users = ref<User[]>([
  {
    id: 1,
    username: 'john_doe',
    email: 'john@example.com',
    phone: '13800138000',
    role: 'student',
    status: 'active',
    avatar: '/default-avatar.png',
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-20T15:45:00Z',
    lastLoginAt: '2024-01-20T15:45:00Z',
    learningProgress: 75,
    totalWords: 1200,
    studyDays: 45,
    studyHours: 120,
    accuracy: 85
  },
  {
    id: 2,
    username: 'jane_smith',
    email: 'jane@example.com',
    phone: '13900139000',
    role: 'teacher',
    status: 'active',
    avatar: '/default-avatar.png',
    createdAt: '2024-01-10T09:20:00Z',
    updatedAt: '2024-01-19T14:30:00Z',
    lastLoginAt: '2024-01-19T14:30:00Z',
    learningProgress: 90,
    totalWords: 2500,
    studyDays: 60,
    studyHours: 200,
    accuracy: 92
  },
  {
    id: 3,
    username: 'admin_user',
    email: 'admin@example.com',
    role: 'admin',
    status: 'active',
    avatar: '/default-avatar.png',
    createdAt: '2024-01-01T08:00:00Z',
    updatedAt: '2024-01-20T16:00:00Z',
    lastLoginAt: '2024-01-20T16:00:00Z',
    learningProgress: 100,
    totalWords: 5000,
    studyDays: 100,
    studyHours: 500,
    accuracy: 95
  }
])

// 计算属性
const filteredUsers = computed(() => {
  return users.value.filter(user => {
    const matchesSearch = !searchQuery.value || 
      user.username.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (user.phone && user.phone.includes(searchQuery.value))
    
    const matchesRole = !filters.role || user.role === filters.role
    const matchesStatus = !filters.status || user.status === filters.status
    
    return matchesSearch && matchesRole && matchesStatus
  })
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
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// 方法
const getRoleLabel = (role: string) => {
  const labels = {
    student: '学生',
    teacher: '教师',
    admin: '管理员'
  }
  return labels[role as keyof typeof labels] || role
}

const getStatusLabel = (status: string) => {
  const labels = {
    active: '活跃',
    inactive: '非活跃',
    banned: '已封禁'
  }
  return labels[status as keyof typeof labels] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const selectAll = () => {
  if (selectedUsers.value.length === filteredUsers.value.length) {
    selectedUsers.value = []
  } else {
    selectedUsers.value = filteredUsers.value.map(user => user.id)
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  filters.role = ''
  filters.status = ''
  currentPage.value = 1
}

const viewUser = (user: User) => {
  selectedUser.value = user
  showDetailModal.value = true
}

const editUser = (user: User) => {
  Object.assign(userForm, {
    id: user.id,
    username: user.username,
    email: user.email,
    phone: user.phone || '',
    role: user.role,
    password: '',
    confirmPassword: ''
  })
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

const batchDelete = () => {
  if (confirm(`确定要删除选中的 ${selectedUsers.value.length} 个用户吗？`)) {
    users.value = users.value.filter(user => !selectedUsers.value.includes(user.id))
    selectedUsers.value = []
  }
}

const toggleUserStatus = (user: User) => {
  const newStatus = user.status === 'banned' ? 'active' : 'banned'
  const action = newStatus === 'banned' ? '封禁' : '解封'
  
  if (confirm(`确定要${action}用户 "${user.username}" 吗？`)) {
    user.status = newStatus
  }
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  resetUserForm()
}

const resetUserForm = () => {
  Object.assign(userForm, {
    id: null,
    username: '',
    email: '',
    phone: '',
    role: 'student',
    password: '',
    confirmPassword: ''
  })
}

const saveUser = () => {
  if (showCreateModal.value) {
    if (userForm.password !== userForm.confirmPassword) {
      alert('密码和确认密码不匹配')
      return
    }
    
    const newUser: User = {
      id: Date.now(),
      username: userForm.username,
      email: userForm.email,
      phone: userForm.phone || undefined,
      role: userForm.role,
      status: 'active',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      learningProgress: 0
    }
    
    users.value.push(newUser)
  } else if (showEditModal.value && userForm.id) {
    const user = users.value.find(u => u.id === userForm.id)
    if (user) {
      user.username = userForm.username
      user.email = userForm.email
      user.phone = userForm.phone || undefined
      user.role = userForm.role
      user.updatedAt = new Date().toISOString()
    }
  }
  
  closeModal()
}

onMounted(() => {
  // 组件挂载时的初始化逻辑
})
</script>

<style scoped lang="scss">
.user-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  
  .header-left {
    h1 {
      color: #2c3e50;
      margin-bottom: 8px;
    }
    
    p {
      color: #7f8c8d;
      margin: 0;
    }
  }
}

.search-filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
  
  .search-box {
    position: relative;
    flex: 1;
    min-width: 300px;
    
    i {
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: #7f8c8d;
    }
    
    .search-input {
      width: 100%;
      padding: 12px 12px 12px 40px;
      border: 2px solid #e9ecef;
      border-radius: 8px;
      font-size: 14px;
      
      &:focus {
        outline: none;
        border-color: #3498db;
      }
    }
  }
  
  .filters {
    display: flex;
    gap: 12px;
    align-items: center;
  }
  
  .filter-select {
    padding: 12px;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    font-size: 14px;
    min-width: 120px;
    
    &:focus {
      outline: none;
      border-color: #3498db;
    }
  }
}

.users-table {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  
  .table-actions {
    display: flex;
    gap: 12px;
  }
  
  .table-info {
    color: #7f8c8d;
    font-size: 14px;
  }
}

.table-container {
  overflow-x: auto;
}

.users-table-content {
  width: 100%;
  border-collapse: collapse;
  
  th, td {
    padding: 16px;
    text-align: left;
    border-bottom: 1px solid #f8f9fa;
  }
  
  th {
    background: #f8f9fa;
    font-weight: 600;
    color: #2c3e50;
    font-size: 14px;
  }
  
  .user-row {
    &:hover {
      background: #f8f9fa;
    }
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .user-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
  }
  
  .user-details {
    .username {
      font-weight: 600;
      color: #2c3e50;
      margin-bottom: 4px;
    }
    
    .email {
      color: #7f8c8d;
      font-size: 13px;
      margin-bottom: 2px;
    }
    
    .phone {
      color: #7f8c8d;
      font-size: 12px;
    }
  }
}

.role-badge, .status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  
  &.role-student {
    background: #e3f2fd;
    color: #1976d2;
  }
  
  &.role-teacher {
    background: #f3e5f5;
    color: #7b1fa2;
  }
  
  &.role-admin {
    background: #ffebee;
    color: #c62828;
  }
  
  &.status-active {
    background: #e8f5e8;
    color: #2e7d32;
  }
  
  &.status-inactive {
    background: #fff3e0;
    color: #f57c00;
  }
  
  &.status-banned {
    background: #ffebee;
    color: #c62828;
  }
}

.date-info {
  color: #7f8c8d;
  font-size: 13px;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .progress-bar {
    width: 60px;
    height: 6px;
    background: #e9ecef;
    border-radius: 3px;
    overflow: hidden;
    
    .progress-fill {
      height: 100%;
      background: #3498db;
      transition: width 0.3s ease;
    }
  }
  
  .progress-text {
    font-size: 12px;
    color: #7f8c8d;
    min-width: 35px;
  }
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: #f8f9fa;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  
  &:hover {
    background: #e9ecef;
    color: #495057;
  }
  
  &.btn-danger {
    &:hover {
      background: #dc3545;
      color: white;
    }
  }
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9fa;
  
  .page-numbers {
    display: flex;
    gap: 4px;
  }
  
  .page-btn {
    width: 36px;
    height: 36px;
    border: none;
    border-radius: 6px;
    background: white;
    color: #6c757d;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    
    &:hover {
      background: #e9ecef;
    }
    
    &.active {
      background: #3498db;
      color: white;
    }
  }
  
  .page-info {
    color: #7f8c8d;
    font-size: 14px;
  }
}

.btn-primary, .btn-secondary, .btn-danger {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.btn-primary {
  background: #3498db;
  color: white;
  
  &:hover:not(:disabled) {
    background: #2980b9;
  }
}

.btn-secondary {
  background: #6c757d;
  color: white;
  
  &:hover:not(:disabled) {
    background: #5a6268;
  }
}

.btn-danger {
  background: #e74c3c;
  color: white;
  
  &:hover:not(:disabled) {
    background: #c0392b;
  }
}

.modal {
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
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 0;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  
  &.large {
    max-width: 800px;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
  
  h3 {
    margin: 0;
    color: #2c3e50;
  }
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #7f8c8d;
  cursor: pointer;
  
  &:hover {
    color: #2c3e50;
  }
}

.modal-body {
  padding: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  
  label {
    color: #2c3e50;
    font-weight: 500;
    margin-bottom: 8px;
    font-size: 14px;
  }
}

.form-input, .form-select {
  padding: 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #3498db;
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.user-detail {
  .detail-section {
    margin-bottom: 32px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    h4 {
      color: #2c3e50;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 2px solid #e9ecef;
    }
  }
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  
  label {
    color: #7f8c8d;
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
  }
  
  span {
    color: #2c3e50;
    font-weight: 500;
  }
}

.detail-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.stat-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  
  .stat-value {
    font-size: 24px;
    font-weight: 700;
    color: #3498db;
    margin-bottom: 4px;
  }
  
  .stat-label {
    color: #7f8c8d;
    font-size: 12px;
    font-weight: 500;
  }
}

@media (max-width: 768px) {
  .user-management {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .search-filters {
    flex-direction: column;
    
    .search-box {
      min-width: auto;
    }
    
    .filters {
      flex-wrap: wrap;
    }
  }
  
  .table-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
    
    .table-actions {
      justify-content: center;
    }
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>