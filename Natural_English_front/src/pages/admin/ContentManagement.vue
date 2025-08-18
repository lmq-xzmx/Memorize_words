<template>
  <div class="content-management" v-permission="'admin.content.view'">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>内容管理</h1>
        <p>管理系统中的学习内容和资源</p>
      </div>
      <div class="header-right">
        <button @click="showCreateModal = true" 
                class="btn-primary"
                v-permission="'admin.content.create'">
          <i class="fas fa-plus"></i>
          添加内容
        </button>
      </div>
    </div>

    <!-- 内容类型标签 -->
    <div class="content-tabs">
      <button v-for="tab in contentTabs" 
              :key="tab.key"
              @click="activeTab = tab.key"
              :class="{ active: activeTab === tab.key }"
              class="tab-btn">
        <i :class="tab.icon"></i>
        {{ tab.label }}
        <span class="count">{{ getContentCount(tab.key) }}</span>
      </button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filters">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input type="text" 
               v-model="searchQuery" 
               placeholder="搜索内容标题、描述或标签"
               class="search-input">
      </div>
      
      <div class="filters">
        <select v-model="filters.difficulty" class="filter-select">
          <option value="">所有难度</option>
          <option value="beginner">初级</option>
          <option value="intermediate">中级</option>
          <option value="advanced">高级</option>
        </select>
        
        <select v-model="filters.status" class="filter-select">
          <option value="">所有状态</option>
          <option value="published">已发布</option>
          <option value="draft">草稿</option>
          <option value="archived">已归档</option>
        </select>
        
        <button @click="resetFilters" class="btn-secondary">
          <i class="fas fa-undo"></i>
          重置
        </button>
      </div>
    </div>

    <!-- 内容列表 -->
    <div class="content-list">
      <div class="list-header">
        <div class="list-actions">
          <button @click="selectAll" class="btn-secondary">
            {{ selectedItems.length === filteredContent.length ? '取消全选' : '全选' }}
          </button>
          <button @click="batchDelete" 
                  :disabled="selectedItems.length === 0"
                  class="btn-danger"
                  v-permission="'admin.content.delete'">
            <i class="fas fa-trash"></i>
            批量删除 ({{ selectedItems.length }})
          </button>
          <button @click="batchPublish" 
                  :disabled="selectedItems.length === 0"
                  class="btn-success"
                  v-permission="'admin.content.publish'">
            <i class="fas fa-globe"></i>
            批量发布 ({{ selectedItems.length }})
          </button>
        </div>
        
        <div class="list-info">
          共 {{ filteredContent.length }} 个内容
        </div>
      </div>
      
      <div class="content-grid">
        <div v-for="item in paginatedContent" 
             :key="item.id" 
             class="content-card">
          <div class="card-header">
            <input type="checkbox" 
                   :value="item.id" 
                   v-model="selectedItems"
                   class="card-checkbox">
            <span :class="`status-badge status-${item.status}`">
              {{ getStatusLabel(item.status) }}
            </span>
          </div>
          
          <div class="card-content">
            <div class="content-thumbnail">
              <img v-if="item.thumbnail" 
                   :src="item.thumbnail" 
                   :alt="item.title" 
                   class="thumbnail-image">
              <div v-else class="thumbnail-placeholder">
                <i :class="getContentIcon(item.type)"></i>
              </div>
            </div>
            
            <div class="content-info">
              <h3 class="content-title">{{ item.title }}</h3>
              <p class="content-description">{{ item.description }}</p>
              
              <div class="content-meta">
                <span class="meta-item">
                  <i class="fas fa-layer-group"></i>
                  {{ getDifficultyLabel(item.difficulty) }}
                </span>
                <span class="meta-item">
                  <i class="fas fa-eye"></i>
                  {{ item.views || 0 }} 浏览
                </span>
                <span class="meta-item">
                  <i class="fas fa-calendar"></i>
                  {{ formatDate(item.createdAt) }}
                </span>
              </div>
              
              <div class="content-tags" v-if="item.tags && item.tags.length">
                <span v-for="tag in item.tags.slice(0, 3)" 
                      :key="tag" 
                      class="tag">
                  {{ tag }}
                </span>
                <span v-if="item.tags.length > 3" class="tag-more">
                  +{{ item.tags.length - 3 }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="card-actions">
            <button @click="viewContent(item)" 
                    class="btn-icon" 
                    title="预览">
              <i class="fas fa-eye"></i>
            </button>
            <button @click="editContent(item)" 
                    class="btn-icon" 
                    title="编辑"
                    v-permission="'admin.content.edit'">
              <i class="fas fa-edit"></i>
            </button>
            <button @click="duplicateContent(item)" 
                    class="btn-icon" 
                    title="复制"
                    v-permission="'admin.content.create'">
              <i class="fas fa-copy"></i>
            </button>
            <button @click="toggleStatus(item)" 
                    class="btn-icon" 
                    :title="item.status === 'published' ? '取消发布' : '发布'"
                    v-permission="'admin.content.publish'">
              <i :class="item.status === 'published' ? 'fas fa-eye-slash' : 'fas fa-globe'"></i>
            </button>
            <button @click="deleteContent(item)" 
                    class="btn-icon btn-danger" 
                    title="删除"
                    v-permission="'admin.content.delete'">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
      
      <!-- 分页 -->
      <div class="pagination" v-if="totalPages > 1">
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

    <!-- 创建/编辑内容弹窗 -->
    <div class="modal" v-if="showCreateModal || showEditModal" @click="closeModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>{{ showCreateModal ? '添加内容' : '编辑内容' }}</h3>
          <button @click="closeModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveContent">
            <div class="form-row">
              <div class="form-group">
                <label for="title">标题 *</label>
                <input type="text" 
                       id="title" 
                       v-model="contentForm.title" 
                       class="form-input"
                       placeholder="请输入内容标题"
                       required>
              </div>
              <div class="form-group">
                <label for="type">类型 *</label>
                <select id="type" v-model="contentForm.type" class="form-select" required>
                  <option value="word">单词</option>
                  <option value="sentence">句子</option>
                  <option value="grammar">语法</option>
                  <option value="listening">听力</option>
                  <option value="reading">阅读</option>
                </select>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="difficulty">难度 *</label>
                <select id="difficulty" v-model="contentForm.difficulty" class="form-select" required>
                  <option value="beginner">初级</option>
                  <option value="intermediate">中级</option>
                  <option value="advanced">高级</option>
                </select>
              </div>
              <div class="form-group">
                <label for="status">状态 *</label>
                <select id="status" v-model="contentForm.status" class="form-select" required>
                  <option value="draft">草稿</option>
                  <option value="published">已发布</option>
                  <option value="archived">已归档</option>
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label for="description">描述</label>
              <textarea id="description" 
                        v-model="contentForm.description" 
                        class="form-textarea"
                        placeholder="请输入内容描述"
                        rows="3">
              </textarea>
            </div>
            
            <div class="form-group">
              <label for="content">内容 *</label>
              <textarea id="content" 
                        v-model="contentForm.content" 
                        class="form-textarea"
                        placeholder="请输入具体内容"
                        rows="8"
                        required>
              </textarea>
            </div>
            
            <div class="form-group">
              <label for="tags">标签</label>
              <input type="text" 
                     id="tags" 
                     v-model="contentForm.tagsInput" 
                     class="form-input"
                     placeholder="请输入标签，用逗号分隔">
              <div class="tags-preview" v-if="contentForm.tags && contentForm.tags.length">
                <span v-for="tag in contentForm.tags" :key="tag" class="tag">
                  {{ tag }}
                  <button type="button" @click="removeTag(tag)" class="tag-remove">
                    <i class="fas fa-times"></i>
                  </button>
                </span>
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

    <!-- 内容预览弹窗 -->
    <div class="modal" v-if="showPreviewModal" @click="showPreviewModal = false">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>内容预览</h3>
          <button @click="showPreviewModal = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body" v-if="selectedContent">
          <div class="preview-content">
            <div class="preview-header">
              <h2>{{ selectedContent.title }}</h2>
              <div class="preview-meta">
                <span class="meta-item">
                  <i class="fas fa-layer-group"></i>
                  {{ getDifficultyLabel(selectedContent.difficulty) }}
                </span>
                <span class="meta-item">
                  <i class="fas fa-calendar"></i>
                  {{ formatDate(selectedContent.createdAt) }}
                </span>
                <span :class="`status-badge status-${selectedContent.status}`">
                  {{ getStatusLabel(selectedContent.status) }}
                </span>
              </div>
            </div>
            
            <div class="preview-description" v-if="selectedContent.description">
              <h4>描述</h4>
              <p>{{ selectedContent.description }}</p>
            </div>
            
            <div class="preview-body">
              <h4>内容</h4>
              <div class="content-body" v-html="formatContent(selectedContent.content)"></div>
            </div>
            
            <div class="preview-tags" v-if="selectedContent.tags && selectedContent.tags.length">
              <h4>标签</h4>
              <div class="tags-list">
                <span v-for="tag in selectedContent.tags" :key="tag" class="tag">
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'

// 接口定义
interface ContentItem {
  id: number
  title: string
  description?: string
  content: string
  type: 'word' | 'sentence' | 'grammar' | 'listening' | 'reading'
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  status: 'draft' | 'published' | 'archived'
  thumbnail?: string
  tags?: string[]
  views?: number
  createdAt: string
  updatedAt: string
  authorId: number
}

// 响应式数据
const activeTab = ref('all')
const searchQuery = ref('')
const selectedItems = ref<number[]>([])
const currentPage = ref(1)
const pageSize = ref(12)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showPreviewModal = ref(false)
const selectedContent = ref<ContentItem | null>(null)

const filters = reactive({
  difficulty: '',
  status: ''
})

const contentForm = reactive({
  id: null as number | null,
  title: '',
  description: '',
  content: '',
  type: 'word' as ContentItem['type'],
  difficulty: 'beginner' as ContentItem['difficulty'],
  status: 'draft' as ContentItem['status'],
  tags: [] as string[],
  tagsInput: ''
})

// 内容类型标签
const contentTabs = [
  { key: 'all', label: '全部', icon: 'fas fa-list' },
  { key: 'word', label: '单词', icon: 'fas fa-font' },
  { key: 'sentence', label: '句子', icon: 'fas fa-quote-left' },
  { key: 'grammar', label: '语法', icon: 'fas fa-book' },
  { key: 'listening', label: '听力', icon: 'fas fa-headphones' },
  { key: 'reading', label: '阅读', icon: 'fas fa-book-open' }
]

// 模拟内容数据
const contentItems = ref<ContentItem[]>([
  {
    id: 1,
    title: 'Apple - 苹果',
    description: '常见水果单词学习',
    content: 'Apple /ˈæpəl/ n. 苹果\n例句：I eat an apple every day.',
    type: 'word',
    difficulty: 'beginner',
    status: 'published',
    tags: ['水果', '名词', '日常用语'],
    views: 1250,
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-20T15:45:00Z',
    authorId: 1
  },
  {
    id: 2,
    title: '现在进行时',
    description: '英语现在进行时语法规则',
    content: '现在进行时表示正在进行的动作\n结构：be + doing\n例句：I am reading a book.',
    type: 'grammar',
    difficulty: 'intermediate',
    status: 'published',
    tags: ['语法', '时态', '进行时'],
    views: 890,
    createdAt: '2024-01-10T09:20:00Z',
    updatedAt: '2024-01-19T14:30:00Z',
    authorId: 2
  },
  {
    id: 3,
    title: '日常对话练习',
    description: '基础日常对话听力练习',
    content: '听力材料：购物对话\n难度：初级\n时长：3分钟',
    type: 'listening',
    difficulty: 'beginner',
    status: 'draft',
    tags: ['对话', '购物', '日常'],
    views: 0,
    createdAt: '2024-01-20T16:00:00Z',
    updatedAt: '2024-01-20T16:00:00Z',
    authorId: 1
  }
])

// 计算属性
const filteredContent = computed(() => {
  return contentItems.value.filter(item => {
    const matchesTab = activeTab.value === 'all' || item.type === activeTab.value
    const matchesSearch = !searchQuery.value || 
      item.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (item.description && item.description.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
      (item.tags && item.tags.some(tag => tag.toLowerCase().includes(searchQuery.value.toLowerCase())))
    
    const matchesDifficulty = !filters.difficulty || item.difficulty === filters.difficulty
    const matchesStatus = !filters.status || item.status === filters.status
    
    return matchesTab && matchesSearch && matchesDifficulty && matchesStatus
  })
})

const totalPages = computed(() => {
  return Math.ceil(filteredContent.value.length / pageSize.value)
})

const paginatedContent = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredContent.value.slice(start, end)
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

// 监听标签输入
watch(() => contentForm.tagsInput, (newValue) => {
  if (newValue) {
    contentForm.tags = newValue.split(',').map(tag => tag.trim()).filter(tag => tag)
  } else {
    contentForm.tags = []
  }
})

// 方法
const getContentCount = (type: string) => {
  if (type === 'all') return contentItems.value.length
  return contentItems.value.filter(item => item.type === type).length
}

const getContentIcon = (type: string) => {
  const icons = {
    word: 'fas fa-font',
    sentence: 'fas fa-quote-left',
    grammar: 'fas fa-book',
    listening: 'fas fa-headphones',
    reading: 'fas fa-book-open'
  }
  return icons[type as keyof typeof icons] || 'fas fa-file'
}

const getDifficultyLabel = (difficulty: string) => {
  const labels = {
    beginner: '初级',
    intermediate: '中级',
    advanced: '高级'
  }
  return labels[difficulty as keyof typeof labels] || difficulty
}

const getStatusLabel = (status: string) => {
  const labels = {
    draft: '草稿',
    published: '已发布',
    archived: '已归档'
  }
  return labels[status as keyof typeof labels] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatContent = (content: string) => {
  return content.replace(/\n/g, '<br>')
}

const selectAll = () => {
  if (selectedItems.value.length === filteredContent.value.length) {
    selectedItems.value = []
  } else {
    selectedItems.value = filteredContent.value.map(item => item.id)
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  filters.difficulty = ''
  filters.status = ''
  currentPage.value = 1
}

const viewContent = (item: ContentItem) => {
  selectedContent.value = item
  showPreviewModal.value = true
}

const editContent = (item: ContentItem) => {
  Object.assign(contentForm, {
    id: item.id,
    title: item.title,
    description: item.description || '',
    content: item.content,
    type: item.type,
    difficulty: item.difficulty,
    status: item.status,
    tags: item.tags || [],
    tagsInput: item.tags ? item.tags.join(', ') : ''
  })
  showEditModal.value = true
}

const duplicateContent = (item: ContentItem) => {
  Object.assign(contentForm, {
    id: null,
    title: `${item.title} (副本)`,
    description: item.description || '',
    content: item.content,
    type: item.type,
    difficulty: item.difficulty,
    status: 'draft',
    tags: item.tags || [],
    tagsInput: item.tags ? item.tags.join(', ') : ''
  })
  showCreateModal.value = true
}

const deleteContent = (item: ContentItem) => {
  if (confirm(`确定要删除内容 "${item.title}" 吗？`)) {
    const index = contentItems.value.findIndex(c => c.id === item.id)
    if (index > -1) {
      contentItems.value.splice(index, 1)
    }
  }
}

const batchDelete = () => {
  if (confirm(`确定要删除选中的 ${selectedItems.value.length} 个内容吗？`)) {
    contentItems.value = contentItems.value.filter(item => !selectedItems.value.includes(item.id))
    selectedItems.value = []
  }
}

const toggleStatus = (item: ContentItem) => {
  const newStatus = item.status === 'published' ? 'draft' : 'published'
  const action = newStatus === 'published' ? '发布' : '取消发布'
  
  if (confirm(`确定要${action}内容 "${item.title}" 吗？`)) {
    item.status = newStatus
    item.updatedAt = new Date().toISOString()
  }
}

const batchPublish = () => {
  if (confirm(`确定要发布选中的 ${selectedItems.value.length} 个内容吗？`)) {
    selectedItems.value.forEach(id => {
      const item = contentItems.value.find(c => c.id === id)
      if (item) {
        item.status = 'published'
        item.updatedAt = new Date().toISOString()
      }
    })
    selectedItems.value = []
  }
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  resetContentForm()
}

const resetContentForm = () => {
  Object.assign(contentForm, {
    id: null,
    title: '',
    description: '',
    content: '',
    type: 'word',
    difficulty: 'beginner',
    status: 'draft',
    tags: [],
    tagsInput: ''
  })
}

const removeTag = (tag: string) => {
  const index = contentForm.tags.indexOf(tag)
  if (index > -1) {
    contentForm.tags.splice(index, 1)
    contentForm.tagsInput = contentForm.tags.join(', ')
  }
}

const saveContent = () => {
  if (showCreateModal.value) {
    const newContent: ContentItem = {
      id: Date.now(),
      title: contentForm.title,
      description: contentForm.description || undefined,
      content: contentForm.content,
      type: contentForm.type,
      difficulty: contentForm.difficulty,
      status: contentForm.status,
      tags: contentForm.tags.length ? contentForm.tags : undefined,
      views: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      authorId: 1
    }
    
    contentItems.value.push(newContent)
  } else if (showEditModal.value && contentForm.id) {
    const item = contentItems.value.find(c => c.id === contentForm.id)
    if (item) {
      item.title = contentForm.title
      item.description = contentForm.description || undefined
      item.content = contentForm.content
      item.type = contentForm.type
      item.difficulty = contentForm.difficulty
      item.status = contentForm.status
      item.tags = contentForm.tags.length ? contentForm.tags : undefined
      item.updatedAt = new Date().toISOString()
    }
  }
  
  closeModal()
}
</script>

<style scoped lang="scss">
.content-management {
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

.content-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #3498db;
  }
  
  &.active {
    background: #3498db;
    color: white;
    border-color: #3498db;
  }
  
  .count {
    background: rgba(255, 255, 255, 0.2);
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 12px;
    min-width: 20px;
    text-align: center;
  }
  
  &.active .count {
    background: rgba(255, 255, 255, 0.3);
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

.content-list {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  
  .list-actions {
    display: flex;
    gap: 12px;
  }
  
  .list-info {
    color: #7f8c8d;
    font-size: 14px;
  }
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  padding: 20px;
}

.content-card {
  border: 1px solid #e9ecef;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.card-checkbox {
  width: 16px;
  height: 16px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  
  &.status-published {
    background: #e8f5e8;
    color: #2e7d32;
  }
  
  &.status-draft {
    background: #fff3e0;
    color: #f57c00;
  }
  
  &.status-archived {
    background: #f5f5f5;
    color: #616161;
  }
}

.card-content {
  padding: 16px;
}

.content-thumbnail {
  width: 100%;
  height: 120px;
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
  
  .thumbnail-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .thumbnail-placeholder {
    width: 100%;
    height: 100%;
    background: #f8f9fa;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #7f8c8d;
    font-size: 24px;
  }
}

.content-info {
  .content-title {
    color: #2c3e50;
    margin-bottom: 8px;
    font-size: 16px;
    font-weight: 600;
    line-height: 1.4;
  }
  
  .content-description {
    color: #7f8c8d;
    font-size: 14px;
    line-height: 1.4;
    margin-bottom: 12px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

.content-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
  
  .meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
    color: #7f8c8d;
    font-size: 12px;
    
    i {
      width: 12px;
    }
  }
}

.content-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  
  .tag {
    background: #e3f2fd;
    color: #1976d2;
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 500;
  }
  
  .tag-more {
    background: #f5f5f5;
    color: #7f8c8d;
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 11px;
  }
}

.card-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

.btn-icon {
  width: 32px;
  height: 32px;
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

.btn-primary, .btn-secondary, .btn-danger, .btn-success {
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

.btn-success {
  background: #27ae60;
  color: white;
  
  &:hover:not(:disabled) {
    background: #229954;
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

.form-input, .form-select, .form-textarea {
  padding: 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #3498db;
  }
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.tags-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
  
  .tag {
    background: #e3f2fd;
    color: #1976d2;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 4px;
    
    .tag-remove {
      background: none;
      border: none;
      color: inherit;
      cursor: pointer;
      padding: 0;
      width: 14px;
      height: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      
      &:hover {
        background: rgba(255, 255, 255, 0.3);
      }
    }
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.preview-content {
  .preview-header {
    margin-bottom: 24px;
    
    h2 {
      color: #2c3e50;
      margin-bottom: 12px;
    }
    
    .preview-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      
      .meta-item {
        display: flex;
        align-items: center;
        gap: 4px;
        color: #7f8c8d;
        font-size: 14px;
      }
    }
  }
  
  .preview-description, .preview-body, .preview-tags {
    margin-bottom: 24px;
    
    h4 {
      color: #2c3e50;
      margin-bottom: 12px;
      font-size: 16px;
    }
    
    p {
      color: #7f8c8d;
      line-height: 1.6;
    }
  }
  
  .content-body {
    background: #f8f9fa;
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid #3498db;
    line-height: 1.6;
    white-space: pre-wrap;
  }
  
  .tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    
    .tag {
      background: #e3f2fd;
      color: #1976d2;
      padding: 4px 8px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
    }
  }
}

@media (max-width: 768px) {
  .content-management {
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
  
  .content-tabs {
    justify-content: center;
  }
  
  .list-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
    
    .list-actions {
      justify-content: center;
    }
  }
  
  .content-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>