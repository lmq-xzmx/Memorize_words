<template>
  <div class="dev-index">
    <!-- 装饰性背景元素 -->
    <div class="background-decoration">
      <div class="floating-circle floating-circle--1"></div>
      <div class="floating-circle floating-circle--2"></div>
      <div class="floating-circle floating-circle--3"></div>
      <div class="floating-circle floating-circle--4"></div>
      <div class="floating-circle floating-circle--5"></div>
    </div>

    <!-- 主要内容 -->
    <div class="header">
      <div class="header-icon">🚀</div>
      <div class="category-tabs">
        <div 
          v-for="category in categories" 
          :key="category.id"
          class="category-tab"
          :class="{ 'category-tab--active': selectedCategory === category.id }"
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
        :class="{ 'page-card--available': page.available, 'page-card--developing': !page.available, [`category-${page.category}`]: true }"
        @click="navigateToPage(page)"
      >
        <div class="card-header">
          <div class="page-icon">{{ page.icon }}</div>
          <div class="status-badge" :class="`status-badge--${page.status}`">{{ page.statusText }}</div>
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
import { userPersonalizationMixin, predefinedElementConfigs } from '../mixins/userPersonalization'

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
          path: '/word-learning/spelling',
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
          path: '/word-learning/flashcard',
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
          path: '/subscription-management',
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

<style lang="scss" scoped>
@use '../styles/variables.scss' as variables;
@use '../styles/mixins.scss' as *;

.dev-index {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow-x: hidden;
  padding: var(--spacing-8) var(--spacing-4);
}

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
  animation: float 6s ease-in-out infinite;
  
  &--1 {
    width: 80px;
    height: 80px;
    top: 10%;
    left: 10%;
    animation-delay: 0s;
  }
  
  &--2 {
    width: 120px;
    height: 120px;
    top: 20%;
    right: 15%;
    animation-delay: 2s;
  }
  
  &--3 {
    width: 60px;
    height: 60px;
    bottom: 30%;
    left: 20%;
    animation-delay: 4s;
  }
  
  &--4 {
    width: 100px;
    height: 100px;
    bottom: 20%;
    right: 10%;
    animation-delay: 1s;
  }
  
  &--5 {
    width: 40px;
    height: 40px;
    top: 50%;
    left: 50%;
    animation-delay: 3s;
  }
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
  margin-bottom: var(--spacing-12);
  position: relative;
  z-index: 1;
}

.header-icon {
  @include text-style('display', '4xl');
  margin-bottom: var(--spacing-4);
  animation: bounce 2s infinite;
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
  @include text-style('display', '3xl');
  font-weight: 700;
  color: white;
  margin-bottom: var(--spacing-4);
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  animation: slideInDown 1s ease-out;
}

.subtitle {
  @include text-style('body', 'xl');
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: var(--spacing-8);
  animation: slideInUp 1s ease-out 0.3s both;
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.category-tabs {
  @include flex-center;
  flex-wrap: wrap;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-8);
}

.category-tab {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: var(--border-radius-full);
  padding: var(--spacing-3) var(--spacing-6);
  cursor: pointer;
  @include transition('all', 0.3s);
  @include flex-start;
  gap: var(--spacing-2);
  color: var(--white);
  font-weight: 500;
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  }
  
  &--active {
    background: rgba(255, 255, 255, 0.4);
    border-color: rgba(255, 255, 255, 0.6);
    transform: scale(1.05);
  }
}

.category-icon {
  @include text-style('body', 'xl');
}

.category-count {
  background: rgba(255, 255, 255, 0.3);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-1) var(--spacing-2);
  @include text-style('body', 'xs');
  font-weight: 600;
}

.element-move-controls {
  @include flex-center;
  gap: var(--spacing-4);
  margin: var(--spacing-8) 0;
  flex-wrap: wrap;
}

.move-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: var(--white);
  padding: var(--spacing-3) var(--spacing-6);
  border-radius: var(--border-radius-full);
  cursor: pointer;
  @include transition('all', 0.3s);
  font-weight: 500;
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  }
}

.restore-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: var(--white);
  padding: var(--spacing-3) var(--spacing-6);
  border-radius: var(--border-radius-full);
  cursor: pointer;
  @include transition('all', 0.3s);
  font-weight: 500;
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  }
}

.inspect-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: var(--white);
  padding: var(--spacing-3) var(--spacing-6);
  border-radius: var(--border-radius-full);
  cursor: pointer;
  @include transition('all', 0.3s);
  font-weight: 500;
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  }
}

.test-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: var(--white);
  padding: var(--spacing-3) var(--spacing-6);
  border-radius: var(--border-radius-full);
  cursor: pointer;
  @include transition('all', 0.3s);
  font-weight: 500;
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  }
}

.check-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: var(--white);
  padding: var(--spacing-3) var(--spacing-6);
  border-radius: var(--border-radius-full);
  cursor: pointer;
  @include transition('all', 0.3s);
  font-weight: 500;
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  }
}

.page-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-8);
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.page-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: var(--border-radius-2xl);
  padding: var(--spacing-8);
  cursor: pointer;
  @include transition('all', 0.3s);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  animation: fadeInUp 0.6s ease-out;
  
  &:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  }
  
  &--available {
    border-left: 4px solid #4CAF50;
  }
  
  &--developing {
    border-left: 4px solid #FF9800;
    opacity: 0.8;
  }
}

.card-header {
  @include flex-between;
  margin-bottom: var(--spacing-6);
}

.page-icon {
  @include text-style('display', '2xl');
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.status-badge {
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--border-radius-2xl);
  @include text-style('body', 'xs');
  font-weight: 600;
  text-transform: uppercase;
  
  &--completed {
    background: #E8F5E8;
    color: #2E7D32;
  }
  
  &--developing {
    background: #FFF3E0;
    color: #F57C00;
  }
}

.card-content {
  // 卡片内容容器
}

.page-title {
  @include text-style('heading', 'xl');
  font-weight: 700;
  color: var(--color-slate-800);
  margin-bottom: var(--spacing-3);
}

.page-description {
  color: var(--color-slate-600);
  line-height: 1.6;
  margin-bottom: var(--spacing-6);
}

.card-footer {
  @include flex-between;
  padding-top: var(--spacing-4);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.page-path {
  font-family: 'Courier New', monospace;
  @include text-style('body', 'sm');
  color: var(--color-slate-500);
  background: var(--color-gray-100);
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--border-radius-md);
}

.visit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: var(--white);
  border: none;
  padding: var(--spacing-2) var(--spacing-5);
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  font-weight: 600;
  @include transition('all', 0.3s);
  text-decoration: none;
  display: inline-block;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
  }
}

.develop-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: var(--white);
  border: none;
  padding: var(--spacing-2) var(--spacing-5);
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  font-weight: 600;
  @include transition('all', 0.3s);
  text-decoration: none;
  display: inline-block;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(240, 147, 251, 0.4);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dev-index {
    padding: var(--spacing-4) var(--spacing-2);
  }
  
  .animated-title {
    @include text-style('display', 'xl');
  }
  
  .subtitle {
    @include text-style('body', 'base');
  }
  
  .page-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-6);
  }
  
  .category-tabs {
    gap: var(--spacing-2);
  }
  
  .category-tab {
    padding: var(--spacing-2) var(--spacing-4);
    @include text-style('body', 'sm');
  }
  
  .element-move-controls {
    gap: var(--spacing-2);
  }
  
  .move-btn {
     padding: var(--spacing-2) var(--spacing-4);
     @include text-style('body', 'sm');
   }
   
   .restore-btn {
     padding: var(--spacing-2) var(--spacing-4);
     @include text-style('body', 'sm');
   }
   
   .inspect-btn {
     padding: var(--spacing-2) var(--spacing-4);
     @include text-style('body', 'sm');
   }
   
   .test-btn {
     padding: var(--spacing-2) var(--spacing-4);
     @include text-style('body', 'sm');
   }
   
   .check-btn {
     padding: var(--spacing-2) var(--spacing-4);
     @include text-style('body', 'sm');
   }
}

@media (max-width: 480px) {
  .page-card {
    padding: var(--spacing-6);
  }
  
  .card-footer {
    flex-direction: column;
    gap: var(--spacing-4);
    align-items: stretch;
  }
  
  .page-path {
    text-align: center;
  }
}
</style>

