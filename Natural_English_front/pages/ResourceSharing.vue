<template>
  <div class="resource-sharing">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>资源分享</h1>
      <p class="subtitle">分享您的学习资源，与他人协作学习</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <button @click="showShareModal = true" class="btn btn-primary">
        <span class="icon">📤</span>
        分享资源
      </button>
      <div class="search-box">
        <input 
          v-model="searchQuery"
          @input="handleSearch"
          placeholder="搜索分享记录..."
          class="search-input"
        >
        <span class="search-icon">🔍</span>
      </div>
    </div>

    <!-- 分享统计 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-number">{{ stats.totalShares }}</div>
        <div class="stat-label">总分享数</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ stats.activeShares }}</div>
        <div class="stat-label">有效分享</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ stats.totalViews }}</div>
        <div class="stat-label">总访问量</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ stats.totalDownloads }}</div>
        <div class="stat-label">总下载量</div>
      </div>
    </div>

    <!-- 分享列表 -->
    <div class="shares-section">
      <div class="section-header">
        <h3>我的分享</h3>
        <div class="filter-tabs">
          <button 
            v-for="filter in filterOptions"
            :key="filter.value"
            @click="currentFilter = filter.value"
            class="filter-tab"
            :class="{ active: currentFilter === filter.value }"
          >
            {{ filter.label }}
          </button>
        </div>
      </div>
      
      <div class="shares-list">
        <div 
          v-for="share in filteredShares"
          :key="share.id"
          class="share-card"
        >
          <div class="share-info">
            <div class="share-header">
              <h4 class="share-title">{{ share.resource_name }}</h4>
              <div class="share-status" :class="share.status">
                {{ getStatusText(share.status) }}
              </div>
            </div>
            <div class="share-meta">
              <span class="share-type">{{ share.resource_type }}</span>
              <span class="share-date">分享于 {{ formatDate(share.created_at) }}</span>
              <span v-if="share.expires_at" class="share-expiry">
                到期时间: {{ formatDate(share.expires_at) }}
              </span>
            </div>
            <div class="share-description" v-if="share.description">
              {{ share.description }}
            </div>
            <div class="share-stats">
              <span class="stat-item">
                <span class="icon">👁️</span>
                {{ share.view_count }} 次查看
              </span>
              <span class="stat-item">
                <span class="icon">⬇️</span>
                {{ share.download_count }} 次下载
              </span>
              <span v-if="share.access_count" class="stat-item">
                <span class="icon">🔗</span>
                {{ share.access_count }} 次访问
              </span>
            </div>
          </div>
          <div class="share-actions">
            <button 
              @click="copyShareLink(share)"
              class="btn btn-sm btn-outline"
              title="复制分享链接"
            >
              📋 复制链接
            </button>
            <button 
              @click="viewShareDetails(share)"
              class="btn btn-sm btn-outline"
              title="查看详情"
            >
              📊 详情
            </button>
            <button 
              v-if="share.status === 'active'"
              @click="revokeShare(share)"
              class="btn btn-sm btn-danger"
              title="撤销分享"
            >
              🚫 撤销
            </button>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="filteredShares.length === 0" class="empty-state">
        <div class="empty-icon">📤</div>
        <div class="empty-text">
          <h3>暂无分享记录</h3>
          <p>开始分享您的学习资源，与他人协作学习吧！</p>
        </div>
        <button @click="showShareModal = true" class="btn btn-primary">
          立即分享
        </button>
      </div>
    </div>

    <!-- 分享资源模态框 -->
    <div v-if="showShareModal" class="modal-overlay" @click="showShareModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>分享资源</h3>
          <button @click="showShareModal = false" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitShare">
            <div class="form-group">
              <label>资源类型</label>
              <select v-model="shareForm.resourceType" class="form-control" required>
                <option value="">请选择资源类型</option>
                <option value="vocabulary">词汇表</option>
                <option value="lesson">课程内容</option>
                <option value="exercise">练习题</option>
                <option value="document">文档资料</option>
                <option value="other">其他</option>
              </select>
            </div>
            <div class="form-group">
              <label>资源ID</label>
              <input 
                v-model="shareForm.resourceId"
                type="text"
                class="form-control"
                placeholder="输入要分享的资源ID"
                required
              >
            </div>
            <div class="form-group">
              <label>分享标题</label>
              <input 
                v-model="shareForm.title"
                type="text"
                class="form-control"
                placeholder="为您的分享起个标题"
                required
              >
            </div>
            <div class="form-group">
              <label>分享描述</label>
              <textarea 
                v-model="shareForm.description"
                class="form-control"
                rows="3"
                placeholder="描述一下您分享的内容..."
              ></textarea>
            </div>
            <div class="form-group">
              <label>访问权限</label>
              <div class="radio-group">
                <label class="radio-option">
                  <input 
                    v-model="shareForm.accessType"
                    type="radio"
                    value="public"
                  >
                  <span>公开访问</span>
                </label>
                <label class="radio-option">
                  <input 
                    v-model="shareForm.accessType"
                    type="radio"
                    value="link"
                  >
                  <span>仅限链接访问</span>
                </label>
                <label class="radio-option">
                  <input 
                    v-model="shareForm.accessType"
                    type="radio"
                    value="private"
                  >
                  <span>私有分享</span>
                </label>
              </div>
            </div>
            <div class="form-group">
              <label>有效期</label>
              <select v-model="shareForm.expiryDays" class="form-control">
                <option value="">永久有效</option>
                <option value="1">1天</option>
                <option value="7">7天</option>
                <option value="30">30天</option>
                <option value="90">90天</option>
              </select>
            </div>
            <div class="form-group">
              <label class="checkbox-option">
                <input 
                  v-model="shareForm.allowDownload"
                  type="checkbox"
                >
                <span>允许下载</span>
              </label>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button @click="showShareModal = false" class="btn btn-outline">取消</button>
          <button @click="submitShare" class="btn btn-primary" :disabled="loading">
            {{ loading ? '分享中...' : '确认分享' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 分享详情模态框 -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="showDetailsModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>分享详情</h3>
          <button @click="showDetailsModal = false" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedShare" class="share-details">
            <div class="detail-group">
              <label>分享链接</label>
              <div class="link-display">
                <input 
                  :value="selectedShare.share_link"
                  readonly
                  class="form-control"
                >
                <button 
                  @click="copyToClipboard(selectedShare.share_link)"
                  class="btn btn-sm btn-outline"
                >
                  复制
                </button>
              </div>
            </div>
            <div class="detail-group">
              <label>访问统计</label>
              <div class="stats-display">
                <div class="stat-item">
                  <span class="label">总访问量:</span>
                  <span class="value">{{ selectedShare.view_count }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">下载次数:</span>
                  <span class="value">{{ selectedShare.download_count }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">最后访问:</span>
                  <span class="value">{{ formatDate(selectedShare.last_accessed) }}</span>
                </div>
              </div>
            </div>
            <div class="detail-group">
              <label>分享设置</label>
              <div class="settings-display">
                <div class="setting-item">
                  <span class="label">访问权限:</span>
                  <span class="value">{{ getAccessTypeText(selectedShare.access_type) }}</span>
                </div>
                <div class="setting-item">
                  <span class="label">允许下载:</span>
                  <span class="value">{{ selectedShare.allow_download ? '是' : '否' }}</span>
                </div>
                <div class="setting-item">
                  <span class="label">有效期:</span>
                  <span class="value">
                    {{ selectedShare.expires_at ? formatDate(selectedShare.expires_at) : '永久有效' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showDetailsModal = false" class="btn btn-outline">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { resourceAuthAPI } from '../utils/api.js'

export default {
  name: 'ResourceSharing',
  data() {
    return {
      loading: false,
      showShareModal: false,
      showDetailsModal: false,
      searchQuery: '',
      currentFilter: 'all',
      selectedShare: null,
      shares: [],
      stats: {
        totalShares: 0,
        activeShares: 0,
        totalViews: 0,
        totalDownloads: 0
      },
      shareForm: {
        resourceType: '',
        resourceId: '',
        title: '',
        description: '',
        accessType: 'link',
        expiryDays: '',
        allowDownload: true
      },
      filterOptions: [
        { label: '全部', value: 'all' },
        { label: '有效', value: 'active' },
        { label: '已过期', value: 'expired' },
        { label: '已撤销', value: 'revoked' }
      ]
    }
  },
  computed: {
    filteredShares() {
      let filtered = this.shares
      
      // 状态过滤
      if (this.currentFilter !== 'all') {
        filtered = filtered.filter(share => share.status === this.currentFilter)
      }
      
      // 搜索过滤
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(share => 
          share.resource_name.toLowerCase().includes(query) ||
          share.description?.toLowerCase().includes(query)
        )
      }
      
      return filtered
    }
  },
  async mounted() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        const [sharesData, statsData] = await Promise.all([
          resourceAuthAPI.getResourceShares(),
          resourceAuthAPI.getAuthorizationStats()
        ])
        
        this.shares = sharesData.data || []
        this.stats = {
          totalShares: this.shares.length,
          activeShares: this.shares.filter(s => s.status === 'active').length,
          totalViews: this.shares.reduce((sum, s) => sum + (s.view_count || 0), 0),
          totalDownloads: this.shares.reduce((sum, s) => sum + (s.download_count || 0), 0)
        }
      } catch (error) {
        console.error('加载分享数据失败:', error)
        this.$message?.error('加载数据失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    async submitShare() {
      this.loading = true
      try {
        const shareData = {
          title: this.shareForm.title,
          description: this.shareForm.description,
          access_type: this.shareForm.accessType,
          allow_download: this.shareForm.allowDownload
        }
        
        if (this.shareForm.expiryDays) {
          const expiryDate = new Date()
          expiryDate.setDate(expiryDate.getDate() + parseInt(this.shareForm.expiryDays))
          shareData.expires_at = expiryDate.toISOString()
        }
        
        await resourceAuthAPI.shareResource(this.shareForm.resourceId, shareData)
        this.$message?.success('资源分享成功！')
        this.showShareModal = false
        this.resetShareForm()
        await this.loadData()
      } catch (error) {
        console.error('分享失败:', error)
        this.$message?.error('分享失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    async revokeShare(share) {
      if (!confirm('确定要撤销这个分享吗？撤销后链接将失效。')) {
        return
      }
      
      try {
        await resourceAuthAPI.revokeResourceShare(share.id)
        this.$message?.success('分享已撤销')
        await this.loadData()
      } catch (error) {
        console.error('撤销分享失败:', error)
        this.$message?.error('撤销失败，请稍后重试')
      }
    },
    
    async copyShareLink(share) {
      try {
        const linkData = await resourceAuthAPI.getShareLink(share.id)
        await this.copyToClipboard(linkData.data.link)
        this.$message?.success('分享链接已复制到剪贴板')
      } catch (error) {
        console.error('获取分享链接失败:', error)
        this.$message?.error('获取链接失败')
      }
    },
    
    async copyToClipboard(text) {
      try {
        await navigator.clipboard.writeText(text)
      } catch (error) {
        // 降级方案
        const textArea = document.createElement('textarea')
        textArea.value = text
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)
      }
    },
    
    viewShareDetails(share) {
      this.selectedShare = share
      this.showDetailsModal = true
    },
    
    handleSearch() {
      // 搜索逻辑在computed中处理
    },
    
    resetShareForm() {
      this.shareForm = {
        resourceType: '',
        resourceId: '',
        title: '',
        description: '',
        accessType: 'link',
        expiryDays: '',
        allowDownload: true
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('zh-CN')
    },
    
    getStatusText(status) {
      const statusMap = {
        'active': '有效',
        'expired': '已过期',
        'revoked': '已撤销',
        'pending': '待激活'
      }
      return statusMap[status] || status
    },
    
    getAccessTypeText(accessType) {
      const typeMap = {
        'public': '公开访问',
        'link': '仅限链接',
        'private': '私有分享'
      }
      return typeMap[accessType] || accessType
    }
  }
}
</script>

<style scoped>
.resource-sharing {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  color: #666;
  font-size: 16px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  gap: 20px;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 300px;
}

.search-input {
  width: 100%;
  padding: 8px 40px 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 8px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.shares-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.filter-tab:hover {
  border-color: #667eea;
}

.filter-tab.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.shares-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.share-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  transition: all 0.3s ease;
}

.share-card:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
}

.share-info {
  flex: 1;
}

.share-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.share-title {
  font-size: 16px;
  color: #333;
  margin: 0;
}

.share-status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.share-status.active {
  background: #e8f5e8;
  color: #4caf50;
}

.share-status.expired {
  background: #ffebee;
  color: #f44336;
}

.share-status.revoked {
  background: #f3e5f5;
  color: #9c27b0;
}

.share-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.share-description {
  color: #666;
  font-size: 14px;
  margin-bottom: 12px;
  line-height: 1.4;
}

.share-stats {
  display: flex;
  gap: 16px;
  font-size: 14px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
}

.share-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-text h3 {
  color: #333;
  margin-bottom: 8px;
}

.empty-text p {
  color: #666;
  margin-bottom: 24px;
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5a6fd8;
}

.btn-outline {
  background: transparent;
  border: 1px solid #667eea;
  color: #667eea;
}

.btn-outline:hover {
  background: #667eea;
  color: white;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-danger:hover {
  background: #d32f2f;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 表单样式 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.radio-group {
  display: flex;
  gap: 16px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.checkbox-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

/* 模态框样式 */
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
}

.modal {
  background: white;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px 20px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  padding: 0 20px 20px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

/* 详情显示样式 */
.detail-group {
  margin-bottom: 20px;
}

.detail-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.link-display {
  display: flex;
  gap: 8px;
}

.link-display input {
  flex: 1;
}

.stats-display,
.settings-display {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item,
.setting-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item:last-child,
.setting-item:last-child {
  border-bottom: none;
}

.label {
  color: #666;
  font-size: 14px;
}

.value {
  color: #333;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .resource-sharing {
    padding: 15px;
  }
  
  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: none;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .filter-tabs {
    justify-content: center;
  }
  
  .share-card {
    flex-direction: column;
    gap: 16px;
  }
  
  .share-actions {
    justify-content: flex-start;
  }
  
  .radio-group {
    flex-direction: column;
  }
}
</style>