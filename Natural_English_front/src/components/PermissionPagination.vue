<template>
  <div class="permission-pagination">
    <!-- 权限数据表格 -->
    <div class="permission-table-container">
      <el-table
        :data="paginatedData"
        :loading="loading"
        stripe
        border
        height="400"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="权限名称" min-width="150" />
        <el-table-column prop="code" label="权限代码" min-width="120" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页控件 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 批量操作 -->
    <div class="batch-operations" v-if="selectedItems.length > 0">
      <el-alert
        :title="`已选择 ${selectedItems.length} 项`"
        type="info"
        show-icon
        :closable="false"
      >
        <template #default>
          <div class="batch-buttons">
            <el-button size="small" @click="handleBatchEnable">批量启用</el-button>
            <el-button size="small" @click="handleBatchDisable">批量禁用</el-button>
            <el-button size="small" type="danger" @click="handleBatchDelete">批量删除</el-button>
          </div>
        </template>
      </el-alert>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filters">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input
            v-model="searchQuery"
            placeholder="搜索权限名称或代码"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <Search />
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-select v-model="typeFilter" placeholder="权限类型" clearable @change="handleFilter">
            <el-option label="全部" value="" />
            <el-option label="页面权限" value="page" />
            <el-option label="功能权限" value="function" />
            <el-option label="数据权限" value="data" />
            <el-option label="API权限" value="api" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="statusFilter" placeholder="状态" clearable @change="handleFilter">
            <el-option label="全部" value="" />
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="handleRefresh">刷新</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 性能统计 -->
    <div class="performance-stats" v-if="showStats">
      <el-card>
        <template #header>
          <span>性能统计</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="总数据量" :value="total" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="加载时间" :value="loadTime" suffix="ms" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="内存使用" :value="memoryUsage" suffix="MB" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="缓存命中率" :value="cacheHitRate" suffix="%" />
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
// @ts-ignore
import { onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

// 权限数据接口
interface PermissionItem {
  id: number
  name: string
  code: string
  type: 'page' | 'function' | 'data' | 'api'
  status: 'active' | 'inactive'
  description: string
  createdAt: string
  updatedAt: string
}

// Props
interface Props {
  showStats?: boolean
  enableVirtualScroll?: boolean
  cacheSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  showStats: false,
  enableVirtualScroll: true,
  cacheSize: 1000
})

// 响应式数据
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchQuery = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const selectedItems = ref<PermissionItem[]>([])

// 性能统计
const loadTime = ref(0)
const memoryUsage = ref(0)
const cacheHitRate = ref(0)

// 数据缓存
const dataCache = new Map<string, PermissionItem[]>()
const allData = ref<PermissionItem[]>([])

// 计算属性
const filteredData = computed(() => {
  let data = allData.value
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    data = data.filter(item => 
      item.name.toLowerCase().includes(query) ||
      item.code.toLowerCase().includes(query)
    )
  }
  
  // 类型过滤
  if (typeFilter.value) {
    data = data.filter(item => item.type === typeFilter.value)
  }
  
  // 状态过滤
  if (statusFilter.value) {
    data = data.filter(item => item.status === statusFilter.value)
  }
  
  return data
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

// 方法
const generateMockData = (count: number): PermissionItem[] => {
  const types: PermissionItem['type'][] = ['page', 'function', 'data', 'api']
  const statuses: PermissionItem['status'][] = ['active', 'inactive']
  
  return Array.from({ length: count }, (_, index) => ({
    id: index + 1,
    name: `权限${index + 1}`,
    code: `permission_${index + 1}`,
    type: types[index % types.length],
    status: statuses[index % 2],
    description: `这是权限${index + 1}的描述信息`,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }))
}

const loadData = async () => {
  const startTime = performance.now()
  loading.value = true
  
  try {
    // 检查缓存
    const cacheKey = `${currentPage.value}-${pageSize.value}-${searchQuery.value}-${typeFilter.value}-${statusFilter.value}`
    
    if (dataCache.has(cacheKey)) {
      allData.value = dataCache.get(cacheKey) || []
      cacheHitRate.value = Math.min(100, cacheHitRate.value + 1)
    } else {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // 生成模拟数据
      const mockData = generateMockData(5000)
      allData.value = mockData
      
      // 缓存数据
      if (dataCache.size < props.cacheSize) {
        dataCache.set(cacheKey, mockData)
      }
    }
    
    total.value = filteredData.value.length
    
    // 更新性能统计
    loadTime.value = Math.round(performance.now() - startTime)
    memoryUsage.value = Math.round(JSON.stringify(allData.value).length / 1024 / 1024 * 100) / 100
    
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error('Load data error:', error)
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadData()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadData()
}

const handleSearch = () => {
  currentPage.value = 1
  total.value = filteredData.value.length
}

const handleFilter = () => {
  currentPage.value = 1
  total.value = filteredData.value.length
}

const handleRefresh = () => {
  dataCache.clear()
  cacheHitRate.value = 0
  loadData()
}

const handleSelectionChange = (selection: PermissionItem[]) => {
  selectedItems.value = selection
}

const handleEdit = (row: PermissionItem) => {
  ElMessage.info(`编辑权限: ${row.name}`)
}

const handleDelete = async (row: PermissionItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除权限 "${row.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.success('删除成功')
    loadData()
  } catch {
    // 用户取消删除
  }
}

const handleBatchEnable = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要启用选中的 ${selectedItems.value.length} 个权限吗？`,
      '批量启用',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    ElMessage.success('批量启用成功')
    selectedItems.value = []
    loadData()
  } catch {
    // 用户取消操作
  }
}

const handleBatchDisable = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要禁用选中的 ${selectedItems.value.length} 个权限吗？`,
      '批量禁用',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.success('批量禁用成功')
    selectedItems.value = []
    loadData()
  } catch {
    // 用户取消操作
  }
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedItems.value.length} 个权限吗？此操作不可恢复！`,
      '批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    ElMessage.success('批量删除成功')
    selectedItems.value = []
    loadData()
  } catch {
    // 用户取消操作
  }
}

const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    page: 'primary',
    function: 'success',
    data: 'warning',
    api: 'info'
  }
  return typeMap[type] || 'default'
}

// 监听器
watch([searchQuery, typeFilter, statusFilter], () => {
  handleFilter()
})

// 生命周期
// @ts-ignore
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.permission-pagination {
  padding: 20px;
}

.permission-table-container {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.batch-operations {
  margin: 20px 0;
}

.batch-buttons {
  margin-top: 10px;
}

.batch-buttons .el-button {
  margin-right: 10px;
}

.search-filters {
  margin-bottom: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.performance-stats {
  margin-top: 20px;
}

.el-statistic {
  text-align: center;
}
</style>