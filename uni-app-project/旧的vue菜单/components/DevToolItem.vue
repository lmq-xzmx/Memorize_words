<template>
  <div class="dev-tool-item" :class="devToolClasses">
    <div class="dev-tool-content" @click="handleClick">
      <!-- 工具图标 -->
      <div class="tool-icon">
        <i :class="tool.icon || 'icon-dev-default'"></i>
      </div>
      
      <!-- 工具信息 -->
      <div class="tool-info" v-if="!collapsed">
        <div class="tool-name">{{ tool.name }}</div>
        <div class="tool-description" v-if="tool.description">
          {{ tool.description }}
        </div>
        <div class="tool-status">
          <span class="status-indicator" :class="statusClass"></span>
          <span class="status-text">{{ statusText }}</span>
        </div>
      </div>
      
      <!-- 工具操作 -->
      <div class="tool-actions" v-if="!collapsed">
        <!-- 启用/禁用切换 -->
        <button 
          class="toggle-btn"
          @click.stop="handleToggle"
          :class="{ 'enabled': enabled }"
          :title="enabled ? '禁用工具' : '启用工具'"
        >
          <i :class="enabled ? 'icon-toggle-on' : 'icon-toggle-off'"></i>
        </button>
        
        <!-- 配置按钮 -->
        <button 
          v-if="tool.configurable"
          class="config-btn"
          @click.stop="handleConfig"
          title="配置工具"
        >
          <i class="icon-config"></i>
        </button>
      </div>
    </div>
    
    <!-- 工具详情 (展开状态) -->
    <transition name="tool-details">
      <div v-if="showDetails && !collapsed" class="tool-details">
        <div class="detail-section">
          <h4>工具信息</h4>
          <div class="detail-item">
            <span class="label">版本:</span>
            <span class="value">{{ tool.version || 'N/A' }}</span>
          </div>
          <div class="detail-item">
            <span class="label">作者:</span>
            <span class="value">{{ tool.author || 'N/A' }}</span>
          </div>
          <div class="detail-item">
            <span class="label">最后更新:</span>
            <span class="value">{{ formatDate(tool.lastUpdated) }}</span>
          </div>
        </div>
        
        <div class="detail-section" v-if="tool.features">
          <h4>功能特性</h4>
          <ul class="feature-list">
            <li v-for="feature in tool.features" :key="feature">
              {{ feature }}
            </li>
          </ul>
        </div>
        
        <div class="detail-section" v-if="tool.dependencies">
          <h4>依赖项</h4>
          <div class="dependency-list">
            <span 
              v-for="dep in tool.dependencies" 
              :key="dep"
              class="dependency-tag"
            >
              {{ dep }}
            </span>
          </div>
        </div>
        
        <div class="detail-actions">
          <button 
            class="detail-btn primary"
            @click="handleUse"
            :disabled="!enabled"
          >
            使用工具
          </button>
          <button 
            class="detail-btn secondary"
            @click="handleViewDocs"
            v-if="tool.docsUrl"
          >
            查看文档
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'DevToolItem',
  
  props: {
    // 工具数据
    tool: {
      type: Object,
      required: true
    },
    
    // 是否启用
    enabled: {
      type: Boolean,
      default: false
    },
    
    // 是否折叠
    collapsed: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      showDetails: false
    }
  },
  
  computed: {
    // 开发工具样式类
    devToolClasses() {
      return {
        'enabled': this.enabled,
        'disabled': !this.enabled,
        'collapsed': this.collapsed,
        'expanded': this.showDetails,
        'configurable': this.tool.configurable
      }
    },
    
    // 状态样式类
    statusClass() {
      if (!this.enabled) return 'status-disabled'
      if (this.tool.status === 'running') return 'status-running'
      if (this.tool.status === 'error') return 'status-error'
      return 'status-ready'
    },
    
    // 状态文本
    statusText() {
      if (!this.enabled) return '已禁用'
      
      switch (this.tool.status) {
        case 'running': return '运行中'
        case 'error': return '错误'
        case 'ready': return '就绪'
        default: return '未知'
      }
    }
  },
  
  methods: {
    /**
     * 处理工具点击
     */
    handleClick() {
      if (this.collapsed) {
        // 折叠状态下点击直接使用工具
        this.handleUse()
      } else {
        // 展开状态下切换详情显示
        this.showDetails = !this.showDetails
      }
    },
    
    /**
     * 处理启用/禁用切换
     */
    handleToggle() {
      this.$emit('toggle', this.tool)
    },
    
    /**
     * 处理工具配置
     */
    handleConfig() {
      this.$emit('config', this.tool)
    },
    
    /**
     * 处理使用工具
     */
    handleUse() {
      if (!this.enabled) {
        this.$emit('error', {
          tool: this.tool,
          message: '工具未启用，请先启用后使用'
        })
        return
      }
      
      this.$emit('click', this.tool)
    },
    
    /**
     * 查看文档
     */
    handleViewDocs() {
      if (this.tool.docsUrl) {
        window.open(this.tool.docsUrl, '_blank')
      }
    },
    
    /**
     * 格式化日期
     * @param {string|Date} date - 日期
     * @returns {string} 格式化后的日期
     */
    formatDate(date) {
      if (!date) return 'N/A'
      
      try {
        const d = new Date(date)
        return d.toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        })
      } catch (error) {
        return 'N/A'
      }
    }
  }
}
</script>

<style scoped>
.dev-tool-item {
  margin-bottom: 4px;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.dev-tool-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.dev-tool-item.enabled {
  border-left: 3px solid #38a169;
}

.dev-tool-item.disabled {
  border-left: 3px solid #718096;
  opacity: 0.7;
}

/* 工具内容 */
.dev-tool-content {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 56px;
}

.dev-tool-content:hover {
  background: rgba(255, 255, 255, 0.1);
}

.dev-tool-item.collapsed .dev-tool-content {
  justify-content: center;
  padding: 12px;
}

/* 工具图标 */
.tool-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 20px;
  color: rgba(255, 255, 255, 0.8);
  flex-shrink: 0;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
}

.dev-tool-item.enabled .tool-icon {
  color: #38a169;
  background: rgba(56, 161, 105, 0.2);
}

.dev-tool-item.collapsed .tool-icon {
  margin-right: 0;
}

/* 工具信息 */
.tool-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tool-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tool-description {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tool-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-disabled { background: #718096; }
.status-ready { background: #38a169; }
.status-running { 
  background: #3182ce;
  animation: pulse 2s infinite;
}
.status-error { background: #e53e3e; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 工具操作 */
.tool-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.toggle-btn,
.config-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  font-size: 14px;
}

.toggle-btn:hover,
.config-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  transform: scale(1.05);
}

.toggle-btn.enabled {
  background: #38a169;
  color: #ffffff;
}

.toggle-btn.enabled:hover {
  background: #2f855a;
}

/* 工具详情 */
.tool-details {
  padding: 16px;
  background: rgba(0, 0, 0, 0.3);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  font-size: 12px;
}

.detail-item .label {
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.detail-item .value {
  color: #ffffff;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  padding: 2px 0;
  position: relative;
  padding-left: 16px;
}

.feature-list li::before {
  content: '•';
  color: #38a169;
  position: absolute;
  left: 0;
}

.dependency-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.dependency-tag {
  font-size: 10px;
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.detail-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.detail-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.detail-btn.primary {
  background: #3182ce;
  color: #ffffff;
}

.detail-btn.primary:hover:not(:disabled) {
  background: #2c5aa0;
  transform: translateY(-1px);
}

.detail-btn.primary:disabled {
  background: #718096;
  cursor: not-allowed;
}

.detail-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.detail-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

/* 过渡动画 */
.tool-details-enter-active,
.tool-details-leave-active {
  transition: all 0.3s ease;
}

.tool-details-enter-from,
.tool-details-leave-to {
  opacity: 0;
  transform: translateY(-10px);
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.tool-details-enter-to,
.tool-details-leave-from {
  opacity: 1;
  transform: translateY(0);
  max-height: 400px;
}

/* 图标 */
.icon-dev-default::before { content: '🔧'; }
.icon-toggle-on::before { content: '🟢'; }
.icon-toggle-off::before { content: '⚪'; }
.icon-config::before { content: '⚙'; }

/* 开发工具图标 */
.icon-console::before { content: '💻'; }
.icon-debugger::before { content: '🐛'; }
.icon-profiler::before { content: '📊'; }
.icon-inspector::before { content: '🔍'; }
.icon-network::before { content: '🌐'; }
.icon-storage::before { content: '💾'; }
.icon-performance::before { content: '⚡'; }
.icon-security::before { content: '🔒'; }
.icon-accessibility::before { content: '♿'; }
.icon-lighthouse::before { content: '🏮'; }
.icon-webpack::before { content: '📦'; }
.icon-babel::before { content: '🔄'; }
.icon-eslint::before { content: '📏'; }
.icon-prettier::before { content: '✨'; }
.icon-jest::before { content: '🧪'; }
.icon-cypress::before { content: '🌲'; }

/* 响应式设计 */
@media (max-width: 768px) {
  .dev-tool-content {
    padding: 10px 12px;
    min-height: 52px;
  }
  
  .tool-icon {
    width: 28px;
    height: 28px;
    font-size: 18px;
    margin-right: 10px;
  }
  
  .tool-name {
    font-size: 13px;
  }
  
  .tool-description {
    font-size: 11px;
  }
  
  .toggle-btn,
  .config-btn {
    width: 24px;
    height: 24px;
    font-size: 12px;
  }
}
</style>