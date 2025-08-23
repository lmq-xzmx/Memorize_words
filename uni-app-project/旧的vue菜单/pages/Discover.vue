<template>
  <div class="dev-index">
    <!-- 装饰性背景元素 -->
    <div class="background-decoration">
      <div class="floating-circle circle-1"></div>
      <div class="floating-circle circle-2"></div>
      <div class="floating-circle circle-3"></div>
      <div class="floating-circle circle-4"></div>
      <div class="floating-circle circle-5"></div>
    </div>

    <!-- 主要内容 -->
    <div class="header">
      <div class="header-icon">🚀</div>
      <div class="category-tabs">
        <div 
          v-for="category in categories" 
          :key="category.id"
          class="category-tab"
          :class="{ 'active': selectedCategory === category.id }"
          @click="selectCategory(category.id)"
        >
          <span class="category-icon">{{ category.icon }}</span>
          <span class="category-name">{{ category.name }}</span>
          <span class="category-count">({{ categoryStats[category.id].total }})</span>
        </div>
      </div>
      <h1 class="animated-title">Natural English 开发中心</h1>
      <p class="subtitle">探索英语学习的无限可能</p>
      
      <!-- DOM元素移动测试控制面板 -->
      <div class="element-move-controls">
         <button @click="executeElementMove" class="move-btn">执行元素移动</button>
         <button @click="restoreElementPosition" class="restore-btn">恢复元素位置</button>
         <button @click="inspectDOM" class="inspect-btn">检查DOM结构</button>
         <button @click="testXPath" class="test-btn">测试XPath</button>
         <button @click="checkSpecificXPath" class="check-btn">检查指定XPath</button>
       </div>
    </div>

    <!-- 分类选择器 -->
    <div class="category-selector">
      <!-- 统计信息 -->
      <div class="stats-summary">
        <span class="stat-label">已完成:</span>
        <span class="stat-value completed">{{ categoryStats[selectedCategory].completed }}</span>
        <div class="stat-item">
          <span class="stat-label">开发中:</span>
          <span class="stat-value developing">{{ categoryStats[selectedCategory].developing }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">总计:</span>
          <span class="stat-value total">{{ categoryStats[selectedCategory].total }}</span>
        </div>
      </div>
    </div>

    <div class="page-grid">
      <div 
        v-for="page in filteredPages" 
        :key="page.path"
        class="page-card"
        :class="{ 'available': page.available, 'developing': !page.available, [`category-${page.category}`]: true }"
        @click="navigateToPage(page)"
      >
        <div class="card-header">
          <div class="page-icon">{{ page.icon }}</div>
          <div class="status-badge" :class="page.status">{{ page.statusText }}</div>
        </div>
        
        <div class="card-content">
          <h3 class="page-title">{{ page.title }}</h3>
          <p class="page-description">{{ page.description }}</p>
        </div>
        
        <div class="card-footer">
          <span class="page-path">{{ page.path }}</span>
          <button 
            v-if="page.available" 
            @click.stop="visitPage(page)"
            class="visit-btn"
          >
            访问页面
          </button>
          <button 
            v-else 
            @click.stop="developPage(page)"
            class="develop-btn"
          >
            开始开发（仅admin有）
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { userPersonalizationMixin, predefinedElementConfigs } from '../mixins/userPersonalization.js'

export default {
  mixins: [userPersonalizationMixin],
  name: 'Discover',
  data() {
    return {
      // 当前选中的分类
      selectedCategory: 'all',
      // 分类列表
      categories: [
        { id: 'all', name: '全部', icon: '🌟' },
        { id: 'word-training', name: '单词训练', icon: '📝' },
        { id: 'reading-training', name: '阅读训练', icon: '📖' },
        { id: 'listening-training', name: '听力训练', icon: '👂' },
        { id: 'conversation-training', name: '对话训练', icon: '💬' },
        { id: 'speaking-practice', name: '口语练习', icon: '🗣️' },
        { id: 'grammar-practice', name: '语法练习', icon: '📚' },
        { id: 'teacher-companion', name: '教师陪伴', icon: '👨‍🏫' },
        { id: 'management', name: '管理模块', icon: '⚙️' }
      ],
      // 所有页面项目（按分类整理）
      pages: [
        // 单词训练
        {
          title: '单词学习',
          description: 'H5版单词学习页面，展示单词详情和多种释义',
          path: '/word-learning',
          icon: '📚',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordLearning.vue',
          category: 'word-training'
        },
        {
          title: '单词详情',
          description: '单词详情页面，包含音标、释义、例句、词根词缀等完整信息',
          path: '/word-detail/institution',
          icon: '📝',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordDetail.vue',
          category: 'word-training'
        },
        {
          title: '词根分解',
          description: '词根拆解展示页面，支持词根分析和学习进度管理',
          path: '/word-root-analysis',
          icon: '🌱',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordRootAnalysis.vue',
          category: 'word-training'
        },
        {
          title: '拼写练习',
          description: '听音拼写练习页面，提升单词记忆',
          path: '/word-spelling',
          icon: '✍️',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordSpelling.vue',
          category: 'word-training'
        },
        {
          title: '闪卡学习',
          description: '翻转卡片学习单词页面',
          path: '/word-flashcard',
          icon: '🃏',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordFlashcard.vue',
          category: 'word-training'
        },
        {
          title: '模式匹配记忆',
          description: '三级学习模式：图片选择、选择题、单词补全，支持多种记忆方式',
          path: '/pattern-memory',
          icon: '🧠',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'PatternMemory.vue',
          category: 'word-training'
        },
        {
          title: '单词挑战',
          description: '单词挑战游戏页面',
          path: '/word-challenge',
          icon: '⚔️',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'word-challenge/index.vue',
          category: 'word-training'
        },
        {
          title: '单词复习',
          description: '单词复习页面',
          path: '/word-review',
          icon: '🔄',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'word-review/index.vue',
          category: 'word-training'
        },
        {
          title: '单词选择',
          description: '单词选择练习页面',
          path: '/word-selection',
          icon: '✅',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'word-selection/index.vue',
          category: 'word-training'
        },
        {
          title: '竞技模式',
          description: '与其他学习者竞技对战，团队挑战',
          path: '/word-selection-practice',
          icon: '🏆',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'word-selection-practice/index.vue',
          category: 'word-training'
        },
        {
          title: '快刷模式',
          description: '快速刷题模式，自动跳转下一题，提升学习效率',
          path: '/word-selection-practice',
          icon: '⚡',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'word-selection-practice/index.vue',
          category: 'word-training'
        },
        // 阅读训练
        {
          title: '单词阅读',
          description: 'H5版单词阅读页面，支持音频播放和进度跟踪',
          path: '/word-reading',
          icon: '📖',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordReading.vue',
          category: 'reading-training'
        },
        {
          title: '故事阅读',
          description: '交互式故事阅读页面，支持词性标注和生词收集功能',
          path: '/story-reading',
          icon: '📚',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'StoryReading.vue',
          category: 'reading-training'
        },
        // 教师陪伴
        {
          title: '师生互动',
          description: '师生互动练习模式，支持单词选择和实时反馈',
          path: '/word-selection-practice2',
          icon: '👥',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordSelection.vue',
          category: 'teacher-companion'
        },
        // 管理模块
        {
          title: '资源授权',
          description: '资源授权管理页面，管理订阅、权限和资源分享',
          path: '/resource-auth',
          icon: '🔐',
          status: 'developing',
          statusText: '开发中',
          available: false,
          component: 'ResourceAuth.vue',
          category: 'management'
        },
        {
          title: '订阅管理',
          description: '订阅功能管理页面，查看和管理您的订阅状态',
          path: '/subscription',
          icon: '💳',
          status: 'developing',
          statusText: '开发中',
          available: false,
          component: 'SubscriptionManagement.vue',
          category: 'management'
        },
        {
          title: '资源分享',
          description: '资源分享管理页面，分享和管理您的学习资源',
          path: '/resource-sharing',
          icon: '📤',
          status: 'developing',
          statusText: '开发中',
          available: false,
          component: 'ResourceSharing.vue',
          category: 'management'
        }
      ]
    }
  },
  computed: {
    // 根据选中分类过滤页面
    filteredPages() {
      if (this.selectedCategory === 'all') {
        return this.pages
      }
      return this.pages.filter(page => page.category === this.selectedCategory)
    },
    // 统计信息
    categoryStats() {
      const stats = {}
      this.categories.forEach(category => {
        if (category.id === 'all') {
          stats[category.id] = {
            total: this.pages.length,
            completed: this.pages.filter(p => p.status === 'completed').length,
            developing: this.pages.filter(p => p.status === 'developing').length
          }
        } else {
          const categoryPages = this.pages.filter(p => p.category === category.id)
          stats[category.id] = {
            total: categoryPages.length,
            completed: categoryPages.filter(p => p.status === 'completed').length,
            developing: categoryPages.filter(p => p.status === 'developing').length
          }
        }
      })
      return stats
    }
  },
  methods: {
    // 选择分类
    selectCategory(categoryId) {
      this.selectedCategory = categoryId
    },
    navigateToPage(page) {
      if (page.available) {
        this.$router.push(page.path)
      } else {
        this.developPage(page)
      }
    },
    visitPage(page) {
      this.$router.push(page.path)
    },
    developPage(page) {
      alert(`开始开发: ${page.title}\n路径: ${page.path}\n组件: ${page.component}`)
    },
    
    // 应用用户个性化设置
    applyUserPersonalization() {
      // 应用预定义的元素配置
      const configs = predefinedElementConfigs.discoverElements
      
      configs.forEach(config => {
        // 获取用户的个性化设置，如果没有则使用默认设置
        const userSettings = this.getElementSettings(config.elementKey, config.defaultSettings)
        
        // 查找并应用设置到对应的DOM元素
        const element = document.evaluate(
          config.xpath,
          document,
          null,
          XPathResult.FIRST_ORDERED_NODE_TYPE,
          null
        ).singleNodeValue
        
        if (element) {
          this.applyElementSettings(config.elementKey, element, userSettings)
        } else {
          console.warn(`未找到元素: ${config.xpath}`)
        }
      })
      
      console.log('用户个性化设置已应用到Discover页面')
    },
    
    // 执行DOM元素移动
    executeElementMove() {
      const moveConfigs = predefinedElementConfigs.moveOperations
      
      moveConfigs.forEach(moveConfig => {
        const result = this.moveElementByXPath(
          moveConfig.sourceXPath,
          moveConfig.targetXPath,
          moveConfig.position
        )
        
        if (result.success) {
          console.log(`元素移动成功: ${moveConfig.sourceXPath} -> ${moveConfig.targetXPath}`)
          alert(`元素移动成功！\n源元素: ${moveConfig.sourceXPath}\n目标容器: ${moveConfig.targetXPath}\n位置: ${moveConfig.position}`)
        } else {
          console.error(`元素移动失败: ${result.message}`)
          alert(`元素移动失败: ${result.message}`)
        }
      })
    },
    
    // 恢复元素移动
    restoreElementPosition() {
      const elementKey = 'move_item1_to_container' // 使用预定义的移动记录键
      const result = this.restoreElementMove(elementKey)
      
      if (result.success) {
        console.log('元素移动已恢复')
        alert('元素移动已恢复到原始位置！')
      } else {
        console.error(`恢复失败: ${result.message}`)
        alert(`恢复失败: ${result.message}`)
      }
    },
    
    // 检查DOM结构
    inspectDOM() {
      const suggestions = this.inspectDOMStructure('app')
      
      console.log('DOM结构检查结果:', suggestions)
      
      // 生成可读的报告
      let report = '=== DOM结构检查报告 ===\n\n'
      suggestions.forEach((item, index) => {
        if (index < 20) { // 只显示前20个元素避免过长
          const indent = '  '.repeat(item.depth)
          report += `${indent}${item.tagName}`
          if (item.id) report += `#${item.id}`
          if (item.className) report += `.${item.className.split(' ').join('.')}`
          report += `\n${indent}XPath: ${item.xpath}\n`
          if (item.textContent) report += `${indent}内容: ${item.textContent}\n`
          report += `\n`
        }
      })
      
      // 查找可能的目标元素
      const possibleTargets = suggestions.filter(item => 
        item.xpath.includes('div[3]') || 
        item.xpath.includes('div[2]') ||
        item.className.includes('content') ||
        item.className.includes('container')
      )
      
      if (possibleTargets.length > 0) {
        report += '\n=== 可能的目标元素 ===\n'
        possibleTargets.forEach(item => {
          report += `XPath: ${item.xpath}\n`
          report += `标签: ${item.tagName}, 类名: ${item.className}\n`
          if (item.textContent) report += `内容: ${item.textContent}\n`
          report += '\n'
        })
      }
      
      alert(report)
      return suggestions
    },
    
    // 测试特定XPath
    testXPath() {
      const testPaths = [
        '//*[@id="app"]/div[3]/div[2]/div[1]/div[1]',
        '//*[@id="app"]/div[3]/div[2]/div[1]',
        '//*[@id="app"]/div[2]/div[2]/div[1]/div[1]',
        '//*[@id="app"]/div[2]/div[2]/div[1]',
        '//*[@id="app"]/div[1]/div[2]/div[1]/div[1]',
        '//*[@id="app"]/div[1]/div[2]/div[1]'
      ]
      
      let report = '=== XPath测试结果 ===\n\n'
      
      testPaths.forEach(xpath => {
        try {
          const element = document.evaluate(
            xpath,
            document,
            null,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null
          ).singleNodeValue
          
          if (element) {
            report += `✅ 找到: ${xpath}\n`
            report += `   标签: ${element.tagName.toLowerCase()}\n`
            report += `   类名: ${element.className || '无'}\n`
            report += `   ID: ${element.id || '无'}\n`
            if (element.textContent) {
              report += `   内容: ${element.textContent.trim().substring(0, 50)}\n`
            }
            report += '\n'
          } else {
            report += `❌ 未找到: ${xpath}\n\n`
          }
        } catch (error) {
          report += `⚠️ 错误: ${xpath} - ${error.message}\n\n`
        }
      })
      
      console.log(report)
      alert(report)
    },
    
    // 检查指定XPath元素
    checkSpecificXPath() {
      const targetXPath = '/html/body/div/div/div[3]/div[2]/div[1]/div[1]/span[2]'
      
      try {
        const element = document.evaluate(
          targetXPath,
          document,
          null,
          XPathResult.FIRST_ORDERED_NODE_TYPE,
          null
        ).singleNodeValue
        
        let report = `=== 检查XPath: ${targetXPath} ===\n\n`
        
        if (element) {
          // 高亮显示元素
          element.style.border = '3px solid red'
          element.style.backgroundColor = 'yellow'
          element.style.zIndex = '9999'
          
          report += `✅ 找到元素!\n`
          report += `标签: ${element.tagName.toLowerCase()}\n`
          report += `类名: ${element.className || '无'}\n`
          report += `ID: ${element.id || '无'}\n`
          report += `文本内容: ${element.textContent?.trim() || '无文本'}\n`
          
          // 检查是否包含图标
          const icons = element.querySelectorAll('i, svg, .icon, [class*="icon"]')
          if (icons.length > 0) {
            report += `图标数量: ${icons.length}\n`
            icons.forEach((icon, index) => {
              report += `  图标${index + 1}: ${icon.tagName.toLowerCase()}`
              if (icon.className) report += ` class="${icon.className}"`
              report += '\n'
            })
          }
          
          // 显示HTML结构
          report += `\nHTML结构:\n${element.outerHTML.substring(0, 200)}...\n`
          
          // 3秒后移除高亮
          setTimeout(() => {
            element.style.border = ''
            element.style.backgroundColor = ''
            element.style.zIndex = ''
          }, 3000)
          
        } else {
          report += `❌ 未找到元素\n\n`
          
          // 尝试查找父级路径
           const parentPaths = [
             '/html/body/div',
             '/html/body/div/div',
             '/html/body/div/div/div[3]',
             '/html/body/div/div/div[3]/div[2]',
             '/html/body/div/div/div[3]/div[2]/div[1]',
             '/html/body/div/div/div[3]/div[2]/div[1]/div[1]',
             '/html/body/div/div/div[3]/div[2]/div[1]/div[1]/span[1]',
             '/html/body/div/div/div[3]/div[2]/div[1]/div[1]/span[3]'
           ]
          
          report += '尝试查找相关路径:\n'
          parentPaths.forEach(path => {
            const testElement = document.evaluate(
              path,
              document,
              null,
              XPathResult.FIRST_ORDERED_NODE_TYPE,
              null
            ).singleNodeValue
            
            if (testElement) {
              report += `✅ ${path}: ${testElement.tagName.toLowerCase()}`
              if (testElement.className) report += ` .${testElement.className}`
              if (testElement.textContent) {
                report += ` "${testElement.textContent.trim().substring(0, 30)}"`
              }
              report += '\n'
            } else {
              report += `❌ ${path}\n`
            }
          })
        }
        
        console.log(report)
        alert(report)
        
      } catch (error) {
        const errorMsg = `检查XPath时出错: ${error.message}`
        console.error(errorMsg)
        alert(errorMsg)
      }
    }
   },
   
   mounted() {
     this.calculateCategoryStats()
     
     // 应用用户个性化设置
     this.$nextTick(() => {
       this.applyUserPersonalization()
     })
   }
 }
</script>

<style scoped>
.dev-index {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  min-height: 100vh;
  color: white;
  position: relative;
  overflow: hidden;
}

/* 装饰性背景元素 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.floating-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 120px;
  height: 120px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 80px;
  height: 80px;
  top: 20%;
  right: 15%;
  animation-delay: 1s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  bottom: 20%;
  left: 5%;
  animation-delay: 2s;
}

.circle-4 {
  width: 100px;
  height: 100px;
  bottom: 30%;
  right: 10%;
  animation-delay: 3s;
}

.circle-5 {
  width: 60px;
  height: 60px;
  top: 50%;
  left: 50%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

.header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
  z-index: 1;
}

.header-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  animation: bounce 2s ease-in-out infinite;
  display: inline-block;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

.animated-title {
  font-size: 2.8rem;
  margin-bottom: 15px;
  text-shadow: 2px 2px 8px rgba(0,0,0,0.4);
  background: linear-gradient(45deg, #fff, #f0f8ff, #fff);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 3s ease-in-out infinite;
  font-weight: 700;
}

@keyframes shimmer {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  text-shadow: 1px 1px 4px rgba(0,0,0,0.3);
}

/* 分类选择器样式 */
.category-selector {
  margin-bottom: 30px;
  position: relative;
  z-index: 1;
}

.category-tabs {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.category-tab {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 25px;
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-weight: 500;
  min-width: 120px;
  justify-content: center;
}

.category-tab:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.category-tab.active {
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.1));
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.category-icon {
  font-size: 1.2rem;
}

.category-name {
  font-size: 0.9rem;
}

.category-count {
  font-size: 0.8rem;
  opacity: 0.8;
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

/* 统计信息样式 */
.stats-summary {
  display: flex;
  justify-content: center;
  gap: 25px;
  flex-wrap: wrap;
}

.stat-item {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.stat-value {
  font-weight: 700;
  font-size: 1rem;
  padding: 2px 8px;
  border-radius: 8px;
  min-width: 25px;
  text-align: center;
}

.stat-value.completed {
  background: linear-gradient(45deg, #28a745, #20c997);
  color: white;
}

.stat-value.developing {
  background: linear-gradient(45deg, #ffc107, #fd7e14);
  color: #333;
}

.stat-value.total {
  background: linear-gradient(45deg, #6f42c1, #e83e8c);
  color: white;
}

.page-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
  position: relative;
  z-index: 1;
}

.page-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 25px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  color: #333;
  position: relative;
  overflow: hidden;
}

.page-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  transition: left 0.5s;
}

.page-card:hover::before {
  left: 100%;
}

.page-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.page-card.available {
  border-left: 4px solid #28a745;
}

.page-card.developing {
  border-left: 4px solid #ffc107;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.page-icon {
  font-size: 2.5rem;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.completed {
  background: linear-gradient(45deg, #28a745, #20c997);
  color: white;
}

.status-badge.developing {
  background: linear-gradient(45deg, #ffc107, #fd7e14);
  color: #333;
}

.card-content {
  margin-bottom: 20px;
}

.page-title {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: #2c3e50;
  background: linear-gradient(45deg, #2c3e50, #3498db);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-description {
  color: #666;
  line-height: 1.6;
  font-size: 0.95rem;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.page-path {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.8rem;
  color: #666;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.visit-btn, .develop-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.visit-btn {
  background: linear-gradient(45deg, #007bff, #0056b3);
  color: white;
}

.visit-btn:hover {
  background: linear-gradient(45deg, #0056b3, #004085);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.develop-btn {
  background: linear-gradient(45deg, #ffc107, #e0a800);
  color: #333;
}

.develop-btn:hover {
  background: linear-gradient(45deg, #e0a800, #d39e00);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dev-index {
    padding: 15px;
  }
  
  .page-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .category-tabs {
    gap: 10px;
  }
  
  .category-tab {
    min-width: 100px;
    padding: 10px 15px;
  }
  
  .stats-summary {
    gap: 15px;
  }
  
  .animated-title {
    font-size: 2.2rem;
  }
  
  .header-icon {
    font-size: 3rem;
  }
}

/* DOM元素移动控制面板样式 */
.element-move-controls {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

.move-btn, .restore-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.move-btn {
  background: linear-gradient(45deg, rgba(40, 167, 69, 0.8), rgba(32, 201, 151, 0.8));
  color: white;
}

.move-btn:hover {
  background: linear-gradient(45deg, rgba(40, 167, 69, 1), rgba(32, 201, 151, 1));
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
}

.restore-btn {
  background: linear-gradient(45deg, rgba(255, 193, 7, 0.8), rgba(253, 126, 20, 0.8));
  color: #333;
}

.inspect-btn {
  background: linear-gradient(45deg, rgba(78, 205, 196, 0.8), rgba(68, 160, 141, 0.8));
  color: white;
}

.test-btn {
  background: linear-gradient(45deg, rgba(255, 167, 38, 0.8), rgba(255, 152, 0, 0.8));
  color: white;
}

.check-btn {
  background: linear-gradient(45deg, rgba(156, 39, 176, 0.8), rgba(103, 58, 183, 0.8));
  color: white;
}

.restore-btn:hover {
  background: linear-gradient(45deg, rgba(255, 193, 7, 1), rgba(253, 126, 20, 1));
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 193, 7, 0.4);
}

.inspect-btn:hover {
  background: linear-gradient(45deg, rgba(78, 205, 196, 1), rgba(68, 160, 141, 1));
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(78, 205, 196, 0.4);
}

.test-btn:hover {
  background: linear-gradient(45deg, rgba(255, 167, 38, 1), rgba(255, 152, 0, 1));
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 167, 38, 0.4);
}

.check-btn:hover {
  background: linear-gradient(45deg, rgba(156, 39, 176, 1), rgba(103, 58, 183, 1));
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(156, 39, 176, 0.4);
}
</style>