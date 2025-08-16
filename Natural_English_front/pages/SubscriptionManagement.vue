<template>
  <div class="subscription-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>订阅管理</h1>
      <p class="subtitle">管理您的订阅功能和权限</p>
    </div>

    <!-- 当前订阅状态 -->
    <div class="current-subscription">
      <div class="subscription-card">
        <div class="subscription-info">
          <h3>当前订阅</h3>
          <div class="subscription-details">
            <div class="subscription-name">{{ currentSubscription.name || '免费版' }}</div>
            <div class="subscription-status" :class="currentSubscription.status">
              {{ getStatusText(currentSubscription.status) }}
            </div>
          </div>
          <div class="subscription-meta">
            <div v-if="currentSubscription.expires_at" class="expiry-date">
              到期时间: {{ formatDate(currentSubscription.expires_at) }}
            </div>
            <div class="auto-renew" v-if="currentSubscription.auto_renew">
              <span class="auto-renew-badge">自动续费</span>
            </div>
          </div>
        </div>
        <div class="subscription-actions">
          <button 
            v-if="currentSubscription.status === 'active'"
            @click="showCancelModal = true"
            class="btn btn-outline"
          >
            取消订阅
          </button>
          <button 
            v-if="currentSubscription.status === 'expired'"
            @click="renewSubscription"
            class="btn btn-primary"
          >
            续费
          </button>
        </div>
      </div>
    </div>

    <!-- 可用订阅功能 -->
    <div class="available-subscriptions">
      <h3>可用订阅功能</h3>
      <div class="subscription-grid">
        <div 
          v-for="feature in subscriptionFeatures"
          :key="feature.id"
          class="feature-card"
          :class="{ 'current': isCurrentFeature(feature.id) }"
        >
          <div class="feature-header">
            <h4>{{ feature.name }}</h4>
            <div class="feature-price">
              <span class="price">¥{{ feature.price }}</span>
              <span class="period">/{{ feature.billing_cycle }}</span>
            </div>
          </div>
          <div class="feature-description">
            {{ feature.description }}
          </div>
          <div class="feature-benefits">
            <div 
              v-for="benefit in feature.benefits"
              :key="benefit"
              class="benefit-item"
            >
              <span class="check-icon">✓</span>
              {{ benefit }}
            </div>
          </div>
          <div class="feature-actions">
            <button 
              v-if="!isCurrentFeature(feature.id)"
              @click="subscribeToFeature(feature)"
              class="btn btn-primary"
              :disabled="loading"
            >
              {{ loading ? '处理中...' : '订阅' }}
            </button>
            <button 
              v-else
              class="btn btn-success"
              disabled
            >
              当前订阅
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 订阅历史 -->
    <div class="subscription-history">
      <h3>订阅历史</h3>
      <div class="history-table">
        <div class="table-header">
          <div class="col">功能名称</div>
          <div class="col">订阅时间</div>
          <div class="col">到期时间</div>
          <div class="col">状态</div>
          <div class="col">操作</div>
        </div>
        <div 
          v-for="record in subscriptionHistory"
          :key="record.id"
          class="table-row"
        >
          <div class="col">{{ record.feature_name }}</div>
          <div class="col">{{ formatDate(record.subscribed_at) }}</div>
          <div class="col">{{ formatDate(record.expires_at) }}</div>
          <div class="col">
            <span class="status-badge" :class="record.status">
              {{ getStatusText(record.status) }}
            </span>
          </div>
          <div class="col">
            <button 
              v-if="record.status === 'active'"
              @click="viewSubscriptionDetails(record)"
              class="btn btn-sm btn-outline"
            >
              详情
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 取消订阅确认模态框 -->
    <div v-if="showCancelModal" class="modal-overlay" @click="showCancelModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>确认取消订阅</h3>
          <button @click="showCancelModal = false" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <p>您确定要取消当前订阅吗？取消后将在到期时间后失去相关权限。</p>
        </div>
        <div class="modal-footer">
          <button @click="showCancelModal = false" class="btn btn-outline">取消</button>
          <button @click="confirmCancelSubscription" class="btn btn-danger">确认取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { resourceAuthAPI } from '../utils/api.js'
import permissionMixin from '../mixins/permissionMixin.js'

export default {
  name: 'SubscriptionManagement',
  mixins: [permissionMixin],
  data() {
    return {
      loading: false,
      showCancelModal: false,
      currentSubscription: {},
      subscriptionFeatures: [],
      subscriptionHistory: []
    }
  },
  async mounted() {
    // 检查用户认证状态和权限
    if (!this.$isAuthenticated()) {
      this.$message?.error('请先登录后再访问订阅管理')
      this.$router.push('/login')
      return
    }
    
    if (!this.$hasPermission('manage_subscriptions')) {
      this.$message?.error('您没有权限访问订阅管理功能')
      this.$router.push('/dashboard')
      return
    }
    
    await this.loadData()
  },
  methods: {
    async loadData() {
      // 再次检查认证状态
      if (!this.$isAuthenticated()) {
        this.$message?.error('认证已失效，请重新登录')
        this.$router.push('/login')
        return
      }
      
      this.loading = true
      try {
        // 并行加载数据
        const [subscriptionData, featuresData, historyData] = await Promise.all([
          resourceAuthAPI.getSubscriptionInfo(),
          resourceAuthAPI.getSubscriptionFeatures(),
          resourceAuthAPI.getSubscriptionHistory()
        ])
        
        this.currentSubscription = subscriptionData.data || {}
        this.subscriptionFeatures = featuresData.data || []
        this.subscriptionHistory = historyData.data || []
      } catch (error) {
        console.error('加载订阅数据失败:', error)
        
        // 检查是否是认证错误
        if (error.message && error.message.includes('未认证')) {
          this.$message?.error('登录状态已失效，请重新登录')
          this.$router.push('/login')
          return
        }
        
        this.$message?.error('加载数据失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    isCurrentFeature(featureId) {
      return this.currentSubscription.feature_id === featureId
    },
    
    async subscribeToFeature(feature) {
      this.loading = true
      try {
        await resourceAuthAPI.subscribeToFeature(feature.id)
        this.$message?.success('订阅成功！')
        await this.loadData()
      } catch (error) {
        console.error('订阅失败:', error)
        this.$message?.error('订阅失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    async renewSubscription() {
      this.loading = true
      try {
        await resourceAuthAPI.renewSubscription(this.currentSubscription.id)
        this.$message?.success('续费成功！')
        await this.loadData()
      } catch (error) {
        console.error('续费失败:', error)
        this.$message?.error('续费失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    async confirmCancelSubscription() {
      this.loading = true
      try {
        await resourceAuthAPI.unsubscribeFromFeature(this.currentSubscription.feature_id)
        this.$message?.success('取消订阅成功')
        this.showCancelModal = false
        await this.loadData()
      } catch (error) {
        console.error('取消订阅失败:', error)
        this.$message?.error('取消订阅失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    viewSubscriptionDetails(record) {
      // 可以跳转到详情页面或显示详情模态框
      console.log('查看订阅详情:', record)
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('zh-CN')
    },
    
    getStatusText(status) {
      const statusMap = {
        'active': '有效',
        'expired': '已过期',
        'cancelled': '已取消',
        'pending': '待激活'
      }
      return statusMap[status] || status
    }
  }
}
</script>

