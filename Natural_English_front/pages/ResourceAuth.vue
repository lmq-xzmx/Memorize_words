<template>
  <div class="resource-auth">
    <div class="header">
      <h1>资源授权管理</h1>
      <p>管理您的资源访问权限和订阅状态</p>
    </div>
    
    <div class="content">
      <!-- 订阅状态卡片 -->
      <div class="subscription-card">
        <div class="card-header">
          <h2>我的订阅</h2>
          <button @click="refreshSubscription" class="refresh-btn">刷新</button>
        </div>
        <div class="subscription-info">
          <div v-if="subscription" class="subscription-active">
            <div class="subscription-type">
              <span class="type-badge" :class="subscription.feature_name">{{ subscription.feature_name }}</span>
              <span class="status" :class="subscription.is_active ? 'active' : 'inactive'">
                {{ subscription.is_active ? '激活' : '已过期' }}
              </span>
            </div>
            <div class="subscription-details">
              <p><strong>开始时间：</strong>{{ formatDate(subscription.start_date) }}</p>
              <p><strong>结束时间：</strong>{{ formatDate(subscription.end_date) }}</p>
              <p v-if="subscription.auto_renew" class="auto-renew">✓ 自动续费已开启</p>
            </div>
          </div>
          <div v-else class="no-subscription">
            <p>您还没有激活任何订阅</p>
            <button @click="showUpgradeModal = true" class="upgrade-btn">立即订阅</button>
          </div>
        </div>
      </div>

      <!-- 资源授权列表 -->
      <div class="authorization-section">
        <div class="section-header">
          <h2>我的资源权限</h2>
          <div class="filters">
            <select v-model="selectedCategory" @change="loadAuthorizations">
              <option value="">所有分类</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
            <select v-model="selectedAccessLevel" @change="loadAuthorizations">
              <option value="">所有权限</option>
              <option value="read">只读</option>
              <option value="write">读写</option>
              <option value="admin">管理员</option>
            </select>
          </div>
        </div>
        
        <div class="authorization-list">
          <div v-if="authorizations.length === 0" class="empty-state">
            <p>暂无资源权限记录</p>
          </div>
          <div v-else>
            <div v-for="auth in authorizations" :key="auth.id" class="auth-item">
              <div class="auth-info">
                <div class="resource-type">
                  <span class="type-icon">{{ getResourceIcon(auth.resource_type) }}</span>
                  <span class="type-name">{{ auth.resource_type }}</span>
                </div>
                <div class="resource-details">
                  <p class="resource-id">资源ID: {{ auth.resource_id }}</p>
                  <p class="access-level">
                    权限级别: 
                    <span class="level-badge" :class="auth.access_level">{{ auth.access_level }}</span>
                  </p>
                </div>
              </div>
              <div class="auth-status">
                <span class="status-badge" :class="auth.is_active ? 'active' : 'inactive'">
                  {{ auth.is_active ? '激活' : '停用' }}
                </span>
                <span v-if="auth.is_public" class="public-badge">公开</span>
                <span v-if="auth.requires_subscription" class="subscription-required">需订阅</span>
              </div>
              <div class="auth-actions">
                <button @click="viewResourceDetails(auth)" class="view-btn">查看详情</button>
                <button v-if="auth.access_level === 'admin'" @click="manageResource(auth)" class="manage-btn">管理</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 资源分享 -->
      <div class="sharing-section">
        <div class="section-header">
          <h2>资源分享</h2>
          <button @click="showShareModal = true" class="share-btn">分享资源</button>
        </div>
        
        <div class="share-list">
          <div v-for="share in shares" :key="share.id" class="share-item">
            <div class="share-info">
              <div class="shared-resource">
                <span class="resource-name">{{ share.resource_type }} - {{ share.resource_id }}</span>
                <span class="share-type">{{ share.share_type }}</span>
              </div>
              <div class="share-details">
                <p>分享给: {{ share.shared_with_username || '公开分享' }}</p>
                <p>分享时间: {{ formatDate(share.created_at) }}</p>
                <p v-if="share.expires_at">过期时间: {{ formatDate(share.expires_at) }}</p>
              </div>
            </div>
            <div class="share-actions">
              <button @click="copyShareLink(share)" class="copy-btn">复制链接</button>
              <button @click="revokeShare(share.id)" class="revoke-btn">撤销分享</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 订阅升级弹窗 -->
    <div v-if="showUpgradeModal" class="modal-overlay" @click="showUpgradeModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>选择订阅计划</h3>
          <button class="close-btn" @click="showUpgradeModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="subscription-plans">
            <div v-for="feature in subscriptionFeatures" :key="feature.id" class="plan-card">
              <h4>{{ feature.name }}</h4>
              <p>{{ feature.description }}</p>
              <div class="plan-features">
                <ul>
                  <li v-for="item in feature.feature_list" :key="item">{{ item }}</li>
                </ul>
              </div>
              <button @click="subscribeToPlan(feature.id)" class="subscribe-btn">
                选择此计划
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 资源分享弹窗 -->
    <div v-if="showShareModal" class="modal-overlay" @click="showShareModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>分享资源</h3>
          <button class="close-btn" @click="showShareModal = false">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="shareResource">
            <div class="form-group">
              <label>资源类型:</label>
              <select v-model="shareForm.resource_type" required>
                <option value="">请选择</option>
                <option value="word">单词</option>
                <option value="wordset">词汇集</option>
                <option value="learning_goal">学习目标</option>
              </select>
            </div>
            <div class="form-group">
              <label>资源ID:</label>
              <input v-model="shareForm.resource_id" type="text" required placeholder="输入资源ID">
            </div>
            <div class="form-group">
              <label>分享类型:</label>
              <select v-model="shareForm.share_type" required>
                <option value="public">公开分享</option>
                <option value="private">私密分享</option>
                <option value="link">链接分享</option>
              </select>
            </div>
            <div v-if="shareForm.share_type === 'private'" class="form-group">
              <label>分享给用户:</label>
              <input v-model="shareForm.shared_with_username" type="text" placeholder="输入用户名">
            </div>
            <div class="form-group">
              <label>过期时间:</label>
              <input v-model="shareForm.expires_at" type="datetime-local">
            </div>
            <div class="form-actions">
              <button type="submit" class="submit-btn">确认分享</button>
              <button type="button" @click="showShareModal = false" class="cancel-btn">取消</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { resourceAuthAPI } from '../utils/api'

export default {
  name: 'ResourceAuth',
  data() {
    return {
      subscription: null,
      authorizations: [],
      shares: [],
      categories: [],
      subscriptionFeatures: [],
      selectedCategory: '',
      selectedAccessLevel: '',
      showUpgradeModal: false,
      showShareModal: false,
      shareForm: {
        resource_type: '',
        resource_id: '',
        share_type: 'public',
        shared_with_username: '',
        expires_at: ''
      }
    }
  },
  async mounted() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      try {
        await Promise.all([
          this.loadSubscription(),
          this.loadAuthorizations(),
          this.loadShares(),
          this.loadCategories(),
          this.loadSubscriptionFeatures()
        ])
      } catch (error) {
        console.error('加载数据失败:', error)
        this.$message?.error('加载数据失败，请刷新页面重试')
      }
    },
    
    async loadSubscription() {
      try {
        const response = await resourceAuthAPI.getMySubscription()
        this.subscription = response.results?.[0] || null
      } catch (error) {
        console.error('加载订阅信息失败:', error)
      }
    },
    
    async loadAuthorizations() {
      try {
        const params = {}
        if (this.selectedCategory) params.category = this.selectedCategory
        if (this.selectedAccessLevel) params.access_level = this.selectedAccessLevel
        
        const response = await resourceAuthAPI.getMyAuthorizations(params)
        this.authorizations = response.results || []
      } catch (error) {
        console.error('加载授权信息失败:', error)
      }
    },
    
    async loadShares() {
      try {
        const response = await resourceAuthAPI.getMyShares()
        this.shares = response.results || []
      } catch (error) {
        console.error('加载分享信息失败:', error)
      }
    },
    
    async loadCategories() {
      try {
        const response = await resourceAuthAPI.getCategories()
        this.categories = response.results || []
      } catch (error) {
        console.error('加载分类信息失败:', error)
      }
    },
    
    async loadSubscriptionFeatures() {
      try {
        const response = await resourceAuthAPI.getSubscriptionFeatures()
        this.subscriptionFeatures = response.results || []
      } catch (error) {
        console.error('加载订阅功能失败:', error)
      }
    },
    
    async refreshSubscription() {
      await this.loadSubscription()
      this.$message?.success('订阅信息已刷新')
    },
    
    async subscribeToPlan(featureId) {
      try {
        await resourceAuthAPI.subscribe(featureId)
        this.showUpgradeModal = false
        await this.loadSubscription()
        this.$message?.success('订阅成功！')
      } catch (error) {
        console.error('订阅失败:', error)
        this.$message?.error('订阅失败，请重试')
      }
    },
    
    async shareResource() {
      try {
        await resourceAuthAPI.shareResource(this.shareForm)
        this.showShareModal = false
        await this.loadShares()
        this.resetShareForm()
        this.$message?.success('资源分享成功！')
      } catch (error) {
        console.error('分享失败:', error)
        this.$message?.error('分享失败，请重试')
      }
    },
    
    async revokeShare(shareId) {
      try {
        await resourceAuthAPI.revokeShare(shareId)
        await this.loadShares()
        this.$message?.success('分享已撤销')
      } catch (error) {
        console.error('撤销分享失败:', error)
        this.$message?.error('撤销分享失败，请重试')
      }
    },
    
    resetShareForm() {
      this.shareForm = {
        resource_type: '',
        resource_id: '',
        share_type: 'public',
        shared_with_username: '',
        expires_at: ''
      }
    },
    
    copyShareLink(share) {
      const link = `${window.location.origin}/shared/${share.id}`
      navigator.clipboard.writeText(link).then(() => {
        this.$message?.success('分享链接已复制到剪贴板')
      })
    },
    
    viewResourceDetails(auth) {
      // 跳转到资源详情页面
      this.$router.push(`/resource/${auth.resource_type}/${auth.resource_id}`)
    },
    
    manageResource(auth) {
      // 跳转到资源管理页面
      this.$router.push(`/manage/${auth.resource_type}/${auth.resource_id}`)
    },
    
    getResourceIcon(resourceType) {
      const icons = {
        'word': '📝',
        'wordset': '📚',
        'learning_goal': '🎯',
        'course': '📖'
      }
      return icons[resourceType] || '📄'
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('zh-CN')
    }
  }
}
</script>

