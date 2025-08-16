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
import { learningAPI } from '../utils/api.js'

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

<style scoped>
.learning-goal-config {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.section-title {
  margin-bottom: 20px;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.current-goal-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.goal-header h4 {
  margin: 0;
  color: #2c3e50;
}

.goal-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.goal-status.active {
  background: #d4edda;
  color: #155724;
}

.goal-status.inactive {
  background: #f8d7da;
  color: #721c24;
}

.goal-info {
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.label {
  font-weight: 500;
  color: #6c757d;
}

.value {
  color: #2c3e50;
}

.progress-bar {
  position: relative;
  width: 200px;
  height: 20px;
  background: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #28a745, #20c997);
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  font-weight: 500;
  color: white;
}

.goal-actions {
  display: flex;
  gap: 10px;
}

.no-goal-prompt {
  text-align: center;
  padding: 40px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.prompt-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.prompt-actions {
  margin-top: 20px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #dee2e6;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6c757d;
}

.modal-body {
  padding: 20px;
}

.goals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.goal-card {
  border: 2px solid #dee2e6;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.goal-card:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0,123,255,0.2);
}

.goal-card.selected {
  border-color: #007bff;
  background: #f8f9ff;
}

.goal-stats {
  display: flex;
  gap: 15px;
  margin-top: 10px;
  font-size: 14px;
  color: #6c757d;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #dee2e6;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-primary:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover {
  background: #1e7e34;
}

.btn-outline {
  background: transparent;
  color: #6c757d;
  border: 1px solid #dee2e6;
}

.btn-outline:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}
</style>