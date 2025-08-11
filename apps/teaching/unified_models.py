/**
 * DOM结构分析工具
 * 用于分析页面DOM结构，生成有效的XPath表达式
 */

export class DOMAnalyzer {
  /**
   * 分析指定容器的DOM结构
   * @param {string} containerId - 容器ID，默认为'app'
   * @param {number} maxDepth - 最大遍历深度，默认为4
   * @returns {Array} DOM结构信息数组
   */
  static analyzeDOMStructure(containerId = 'app', maxDepth = 4) {
    const container = document.getElementById(containerId)
    if (!container) {
      console.warn(`未找到容器: ${containerId}`)
      return []
    }

    const results = []
    
    const traverse = (element, depth = 0, path = []) => {
      if (depth > maxDepth) return
      
      const tagName = element.tagName.toLowerCase()
      const currentPath = [...path, tagName]
      
      // 生成XPath
      const xpath = this.generateXPath(element)
      
      // 收集元素信息
      const elementInfo = {
        xpath,
        tagName,
        id: element.id || '',
        className: element.className || '',
        textContent: element.textContent ? element.textContent.trim().substring(0, 100) : '',
        childrenCount: element.children.length,
        depth,
        path: currentPath.join(' > '),
        hasId: !!element.id,
        hasClass: !!element.className,
        isVisible: this.isElementVisible(element)
      }
      
      results.push(elementInfo)
      
      // 遍历子元素
      Array.from(element.children).forEach((child, index) => {
        traverse(child, depth + 1, currentPath)
      })
    }
    
    traverse(container)
    return results
  }
  
  /**
   * 生成元素的XPath表达式
   * @param {Element} element - DOM元素
   * @returns {string} XPath字符串
   */
  static generateXPath(element) {
    if (!element || element.nodeType !== Node.ELEMENT_NODE) {
      return ''
    }
    
    // 如果有ID，优先使用ID
    if (element.id) {
      return `//*[@id="${element.id}"]`
    }
    
    const parts = []
    let current = element
    
    while (current && current.nodeType === Node.ELEMENT_NODE && current !== document.body) {
      let index = 1
      let sibling = current.previousElementSibling
      
      while (sibling) {
        if (sibling.tagName === current.tagName) {
          index++
        }
        sibling = sibling.previousElementSibling
      }
      
      const tagName = current.tagName.toLowerCase()
      const pathPart = index > 1 ? `${tagName}[${index}]` : tagName
      parts.unshift(pathPart)
      
      current = current.parentElement
    }
    
    return '/' + parts.join('/')
  }
  
  /**
   * 检查元素是否可见
   * @param {Element} element - DOM元素
   * @returns {boolean} 是否可见
   */
  static isElementVisible(element) {
    const style = window.getComputedStyle(element)
    return style.display !== 'none' && 
           style.visibility !== 'hidden' && 
           style.opacity !== '0'
  }
  
  /**
   * 查找包含特定文本的元素
   * @param {string} text - 要查找的文本
   * @param {string} containerId - 容器ID
   * @returns {Array} 匹配的元素信息
   */
  static findElementsByText(text, containerId = 'app') {
    const structure = this.analyzeDOMStructure(containerId)
    return structure.filter(item => 
      item.textContent.toLowerCase().includes(text.toLowerCase())
    )
  }
  
  /**
   * 验证XPath表达式是否有效
   * @param {string} xpath - XPath表达式
   * @returns {Object} 验证结果
   */
  static validateXPath(xpath) {
    try {
      const result = document.evaluate(
        xpath,
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
      )
      
      const element = result.singleNodeValue
      return {
        isValid: !!element,
        element: element,
        xpath: xpath,
        message: element ? 'XPath有效' : 'XPath无效 - 未找到匹配元素'
      }
    } catch (error) {
      return {
        isValid: false,
        element: null,
        xpath: xpath,
        message: `XPath语法错误: ${error.message}`
      }
    }
  }
  
  /**
   * 生成DOM结构报告
   * @param {string} containerId - 容器ID
   * @returns {string} 格式化的报告
   */
  static generateDOMReport(containerId = 'app') {
    const structure = this.analyzeDOMStructure(containerId)
    
    let report = `DOM结构分析报告 (容器: ${containerId})\n`
    report += `总元素数量: ${structure.length}\n\n`
    
    structure.forEach((item, index) => {
      const indent = '  '.repeat(item.depth)
      report += `${index + 1}. ${indent}${item.tagName}`
      
      if (item.id) report += ` #${item.id}`
      if (item.className) report += ` .${item.className.split(' ').join('.')}`
      
      report += `\n${indent}   XPath: ${item.xpath}\n`
      
      if (item.textContent) {
        report += `${indent}   文本: ${item.textContent}\n`
      }
      
      report += `${indent}   可见: ${item.isVisible ? '是' : '否'}\n\n`
    })
    
    return report
  }
  
  /**
   * 在控制台输出DOM结构
   * @param {string} containerId - 容器ID
   */
  static logDOMStructure(containerId = 'app') {
    console.log(this.generateDOMReport(containerId))
  }
}

// 将工具暴露到全局，方便调试使用
if (typeof window !== 'undefined') {
  window.DOMAnalyzer = DOMAnalyzer
}

export default DOMAnalyzer