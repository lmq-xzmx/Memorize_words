<template>
  <div class="element-move-demo">
    <h1>DOM元素移动演示</h1>
    
    <!-- 控制面板 -->
    <div class="control-panel">
      <h2>移动操作控制</h2>
      <div class="move-controls">
        <button @click="performMove" class="move-btn">
          执行移动: div[1] → 父容器
        </button>
        <button @click="restoreMove" class="restore-btn">
          恢复移动操作
        </button>
        <button @click="resetDemo" class="reset-btn">
          重置演示
        </button>
      </div>
      
      <div class="status-info">
        <p><strong>操作状态:</strong> {{ moveStatus }}</p>
        <p><strong>移动记录:</strong> {{ moveRecord ? '已保存' : '无' }}</p>
      </div>
    </div>
    
    <!-- 演示区域 -->
    <div class="demo-area">
      <h2>演示区域</h2>
      <div class="app-simulation" id="app">
        <div class="level-1">
          <div class="level-2">
            <div class="level-3">
              <div class="container" data-path="//*[@id='app']/div[3]/div[2]/div[1]">
                <h3>目标容器 (div[1])</h3>
                <p>XPath: //*[@id="app"]/div[3]/div[2]/div[1]</p>
                
                <div class="moveable-item" data-path="//*[@id='app']/div[3]/div[2]/div[1]/div[1]">
                  <h4>可移动元素 (div[1])</h4>
                  <p>XPath: //*[@id="app"]/div[3]/div[2]/div[1]/div[1]</p>
                  <p>这个元素将被移动到父容器中</p>
                </div>
                
                <div class="static-item">
                  <h4>静态元素 (div[2])</h4>
                  <p>这个元素不会被移动</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 操作日志 -->
    <div class="operation-log">
      <h2>操作日志</h2>
      <div class="log-content">
        <div v-for="(log, index) in operationLogs" :key="index" class="log-item">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { userPersonalizationMixin, predefinedElementConfigs } from '../mixins/userPersonalization'

export default {
  name: 'ElementMoveDemo',
  mixins: [userPersonalizationMixin],
  
  data() {
    return {
      moveStatus: '待操作',
      moveRecord: null,
      operationLogs: [],
      originalParent: null,
      originalNextSibling: null
    }
  },
  
  methods: {
    /**
     * 执行元素移动操作
     */
    performMove() {
      const sourceXPath = '//*[@id="app"]/div[3]/div[2]/div[1]/div[1]'
      const targetXPath = '//*[@id="app"]/div[3]/div[2]/div[1]'
      
      // 保存原始位置信息
      this.saveOriginalPosition(sourceXPath)
      
      // 执行移动
      const success = this.moveElementByXPath(
        sourceXPath,
        targetXPath,
        'append',
        'demo_move_operation'
      )
      
      if (success) {
        this.moveStatus = '移动成功'
        this.moveRecord = this.getElementSettings('demo_move_operation')
        this.addLog('✅ 元素移动成功: div[1] 已移动到父容器末尾')
      } else {
        this.moveStatus = '移动失败'
        this.addLog('❌ 元素移动失败')
      }
    },
    
    /**
     * 恢复移动操作
     */
    restoreMove() {
      const success = this.restoreElementMove('demo_move_operation')
      
      if (success) {
        this.moveStatus = '恢复成功'
        this.addLog('🔄 移动操作已恢复')
      } else {
        this.moveStatus = '恢复失败'
        this.addLog('❌ 移动操作恢复失败')
      }
    },
    
    /**
     * 重置演示
     */
    resetDemo() {
      // 清除移动记录
      this.removeElementSettings('demo_move_operation')
      
      // 重置状态
      this.moveStatus = '已重置'
      this.moveRecord = null
      
      // 恢复原始位置
      if (this.originalParent && this.originalNextSibling) {
        const sourceElement = document.evaluate(
          '//*[@id="app"]/div[3]/div[2]/div[1]/div[1]',
          document,
          null,
          XPathResult.FIRST_ORDERED_NODE_TYPE,
          null
        ).singleNodeValue
        
        if (sourceElement) {
          this.originalParent.insertBefore(sourceElement, this.originalNextSibling)
        }
      }
      
      this.addLog('🔄 演示已重置到初始状态')
      
      // 重新加载页面以确保完全重置
      setTimeout(() => {
        location.reload()
      }, 1000)
    },
    
    /**
     * 保存元素原始位置
     */
    saveOriginalPosition(xpath) {
      const element = document.evaluate(
        xpath,
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
      ).singleNodeValue
      
      if (element) {
        this.originalParent = element.parentNode
        this.originalNextSibling = element.nextSibling
      }
    },
    
    /**
     * 添加操作日志
     */
    addLog(message) {
      const now = new Date()
      const time = now.toLocaleTimeString()
      
      this.operationLogs.unshift({
        time,
        message
      })
      
      // 限制日志数量
      if (this.operationLogs.length > 10) {
        this.operationLogs.pop()
      }
    },
    
    /**
     * 初始化演示
     */
    initializeDemo() {
      // 应用预定义样式
      this.$nextTick(() => {
        const configs = predefinedElementConfigs.appElements
        
        configs.forEach(config => {
          const element = document.evaluate(
            config.xpath,
            document,
            null,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null
          ).singleNodeValue
          
          if (element) {
            this.applyElementSettings(config.elementKey, element, config.defaultSettings)
          }
        })
        
        this.addLog('🚀 演示初始化完成')
      })
    }
  },
  
  mounted() {
    this.initializeDemo()
    
    // 检查是否有已保存的移动记录
    this.moveRecord = this.getElementSettings('demo_move_operation')
    if (this.moveRecord && this.moveRecord.sourceXPath) {
      this.moveStatus = '已有移动记录'
      this.addLog('📋 检测到已保存的移动记录')
    }
  }
}
</script>

