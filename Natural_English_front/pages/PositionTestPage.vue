<template>
  <div class="position-test-page">
    <div class="test-header">
      <h1>位置限制清除测试页面</h1>
      <p>此页面用于测试XPath元素的位置限制是否已被清除</p>
    </div>
    
    <div class="test-controls">
      <button @click="testXPathElements" class="test-btn">测试XPath元素</button>
      <button @click="clearRestrictions" class="test-btn">手动清除限制</button>
      <button @click="showTestReport" class="test-btn">显示测试报告</button>
    </div>
    
    <div class="test-results" v-if="testResults.length > 0">
      <h2>测试结果</h2>
      <div v-for="(result, index) in testResults" :key="index" class="test-result-item">
        <div class="result-header">
          <span class="result-status" :class="result.status">{{ result.status === 'success' ? '✅' : '❌' }}</span>
          <span class="result-xpath">{{ result.xpath }}</span>
        </div>
        <div class="result-details">
          <p><strong>描述:</strong> {{ result.description }}</p>
          <p><strong>位置:</strong> {{ result.position }}</p>
          <p><strong>层级:</strong> {{ result.zIndex }}</p>
          <p><strong>变换:</strong> {{ result.transform }}</p>
        </div>
      </div>
    </div>
    
    <div class="xpath-info">
      <h2>目标XPath元素</h2>
      <div class="xpath-list">
        <div class="xpath-item">
          <code>//*[@id="app"]/div[3]/div[2]/div[1]/div[5]</code>
          <span class="xpath-desc">Dev-index链接元素</span>
        </div>
        <div class="xpath-item">
          <code>//*[@id="app"]/div[3]/div[2]/div[1]</code>
          <span class="xpath-desc">词汇阅读中心容器</span>
        </div>
        <div class="xpath-item">
          <code>//*[@id="app"]/div[2]/div/div[2]/div[1]</code>
          <span class="xpath-desc">需要取消置顶的元素</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PositionTestPage',
  data() {
    return {
      testResults: [],
      targetXPaths: [
        {
          xpath: '//*[@id="app"]/div[3]/div[2]/div[1]/div[5]',
          description: 'Dev-index链接元素，应该打开 http://localhost:3000/dev-index'
        },
        {
          xpath: '//*[@id="app"]/div[3]/div[2]/div[1]',
          description: '词汇阅读中心容器，不应该被置顶'
        },
        {
          xpath: '//*[@id="app"]/div[2]/div/div[2]/div[1]',
          description: '需要取消置顶的元素，应该是静态定位'
        }
      ]
    }
  },
  
  mounted() {
    // 页面加载后自动测试
    setTimeout(() => {
      this.testXPathElements()
    }, 1000)
  },
  
  methods: {
    /**
     * 测试XPath元素
     */
    testXPathElements() {
      this.testResults = []
      
      this.targetXPaths.forEach(target => {
        try {
          const element = document.evaluate(
            target.xpath,
            document,
            null,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null
          ).singleNodeValue
          
          if (element) {
            const styles = window.getComputedStyle(element)
            const result = {
              xpath: target.xpath,
              description: target.description,
              status: this.isPositionNormal(styles) ? 'success' : 'error',
              position: styles.position,
              zIndex: styles.zIndex,
              transform: styles.transform,
              top: styles.top,
              element: element
            }
            
            this.testResults.push(result)
            
            // 高亮显示找到的元素
            this.highlightElement(element, result.status === 'success')
          } else {
            this.testResults.push({
              xpath: target.xpath,
              description: target.description,
              status: 'error',
              position: '元素未找到',
              zIndex: 'N/A',
              transform: 'N/A',
              top: 'N/A'
            })
          }
        } catch (error) {
          this.testResults.push({
            xpath: target.xpath,
            description: target.description,
            status: 'error',
            position: `错误: ${error.message}`,
            zIndex: 'N/A',
            transform: 'N/A',
            top: 'N/A'
          })
        }
      })
    },
    
    /**
     * 检查位置是否正常
     */
    isPositionNormal(styles) {
      return styles.position === 'static' && 
             (styles.zIndex === 'auto' || styles.zIndex === '0') &&
             styles.transform === 'none'
    },
    
    /**
     * 高亮显示元素
     */
    highlightElement(element, isSuccess) {
      const originalStyle = {
        border: element.style.border,
        backgroundColor: element.style.backgroundColor,
        zIndex: element.style.zIndex
      }
      
      // 设置高亮样式
      element.style.border = isSuccess ? '3px solid green' : '3px solid red'
      element.style.backgroundColor = isSuccess ? 'rgba(0, 255, 0, 0.1)' : 'rgba(255, 0, 0, 0.1)'
      element.style.zIndex = '9999'
      
      // 3秒后恢复原样
      setTimeout(() => {
        element.style.border = originalStyle.border
        element.style.backgroundColor = originalStyle.backgroundColor
        element.style.zIndex = originalStyle.zIndex
      }, 3000)
    },
    
    /**
     * 手动清除限制
     */
    clearRestrictions() {
      if (window.clearPositionRestrictions) {
        window.clearPositionRestrictions()
        this.$nextTick(() => {
          setTimeout(() => {
            this.testXPathElements()
          }, 500)
        })
      } else {
        alert('位置清除工具未加载')
      }
    },
    
    /**
     * 显示测试报告
     */
    showTestReport() {
      const report = this.generateTestReport()
      console.log('=== 位置测试报告 ===')
      console.log(report)
      alert('测试报告已输出到控制台，请按F12查看')
    },
    
    /**
     * 生成测试报告
     */
    generateTestReport() {
      let report = '位置限制清除测试报告\n'
      report += '=' .repeat(50) + '\n\n'
      
      this.testResults.forEach((result, index) => {
        report += `测试 ${index + 1}: ${result.status === 'success' ? '通过' : '失败'}\n`
        report += `XPath: ${result.xpath}\n`
        report += `描述: ${result.description}\n`
        report += `位置: ${result.position}\n`
        report += `层级: ${result.zIndex}\n`
        report += `变换: ${result.transform}\n`
        if (result.top) report += `顶部: ${result.top}\n`
        report += '-'.repeat(30) + '\n\n'
      })
      
      const successCount = this.testResults.filter(r => r.status === 'success').length
      const totalCount = this.testResults.length
      
      report += `总结: ${successCount}/${totalCount} 个元素通过测试\n`
      report += `成功率: ${((successCount / totalCount) * 100).toFixed(1)}%\n`
      
      return report
    }
  }
}
</script>

