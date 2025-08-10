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

export default {
  name: 'SubscriptionManagement',
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
    await this.loadData()
  },
  methods: {
    async loadData() {
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

<style scoped>
.subscription-management {
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

.current-subscription {
  margin-bottom: 40px;
}

.subscription-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subscription-details {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.subscription-name {
  font-size: 24px;
  font-weight: bold;
}

.subscription-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.2);
}

.subscription-status.active {
  background: rgba(76, 175, 80, 0.8);
}

.subscription-status.expired {
  background: rgba(244, 67, 54, 0.8);
}

.subscription-meta {
  display: flex;
  gap: 15px;
  font-size: 14px;
  opacity: 0.9;
}

.auto-renew-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.available-subscriptions {
  margin-bottom: 40px;
}

.available-subscriptions h3 {
  font-size: 20px;
  margin-bottom: 20px;
  color: #333;
}

.subscription-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.feature-card {
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 24px;
  background: white;
  transition: all 0.3s ease;
}

.feature-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.feature-card.current {
  border-color: #4caf50;
  background: #f8fff8;
}

.feature-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.feature-header h4 {
  font-size: 18px;
  color: #333;
  margin: 0;
}

.feature-price {
  text-align: right;
}

.price {
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
}

.period {
  font-size: 14px;
  color: #666;
}

.feature-description {
  color: #666;
  margin-bottom: 16px;
  line-height: 1.5;
}

.feature-benefits {
  margin-bottom: 20px;
}

.benefit-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
}

.check-icon {
  color: #4caf50;
  font-weight: bold;
}

.subscription-history h3 {
  font-size: 20px;
  margin-bottom: 20px;
  color: #333;
}

.history-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1.5fr 1fr 1fr;
  background: #f5f5f5;
  padding: 16px;
  font-weight: bold;
  color: #333;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1.5fr 1fr 1fr;
  padding: 16px;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.table-row:last-child {
  border-bottom: none;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.active {
  background: #e8f5e8;
  color: #4caf50;
}

.status-badge.expired {
  background: #ffebee;
  color: #f44336;
}

.status-badge.cancelled {
  background: #f3e5f5;
  color: #9c27b0;
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
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

.btn-success {
  background: #4caf50;
  color: white;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  max-width: 400px;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .subscription-management {
    padding: 15px;
  }
  
  .subscription-card {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .subscription-grid {
    grid-template-columns: 1fr;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .table-header {
    display: none;
  }
  
  .table-row {
    display: block;
    padding: 16px;
    border: 1px solid #eee;
    border-radius: 8px;
    margin-bottom: 8px;
  }
}
</style>