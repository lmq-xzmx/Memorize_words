<template>
  <div class="progress-grid-container">
    <div class="progress-grid">
      <!-- 中心圆形区域 -->
      <div class="center-circle">
        <div class="center-content">
          <h3 class="center-title">{{ gridTitle }}</h3>
          <p class="center-subtitle">{{ gridSubtitle }}</p>
        </div>
      </div>
      
      <!-- 八个扇形区域 -->
      <div 
        v-for="(item, index) in gridItems" 
        :key="index"
        :class="`grid-item grid-item-${index + 1}`"
        :data-category="item.category"
        :data-value="item.value"
        :style="{ background: item.color }"
        @click="handleItemClick(item)"
      >
        <div class="item-content">
          <div class="item-label">{{ item.label }}</div>
          <div class="item-value">{{ item.value }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

// Props定义
const props = defineProps({
  gridTitle: {
    type: String,
    default: '九宫格进程'
  },
  gridSubtitle: {
    type: String,
    default: ''
  },
  gridItems: {
    type: Array,
    default: () => [
      { label: '掌握', value: 49, color: 'linear-gradient(135deg, #4CAF50, #45a049)', category: '掌握' },
      { label: '遗忘', value: 0, color: 'linear-gradient(135deg, #f44336, #d32f2f)', category: '遗忘' },
      { label: '学习中', value: 15, color: 'linear-gradient(135deg, #FFC107, #FF8F00)', category: '学习中' },
      { label: '测试', value: 0, color: 'linear-gradient(135deg, #8BC34A, #689F38)', category: '测试' },
      { label: '口音文本', value: 0, color: 'linear-gradient(135deg, #4CAF50, #388E3C)', category: '口音文本' },
      { label: '口音文件', value: 0, color: 'linear-gradient(135deg, #4CAF50, #2E7D32)', category: '口音文件' },
      { label: '区域化任务', value: 0, color: 'linear-gradient(135deg, #4CAF50, #1B5E20)', category: '区域化任务' },
      { label: '解决方案', value: 0, color: 'linear-gradient(135deg, #4CAF50, #0D4F0C)', category: '解决方案' }
    ]
  },
  animated: {
    type: Boolean,
    default: true
  }
})

// 事件定义
const emit = defineEmits(['item-click'])

// 处理项目点击
const handleItemClick = (item) => {
  emit('item-click', {
    category: item.category,
    value: item.value,
    label: item.label
  })
}
</script>

<style scoped>
.progress-grid-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 400px;
}

.progress-grid {
  position: relative;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.center-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: #fff;
  border: 3px solid #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.center-content {
  text-align: center;
  padding: 0.5rem;
}

.center-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #495057;
  margin: 0;
  line-height: 1.2;
}

.center-subtitle {
  font-size: 0.7rem;
  color: #6c757d;
  margin: 0.2rem 0 0 0;
}

.grid-item {
  position: absolute;
  width: 80px;
  height: 80px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.grid-item:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.item-content {
  text-align: center;
  padding: 0.5rem;
}

.item-label {
  font-size: 0.7rem;
  margin-bottom: 0.2rem;
  opacity: 0.9;
}

.item-value {
  font-size: 1.2rem;
  font-weight: 700;
}

/* 八个位置的定位 */
.grid-item-1 { /* 掌握 */
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
}

.grid-item-2 { /* 遗忘 */
  top: 20px;
  right: 20px;
}

.grid-item-3 { /* 学习中 */
  top: 50%;
  right: 20px;
  transform: translateY(-50%);
}

.grid-item-4 { /* 测试 */
  bottom: 20px;
  right: 20px;
}

.grid-item-5 { /* 口音文本 */
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
}

.grid-item-6 { /* 口音文件 */
  bottom: 20px;
  left: 20px;
}

.grid-item-7 { /* 区域化任务 */
  top: 50%;
  left: 20px;
  transform: translateY(-50%);
}

.grid-item-8 { /* 解决方案 */
  top: 20px;
  left: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .progress-grid {
    width: 250px;
    height: 250px;
  }
  
  .center-circle {
    width: 100px;
    height: 100px;
  }
  
  .center-title {
    font-size: 0.8rem;
  }
  
  .grid-item {
    width: 65px;
    height: 65px;
  }
  
  .item-value {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .progress-grid {
    width: 200px;
    height: 200px;
  }
  
  .center-circle {
    width: 80px;
    height: 80px;
  }
  
  .grid-item {
    width: 50px;
    height: 50px;
  }
  
  .item-label {
    font-size: 0.6rem;
  }
  
  .item-value {
    font-size: 0.9rem;
  }
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.grid-item {
  animation: fadeInUp 0.6s ease forwards;
}

.grid-item-1 { animation-delay: 0.1s; }
.grid-item-2 { animation-delay: 0.2s; }
.grid-item-3 { animation-delay: 0.3s; }
.grid-item-4 { animation-delay: 0.4s; }
.grid-item-5 { animation-delay: 0.5s; }
.grid-item-6 { animation-delay: 0.6s; }
.grid-item-7 { animation-delay: 0.7s; }
.grid-item-8 { animation-delay: 0.8s; }
</style>