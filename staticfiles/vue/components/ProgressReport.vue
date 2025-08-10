<template>
  <div class="report-container">
    <!-- 报告头部 -->
    <div class="report-header text-center">
      <h1 class="mb-3">
        <i class="fas fa-chart-pie me-3"></i>学习进度分析报告
      </h1>
      <p class="lead mb-0">导入学习数据，生成可视化进度报告</p>
    </div>

    <!-- 数据导入区域 -->
    <div class="data-import-section">
      <h3 class="mb-4">
        <i class="fas fa-upload me-2"></i>数据导入
      </h3>
      
      <div class="row">
        <div class="col-md-8">
          <div 
            class="upload-area"
            :class="{ 'dragover': isDragOver }"
            @dragover.prevent="handleDragOver"
            @dragleave="handleDragLeave"
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
            <h5>拖拽文件到此处或点击上传</h5>
            <p class="text-muted">支持 CSV, Excel, JSON 格式</p>
            <input 
              ref="fileInput"
              type="file" 
              class="file-input" 
              accept=".csv,.xlsx,.xls,.json" 
              multiple
              @change="handleFileSelect"
            >
            <button type="button" class="btn btn-custom mt-3">
              <i class="fas fa-file-upload me-2"></i>选择文件
            </button>
          </div>
          
          <!-- 文件列表 -->
          <div v-if="uploadedFiles.length > 0" class="mt-3">
            <div 
              v-for="(file, index) in uploadedFiles" 
              :key="index"
              class="alert alert-info d-flex justify-content-between align-items-center"
            >
              <div>
                <i class="fas fa-file me-2"></i>
                <strong>{{ file.name }}</strong>
                <small class="text-muted ms-2">({{ formatFileSize(file.size) }})</small>
              </div>
              <span class="badge bg-primary">已选择</span>
            </div>
          </div>
          
          <!-- 进度条 -->
          <div v-if="isUploading" class="mt-3">
            <div class="progress">
              <div 
                class="progress-bar progress-bar-custom" 
                role="progressbar" 
                :style="{ width: uploadProgress + '%' }"
              ></div>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="card border-0 bg-light">
            <div class="card-body">
              <h6 class="card-title">
                <i class="fas fa-info-circle me-2"></i>数据格式说明
              </h6>
              <ul class="list-unstyled small">
                <li><i class="fas fa-check text-success me-2"></i>CSV: 逗号分隔值文件</li>
                <li><i class="fas fa-check text-success me-2"></i>Excel: .xlsx 或 .xls 格式</li>
                <li><i class="fas fa-check text-success me-2"></i>JSON: 标准JSON格式</li>
              </ul>
              <hr>
              <h6><i class="fas fa-columns me-2"></i>必需字段</h6>
              <ul class="list-unstyled small">
                <li>• category (类别)</li>
                <li>• value (数值)</li>
                <li>• label (标签)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      <div class="text-center mt-4">
        <button 
          type="button" 
          class="btn btn-custom btn-lg" 
          :disabled="!canGenerateReport || isGenerating"
          @click="generateReport"
        >
          <span 
            v-if="isGenerating" 
            class="spinner-border spinner-border-sm me-2" 
            role="status"
          ></span>
          <i class="fas fa-chart-line me-2"></i>生成报告
        </button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div v-if="showStats" class="row mb-4">
      <div class="col-md-3">
        <div class="stats-card">
          <div class="stats-icon text-primary">
            <i class="fas fa-database"></i>
          </div>
          <h4>{{ stats.totalRecords }}</h4>
          <p class="text-muted mb-0">总记录数</p>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stats-card">
          <div class="stats-icon text-success">
            <i class="fas fa-check-circle"></i>
          </div>
          <h4>{{ stats.completedItems }}</h4>
          <p class="text-muted mb-0">已完成</p>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stats-card">
          <div class="stats-icon text-warning">
            <i class="fas fa-clock"></i>
          </div>
          <h4>{{ stats.pendingItems }}</h4>
          <p class="text-muted mb-0">进行中</p>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stats-card">
          <div class="stats-icon text-info">
            <i class="fas fa-percentage"></i>
          </div>
          <h4>{{ stats.completionRate }}%</h4>
          <p class="text-muted mb-0">完成率</p>
        </div>
      </div>
    </div>

    <!-- 九宫格进度展示 -->
    <div v-if="showProgressGrid" class="progress-section">
      <h3 class="mb-4 text-center">
        <i class="fas fa-chart-pie me-2"></i>学习进度可视化
      </h3>
      
      <!-- 九宫格组件 -->
      <ProgressGrid 
        :grid-title="reportTitle"
        :grid-subtitle="reportSubtitle"
        :grid-items="progressData"
        @item-click="handleGridItemClick"
      />
      
      <!-- 导出选项 -->
      <div class="text-center mt-4">
        <div class="btn-group" role="group">
          <button 
            type="button" 
            class="btn btn-outline-primary" 
            @click="exportReport('pdf')"
            :disabled="isExporting"
          >
            <i class="fas fa-file-pdf me-2"></i>导出PDF
          </button>
          <button 
            type="button" 
            class="btn btn-outline-success" 
            @click="exportReport('excel')"
            :disabled="isExporting"
          >
            <i class="fas fa-file-excel me-2"></i>导出Excel
          </button>
          <button 
            type="button" 
            class="btn btn-outline-info" 
            @click="exportReport('image')"
            :disabled="isExporting"
          >
            <i class="fas fa-image me-2"></i>导出图片
          </button>
        </div>
      </div>
    </div>

    <!-- 消息提示 -->
    <div 
      v-for="(alert, index) in alerts" 
      :key="index"
      :class="`alert alert-${alert.type} alert-dismissible fade show`"
      style="position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;"
    >
      {{ alert.message }}
      <button 
        type="button" 
        class="btn-close" 
        @click="removeAlert(index)"
      ></button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import ProgressGrid from './ProgressGrid.vue'
import axios from 'axios'

// 响应式数据
const isDragOver = ref(false)
const uploadedFiles = ref([])
const isUploading = ref(false)
const uploadProgress = ref(0)
const isGenerating = ref(false)
const isExporting = ref(false)
const showStats = ref(false)
const showProgressGrid = ref(false)
const fileInput = ref(null)
const alerts = ref([])

// 报告数据
const reportTitle = ref('九宫格进程')
const reportSubtitle = ref('学习进度分析')
const progressData = ref([])
const uploadedData = ref([])

// 统计数据
const stats = reactive({
  totalRecords: 0,
  completedItems: 0,
  pendingItems: 0,
  completionRate: 0
})

// 计算属性
const canGenerateReport = computed(() => {
  return uploadedFiles.value.length > 0 || uploadedData.value.length > 0
})

// 方法
const handleDragOver = () => {
  isDragOver.value = true
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = (event) => {
  isDragOver.value = false
  const files = Array.from(event.dataTransfer.files)
  handleFiles(files)
}

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  handleFiles(files)
}

const handleFiles = (files) => {
  const validFiles = files.filter(file => validateFile(file))
  
  if (validFiles.length !== files.length) {
    showAlert('部分文件格式不支持，已自动过滤', 'warning')
  }
  
  uploadedFiles.value = validFiles
  processFiles(validFiles)
}

const validateFile = (file) => {
  const validTypes = ['text/csv', 'application/vnd.ms-excel', 
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     'application/json']
  return validTypes.includes(file.type) || 
         file.name.match(/\.(csv|xlsx|xls|json)$/i)
}

const processFiles = async (files) => {
  isUploading.value = true
  uploadProgress.value = 0
  
  try {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })
    
    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)
    
    // 这里可以调用实际的API
    // const response = await axios.post('/api/reports/upload/', formData)
    
    // 模拟处理
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    clearInterval(progressInterval)
    uploadProgress.value = 100
    
    // 模拟解析文件数据
    const mockData = files.map(file => ({
      category: '掌握',
      value: Math.floor(Math.random() * 50),
      label: file.name.split('.')[0]
    }))
    
    uploadedData.value = mockData
    showAlert(`成功处理 ${files.length} 个文件`, 'success')
    
  } catch (error) {
    console.error('文件处理失败:', error)
    showAlert('文件处理失败，请重试', 'danger')
  } finally {
    isUploading.value = false
    setTimeout(() => {
      uploadProgress.value = 0
    }, 1000)
  }
}

const generateReport = async () => {
  isGenerating.value = true
  
  try {
    // 这里可以调用实际的API
    // const response = await axios.post('/api/reports/generate/', {
    //   data: uploadedData.value
    // })
    
    // 模拟生成报告
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 生成模拟数据
    progressData.value = [
      { label: '掌握', value: 49, color: 'linear-gradient(135deg, #4CAF50, #45a049)', category: '掌握' },
      { label: '遗忘', value: 0, color: 'linear-gradient(135deg, #f44336, #d32f2f)', category: '遗忘' },
      { label: '学习中', value: 15, color: 'linear-gradient(135deg, #FFC107, #FF8F00)', category: '学习中' },
      { label: '测试', value: 0, color: 'linear-gradient(135deg, #8BC34A, #689F38)', category: '测试' },
      { label: '口音文本', value: 0, color: 'linear-gradient(135deg, #4CAF50, #388E3C)', category: '口音文本' },
      { label: '口音文件', value: 0, color: 'linear-gradient(135deg, #4CAF50, #2E7D32)', category: '口音文件' },
      { label: '区域化任务', value: 0, color: 'linear-gradient(135deg, #4CAF50, #1B5E20)', category: '区域化任务' },
      { label: '解决方案', value: 0, color: 'linear-gradient(135deg, #4CAF50, #0D4F0C)', category: '解决方案' }
    ]
    
    // 计算统计数据
    const total = progressData.value.reduce((sum, item) => sum + item.value, 0)
    const completed = progressData.value.filter(item => 
      ['掌握', '测试'].includes(item.category)
    ).reduce((sum, item) => sum + item.value, 0)
    const pending = progressData.value.filter(item => 
      ['学习中', '口音文本'].includes(item.category)
    ).reduce((sum, item) => sum + item.value, 0)
    
    stats.totalRecords = total
    stats.completedItems = completed
    stats.pendingItems = pending
    stats.completionRate = total > 0 ? Math.round((completed / total) * 100) : 0
    
    showStats.value = true
    showProgressGrid.value = true
    
    showAlert('报告生成成功', 'success')
    
  } catch (error) {
    console.error('生成报告失败:', error)
    showAlert('生成报告失败，请重试', 'danger')
  } finally {
    isGenerating.value = false
  }
}

const handleGridItemClick = (detail) => {
  showAlert(`点击了 ${detail.category}，数值：${detail.value}`, 'info')
}

const exportReport = async (format) => {
  isExporting.value = true
  
  try {
    // 这里可以调用实际的API
    // const response = await axios.post('/api/reports/export/', {
    //   format: format,
    //   data: progressData.value
    // })
    
    // 模拟导出
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    showAlert(`正在导出 ${format.toUpperCase()} 格式报告...`, 'info')
    
  } catch (error) {
    console.error('导出失败:', error)
    showAlert('导出失败，请重试', 'danger')
  } finally {
    isExporting.value = false
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const showAlert = (message, type = 'info') => {
  const alert = { message, type }
  alerts.value.push(alert)
  
  setTimeout(() => {
    const index = alerts.value.indexOf(alert)
    if (index > -1) {
      alerts.value.splice(index, 1)
    }
  }, 5000)
}

const removeAlert = (index) => {
  alerts.value.splice(index, 1)
}

// 生命周期
onMounted(() => {
  // 组件挂载后的初始化逻辑
})
</script>

<style scoped>
.report-container {
  background: #f8f9fa;
  min-height: 100vh;
  padding: 2rem;
}

.report-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  border-radius: 15px;
  margin-bottom: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.data-import-section {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.progress-section {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.upload-area {
  border: 2px dashed #dee2e6;
  border-radius: 10px;
  padding: 3rem;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
}

.upload-area:hover {
  border-color: #007bff;
  background-color: #f8f9ff;
}

.upload-area.dragover {
  border-color: #28a745;
  background-color: #f0fff4;
}

.file-input {
  display: none;
}

.btn-custom {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 25px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-custom:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
  color: white;
}

.btn-custom:disabled {
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

.stats-card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-5px);
}

.stats-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.progress-bar-custom {
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}
</style>