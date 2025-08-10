// Vue3 + Django 九宫格报告组件使用示例
// 适用于前台Vue3应用

import { createApp } from 'vue'
import ProgressGrid from '../components/ProgressGrid.vue'
import ProgressReport from '../components/ProgressReport.vue'

// 1. 单独使用九宫格组件
const gridApp = createApp({
  components: {
    ProgressGrid
  },
  data() {
    return {
      gridData: [
        { label: '掌握', value: 49, color: 'linear-gradient(135deg, #4CAF50, #45a049)', category: '掌握' },
        { label: '遗忘', value: 0, color: 'linear-gradient(135deg, #f44336, #d32f2f)', category: '遗忘' },
        { label: '学习中', value: 15, color: 'linear-gradient(135deg, #FFC107, #FF8F00)', category: '学习中' },
        { label: '测试', value: 0, color: 'linear-gradient(135deg, #8BC34A, #689F38)', category: '测试' },
        { label: '口音文本', value: 0, color: 'linear-gradient(135deg, #4CAF50, #388E3C)', category: '口音文本' },
        { label: '口音文件', value: 0, color: 'linear-gradient(135deg, #4CAF50, #2E7D32)', category: '口音文件' },
        { label: '区域化任务', value: 0, color: 'linear-gradient(135deg, #4CAF50, #1B5E20)', category: '区域化任务' },
        { label: '解决方案', value: 0, color: 'linear-gradient(135deg, #4CAF50, #0D4F0C)', category: '解决方案' }
      ]
    }
  },
  methods: {
    handleGridClick(detail) {
      console.log('九宫格点击事件:', detail)
      // 处理点击逻辑
    }
  },
  template: `
    <div>
      <h2>学习进度展示</h2>
      <ProgressGrid 
        :grid-items="gridData"
        grid-title="学习进度"
        grid-subtitle="实时更新"
        @item-click="handleGridClick"
      />
    </div>
  `
})

// 2. 使用完整报告组件
const reportApp = createApp({
  components: {
    ProgressReport
  },
  template: `
    <div>
      <ProgressReport />
    </div>
  `
})

// 3. 在现有Vue应用中集成
const existingApp = createApp({
  components: {
    ProgressGrid,
    ProgressReport
  },
  data() {
    return {
      showReport: false,
      currentData: []
    }
  },
  methods: {
    async loadReportData() {
      try {
        // 从Django API获取数据
        const response = await fetch('/api/reports/data/')
        const data = await response.json()
        this.currentData = data.results
        this.showReport = true
      } catch (error) {
        console.error('加载报告数据失败:', error)
      }
    },
    
    handleReportGenerated(reportData) {
      console.log('报告生成完成:', reportData)
      // 处理报告生成后的逻辑
    }
  },
  template: `
    <div class="app-container">
      <nav class="navbar">
        <h1>学习管理系统</h1>
        <button @click="loadReportData" class="btn btn-primary">
          查看进度报告
        </button>
      </nav>
      
      <main>
        <div v-if="!showReport" class="welcome-section">
          <h2>欢迎使用学习进度分析系统</h2>
          <p>点击上方按钮查看您的学习进度</p>
        </div>
        
        <ProgressReport 
          v-if="showReport"
          @report-generated="handleReportGenerated"
        />
      </main>
    </div>
  `
})

// 4. 与Django后端API集成的工具函数
class ReportAPI {
  constructor(baseURL = '/api/reports/') {
    this.baseURL = baseURL
    this.csrfToken = this.getCSRFToken()
  }
  
  getCSRFToken() {
    const cookies = document.cookie.split(';')
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=')
      if (name === 'csrftoken') {
        return value
      }
    }
    return null
  }
  
  async uploadData(files) {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })
    
    const response = await fetch(`${this.baseURL}upload/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': this.csrfToken
      },
      body: formData
    })
    
    return response.json()
  }
  
  async generateReport(data) {
    const response = await fetch(`${this.baseURL}generate/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.csrfToken
      },
      body: JSON.stringify({ data })
    })
    
    return response.json()
  }
  
  async exportReport(format, reportData) {
    const response = await fetch(`${this.baseURL}export/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.csrfToken
      },
      body: JSON.stringify({ 
        format, 
        report_data: reportData 
      })
    })
    
    return response.json()
  }
}

// 5. 响应式数据管理（使用Pinia或Vuex）
import { defineStore } from 'pinia'

export const useReportStore = defineStore('report', {
  state: () => ({
    reportData: [],
    isLoading: false,
    error: null,
    stats: {
      totalRecords: 0,
      completedItems: 0,
      pendingItems: 0,
      completionRate: 0
    }
  }),
  
  actions: {
    async uploadFiles(files) {
      this.isLoading = true
      this.error = null
      
      try {
        const api = new ReportAPI()
        const result = await api.uploadData(files)
        
        if (result.success) {
          return result
        } else {
          throw new Error(result.error)
        }
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async generateReport(data) {
      this.isLoading = true
      this.error = null
      
      try {
        const api = new ReportAPI()
        const result = await api.generateReport(data)
        
        if (result.success) {
          this.reportData = result.report_data
          this.stats = result.stats
          return result
        } else {
          throw new Error(result.error)
        }
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.isLoading = false
      }
    }
  }
})

// 6. 组件使用示例（在.vue文件中）
/*
<template>
  <div class="report-page">
    <!-- 使用九宫格组件 -->
    <ProgressGrid 
      :grid-items="reportStore.reportData"
      grid-title="学习进度"
      @item-click="handleGridClick"
    />
    
    <!-- 使用完整报告组件 -->
    <ProgressReport />
  </div>
</template>

<script setup>
import { useReportStore } from '@/stores/report'
import ProgressGrid from '@/components/ProgressGrid.vue'
import ProgressReport from '@/components/ProgressReport.vue'

const reportStore = useReportStore()

const handleGridClick = (detail) => {
  console.log('点击了:', detail)
}
</script>
*/

// 7. 路由配置示例（Vue Router）
const routes = [
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/ReportsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/reports/progress',
    name: 'ProgressReport',
    component: () => import('@/components/ProgressReport.vue'),
    meta: { requiresAuth: true }
  }
]

// 导出供其他模块使用
export {
  gridApp,
  reportApp,
  existingApp,
  ReportAPI,
  useReportStore
}

// 使用说明：
// 1. 确保已安装Vue 3和相关依赖
// 2. 在Django项目中配置好API路由
// 3. 根据需要选择使用单独的九宫格组件或完整的报告组件
// 4. 可以通过props传递数据，也可以通过API动态加载
// 5. 支持文件上传、数据处理、报告生成和导出功能