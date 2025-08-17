<template>
  <div class="learning-goal-config">
    <!-- 学习目标配置区域 -->
    <div class="goal-section">
      <h3 class="section-title">学习目标配置</h3>
      
      <!-- 当前学习目标显示 -->
      <div v-if="localCurrentGoal" class="current-goal-card">
        <div class="goal-header">
          <h4>{{ localCurrentGoal.name }}</h4>
          <span class="goal-status" :class="localCurrentGoal.is_active ? 'active' : 'inactive'">
            {{ localCurrentGoal.is_active ? '进行中' : '已暂停' }}
          </span>
        </div>
        
        <div class="goal-info">
          <div class="info-item">
            <span class="label">目标描述:</span>
            <span class="value">{{ localCurrentGoal.description || '暂无描述' }}</span>
          </div>
          <div class="info-item">
            <span class="label">总单词数:</span>
            <span class="value">{{ localCurrentGoal.total_words }}</span>
          </div>
          <div class="info-item">
            <span class="label">已学单词:</span>
            <span class="value">{{ localCurrentGoal.learned_words }}</span>
          </div>
          <div class="info-item">
            <span class="label">学习进度:</span>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
              <span class="progress-text">{{ progressPercentage }}%</span>
            </div>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="goal-actions">
          <button class="btn btn-primary" @click="showGoalSelector = true">
            切换学习目标
          </button>
          <button class="btn btn-success" @click="showPlanCreator = true">
            创建学习计划
          </button>
        </div>
      </div>
      
      <!-- 无学习目标时的提示 -->
      <div v-else class="no-goal-prompt">
        <div class="prompt-icon">🎯</div>
        <h4>尚未设置学习目标</h4>
        <p>请选择或创建一个学习目标来开始您的学习之旅</p>
        <div class="prompt-actions">
          <button class="btn btn-primary" @click="showGoalSelector = true">
            选择学习目标
          </button>
        </div>
      </div>
    </div>
    
    <!-- 学习目标选择弹窗 -->
    <div v-if="showGoalSelector" class="modal-overlay" @click="closeGoalSelector">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>选择学习目标</h3>
          <button class="close-btn" @click="closeGoalSelector">×</button>
        </div>
        <div class="modal-body">
          <div class="goals-grid">
            <div 
              v-for="goal in localAvailableGoals" 
              :key="goal.id"
              class="goal-card"
              :class="{ 'selected': goal.id === selectedGoalId }"
              @click="selectGoal(goal)"
            >
              <h4>{{ goal.name }}</h4>
              <p>{{ goal.description || '暂无描述' }}</p>
              <div class="goal-stats">
                <span>总词数: {{ goal.total_words || 0 }}</span>
                <span>已学: {{ goal.learned_words || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="closeGoalSelector">
            取消
          </button>
          <button 
            class="btn btn-primary" 
            :disabled="!selectedGoalId"
            @click="confirmGoalSelection"
          >
            确认选择
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { learningAPI } from '../utils/api'

export default {
  name: 'LearningGoalConfig',
  
  props: {
    currentGoal: {
      type: Object,
      default: null
    },
    availableGoals: {
      type: Array,
      default: () => []
    }
  },
  
  data() {
    return {
      localCurrentGoal: this.currentGoal,
      localAvailableGoals: this.availableGoals,
      showGoalSelector: false,
      showPlanCreator: false,
      selectedGoalId: null,
      loading: false
    }
  },
  
  computed: {
    progressPercentage() {
      if (!this.localCurrentGoal || this.localCurrentGoal.total_words === 0) return 0
      return Math.round((this.localCurrentGoal.learned_words / this.localCurrentGoal.total_words) * 100)
    }
  },
  
  watch: {
    currentGoal: {
      handler(newVal) {
        this.localCurrentGoal = newVal
      },
      immediate: true
    },
    availableGoals: {
      handler(newVal) {
        this.localAvailableGoals = newVal
      },
      immediate: true
    }
  },
  
  methods: {
    // 选择学习目标
    selectGoal(goal) {
      this.selectedGoalId = goal.id
    },
    
    // 确认学习目标选择
    async confirmGoalSelection() {
      if (!this.selectedGoalId) return
      
      try {
        this.loading = true
        const selectedGoal = this.localAvailableGoals.find(g => g.id === this.selectedGoalId)
        
        // 更新当前目标状态
        await learningAPI.updateLearningGoal(this.selectedGoalId, { is_current: true })
        
        this.localCurrentGoal = selectedGoal
        this.closeGoalSelector()
        this.$emit('goal-changed', selectedGoal)
        
        console.log('学习目标切换成功')
      } catch (error) {
        console.error('切换学习目标失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    // 关闭学习目标选择器
    closeGoalSelector() {
      this.showGoalSelector = false
      this.selectedGoalId = null
    }
  }
}
</script>

<style lang="scss" scoped>
@use '../styles/index.scss';
@use '../styles/variables.scss' as *;
@use '../styles/mixins.scss' as *;

.learning-goal-config {
  padding: var(--spacing-5);
  background: var(--color-gray-50);
  border-radius: var(--border-radius-md);
}

.section-title {
  margin-bottom: var(--spacing-5);
  color: var(--color-gray-800);
  @include text-style('lg', 'semibold');
}

.current-goal-card {
  background: var(--color-white);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-5);
  box-shadow: var(--shadow-sm);
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-4);

  h4 {
    margin: 0;
    color: var(--color-gray-800);
  }
}

.goal-status {
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--border-radius-full);
  @include text-style('xs', 'medium');

  &.active {
    background: var(--color-success-50);
    color: var(--color-success-600);
  }

  &.inactive {
    background: var(--color-red-100);
    color: var(--color-red-600);
  }
}

.goal-info {
  margin-bottom: var(--spacing-5);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-2);
}

.label {
  @include text-style('base', 'medium');
  color: var(--color-gray-600);
}

.value {
  color: var(--color-gray-800);
}

.progress-bar {
  position: relative;
  width: 200px;
  height: 20px;
  background: var(--color-gray-200);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-success-500), var(--color-primary-500));
  @include transition;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  @include text-style('xs', 'medium');
  color: var(--color-white);
}

.goal-actions {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: var(--spacing-3);
}

.no-goal-prompt {
  text-align: center;
  padding: var(--spacing-10) var(--spacing-5);
  background: var(--color-white);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-sm);
}

.prompt-icon {
  font-size: 48px;
  margin-bottom: var(--spacing-4);
}

.prompt-actions {
  margin-top: var(--spacing-5);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(var(--color-black), 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--color-white);
  border-radius: var(--border-radius-md);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-5);
  border-bottom: 1px solid var(--color-gray-300);
}

.close-btn {
  background: none;
  border: none;
  @include text-style('2xl');
  cursor: pointer;
  color: var(--color-gray-600);
}

.modal-body {
  padding: var(--spacing-5);
}

.goals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--spacing-4);
}

.goal-card {
  border: 2px solid var(--color-gray-300);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-4);
  cursor: pointer;
  @include transition;

  &:hover {
    border-color: var(--color-primary-500);
    box-shadow: 0 2px 8px rgba(var(--color-primary-500), 0.2);
  }

  &.selected {
    border-color: var(--color-primary-500);
    background: var(--color-primary-50);
  }
}

.goal-stats {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: var(--spacing-4);
  margin-top: var(--spacing-3);
  @include text-style('sm');
  color: var(--color-gray-600);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-5);
  border-top: 1px solid var(--color-gray-300);
}

.btn {
  padding: var(--spacing-2) var(--spacing-4);
  border: none;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  @include text-style('sm', 'medium');
  @include transition;

  &.btn-primary {
    background: var(--color-primary-500);
    color: var(--color-white);

    &:hover {
      background: var(--color-primary-600);
    }

    &:disabled {
      background: var(--color-gray-600);
      cursor: not-allowed;
    }
  }

  &.btn-success {
    background: var(--color-success-500);
    color: var(--color-white);

    &:hover {
      background: var(--color-success-600);
    }
  }

  &.btn-outline {
    background: transparent;
    color: var(--color-gray-600);
    border: 1px solid var(--color-gray-300);

    &:hover {
      background: var(--color-gray-50);
      border-color: var(--color-gray-400);
    }
  }
}
</style>