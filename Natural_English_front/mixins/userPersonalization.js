// 预定义元素配置
export const predefinedElementConfigs = {
  discoverElements: {
    // 发现页面元素配置
    mainContainer: {
      position: { x: 0, y: 0 },
      size: { width: '100%', height: 'auto' }
    },
    searchBar: {
      position: { x: 20, y: 20 },
      size: { width: '300px', height: '40px' }
    },
    contentGrid: {
      position: { x: 0, y: 80 },
      size: { width: '100%', height: 'auto' }
    }
  },
  
  moveOperations: {
    // 移动操作配置
    dragThreshold: 5,
    snapToGrid: true,
    gridSize: 10,
    boundaries: {
      minX: 0,
      minY: 0,
      maxX: 1200,
      maxY: 800
    }
  },
  
  appElements: {
    // 应用元素配置
    header: {
      position: { x: 0, y: 0 },
      size: { width: '100%', height: '60px' }
    },
    sidebar: {
      position: { x: 0, y: 60 },
      size: { width: '250px', height: 'calc(100vh - 60px)' }
    },
    mainContent: {
      position: { x: 250, y: 60 },
      size: { width: 'calc(100% - 250px)', height: 'calc(100vh - 60px)' }
    }
  },
  
  competitionElements: {
    // 竞赛元素配置
    timerDisplay: {
      position: { x: 20, y: 20 },
      size: { width: '120px', height: '40px' }
    },
    scoreBoard: {
      position: { x: 160, y: 20 },
      size: { width: '150px', height: '40px' }
    },
    questionArea: {
      position: { x: 20, y: 80 },
      size: { width: 'calc(100% - 40px)', height: '300px' }
    },
    answerOptions: {
      position: { x: 20, y: 400 },
      size: { width: 'calc(100% - 40px)', height: '200px' }
    }
  }
}

// 用户个性化 Mixin
const userPersonalizationMixin = {
  data() {
    return {
      userPreferences: {
        theme: 'light',
        language: 'zh-CN',
        fontSize: 'medium',
        autoSave: true
      },
      personalizedContent: {
        recommendedWords: [],
        learningProgress: {},
        achievements: []
      }
    }
  },
  
  computed: {
    currentTheme() {
      return this.userPreferences.theme
    },
    
    currentLanguage() {
      return this.userPreferences.language
    },
    
    isAutoSaveEnabled() {
      return this.userPreferences.autoSave
    }
  },
  
  methods: {
    // 加载用户偏好设置
    loadUserPreferences() {
      try {
        const saved = localStorage.getItem('userPreferences')
        if (saved) {
          this.userPreferences = { ...this.userPreferences, ...JSON.parse(saved) }
        }
      } catch (error) {
        console.warn('Failed to load user preferences:', error)
      }
    },
    
    // 保存用户偏好设置
    saveUserPreferences() {
      try {
        localStorage.setItem('userPreferences', JSON.stringify(this.userPreferences))
      } catch (error) {
        console.warn('Failed to save user preferences:', error)
      }
    },
    
    // 更新主题
    updateTheme(theme) {
      this.userPreferences.theme = theme
      this.saveUserPreferences()
      this.applyTheme(theme)
    },
    
    // 应用主题
    applyTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme)
    },
    
    // 更新语言
    updateLanguage(language) {
      this.userPreferences.language = language
      this.saveUserPreferences()
      // 这里可以添加语言切换逻辑
    },
    
    // 更新字体大小
    updateFontSize(size) {
      this.userPreferences.fontSize = size
      this.saveUserPreferences()
      this.applyFontSize(size)
    },
    
    // 应用字体大小
    applyFontSize(size) {
      const sizeMap = {
        small: '14px',
        medium: '16px',
        large: '18px'
      }
      document.documentElement.style.fontSize = sizeMap[size] || '16px'
    },
    
    // 切换自动保存
    toggleAutoSave() {
      this.userPreferences.autoSave = !this.userPreferences.autoSave
      this.saveUserPreferences()
    },
    
    // 加载个性化内容
    async loadPersonalizedContent() {
      try {
        // 这里可以添加从API获取个性化内容的逻辑
        console.log('Loading personalized content...')
      } catch (error) {
        console.error('Failed to load personalized content:', error)
      }
    },
    
    // 重置用户偏好
    resetUserPreferences() {
      this.userPreferences = {
        theme: 'light',
        language: 'zh-CN',
        fontSize: 'medium',
        autoSave: true
      }
      this.saveUserPreferences()
      this.applyTheme('light')
      this.applyFontSize('medium')
    }
  },
  
  mounted() {
    this.loadUserPreferences()
    this.applyTheme(this.userPreferences.theme)
    this.applyFontSize(this.userPreferences.fontSize)
    this.loadPersonalizedContent()
  }
}

// 导出 mixin 作为默认导出
export default userPersonalizationMixin

// 同时支持命名导出
export { userPersonalizationMixin }