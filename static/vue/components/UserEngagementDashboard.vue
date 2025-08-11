<template>
  <div class="user-engagement-dashboard">
    <!-- 页面标题 -->
    <div class="dashboard-header">
      <h2 class="title">用户粘性游戏化分析</h2>
      <div class="date-selector">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="fetchData"
        />
      </div>
    </div>

    <!-- 核心指标卡片 -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">
          <i class="el-icon-user"></i>
        </div>
        <div class="metric-content">
          <h3>{{ engagementMetrics.daily_active_users || 0 }}</h3>
          <p>日活跃用户</p>
          <span class="metric-change" :class="getChangeClass(engagementMetrics.dau_change)">
            {{ formatChange(engagementMetrics.dau_change) }}
          </span>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">
          <i class="el-icon-time"></i>
        </div>
        <div class="metric-content">
          <h3>{{ formatDuration(engagementMetrics.avg_session_duration) }}</h3>
          <p>平均会话时长</p>
          <span class="metric-change" :class="getChangeClass(engagementMetrics.session_duration_change)">
            {{ formatChange(engagementMetrics.session_duration_change) }}
          </span>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">
          <i class="el-icon-refresh"></i>
        </div>
        <div class="metric-content">
          <h3>{{ engagementMetrics.retention_rate || 0 }}%</h3>
          <p>7日留存率</p>
          <span class="metric-change" :class="getChangeClass(engagementMetrics.retention_change)">
            {{ formatChange(engagementMetrics.retention_change) }}
          </span>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">
          <i class="el-icon-trophy"></i>
        </div>
        <div class="metric-content">
          <h3>{{ engagementMetrics.game_engagement_score || 0 }}</h3>
          <p>游戏化参与度</p>
          <span class="metric-change" :class="getChangeClass(engagementMetrics.engagement_change)">
            {{ formatChange(engagementMetrics.engagement_change) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="chart-row">
        <!-- 用户行为分析图表 -->
        <div class="chart-container">
          <h3>用户行为模式分析</h3>
          <div ref="behaviorChart" class="chart"></div>
        </div>

        <!-- 游戏化元素效果图表 -->
        <div class="chart-container">
          <h3>游戏化元素效果</h3>
          <div ref="gameElementChart" class="chart"></div>
        </div>
      </div>

      <div class="chart-row">
        <!-- 留存率趋势图表 -->
        <div class="chart-container full-width">
          <h3>用户留存率趋势</h3>
          <div ref="retentionChart" class="chart"></div>
        </div>
      </div>
    </div>

    <!-- A/B测试结果 -->
    <div class="ab-test-section">
      <h3>A/B测试结果</h3>
      <el-table :data="abTestResults" style="width: 100%">
        <el-table-column prop="experiment_name" label="实验名称" width="200"></el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="control_group_size" label="对照组" width="100"></el-table-column>
        <el-table-column prop="test_group_size" label="实验组" width="100"></el-table-column>
        <el-table-column prop="conversion_rate_control" label="对照组转化率" width="120">
          <template #default="scope">
            {{ (scope.row.conversion_rate_control * 100).toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="conversion_rate_test" label="实验组转化率" width="120">
          <template #default="scope">
            {{ (scope.row.conversion_rate_test * 100).toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="statistical_significance" label="统计显著性" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.statistical_significance ? 'success' : 'warning'">
              {{ scope.row.statistical_significance ? '显著' : '不显著' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="viewTestDetails(scope.row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import axios from 'axios'

export default {
  name: 'UserEngagementDashboard',
  data() {
    return {
      dateRange: [],
      engagementMetrics: {},
      behaviorAnalysis: {},
      gameElementEffectiveness: {},
      abTestResults: [],
      loading: false
    }
  },
  mounted() {
    this.initDateRange()
    this.fetchData()
  },
  methods: {
    initDateRange() {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30) // 30天前
      this.dateRange = [start, end]
    },

    async fetchData() {
      this.loading = true
      try {
        await Promise.all([
          this.fetchEngagementMetrics(),
          this.fetchBehaviorAnalysis(),
          this.fetchGameElementEffectiveness(),
          this.fetchABTestResults()
        ])
        this.renderCharts()
      } catch (error) {
        console.error('获取数据失败:', error)
        this.$message.error('数据加载失败')
      } finally {
        this.loading = false
      }
    },

    async fetchEngagementMetrics() {
      const params = this.getDateParams()
      const response = await axios.get('/api/engagement/user-engagement-metrics/', { params })
      this.engagementMetrics = response.data
    },

    async fetchBehaviorAnalysis() {
      const params = this.getDateParams()
      const response = await axios.get('/api/engagement/behavior-analysis/', { params })
      this.behaviorAnalysis = response.data
    },

    async fetchGameElementEffectiveness() {
      const params = this.getDateParams()
      const response = await axios.get('/api/engagement/game-element-effectiveness/', { params })
      this.gameElementEffectiveness = response.data
    },

    async fetchABTestResults() {
      const response = await axios.get('/api/engagement/ab-test-results/')
      this.abTestResults = response.data.results || []
    },

    getDateParams() {
      if (!this.dateRange || this.dateRange.length !== 2) return {}
      return {
        start_date: this.formatDate(this.dateRange[0]),
        end_date: this.formatDate(this.dateRange[1])
      }
    },

    formatDate(date) {
      return date.toISOString().split('T')[0]
    },

    formatDuration(seconds) {
      if (!seconds) return '0分钟'
      const minutes = Math.floor(seconds / 60)
      return `${minutes}分钟`
    },

    formatChange(change) {
      if (!change) return '0%'
      const sign = change > 0 ? '+' : ''
      return `${sign}${(change * 100).toFixed(1)}%`
    },

    getChangeClass(change) {
      if (!change) return 'neutral'
      return change > 0 ? 'positive' : 'negative'
    },

    getStatusType(status) {
      const statusMap = {
        'active': 'success',
        'completed': 'info',
        'paused': 'warning',
        'draft': 'info'
      }
      return statusMap[status] || 'info'
    },

    renderCharts() {
      this.renderBehaviorChart()
      this.renderGameElementChart()
      this.renderRetentionChart()
    },

    renderBehaviorChart() {
      const chart = echarts.init(this.$refs.behaviorChart)
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 10,
          data: ['早晨学习', '下午学习', '晚上学习', '深夜学习']
        },
        series: [
          {
            name: '学习时间偏好',
            type: 'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            data: this.behaviorAnalysis.time_preferences || []
          }
        ]
      }
      chart.setOption(option)
    },

    renderGameElementChart() {
      const chart = echarts.init(this.$refs.gameElementChart)
      const data = this.gameElementEffectiveness.elements || []
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value'
        },
        yAxis: {
          type: 'category',
          data: data.map(item => item.element_name)
        },
        series: [
          {
            name: '效果评分',
            type: 'bar',
            data: data.map(item => item.effectiveness_score),
            itemStyle: {
              color: '#5470c6'
            }
          }
        ]
      }
      chart.setOption(option)
    },

    renderRetentionChart() {
      const chart = echarts.init(this.$refs.retentionChart)
      const retentionData = this.engagementMetrics.retention_trend || []
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['1日留存', '3日留存', '7日留存', '30日留存']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: retentionData.map(item => item.date)
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [
          {
            name: '1日留存',
            type: 'line',
            data: retentionData.map(item => item.day1_retention)
          },
          {
            name: '3日留存',
            type: 'line',
            data: retentionData.map(item => item.day3_retention)
          },
          {
            name: '7日留存',
            type: 'line',
            data: retentionData.map(item => item.day7_retention)
          },
          {
            name: '30日留存',
            type: 'line',
            data: retentionData.map(item => item.day30_retention)
          }
        ]
      }
      chart.setOption(option)
    },

    viewTestDetails(test) {
      // 查看A/B测试详情的逻辑
      this.$message.info(`查看测试详情: ${test.experiment_name}`)
    }
  }
}
</script>

<style scoped>
.user-engagement-dashboard {
  padding: 20px;
  background-color: #f5f5f5;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.title {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.metric-icon i {
  font-size: 24px;
  color: white;
}

.metric-content h3 {
  margin: 0 0 5px 0;
  font-size: 28px;
  font-weight: 700;
  color: #333;
}

.metric-content p {
  margin: 0 0 5px 0;
  color: #666;
  font-size: 14px;
}

.metric-change {
  font-size: 12px;
  font-weight: 600;
}

.metric-change.positive {
  color: #67c23a;
}

.metric-change.negative {
  color: #f56c6c;
}

.metric-change.neutral {
  color: #909399;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-container.full-width {
  grid-column: 1 / -1;
}

.chart-container h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.chart {
  width: 100%;
  height: 300px;
}

.ab-test-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.ab-test-section h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

@media (max-width: 768px) {
  .chart-row {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 15px;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>