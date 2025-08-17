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
import { resourceAuthAPI } from '../utils/api'

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

