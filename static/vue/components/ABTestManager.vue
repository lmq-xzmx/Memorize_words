<template>
  <div class="ab-test-manager">
    <!-- 页面标题和操作按钮 -->
    <div class="header-section">
      <h2 class="page-title">A/B测试管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <i class="el-icon-plus"></i>
        创建新实验
      </el-button>
    </div>

    <!-- 实验列表 -->
    <div class="experiments-list">
      <el-table :data="experiments" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="实验名称" width="200">
          <template #default="scope">
            <div class="experiment-name">
              <strong>{{ scope.row.name }}</strong>
              <p class="experiment-desc">{{ scope.row.description }}</p>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="start_date" label="开始时间" width="120">
          <template #default="scope">
            {{ formatDate(scope.row.start_date) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="end_date" label="结束时间" width="120">
          <template #default="scope">
            {{ formatDate(scope.row.end_date) }}
          </template>
        </el-table-column>
        
        <el-table-column label="参与者" width="120">
          <template #default="scope">
            <div class="participants-info">
              <div>对照组: {{ scope.row.control_group_size || 0 }}</div>
              <div>实验组: {{ scope.row.test_group_size || 0 }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="转化率" width="150">
          <template #default="scope">
            <div class="conversion-rates">
              <div>对照组: {{ formatPercentage(scope.row.conversion_rate_control) }}</div>
              <div>实验组: {{ formatPercentage(scope.row.conversion_rate_test) }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="统计显著性" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.statistical_significance ? 'success' : 'warning'">
              {{ scope.row.statistical_significance ? '显著' : '不显著' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button-group>
              <el-button size="small" @click="viewResults(scope.row)">查看结果</el-button>
              <el-button size="small" @click="editExperiment(scope.row)" :disabled="scope.row.status === 'completed'">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteExperiment(scope.row)" :disabled="scope.row.status === 'active'">删除</el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 创建/编辑实验对话框 -->
    <el-dialog
      :title="editingExperiment ? '编辑实验' : '创建新实验'"
      v-model="showCreateDialog"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="experimentForm" :rules="formRules" ref="experimentFormRef" label-width="120px">
        <el-form-item label="实验名称" prop="name">
          <el-input v-model="experimentForm.name" placeholder="请输入实验名称"></el-input>
        </el-form-item>
        
        <el-form-item label="实验描述" prop="description">
          <el-input
            type="textarea"
            v-model="experimentForm.description"
            placeholder="请输入实验描述"
            :rows="3"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="实验类型" prop="experiment_type">
          <el-select v-model="experimentForm.experiment_type" placeholder="请选择实验类型">
            <el-option label="游戏化元素" value="gamification"></el-option>
            <el-option label="界面设计" value="ui_design"></el-option>
            <el-option label="学习算法" value="algorithm"></el-option>
            <el-option label="推送策略" value="notification"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="目标指标" prop="target_metric">
          <el-select v-model="experimentForm.target_metric" placeholder="请选择目标指标">
            <el-option label="用户留存率" value="retention_rate"></el-option>
            <el-option label="学习时长" value="study_duration"></el-option>
            <el-option label="完成率" value="completion_rate"></el-option>
            <el-option label="参与度" value="engagement_score"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="实验时间">
          <el-date-picker
            v-model="experimentDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          >
          </el-date-picker>
        </el-form-item>
        
        <el-form-item label="流量分配">
          <div class="traffic-allocation">
            <div class="allocation-item">
              <label>对照组比例:</label>
              <el-slider
                v-model="experimentForm.control_percentage"
                :min="10"
                :max="90"
                :step="5"
                show-input
                style="margin-left: 10px;"
              ></el-slider>
            </div>
            <div class="allocation-item">
              <label>实验组比例:</label>
              <span>{{ 100 - experimentForm.control_percentage }}%</span>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="实验配置" prop="configuration">
          <el-input
            type="textarea"
            v-model="experimentForm.configuration"
            placeholder="请输入实验配置（JSON格式）"
            :rows="4"
          ></el-input>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="saveExperiment" :loading="saving">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 实验结果详情对话框 -->
    <el-dialog
      title="实验结果详情"
      v-model="showResultsDialog"
      width="800px"
    >
      <div v-if="selectedExperiment" class="results-content">
        <div class="results-summary">
          <h3>{{ selectedExperiment.name }}</h3>
          <p>{{ selectedExperiment.description }}</p>
          
          <div class="metrics-comparison">
            <div class="metric-group">
              <h4>对照组</h4>
              <div class="metric-item">
                <span>参与者数量:</span>
                <strong>{{ selectedExperiment.control_group_size }}</strong>
              </div>
              <div class="metric-item">
                <span>转化率:</span>
                <strong>{{ formatPercentage(selectedExperiment.conversion_rate_control) }}</strong>
              </div>
            </div>
            
            <div class="metric-group">
              <h4>实验组</h4>
              <div class="metric-item">
                <span>参与者数量:</span>
                <strong>{{ selectedExperiment.test_group_size }}</strong>
              </div>
              <div class="metric-item">
                <span>转化率:</span>
                <strong>{{ formatPercentage(selectedExperiment.conversion_rate_test) }}</strong>
              </div>
            </div>
          </div>
          
          <div class="statistical-analysis">
            <h4>统计分析</h4>
            <div class="analysis-item">
              <span>统计显著性:</span>
              <el-tag :type="selectedExperiment.statistical_significance ? 'success' : 'warning'">
                {{ selectedExperiment.statistical_significance ? '显著' : '不显著' }}
              </el-tag>
            </div>
            <div class="analysis-item">
              <span>置信度:</span>
              <strong>{{ formatPercentage(selectedExperiment.confidence_level) }}</strong>
            </div>
            <div class="analysis-item">
              <span>效果提升:</span>
              <strong :class="getImprovementClass(selectedExperiment.improvement_percentage)">
                {{ formatChange(selectedExperiment.improvement_percentage) }}
              </strong>
            </div>
          </div>
        </div>
        
        <!-- 结果图表 -->
        <div class="results-chart">
          <div ref="resultsChart" style="width: 100%; height: 300px;"></div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import axios from 'axios'

export default {
  name: 'ABTestManager',
  data() {
    return {
      experiments: [],
      loading: false,
      saving: false,
      showCreateDialog: false,
      showResultsDialog: false,
      editingExperiment: null,
      selectedExperiment: null,
      experimentDateRange: [],
      experimentForm: {
        name: '',
        description: '',
        experiment_type: '',
        target_metric: '',
        start_date: '',
        end_date: '',
        control_percentage: 50,
        configuration: '{}'
      },
      formRules: {
        name: [{ required: true, message: '请输入实验名称', trigger: 'blur' }],
        description: [{ required: true, message: '请输入实验描述', trigger: 'blur' }],
        experiment_type: [{ required: true, message: '请选择实验类型', trigger: 'change' }],
        target_metric: [{ required: true, message: '请选择目标指标', trigger: 'change' }]
      }
    }
  },
  mounted() {
    this.fetchExperiments()
  },
  watch: {
    experimentDateRange(val) {
      if (val && val.length === 2) {
        this.experimentForm.start_date = val[0]
        this.experimentForm.end_date = val[1]
      }
    }
  },
  methods: {
    async fetchExperiments() {
      this.loading = true
      try {
        const response = await axios.get('/api/engagement/ab-test-results/')
        this.experiments = response.data.results || []
      } catch (error) {
        console.error('获取实验列表失败:', error)
        this.$message.error('获取实验列表失败')
      } finally {
        this.loading = false
      }
    },

    async saveExperiment() {
      try {
        await this.$refs.experimentFormRef.validate()
        this.saving = true
        
        const data = { ...this.experimentForm }
        
        if (this.editingExperiment) {
          await axios.put(`/api/engagement/ab-test/${this.editingExperiment.id}/`, data)
          this.$message.success('实验更新成功')
        } else {
          await axios.post('/api/engagement/create-ab-test/', data)
          this.$message.success('实验创建成功')
        }
        
        this.showCreateDialog = false
        this.fetchExperiments()
      } catch (error) {
        console.error('保存实验失败:', error)
        this.$message.error('保存实验失败')
      } finally {
        this.saving = false
      }
    },

    editExperiment(experiment) {
      this.editingExperiment = experiment
      this.experimentForm = { ...experiment }
      this.experimentDateRange = [experiment.start_date, experiment.end_date]
      this.showCreateDialog = true
    },

    async deleteExperiment(experiment) {
      try {
        await this.$confirm('确定要删除这个实验吗？', '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await axios.delete(`/api/engagement/ab-test/${experiment.id}/`)
        this.$message.success('实验删除成功')
        this.fetchExperiments()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除实验失败:', error)
          this.$message.error('删除实验失败')
        }
      }
    },

    viewResults(experiment) {
      this.selectedExperiment = experiment
      this.showResultsDialog = true
      this.$nextTick(() => {
        this.renderResultsChart()
      })
    },

    renderResultsChart() {
      if (!this.$refs.resultsChart || !this.selectedExperiment) return
      
      const chart = echarts.init(this.$refs.resultsChart)
      const option = {
        title: {
          text: '转化率对比',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['对照组', '实验组'],
          top: 30
        },
        xAxis: {
          type: 'category',
          data: ['转化率']
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [
          {
            name: '对照组',
            type: 'bar',
            data: [(this.selectedExperiment.conversion_rate_control * 100).toFixed(2)],
            itemStyle: {
              color: '#91cc75'
            }
          },
          {
            name: '实验组',
            type: 'bar',
            data: [(this.selectedExperiment.conversion_rate_test * 100).toFixed(2)],
            itemStyle: {
              color: '#5470c6'
            }
          }
        ]
      }
      chart.setOption(option)
    },

    resetForm() {
      this.editingExperiment = null
      this.experimentForm = {
        name: '',
        description: '',
        experiment_type: '',
        target_metric: '',
        start_date: '',
        end_date: '',
        control_percentage: 50,
        configuration: '{}'
      }
      this.experimentDateRange = []
      if (this.$refs.experimentFormRef) {
        this.$refs.experimentFormRef.resetFields()
      }
    },

    getStatusType(status) {
      const statusMap = {
        'draft': 'info',
        'active': 'success',
        'paused': 'warning',
        'completed': 'info'
      }
      return statusMap[status] || 'info'
    },

    getStatusText(status) {
      const statusMap = {
        'draft': '草稿',
        'active': '进行中',
        'paused': '暂停',
        'completed': '已完成'
      }
      return statusMap[status] || status
    },

    formatDate(date) {
      if (!date) return '-'
      return new Date(date).toLocaleDateString()
    },

    formatPercentage(value) {
      if (value === null || value === undefined) return '-'
      return `${(value * 100).toFixed(2)}%`
    },

    formatChange(value) {
      if (value === null || value === undefined) return '-'
      const sign = value > 0 ? '+' : ''
      return `${sign}${(value * 100).toFixed(2)}%`
    },

    getImprovementClass(value) {
      if (!value) return ''
      return value > 0 ? 'positive' : 'negative'
    }
  }
}
</script>

<style scoped>
.ab-test-manager {
  padding: 20px;
  background-color: #f5f5f5;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.page-title {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.experiments-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.experiment-name strong {
  display: block;
  margin-bottom: 4px;
}

.experiment-desc {
  margin: 0;
  color: #666;
  font-size: 12px;
}

.participants-info,
.conversion-rates {
  font-size: 12px;
}

.participants-info div,
.conversion-rates div {
  margin-bottom: 2px;
}

.traffic-allocation {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
}

.allocation-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.allocation-item label {
  width: 100px;
  font-weight: 500;
}

.results-content {
  padding: 20px 0;
}

.results-summary h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.results-summary p {
  margin: 0 0 20px 0;
  color: #666;
}

.metrics-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.metric-group {
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.metric-group h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.statistical-analysis {
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.statistical-analysis h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.analysis-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.positive {
  color: #67c23a;
  font-weight: 600;
}

.negative {
  color: #f56c6c;
  font-weight: 600;
}

.results-chart {
  margin-top: 20px;
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    gap: 15px;
  }
  
  .metrics-comparison {
    grid-template-columns: 1fr;
  }
}
</style>