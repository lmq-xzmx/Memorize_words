/**
 * 元素位置重置混入
 * 用于清除可能影响元素位置的样式
 */

import { defineComponent, nextTick, onMounted, onUpdated } from 'vue'

// 元素样式重置接口
interface ElementStyle {
  position?: string
  top?: string
  left?: string
  right?: string
  bottom?: string
  transform?: string
  margin?: string
  padding?: string
  zIndex?: string
}

/**
 * 重置元素位置样式
 */
function resetElementPositions(): void {
  try {
    // 重置XPath指定的元素
    resetElementByXPath('//*[@id="app"]/div[3]/div[2]/div[1]/div[5]')
    resetElementByXPath('//*[@id="app"]/div[3]/div[2]/div[1]')
    resetElementByXPath('//*[@id="app"]/div[2]/div/div[2]/div[1]')
    
    // 重置用户报告的按钮样式失效问题
    resetElementByXPath('//*[@id="app"]/div[2]/div/div[3]')
    
    // 重置用户报告的样式表丢失问题
    resetElementByXPath('//*[@id="app"]/div[3]/div/div[1]/div[1]')
    
    // 重置可能的词汇阅读中心相关元素
    resetVocabularyReadingCenter()
    
    console.log('元素位置样式已重置')
  } catch (error) {
    console.error('重置元素位置失败:', error)
  }
}

/**
 * 通过XPath重置元素样式
 * @param xpath - XPath表达式
 */
function resetElementByXPath(xpath: string): void {
  try {
    const element = document.evaluate(
      xpath,
      document,
      null,
      XPathResult.FIRST_ORDERED_NODE_TYPE,
      null
    ).singleNodeValue as HTMLElement
    
    if (element) {
      resetElementStyle(element)
    }
  } catch (error) {
    console.warn(`XPath重置失败: ${xpath}`, error)
  }
}

/**
 * 重置单个元素的样式
 * @param element - 要重置的HTML元素
 */
function resetElementStyle(element: HTMLElement): void {
  const resetStyles: ElementStyle = {
    position: '',
    top: '',
    left: '',
    right: '',
    bottom: '',
    transform: '',
    margin: '',
    padding: '',
    zIndex: ''
  }
  
  Object.keys(resetStyles).forEach(key => {
    element.style.setProperty(key, resetStyles[key as keyof ElementStyle] || '')
  })
}

/**
 * 重置词汇阅读中心相关元素
 */
function resetVocabularyReadingCenter(): void {
  try {
    const selectors = [
      '.vocabulary-reading-center',
      '.word-display-area',
      '.reading-progress-bar',
      '.vocabulary-controls'
    ]
    
    selectors.forEach(selector => {
      const elements = document.querySelectorAll(selector)
      elements.forEach(element => {
        resetElementStyle(element as HTMLElement)
      })
    })
  } catch (error) {
    console.warn('词汇阅读中心重置失败:', error)
  }
}

/**
 * 强制重置所有固定定位元素
 */
function forceResetAllPinnedElements(): void {
  try {
    const pinnedElements = document.querySelectorAll('[style*="position: fixed"], [style*="position: absolute"]')
    pinnedElements.forEach(element => {
      resetElementStyle(element as HTMLElement)
    })
    
    console.log('所有固定定位元素已重置')
  } catch (error) {
    console.error('强制重置固定定位元素失败:', error)
  }
}

export default defineComponent({
  name: 'ElementPositionReset',
  
  setup() {
    onMounted(() => {
      nextTick(() => {
        resetElementPositions()
      })
    })

    onUpdated(() => {
      nextTick(() => {
        resetElementPositions()
      })
    })

    return {
      resetElementPositions,
      resetElementByXPath,
      resetElementStyle,
      resetVocabularyReadingCenter,
      forceResetAllPinnedElements
    }
  }
})

export type { ElementStyle }