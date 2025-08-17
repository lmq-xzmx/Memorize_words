<template>
  <div class="permission-test-page">
    <div class="test-header">
      <h1>🔐 权限管理系统测试</h1>
      <p>全面测试不同角色的权限功能</p>
    </div>

    <div class="test-controls">
      <div class="control-group">
        <label>选择测试角色:</label>
        <select v-model="selectedRole" @change="onRoleChange">
          <option value="">请选择角色</option>
          <option v-for="role in availableRoles" :key="role.key" :value="role.key">
            {{ role.name }}
          </option>
        </select>
      </div>
      
      <div class="control-group">
        <button @click="runFullTest" :disabled="isRunning" class="btn-primary">
          {{ isRunning ? '测试中...' : '运行完整测试' }}
        </button>
        
        <button @click="runRoleTest" :disabled="!selectedRole || isRunning" class="btn-secondary">
          测试选中角色
        </button>
        
        <button @click="clearResults" class="btn-outline">
          清除结果
        </button>
      </div>
    </div>

    <div v-if="currentUser" class="current-user-info">
      <h3>当前测试用户</h3>
      <div class="user-details">
        <span><strong>角色:</strong> {{ currentUser.role }}</span>
        <span><strong>权限数:</strong> {{ currentUser.permissions.length }}</span>
        <span><strong>登录时间:</strong> {{ formatTime(currentUser.loginTime) }}</span>
      </div>
    </div>

    <div v-if="testResults.length > 0" class="test-results">
      <div class="results-header">
        <h3>测试结果</h3>
        <div class="results-summary">
          <span class="total">总计: {{ testResults.length }}</span>
          <span class="passed">通过: {{ passedCount }}</span>
          <span class="failed">失败: {{ failedCount }}</span>
          <span class="rate">成功率: {{ successRate }}%</span>
        </div>
      </div>

      <div class="results-filters">
        <label>
          <input type="checkbox" v-model="showPassed"> 显示通过的测试
        </label>
        <label>
          <input type="checkbox" v-model="showFailed"> 显示失败的测试
        </label>
        <select v-model="filterSuite">
          <option value="">所有测试套件</option>
          <option v-for="suite in testSuites" :key="suite" :value="suite">
            {{ suite }}
          </option>
        </select>
      </div>

      <div class="results-list">
        <div 
          v-for="result in filteredResults" 
          :key="result.id"
          :class="['result-item', result.passed ? 'passed' : 'failed']"
        >
          <div class="result-header">
            <span class="status-icon">{{ result.passed ? '✅' : '❌' }}</span>
            <span class="test-suite">{{ result.testSuite }}</span>
            <span class="test-type">{{ result.testType }}</span>
            <span class="timestamp">{{ formatTime(result.timestamp) }}</span>
          </div>
          <div class="result-description">{{ result.description }}</div>
          <div class="result-user">测试用户: {{ result.user }}</div>
        </div>
      </div>
    </div>

    <div v-if="testProgress.show" class="test-progress">
      <h3>测试进度</h3>
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: testProgress.percentage + '%' }"
        ></div>
      </div>
      <p>{{ testProgress.current }} / {{ testProgress.total }} - {{ testProgress.message }}</p>
    </div>

    <div class="export-section">
      <h3>导出测试结果</h3>
      <div class="export-controls">
        <button @click="exportResults('json')" class="btn-outline">
          导出 JSON
        </button>
        <button @click="exportResults('csv')" class="btn-outline">
          导出 CSV
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { permissionTestSuite } from '../tests/permissionTestSuite';
import { ROLES } from '../utils/permissionConstants';

export default {
  name: 'PermissionTest',
  setup() {
    // 响应式数据
    const selectedRole = ref('');
    const isRunning = ref(false);
    const testResults = ref([]);
    const currentUser = ref(null);
    const testProgress = ref({
      show: false,
      current: 0,
      total: 0,
      percentage: 0,
      message: ''
    });
    
    // 过滤选项
    const showPassed = ref(true);
    const showFailed = ref(true);
    const filterSuite = ref('');
    
    // 可用角色
    const availableRoles = ref([
      { key: 'student', name: '学生' },
      { key: 'teacher', name: '教师' },
      { key: 'parent', name: '家长' },
      { key: 'academic_director', name: '学术主管' },
      { key: 'research_leader', name: '研究负责人' },
      { key: 'dean', name: '教导主任' },
      { key: 'admin', name: '管理员' }
    ]);
    
    // 计算属性
    const passedCount = computed(() => 
      testResults.value.filter(r => r.passed).length
    );
    
    const failedCount = computed(() => 
      testResults.value.filter(r => !r.passed).length
    );
    
    const successRate = computed(() => {
      if (testResults.value.length === 0) return 0;
      return ((passedCount.value / testResults.value.length) * 100).toFixed(2);
    });
    
    const testSuites = computed(() => {
      const suites = [...new Set(testResults.value.map(r => r.testSuite))];
      return suites.sort();
    });
    
    const filteredResults = computed(() => {
      return testResults.value.filter(result => {
        // 过滤通过/失败状态
        if (!showPassed.value && result.passed) return false;
        if (!showFailed.value && !result.passed) return false;
        
        // 过滤测试套件
        if (filterSuite.value && result.testSuite !== filterSuite.value) return false;
        
        return true;
      }).map((result, index) => ({ ...result, id: index }));
    });
    
    // 方法
    const onRoleChange = () => {
      console.log('选择角色:', selectedRole.value);
    };
    
    const runFullTest = async () => {
      if (isRunning.value) return;
      
      isRunning.value = true;
      testProgress.value = {
        show: true,
        current: 0,
        total: 100,
        percentage: 0,
        message: '开始运行完整测试套件...'
      };
      
      try {
        // 监听测试进度
        const progressHandler = (event) => {
          if (event.detail) {
            testProgress.value.current = event.detail.current || 0;
            testProgress.value.total = event.detail.total || 100;
            testProgress.value.percentage = (testProgress.value.current / testProgress.value.total) * 100;
            testProgress.value.message = event.detail.message || '测试中...';
          }
        };
        
        window.addEventListener('testProgress', progressHandler);
        
        // 运行测试
        const results = await permissionTestSuite.runFullTestSuite();
        testResults.value = results;
        currentUser.value = permissionTestSuite.currentUser;
        
        window.removeEventListener('testProgress', progressHandler);
        
        testProgress.value.show = false;
        console.log('完整测试完成:', results);
        
      } catch (error) {
        console.error('测试运行失败:', error);
        alert('测试运行失败: ' + error.message);
      } finally {
        isRunning.value = false;
      }
    };
    
    const runRoleTest = async () => {
      if (!selectedRole.value || isRunning.value) return;
      
      isRunning.value = true;
      testProgress.value = {
        show: true,
        current: 0,
        total: 50,
        percentage: 0,
        message: `测试角色: ${selectedRole.value}...`
      };
      
      try {
        const scenario = permissionTestSuite.testScenarios[selectedRole.value];
        if (scenario) {
          await permissionTestSuite.testRoleScenario(selectedRole.value, scenario);
          testResults.value = permissionTestSuite.testResults;
          currentUser.value = permissionTestSuite.currentUser;
        }
        
        testProgress.value.show = false;
        console.log('角色测试完成:', selectedRole.value);
        
      } catch (error) {
        console.error('角色测试失败:', error);
        alert('角色测试失败: ' + error.message);
      } finally {
        isRunning.value = false;
      }
    };
    
    const clearResults = () => {
      testResults.value = [];
      currentUser.value = null;
      permissionTestSuite.testResults = [];
      console.log('测试结果已清除');
    };
    
    const exportResults = (format) => {
      try {
        const data = permissionTestSuite.exportResults(format);
        const blob = new Blob([data], { 
          type: format === 'json' ? 'application/json' : 'text/csv' 
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `permission-test-results.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log(`测试结果已导出为 ${format.toUpperCase()} 格式`);
      } catch (error) {
        console.error('导出失败:', error);
        alert('导出失败: ' + error.message);
      }
    };
    
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleString('zh-CN');
    };
    
    // 生命周期
    onMounted(() => {
      console.log('权限测试页面已加载');
    });
    
    return {
      selectedRole,
      isRunning,
      testResults,
      currentUser,
      testProgress,
      showPassed,
      showFailed,
      filterSuite,
      availableRoles,
      passedCount,
      failedCount,
      successRate,
      testSuites,
      filteredResults,
      onRoleChange,
      runFullTest,
      runRoleTest,
      clearResults,
      exportResults,
      formatTime
    };
  }
};
</script>

<style scoped>
.permission-test-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.test-header {
  text-align: center;
  margin-bottom: 30px;
}

.test-header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.test-header p {
  color: #7f8c8d;
  font-size: 16px;
}

.test-controls {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.control-group:last-child {
  margin-bottom: 0;
}

.control-group label {
  font-weight: 600;
  min-width: 120px;
}

.control-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.btn-primary, .btn-secondary, .btn-outline {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
}

.btn-outline {
  background: transparent;
  color: #3498db;
  border: 1px solid #3498db;
}

.btn-outline:hover {
  background: #3498db;
  color: white;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.current-user-info {
  background: #e8f5e8;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.current-user-info h3 {
  margin: 0 0 10px 0;
  color: #27ae60;
}

.user-details {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.user-details span {
  font-size: 14px;
}

.test-results {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 30px;
}

.results-header {
  background: #f8f9fa;
  padding: 15px 20px;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.results-header h3 {
  margin: 0;
  color: #2c3e50;
}

.results-summary {
  display: flex;
  gap: 15px;
  font-size: 14px;
}

.results-summary .total {
  color: #34495e;
}

.results-summary .passed {
  color: #27ae60;
  font-weight: 600;
}

.results-summary .failed {
  color: #e74c3c;
  font-weight: 600;
}

.results-summary .rate {
  color: #3498db;
  font-weight: 600;
}

.results-filters {
  padding: 15px 20px;
  border-bottom: 1px solid #ddd;
  display: flex;
  gap: 20px;
  align-items: center;
  background: #fafafa;
}

.results-filters label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
}

.results-filters select {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.results-list {
  max-height: 600px;
  overflow-y: auto;
}

.result-item {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.result-item:last-child {
  border-bottom: none;
}

.result-item.passed {
  background: #f8fff8;
  border-left: 4px solid #27ae60;
}

.result-item.failed {
  background: #fff8f8;
  border-left: 4px solid #e74c3c;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 8px;
}

.status-icon {
  font-size: 16px;
}

.test-suite {
  font-weight: 600;
  color: #2c3e50;
}

.test-type {
  background: #ecf0f1;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  color: #7f8c8d;
}

.timestamp {
  font-size: 12px;
  color: #95a5a6;
  margin-left: auto;
}

.result-description {
  font-size: 14px;
  color: #34495e;
  margin-bottom: 5px;
}

.result-user {
  font-size: 12px;
  color: #7f8c8d;
}

.test-progress {
  background: #fff3cd;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.test-progress h3 {
  margin: 0 0 15px 0;
  color: #856404;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: #f8f9fa;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2980b9);
  transition: width 0.3s ease;
}

.export-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.export-section h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.export-controls {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .control-group {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .results-filters {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .result-header {
    flex-wrap: wrap;
  }
  
  .export-controls {
    flex-direction: column;
  }
}
</style>