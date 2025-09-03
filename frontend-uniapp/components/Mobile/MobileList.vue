<template>
  <view class="mobile-list" :class="listClasses">
    <!-- 列表头部 -->
    <view v-if="title || $slots.header" class="list-header">
      <view v-if="title" class="list-title">
        <text class="title-text">{{ title }}</text>
        <text v-if="subtitle" class="subtitle-text">{{ subtitle }}</text>
      </view>
      <slot name="header"></slot>
    </view>
    
    <!-- 列表内容 -->
    <view class="list-content">
      <!-- 空状态 -->
      <view v-if="isEmpty" class="list-empty">
        <view class="empty-icon">
          <text class="iconfont icon-empty">📝</text>
        </view>
        <text class="empty-text">{{ emptyText }}</text>
        <view v-if="$slots.empty" class="empty-action">
          <slot name="empty"></slot>
        </view>
      </view>
      
      <!-- 列表项 -->
      <view v-else>
        <view 
          v-for="(item, index) in dataSource" 
          :key="getItemKey(item, index)"
          class="list-item"
          :class="getItemClasses(item, index)"
          @tap="handleItemTap(item, index)"
        >
          <!-- 自定义渲染 -->
          <slot 
            v-if="$slots.default" 
            :item="item" 
            :index="index"
          ></slot>
          
          <!-- 默认渲染 -->
          <template v-else>
            <!-- 左侧图标/头像 -->
            <view v-if="item.avatar || item.icon" class="item-avatar">
              <image v-if="item.avatar" :src="item.avatar" class="avatar-image" mode="aspectFill" />
              <text v-else-if="item.icon" class="iconfont" :class="item.icon"></text>
            </view>
            
            <!-- 主要内容 -->
            <view class="item-content">
              <view class="item-main">
                <text class="item-title">{{ item.title || item.name }}</text>
                <text v-if="item.subtitle || item.description" class="item-subtitle">
                  {{ item.subtitle || item.description }}
                </text>
              </view>
              
              <!-- 右侧内容 -->
              <view v-if="item.value || item.time || item.badge" class="item-extra">
                <text v-if="item.value" class="item-value">{{ item.value }}</text>
                <text v-if="item.time" class="item-time">{{ item.time }}</text>
                <view v-if="item.badge" class="item-badge" :class="{ 'badge-dot': item.badge === true }">
                  <text v-if="item.badge !== true" class="badge-text">{{ item.badge }}</text>
                </view>
              </view>
            </view>
            
            <!-- 右侧箭头 -->
            <view v-if="showArrow && item.clickable !== false" class="item-arrow">
              <text class="iconfont icon-arrow-right">›</text>
            </view>
          </template>
        </view>
      </view>
    </view>
    
    <!-- 列表底部 -->
    <view v-if="$slots.footer" class="list-footer">
      <slot name="footer"></slot>
    </view>
  </view>
</template>

<script>
export default {
  name: 'MobileList',
  props: {
    // 列表标题
    title: {
      type: String,
      default: ''
    },
    // 列表副标题
    subtitle: {
      type: String,
      default: ''
    },
    // 数据源
    dataSource: {
      type: Array,
      default: () => []
    },
    // 是否显示箭头
    showArrow: {
      type: Boolean,
      default: true
    },
    // 是否显示分割线
    showDivider: {
      type: Boolean,
      default: true
    },
    // 空状态文本
    emptyText: {
      type: String,
      default: '暂无数据'
    },
    // 列表类型
    type: {
      type: String,
      default: 'default',
      validator: value => ['default', 'card', 'inset'].includes(value)
    },
    // 项目唯一键
    rowKey: {
      type: [String, Function],
      default: 'id'
    },
    // 是否可点击
    clickable: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    listClasses() {
      return {
        [`list-${this.type}`]: this.type !== 'default',
        'list-no-divider': !this.showDivider
      }
    },
    
    isEmpty() {
      return !this.dataSource || this.dataSource.length === 0
    }
  },
  methods: {
    getItemKey(item, index) {
      if (typeof this.rowKey === 'function') {
        return this.rowKey(item, index)
      }
      return item[this.rowKey] || index
    },
    
    getItemClasses(item, index) {
      return {
        'item-clickable': this.clickable && item.clickable !== false,
        'item-disabled': item.disabled,
        'item-first': index === 0,
        'item-last': index === this.dataSource.length - 1
      }
    },
    
    handleItemTap(item, index) {
      if (!this.clickable || item.disabled || item.clickable === false) {
        return
      }
      
      this.$emit('item-click', {
        item,
        index
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.mobile-list {
  background-color: var(--card-background);
  
  &.list-card {
    border-radius: var(--border-radius);
    margin: var(--spacing-md);
    box-shadow: var(--shadow-light);
  }
  
  &.list-inset {
    margin: var(--spacing-md);
    border-radius: var(--border-radius);
  }
}

.list-header {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  
  .list-title {
    .title-text {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
      line-height: 1.4;
    }
    
    .subtitle-text {
      font-size: 14px;
      color: var(--text-secondary);
      margin-top: var(--spacing-xs);
      line-height: 1.4;
    }
  }
}

.list-content {
  .list-item {
    display: flex;
    align-items: center;
    padding: var(--spacing-md);
    transition: background-color 0.2s ease;
    
    &:not(.item-last) {
      border-bottom: 1px solid var(--border-color);
    }
    
    &.item-clickable {
      cursor: pointer;
      
      &:active {
        background-color: rgba(0, 0, 0, 0.05);
      }
    }
    
    &.item-disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    .item-avatar {
      margin-right: var(--spacing-md);
      
      .avatar-image {
        width: 40px;
        height: 40px;
        border-radius: 50%;
      }
      
      .iconfont {
        font-size: 24px;
        color: var(--primary-color);
      }
    }
    
    .item-content {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: space-between;
      
      .item-main {
        flex: 1;
        
        .item-title {
          font-size: 16px;
          color: var(--text-primary);
          line-height: 1.4;
          margin-bottom: var(--spacing-xs);
        }
        
        .item-subtitle {
          font-size: 14px;
          color: var(--text-secondary);
          line-height: 1.4;
        }
      }
      
      .item-extra {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        margin-left: var(--spacing-md);
        
        .item-value {
          font-size: 16px;
          color: var(--text-primary);
          font-weight: 500;
        }
        
        .item-time {
          font-size: 12px;
          color: var(--text-disabled);
          margin-top: var(--spacing-xs);
        }
        
        .item-badge {
          background-color: var(--error-color);
          color: white;
          border-radius: 10px;
          padding: 2px 6px;
          font-size: 12px;
          min-width: 16px;
          text-align: center;
          margin-top: var(--spacing-xs);
          
          &.badge-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            padding: 0;
            min-width: auto;
          }
          
          .badge-text {
            line-height: 1;
          }
        }
      }
    }
    
    .item-arrow {
      margin-left: var(--spacing-sm);
      color: var(--text-disabled);
      
      .iconfont {
        font-size: 16px;
      }
    }
  }
}

.list-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
  text-align: center;
  
  .empty-icon {
    font-size: 48px;
    color: var(--text-disabled);
    margin-bottom: var(--spacing-md);
  }
  
  .empty-text {
    font-size: 16px;
    color: var(--text-secondary);
    margin-bottom: var(--spacing-md);
  }
  
  .empty-action {
    margin-top: var(--spacing-md);
  }
}

.list-footer {
  padding: var(--spacing-md);
  border-top: 1px solid var(--border-color);
  background-color: rgba(0, 0, 0, 0.02);
}

.list-no-divider {
  .list-item {
    border-bottom: none;
  }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .mobile-list {
    .list-item.item-clickable:active {
      background-color: rgba(255, 255, 255, 0.05);
    }
  }
  
  .list-footer {
    background-color: rgba(255, 255, 255, 0.02);
  }
}
</style>