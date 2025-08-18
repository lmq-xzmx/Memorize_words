<template>
  <div class="role-management" v-permission="['admin']">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>角色管理</h1>
      <p>管理系统角色和权限配置</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="search-section">
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="搜索角色名称或描述..."
            @input="handleSearch"
          >
          <button class="search-btn">
            <i class="icon-search"></i>
          </button>
        </div>
        <div class="filter-section">
          <select v-model="statusFilter" @change="handleFilter">
            <option value="">全部状态</option>
            <option value="active">启用</option>
            <option value="inactive">禁用</option>
          </select>
          <select v-model="typeFilter" @change="handleFilter">
            <option value="">全部类型</option>
            <option value="system">系统角色</option>
            <option value="custom">自定义角色</option>
          </select>
        </div>
      </div>
      <div class="action-buttons">
        <button class="add-btn" @click="showAddRole">
          <i class="icon-plus"></i>
          添加角色
        </button>
        <button class="refresh-btn" @click="refreshData">
          <i class="icon-refresh"></i>
          刷新
        </button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="icon-role"></i>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalRoles }}</div>
          <div class="stat-label">总角色数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="icon-permission"></i>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalPermissions }}</div>
          <div class="stat-label">权限总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="icon-user"></i>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.assignedUsers }}</div>
          <div class="stat-label">已分配用户</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="icon-active"></i>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.activeRoles }}</div>
          <div class="stat-label">活跃角色</div>
        </div>
      </div>
    </div>

    <!-- 角色列表 -->
    <div class="roles-section">
      <div class="section-header">
        <h2>角色列表</h2>
        <div class="view-controls">
          <button 
            :class="['view-btn', { active: viewMode === 'table' }]"
            @click="viewMode = 'table'"
          >
            <i class="icon-table"></i>
            表格视图
          </button>
          <button 
            :class="['view-btn', { active: viewMode === 'card' }]"
            @click="viewMode = 'card'"
          >
            <i class="icon-grid"></i>
            卡片视图
          </button>
        </div>
      </div>

      <!-- 表格视图 -->
      <div v-if="viewMode === 'table'" class="table-view">
        <table class="roles-table">
          <thead>
            <tr>
              <th>
                <input 
                  type="checkbox" 
                  v-model="selectAll" 
                  @change="handleSelectAll"
                >
              </th>
              <th @click="handleSort('name')">
                角色标识
                <i :class="getSortIcon('name')"></i>
              </th>
              <th>显示名称</th>
              <th>描述</th>
              <th @click="handleSort('category')">
                分类
                <i :class="getSortIcon('category')"></i>
              </th>
              <th>级别</th>
              <th>权限数量</th>
              <th>用户数量</th>
              <th>模板</th>
              <th @click="handleSort('isActive')">
                状态
                <i :class="getSortIcon('isActive')"></i>
              </th>
              <th @click="handleSort('created_at')">
                创建时间
                <i :class="getSortIcon('created_at')"></i>
              </th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="role in paginatedRoles" :key="role.id">
              <td>
                <input 
                  type="checkbox" 
                  v-model="selectedRoles" 
                  :value="role.id"
                >
              </td>
              <td>
                <div class="role-name">
                  <i :class="getRoleIcon(role.category || 'custom')"></i>
                  {{ role.role }}
                </div>
              </td>
              <td>{{ role.display_name }}</td>
              <td>{{ role.description }}</td>
              <td>
                <span :class="['type-badge', role.category || 'custom']">
                  {{ getRoleTypeText(role.category || 'custom') }}
                </span>
              </td>
              <td>{{ role.level || 1 }}</td>
              <td>{{ role.permissions?.length || 0 }}</td>
              <td>{{ role.user_count || 0 }}</td>
              <td>
                <span v-if="role.template_id" class="template-badge">
                  模板角色
                </span>
                <span v-else class="no-template">
                  自定义
                </span>
              </td>
              <td>
                <span :class="['status-badge', role.is_active ? 'active' : 'inactive']">
                  {{ getStatusText(role.is_active) }}
                </span>
              </td>
              <td>{{ formatDate(role.created_at) }}</td>
              <td>
                <div class="action-buttons">
                  <button 
                    class="action-btn view-btn"
                    @click="viewRole(role)"
                    title="查看详情"
                  >
                    <i class="icon-eye"></i>
                  </button>
                  <button 
                    class="action-btn edit-btn"
                    @click="editRole(role)"
                    title="编辑"
                    :disabled="role.category === 'system'"
                  >
                    <i class="icon-edit"></i>
                  </button>
                  <button 
                    class="action-btn permission-btn"
                    @click="managePermissions(role)"
                    title="权限管理"
                  >
                    <i class="icon-permission"></i>
                  </button>
                  <button 
                    class="action-btn sync-btn"
                    @click="syncRoleToGroup(String(role.id))"
                    title="同步到组"
                    v-if="role.auto_sync"
                  >
                    <i class="icon-sync"></i>
                  </button>
                  <button 
                    class="action-btn validate-btn"
                    @click="validatePermissions(String(role.id))"
                    title="验证权限"
                  >
                    <i class="icon-check"></i>
                  </button>
                  <button 
                    class="action-btn delete-btn"
                    @click="deleteRole(role)"
                    title="删除"
                    :disabled="role.category === 'system' || role.userCount > 0"
                  >
                    <i class="icon-delete"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 卡片视图 -->
      <div v-if="viewMode === 'card'" class="card-view">
        <div class="roles-grid">
          <div 
            v-for="role in paginatedRoles" 
            :key="role.id" 
            class="role-card"
            @click="viewRole(role)"
          >
            <div class="card-header">
              <div class="role-info">
                <i :class="getRoleIcon(role.type)"></i>
                <h3>{{ role.name }}</h3>
                <span :class="['type-badge', role.category || 'custom']">
                  {{ getRoleTypeText(role.category || 'custom') }}
                </span>
              </div>
              <div class="card-actions">
                <input 
                  type="checkbox" 
                  v-model="selectedRoles" 
                  :value="role.id"
                  @click.stop
                >
              </div>
            </div>
            <div class="card-body">
              <p class="role-description">{{ role.description }}</p>
              <div class="role-stats">
                <div class="stat-item">
                  <i class="icon-permission"></i>
                  <span>{{ role.permissions?.length || 0 }} 权限</span>
                </div>
                <div class="stat-item">
                  <i class="icon-user"></i>
                  <span>{{ role.user_count || 0 }} 用户</span>
                </div>
              </div>
            </div>
            <div class="card-footer">
              <span :class="['status-badge', role.is_active ? 'active' : 'inactive']">
                {{ getStatusText(role.is_active) }}
              </span>
              <div class="card-actions">
                <button 
                  class="action-btn edit-btn"
                  @click.stop="editRole(role)"
                  :disabled="role.category === 'system'"
                >
                  <i class="icon-edit"></i>
                </button>
                <button 
                  class="action-btn permission-btn"
                  @click.stop="managePermissions(role)"
                >
                  <i class="icon-permission"></i>
                </button>
                <button 
                  class="action-btn delete-btn"
                  @click.stop="deleteRole(role)"
                  :disabled="role.category === 'system' || role.user_count > 0"
                >
                  <i class="icon-delete"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <div class="pagination-info">
          显示 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredRoles.length) }} 条，
          共 {{ filteredRoles.length }} 条记录
        </div>
        <div class="pagination-controls">
          <button 
            class="page-btn"
            @click="currentPage = 1"
            :disabled="currentPage === 1"
          >
            首页
          </button>
          <button 
            class="page-btn"
            @click="currentPage--"
            :disabled="currentPage === 1"
          >
            上一页
          </button>
          <div class="page-numbers">
            <button 
              v-for="page in visiblePages" 
              :key="page"
              :class="['page-number', { active: page === currentPage }]"
              @click="currentPage = page"
            >
              {{ page }}
            </button>
          </div>
          <button 
            class="page-btn"
            @click="currentPage++"
            :disabled="currentPage === totalPages"
          >
            下一页
          </button>
          <button 
            class="page-btn"
            @click="currentPage = totalPages"
            :disabled="currentPage === totalPages"
          >
            末页
          </button>
        </div>
      </div>
    </div>

    <!-- 角色表单弹窗 -->
    <div v-if="showRoleModal" class="modal-overlay" @click="closeRoleModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? '编辑角色' : '添加角色' }}</h3>
          <button class="close-btn" @click="closeRoleModal">
            <i class="icon-close"></i>
          </button>
        </div>
        <div class="modal-body">
          <form class="role-form" @submit.prevent="saveRole">
            <div class="form-row">
              <div class="form-group">
                <label>角色标识 *</label>
                <input 
                  type="text" 
                  v-model="roleForm.role" 
                  placeholder="请输入角色标识（英文）"
                  required
                >
              </div>
              <div class="form-group">
                <label>显示名称 *</label>
                <input 
                  type="text" 
                  v-model="roleForm.display_name" 
                  placeholder="请输入显示名称"
                  required
                >
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>角色分类</label>
                <select v-model="roleForm.category" :disabled="isEditing">
                  <option value="custom">自定义角色</option>
                  <option value="system">系统角色</option>
                  <option value="education">教育角色</option>
                  <option value="business">业务角色</option>
                </select>
              </div>
              <div class="form-group">
                <label>角色级别</label>
                <input 
                  type="number" 
                  v-model="roleForm.level" 
                  min="1" 
                  max="10"
                  placeholder="1-10"
                >
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>角色模板</label>
                <select v-model="roleForm.template_id">
                  <option value="">无模板</option>
                  <option v-for="template in roleTemplates" :key="template.id" :value="template.id">
                     {{ template.template_name }}
                   </option>
                </select>
              </div>
              <div class="form-group">
                <label>父级角色</label>
                <select v-model="roleForm.parent">
                  <option value="">无父级</option>
                  <option v-for="role in roles" :key="role.id" :value="role.id">
                    {{ role.display_name || role.role }}
                  </option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full-width">
                <label>角色描述</label>
                <textarea 
                  v-model="roleForm.description" 
                  placeholder="请输入角色描述"
                  rows="3"
                ></textarea>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="checkbox-label">
                  <input 
                    type="checkbox" 
                    v-model="roleForm.is_active"
                  >
                  启用角色
                </label>
              </div>
              <div class="form-group">
                <label class="checkbox-label">
                  <input 
                    type="checkbox" 
                    v-model="roleForm.auto_sync"
                  >
                  自动同步到组
                </label>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="cancel-btn" @click="closeRoleModal">
                取消
              </button>
              <button type="submit" class="submit-btn">
                {{ isEditing ? '更新' : '创建' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 权限管理弹窗 -->
    <div v-if="showPermissionModal" class="modal-overlay" @click="closePermissionModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>权限管理 - {{ currentRole?.name }}</h3>
          <button class="close-btn" @click="closePermissionModal">
            <i class="icon-close"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="permission-management">
            <div class="permission-search">
              <input 
                type="text" 
                v-model="permissionSearch" 
                placeholder="搜索权限..."
              >
            </div>
            <div class="permission-categories">
              <div 
                v-for="category in permissionCategories" 
                :key="category.name"
                class="permission-category"
              >
                <div class="category-header">
                  <h4>{{ category.name }}</h4>
                  <div class="category-actions">
                    <button 
                      class="select-all-btn"
                      @click="selectAllInCategory(category)"
                    >
                      全选
                    </button>
                    <button 
                      class="deselect-all-btn"
                      @click="deselectAllInCategory(category)"
                    >
                      取消全选
                    </button>
                  </div>
                </div>
                <div class="permission-list">
                  <div 
                    v-for="permission in category.permissions" 
                    :key="permission.id"
                    class="permission-item"
                  >
                    <input 
                      type="checkbox" 
                      :id="`perm-${permission.id}`"
                      v-model="selectedPermissions" 
                      :value="permission.id"
                    >
                    <label :for="`perm-${permission.id}`">
                      <div class="permission-info">
                        <span class="permission-name">{{ permission.name }}</span>
                        <span class="permission-description">{{ permission.description }}</span>
                      </div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
            <div class="permission-actions">
              <button class="cancel-btn" @click="closePermissionModal">
                取消
              </button>
              <button class="submit-btn" @click="savePermissions">
                保存权限
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import roleService from '@/services/roleService'
import permissionService from '@/services/permissionService'
import type { Role, RoleTemplate } from '@/services/roleService'
import type { Permission } from '@/services/permissionService'

// 响应式数据
const searchQuery = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const templateFilter = ref('')
const viewMode = ref('table')
const currentPage = ref(1)
const pageSize = ref(10)
const sortField = ref('created_at')
const sortOrder = ref('desc')
const selectAll = ref(false)
const selectedRoles = ref<string[]>([])
const loading = ref(false)

// 弹窗状态
const showRoleModal = ref(false)
const showPermissionModal = ref(false)
const showTemplateModal = ref(false)
const showAuditModal = ref(false)
const showSecurityModal = ref(false)
const isEditing = ref(false)
const currentRole = ref<Role | null>(null)

// 数据列表
const roles = ref<any[]>([])
const roleTemplates = ref<RoleTemplate[]>([])
const permissions = ref<Permission[]>([])
const auditLogs = ref<any[]>([])
const securityReport = ref<any>(null)

// 表单数据
const roleForm = ref<any>({
  role: '',
  display_name: '',
  description: '',
  category: '',
  level: 1,
  is_active: true,
  permissions: [],
  template_id: '',
  parent: null,
  auto_sync: true
})

// 权限管理
const permissionSearch = ref('')
const selectedPermissions = ref<any[]>([])

// 统计数据
const stats = ref({
  totalRoles: 0,
  totalPermissions: 0,
  assignedUsers: 0,
  activeRoles: 0,
  templatesCount: 0,
  recentChanges: 0
})

// 移除模拟数据，使用API加载

// 权限分类数据
const permissionCategories = ref<any[]>([])

// 计算属性
const filteredRoles = computed(() => {
  let filtered = roles.value
  
  if (searchQuery.value) {
    filtered = filtered.filter((role: any) => 
      role.role?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      role.display_name?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      role.description?.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }
  
  if (statusFilter.value) {
    filtered = filtered.filter((role: any) => 
      statusFilter.value === 'active' ? role.is_active : !role.is_active
    )
  }
  
  if (typeFilter.value) {
    filtered = filtered.filter((role: any) => role.category === typeFilter.value)
  }
  
  if (templateFilter.value) {
    filtered = filtered.filter((role: any) => role.template_id === templateFilter.value)
  }
  
  return filtered
})

const paginatedRoles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRoles.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredRoles.value.length / pageSize.value)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  let start = Math.max(1, current - 2)
  let end = Math.min(total, current + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// API方法
const loadRoles = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      pageSize: pageSize.value,
      search: searchQuery.value,
      category: typeFilter.value,
      template: templateFilter.value,
      isActive: statusFilter.value ? statusFilter.value === 'active' : undefined,
      orderBy: sortField.value,
      orderDirection: sortOrder.value === 'desc' ? 'desc' : 'asc'
    }
    const response = await roleService.getRoles(params)
    roles.value = response
    stats.value.totalRoles = response.length
  } catch (error) {
    ElMessage.error('加载角色列表失败')
    console.error('加载角色失败:', error)
  } finally {
    loading.value = false
  }
}

const loadRoleTemplates = async () => {
  try {
    const response = await roleService.getRoleTemplates()
    roleTemplates.value = response
    stats.value.templatesCount = response.length
  } catch (error) {
    console.error('加载角色模板失败:', error)
  }
}

const loadPermissions = async () => {
  try {
    const allPermissions = await permissionService.getAllPermissions()
    permissions.value = allPermissions
    stats.value.totalPermissions = allPermissions.length
    
    // 按分类组织权限
    const categories = allPermissions.reduce((acc, permission) => {
      if (!acc[permission.category]) {
        acc[permission.category] = {
          name: permission.category,
          permissions: []
        }
      }
      acc[permission.category].permissions.push(permission)
      return acc
    }, {} as any)
    
    permissionCategories.value = Object.values(categories)
  } catch (error) {
    console.error('加载权限列表失败:', error)
  }
}

const loadStats = async () => {
  try {
    const roleStats = await roleService.getRoleStats()
    stats.value = {
      ...stats.value,
      ...roleStats
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 事件处理方法
const handleSearch = () => {
  currentPage.value = 1
  loadRoles()
}

const handleFilter = () => {
  currentPage.value = 1
  loadRoles()
}

const handleSort = (field: string) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'asc'
  }
}

const getSortIcon = (field: string) => {
  if (sortField.value !== field) return 'icon-sort'
  return sortOrder.value === 'asc' ? 'icon-sort-up' : 'icon-sort-down'
}

const handleSelectAll = () => {
  if (selectAll.value) {
    selectedRoles.value = paginatedRoles.value.map(role => role.id)
  } else {
    selectedRoles.value = []
  }
}

const refreshData = () => {
  loadRoles()
  loadRoleTemplates()
  loadPermissions()
  loadStats()
}

const showAddRole = () => {
  isEditing.value = false
  roleForm.value = {
    name: '',
    displayName: '',
    description: '',
    category: '',
    level: 1,
    isActive: true,
    permissions: [],
    templateId: '',
    parentRole: '',
    autoSync: true
  }
  showRoleModal.value = true
}

const editRole = (role: any) => {
  isEditing.value = true
  currentRole.value = role
  roleForm.value = { ...role }
  showRoleModal.value = true
}

const viewRole = (role: any) => {
  console.log('查看角色详情:', role)
}

const deleteRole = async (role: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色 "${role.display_name || role.role}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await roleService.deleteRole(role.id)
    ElMessage.success('角色删除成功')
    loadRoles()
    loadStats()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('角色删除失败')
      console.error('删除角色失败:', error)
    }
  }
}

const managePermissions = (role: any) => {
  currentRole.value = role
  selectedPermissions.value = [...(role.permissions || [])]
  showPermissionModal.value = true
}

const closeRoleModal = () => {
  showRoleModal.value = false
  currentRole.value = null
}

const closePermissionModal = () => {
  showPermissionModal.value = false
  currentRole.value = null
  selectedPermissions.value = []
}

const saveRole = async () => {
  try {
    if (isEditing.value && currentRole.value) {
      await roleService.updateRole(currentRole.value.id, roleForm.value)
      ElMessage.success('角色更新成功')
    } else {
      await roleService.createRole(roleForm.value as any)
      ElMessage.success('角色创建成功')
    }
    closeRoleModal()
    loadRoles()
    loadStats()
  } catch (error) {
    ElMessage.error(isEditing.value ? '角色更新失败' : '角色创建失败')
    console.error('角色操作失败:', error)
  }
}

const savePermissions = async () => {
  try {
    if (currentRole.value) {
      await roleService.updateRolePermissions(currentRole.value.id, selectedPermissions.value)
      ElMessage.success('权限更新成功')
      closePermissionModal()
      loadRoles()
    }
  } catch (error) {
    ElMessage.error('权限更新失败')
    console.error('更新角色权限失败:', error)
  }
}

const selectAllInCategory = (category: any) => {
  category.permissions.forEach((permission: any) => {
    if (!selectedPermissions.value.includes(permission.id)) {
      selectedPermissions.value.push(permission.id)
    }
  })
}

const deselectAllInCategory = (category: any) => {
  category.permissions.forEach((permission: any) => {
    const index = selectedPermissions.value.indexOf(permission.id)
    if (index > -1) {
      selectedPermissions.value.splice(index, 1)
    }
  })
}

// 新增功能方法
const syncRoleToGroup = async (roleId: string) => {
  try {
    await roleService.syncRoleToGroup(roleId)
    ElMessage.success('角色同步成功')
    loadRoles()
  } catch (error) {
    ElMessage.error('角色同步失败')
    console.error('同步角色失败:', error)
  }
}

const validatePermissions = async (roleId: string) => {
  try {
    const result = await roleService.validateUserPermissions(parseInt(roleId))
    if (result.isValid) {
      ElMessage.success('权限验证通过')
    } else {
      ElMessage.warning(`发现 ${result.issues.length} 个权限问题`)
    }
  } catch (error) {
    ElMessage.error('权限验证失败')
    console.error('验证权限失败:', error)
  }
}

const generateSecurityReport = async () => {
  try {
    securityReport.value = await roleService.generateSecurityReport()
    showSecurityModal.value = true
    ElMessage.success('安全报告生成成功')
  } catch (error) {
    ElMessage.error('生成安全报告失败')
    console.error('生成安全报告失败:', error)
  }
}

const loadAuditLogs = async () => {
  try {
    // 暂时使用空数组，等待后端API实现
    auditLogs.value = []
  } catch (error) {
    console.error('加载审计日志失败:', error)
  }
}

const showAuditLogs = () => {
  loadAuditLogs()
  showAuditModal.value = true
}

const exportRoles = async () => {
  try {
    const blob = await roleService.exportRoles('excel')
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `roles_${new Date().toISOString().split('T')[0]}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
    console.error('导出角色失败:', error)
  }
}

const importRoles = (file: File) => {
  roleService.importRoles(file)
    .then(result => {
      if (result.failed > 0) {
        ElMessage.warning(`导入完成，成功 ${result.success} 个，失败 ${result.failed} 个`)
      } else {
        ElMessage.success('导入成功')
      }
      loadRoles()
      loadStats()
    })
    .catch(error => {
      ElMessage.error('导入失败')
      console.error('导入角色失败:', error)
    })
}

// 工具方法
const getRoleIcon = (category: string) => {
  const iconMap: Record<string, string> = {
    'system': 'icon-system',
    'education': 'icon-education',
    'business': 'icon-business',
    'custom': 'icon-custom'
  }
  return iconMap[category] || 'icon-custom'
}

const getRoleTypeText = (category: string) => {
  const typeMap: Record<string, string> = {
    'system': '系统角色',
    'education': '教育角色',
    'business': '业务角色',
    'custom': '自定义角色'
  }
  return typeMap[category] || '自定义角色'
}

const getStatusText = (isActive: boolean) => {
  return isActive ? '启用' : '禁用'
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

// 组件挂载
onMounted(() => {
  loadRoles()
  loadRoleTemplates()
  loadPermissions()
  loadStats()
})
</script>

<style lang="scss" scoped>
.role-management {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;

  .page-header {
    margin-bottom: 30px;
    
    h1 {
      color: #333;
      margin-bottom: 10px;
      font-size: 28px;
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
    margin-bottom: 30px;
    padding: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    
    .search-section {
      display: flex;
      gap: 15px;
      align-items: center;
      
      .search-box {
        position: relative;
        
        input {
          width: 300px;
          padding: 10px 40px 10px 15px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
          
          &:focus {
            outline: none;
            border-color: #007bff;
          }
        }
        
        .search-btn {
          position: absolute;
          right: 10px;
          top: 50%;
          transform: translateY(-50%);
          background: none;
          border: none;
          color: #666;
          cursor: pointer;
        }
      }
      
      .filter-section {
        display: flex;
        gap: 10px;
        
        select {
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
          
          &:focus {
            outline: none;
            border-color: #007bff;
          }
        }
      }
    }
    
    .action-buttons {
      display: flex;
      gap: 10px;
      
      button {
        padding: 10px 15px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 5px;
        transition: all 0.2s;
        
        &.add-btn {
          background: #28a745;
          color: white;
          
          &:hover {
            background: #1e7e34;
          }
        }
        
        &.refresh-btn {
          background: #6c757d;
          color: white;
          
          &:hover {
            background: #545b62;
          }
        }
      }
    }
  }

  .stats-overview {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 30px;
    
    .stat-card {
      background: white;
      padding: 25px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      display: flex;
      align-items: center;
      gap: 20px;
      
      .stat-icon {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: white;
        
        &:nth-child(1) {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        &:nth-child(2) {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        &:nth-child(3) {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        
        &:nth-child(4) {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
      }
      
      .stat-info {
        .stat-value {
          font-size: 32px;
          font-weight: bold;
          color: #333;
          margin-bottom: 5px;
        }
        
        .stat-label {
          font-size: 14px;
          color: #666;
        }
      }
    }
  }

  .roles-section {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px;
      border-bottom: 1px solid #eee;
      
      h2 {
        color: #333;
        margin: 0;
      }
      
      .view-controls {
        display: flex;
        gap: 5px;
        
        .view-btn {
          padding: 8px 12px;
          border: 1px solid #ddd;
          background: white;
          cursor: pointer;
          font-size: 12px;
          display: flex;
          align-items: center;
          gap: 5px;
          
          &:first-child {
            border-radius: 4px 0 0 4px;
          }
          
          &:last-child {
            border-radius: 0 4px 4px 0;
          }
          
          &.active {
            background: #007bff;
            color: white;
            border-color: #007bff;
          }
        }
      }
    }
    
    .table-view {
      .roles-table {
        width: 100%;
        border-collapse: collapse;
        
        th, td {
          padding: 15px;
          text-align: left;
          border-bottom: 1px solid #eee;
        }
        
        th {
          background: #f8f9fa;
          font-weight: 600;
          color: #333;
          cursor: pointer;
          user-select: none;
          
          &:hover {
            background: #e9ecef;
          }
          
          i {
            margin-left: 5px;
            font-size: 12px;
          }
        }
        
        .role-name {
          display: flex;
          align-items: center;
          gap: 10px;
          
          i {
            font-size: 16px;
            color: #007bff;
          }
        }
        
        .type-badge {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
          
          &.system {
            background: #e3f2fd;
            color: #1976d2;
          }
          
          &.custom {
            background: #f3e5f5;
            color: #7b1fa2;
          }
        }
        
        .status-badge {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
          
          &.active {
            background: #d4edda;
            color: #155724;
          }
          
          &.inactive {
            background: #f8d7da;
            color: #721c24;
          }
        }
        
        .action-buttons {
          display: flex;
          gap: 5px;
          
          .action-btn {
            width: 32px;
            height: 32px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            transition: all 0.2s;
            
            &:disabled {
              opacity: 0.5;
              cursor: not-allowed;
            }
            
            &.view-btn {
              background: #17a2b8;
              color: white;
              
              &:hover:not(:disabled) {
                background: #138496;
              }
            }
            
            &.edit-btn {
              background: #ffc107;
              color: #212529;
              
              &:hover:not(:disabled) {
                background: #e0a800;
              }
            }
            
            &.permission-btn {
              background: #6f42c1;
              color: white;
              
              &:hover:not(:disabled) {
                background: #5a32a3;
              }
            }
            
            &.delete-btn {
              background: #dc3545;
              color: white;
              
              &:hover:not(:disabled) {
                background: #c82333;
              }
            }
          }
        }
      }
    }
    
    .card-view {
      padding: 20px;
      
      .roles-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 20px;
        
        .role-card {
          border: 1px solid #eee;
          border-radius: 8px;
          padding: 20px;
          cursor: pointer;
          transition: all 0.2s;
          
          &:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transform: translateY(-2px);
          }
          
          .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
            
            .role-info {
              display: flex;
              align-items: center;
              gap: 10px;
              
              i {
                font-size: 20px;
                color: #007bff;
              }
              
              h3 {
                margin: 0;
                color: #333;
                font-size: 18px;
              }
              
              .type-badge {
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
                
                &.system {
                  background: #e3f2fd;
                  color: #1976d2;
                }
                
                &.custom {
                  background: #f3e5f5;
                  color: #7b1fa2;
                }
              }
            }
          }
          
          .card-body {
            margin-bottom: 15px;
            
            .role-description {
              color: #666;
              margin-bottom: 15px;
              line-height: 1.5;
            }
            
            .role-stats {
              display: flex;
              gap: 20px;
              
              .stat-item {
                display: flex;
                align-items: center;
                gap: 5px;
                color: #666;
                font-size: 14px;
                
                i {
                  color: #007bff;
                }
              }
            }
          }
          
          .card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            
            .status-badge {
              padding: 4px 8px;
              border-radius: 12px;
              font-size: 12px;
              font-weight: 500;
              
              &.active {
                background: #d4edda;
                color: #155724;
              }
              
              &.inactive {
                background: #f8d7da;
                color: #721c24;
              }
            }
            
            .card-actions {
              display: flex;
              gap: 5px;
              
              .action-btn {
                width: 32px;
                height: 32px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                transition: all 0.2s;
                
                &:disabled {
                  opacity: 0.5;
                  cursor: not-allowed;
                }
                
                &.edit-btn {
                  background: #ffc107;
                  color: #212529;
                  
                  &:hover:not(:disabled) {
                    background: #e0a800;
                  }
                }
                
                &.permission-btn {
                  background: #6f42c1;
                  color: white;
                  
                  &:hover:not(:disabled) {
                    background: #5a32a3;
                  }
                }
                
                &.delete-btn {
                  background: #dc3545;
                  color: white;
                  
                  &:hover:not(:disabled) {
                    background: #c82333;
                  }
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
      padding: 20px;
      border-top: 1px solid #eee;
      
      .pagination-info {
        color: #666;
        font-size: 14px;
      }
      
      .pagination-controls {
        display: flex;
        align-items: center;
        gap: 10px;
        
        .page-btn {
          padding: 8px 12px;
          border: 1px solid #ddd;
          background: white;
          cursor: pointer;
          border-radius: 4px;
          font-size: 14px;
          
          &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
          }
          
          &:hover:not(:disabled) {
            background: #f8f9fa;
          }
        }
        
        .page-numbers {
          display: flex;
          gap: 5px;
          
          .page-number {
            width: 36px;
            height: 36px;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            
            &.active {
              background: #007bff;
              color: white;
              border-color: #007bff;
            }
            
            &:hover:not(.active) {
              background: #f8f9fa;
            }
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
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    
    .modal-content {
      background: white;
      border-radius: 8px;
      width: 90%;
      max-width: 600px;
      max-height: 90vh;
      overflow-y: auto;
      
      &.large {
        max-width: 900px;
      }
      
      .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        border-bottom: 1px solid #eee;
        
        h3 {
          margin: 0;
          color: #333;
        }
        
        .close-btn {
          background: none;
          border: none;
          font-size: 20px;
          cursor: pointer;
          color: #666;
          
          &:hover {
            color: #333;
          }
        }
      }
      
      .modal-body {
        padding: 20px;
        
        .role-form {
          .form-row {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            
            &:last-child {
              margin-bottom: 0;
            }
            
            .form-group {
              flex: 1;
              
              &.full-width {
                flex: none;
                width: 100%;
              }
              
              label {
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                color: #333;
              }
              
              input, select, textarea {
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
              
              textarea {
                resize: vertical;
                min-height: 80px;
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
        
        .permission-management {
          .permission-search {
            margin-bottom: 20px;
            
            input {
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
          }
          
          .permission-categories {
            max-height: 400px;
            overflow-y: auto;
            margin-bottom: 20px;
            
            .permission-category {
              margin-bottom: 25px;
              
              .category-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #007bff;
                
                h4 {
                  margin: 0;
                  color: #333;
                  font-size: 16px;
                }
                
                .category-actions {
                  display: flex;
                  gap: 10px;
                  
                  button {
                    padding: 5px 10px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 12px;
                    
                    &.select-all-btn {
                      background: #28a745;
                      color: white;
                      
                      &:hover {
                        background: #1e7e34;
                      }
                    }
                    
                    &.deselect-all-btn {
                      background: #6c757d;
                      color: white;
                      
                      &:hover {
                        background: #545b62;
                      }
                    }
                  }
                }
              }
              
              .permission-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 10px;
                
                .permission-item {
                  display: flex;
                  align-items: flex-start;
                  gap: 10px;
                  padding: 10px;
                  border: 1px solid #eee;
                  border-radius: 4px;
                  
                  &:hover {
                    background: #f8f9fa;
                  }
                  
                  input[type="checkbox"] {
                    margin-top: 2px;
                  }
                  
                  label {
                    flex: 1;
                    cursor: pointer;
                    
                    .permission-info {
                      .permission-name {
                        display: block;
                        font-weight: 500;
                        color: #333;
                        margin-bottom: 5px;
                      }
                      
                      .permission-description {
                        display: block;
                        font-size: 12px;
                        color: #666;
                        line-height: 1.4;
                      }
                    }
                  }
                }
              }
            }
          }
          
          .permission-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            
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
      }
    }
  }
}

@media (max-width: 768px) {
  .role-management {
    padding: 15px;
  }
  
  .action-bar {
    flex-direction: column;
    align-items: stretch;
    
    .search-section {
      flex-direction: column;
      
      .search-box {
        input {
          width: 100%;
        }
      }
      
      .filter-section {
        justify-content: space-between;
        
        select {
          flex: 1;
        }
      }
    }
  }
  
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .roles-section {
    .section-header {
      flex-direction: column;
      align-items: stretch;
      gap: 15px;
    }
    
    .table-view {
      overflow-x: auto;
      
      .roles-table {
        min-width: 800px;
        font-size: 12px;
        
        th, td {
          padding: 10px;
        }
      }
    }
    
    .card-view {
      .roles-grid {
        grid-template-columns: 1fr;
      }
    }
    
    .pagination {
      flex-direction: column;
      gap: 15px;
      
      .pagination-controls {
        .page-numbers {
          flex-wrap: wrap;
        }
      }
    }
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
    
    .modal-body {
      .role-form {
        .form-row {
          flex-direction: column;
        }
      }
      
      .permission-management {
        .permission-categories {
          .permission-category {
            .category-header {
              flex-direction: column;
              align-items: stretch;
              gap: 10px;
            }
            
            .permission-list {
              grid-template-columns: 1fr;
            }
          }
        }
      }
    }
  }
}
</style>