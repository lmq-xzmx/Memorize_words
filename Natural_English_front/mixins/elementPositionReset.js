/**
 * 元素位置重置混入
 * 用于清除可能影响元素位置的样式
 */

export default {
  name: 'ElementPositionReset',
  
  mounted() {
    this.resetElementPositions()
  },
  
  updated() {
    this.resetElementPositions()
  },
  
  methods: {
    /**
     * 重置元素位置样式
     */
    resetElementPositions() {
      try {
        // 重置XPath指定的元素
        this.resetElementByXPath('//*[@id="app"]/div[3]/div[2]/div[1]/div[5]')
        this.resetElementByXPath('//*[@id="app"]/div[3]/div[2]/div[1]')
        this.resetElementByXPath('//*[@id="app"]/div[2]/div/div[2]/div[1]')
        
        // 重置用户报告的按钮样式失效问题
        this.resetElementByXPath('//*[@id="app"]/div[2]/div/div[3]')
        
        // 重置用户报告的样式表丢失问题
        this.resetElementByXPath('//*[@id="app"]/div[3]/div/div[1]/div[1]')
        
        // 重置可能的词汇阅读中心相关元素
        this.resetVocabularyReadingCenter()
        
        console.log('元素位置样式已重置')
      } catch (error) {
        console.error('重置元素位置失败:', error)
      }
    },
    
    /**
     * 通过XPath重置元素样式
     * @param {string} xpath - XPath表达式
     */
    resetElementByXPath(xpath) {
      try {
        const element = document.evaluate(
          xpath,
          document,
          null,
          XPathResult.FIRST_ORDERED_NODE_TYPE,
          null
        ).singleNodeValue
        
        if (element) {
          this.resetElementStyle(element)
          console.log(`已重置元素样式: ${xpath}`)
        }
      } catch (error) {
        console.warn(`重置XPath元素失败: ${xpath}`, error)
      }
    },
    
    /**
     * 重置单个元素的样式
     * @param {HTMLElement} element - 要重置的元素
     */
    resetElementStyle(element) {
      if (!element) return
      
      // 重置位置相关样式
      element.style.position = 'static'
      element.style.top = 'auto'
      element.style.left = 'auto'
      element.style.right = 'auto'
      element.style.bottom = 'auto'
      element.style.zIndex = 'auto'
      element.style.transform = 'none'
      
      // 移除可能的置顶类名
      const pinnedClasses = [
        'pinned', 'sticky', 'fixed-top', 'position-fixed', 
        'position-sticky', 'position-absolute', 'top-0'
      ]
      
      pinnedClasses.forEach(className => {
        element.classList.remove(className)
      })
    },
    
    /**
     * 重置词汇阅读中心相关元素
     */
    resetVocabularyReadingCenter() {
      try {
        // 通过文本内容查找词汇阅读中心元素
        const elements = document.querySelectorAll('*')
        elements.forEach(element => {
          if (element.textContent && element.textContent.includes('词汇阅读中心')) {
            this.resetElementStyle(element)
          }
        })
        
        // 通过类名查找可能的相关元素
        const possibleClasses = [
          '.vocabulary-center', '.reading-center', '.learning-center',
          '.vocabulary-reading-center', '.moveable-element', '.user-personalized'
        ]
        
        possibleClasses.forEach(selector => {
          const elements = document.querySelectorAll(selector)
          elements.forEach(element => {
            this.resetElementStyle(element)
          })
        })
      } catch (error) {
        console.warn('重置词汇阅读中心元素失败:', error)
      }
    },
    
    /**
     * 强制重置所有可能的置顶元素
     */
    forceResetAllPinnedElements() {
      try {
        // 查找所有可能被置顶的元素
        const selectors = [
          '[style*="position: fixed"]',
          '[style*="position: sticky"]',
          '[style*="position: absolute"]',
          '[style*="top: 0"]',
          '.pinned', '.sticky', '.fixed-top'
        ]
        
        selectors.forEach(selector => {
          const elements = document.querySelectorAll(selector)
          elements.forEach(element => {
            this.resetElementStyle(element)
          })
        })
        
        console.log('已强制重置所有置顶元素')
      } catch (error) {
        console.error('强制重置置顶元素失败:', error)
      }
    }
  }
}