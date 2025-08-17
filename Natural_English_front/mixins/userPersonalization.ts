/**
 * 用户个性化混入
 * 提供用户偏好设置和个性化内容管理功能
 */

import { defineComponent } from 'vue'

// 用户偏好设置接口
interface UserPreferences {
  theme: 'light' | 'dark' | 'auto'
  language: string
  fontSize: 'small' | 'medium' | 'large'
  autoSave: boolean
}

// 个性化内容接口
interface PersonalizedContent {
  recommendedWords: string[]
  learningProgress: Record<string, any>
  achievements: Achievement[]
}

// 成就接口
interface Achievement {
  id: string
  name: string
  description: string
  earnedAt: Date
  category: string
}

// 元素位置配置接口
interface ElementPosition {
  x: number
  y: number
}

// 元素尺寸配置接口
interface ElementSize {
  width: string | number
  height: string | number
}

// 元素配置接口
interface ElementConfig {
  position: ElementPosition
  size: ElementSize
}

// 移动操作配置接口
interface MoveOperations {
  dragThreshold: number
  snapToGrid: boolean
  gridSize: number
  boundaries: {
    minX: number
    minY: number
    maxX: number
    maxY: number
  }
}

// 预定义元素配置接口
interface PredefinedElementConfigs {
  discoverElements: Record<string, ElementConfig>
  moveOperations: MoveOperations
  appElements: Record<string, ElementConfig>
  competitionElements: Record<string, ElementConfig>
}

// 预定义元素配置
export const predefinedElementConfigs: PredefinedElementConfigs = {
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
const userPersonalizationMixin = defineComponent({
  name: 'UserPersonalizationMixin',
  
  data() {
    return {
      userPreferences: {
        theme: 'light' as const,
        language: 'zh-CN',
        fontSize: 'medium' as const,
        autoSave: true
      } as UserPreferences,
      personalizedContent: {
        recommendedWords: [],
        learningProgress: {},
        achievements: []
      } as PersonalizedContent
    }
  },
  
  computed: {
    currentTheme(): string {
      return this.userPreferences.theme
    },
    
    currentLanguage(): string {
      return this.userPreferences.language
    },
    
    isAutoSaveEnabled(): boolean {
      return this.userPreferences.autoSave
    }
  },
  
  methods: {
    /**
     * 加载用户偏好设置
     */
    loadUserPreferences(): void {
      try {
        const saved = localStorage.getItem('userPreferences')
        if (saved) {
          this.userPreferences = { ...this.userPreferences, ...JSON.parse(saved) }
        }
      } catch (error) {
        console.error('加载用户偏好设置失败:', error)
      }
    },
    
    /**
     * 保存用户偏好设置
     */
    saveUserPreferences(): void {
      try {
        localStorage.setItem('userPreferences', JSON.stringify(this.userPreferences))
      } catch (error) {
        console.error('保存用户偏好设置失败:', error)
      }
    },
    
    /**
     * 更新主题
     * @param theme - 主题名称
     */
    updateTheme(theme: UserPreferences['theme']): void {
      this.userPreferences.theme = theme
      this.applyTheme(theme)
      this.saveUserPreferences()
    },
    
    /**
     * 应用主题
     * @param theme - 主题名称
     */
    applyTheme(theme: string): void {
      document.documentElement.setAttribute('data-theme', theme)
    },
    
    /**
     * 更新语言
     * @param language - 语言代码
     */
    updateLanguage(language: string): void {
      this.userPreferences.language = language
      this.saveUserPreferences()
    },
    
    /**
     * 更新字体大小
     * @param size - 字体大小
     */
    updateFontSize(size: UserPreferences['fontSize']): void {
      this.userPreferences.fontSize = size
      this.applyFontSize(size)
      this.saveUserPreferences()
    },
    
    /**
     * 应用字体大小
     * @param size - 字体大小
     */
    applyFontSize(size: string): void {
      const sizeMap = {
        small: '14px',
        medium: '16px',
        large: '18px'
      }
      document.documentElement.style.fontSize = sizeMap[size as keyof typeof sizeMap] || '16px'
    },
    
    /**
     * 切换自动保存
     */
    toggleAutoSave(): void {
      this.userPreferences.autoSave = !this.userPreferences.autoSave
      this.saveUserPreferences()
    },
    
    /**
     * 加载个性化内容
     */
    async loadPersonalizedContent(): Promise<void> {
      try {
        // 这里可以从API加载个性化内容
        // const response = await api.getPersonalizedContent()
        // this.personalizedContent = response.data
        console.log('个性化内容加载完成')
      } catch (error) {
        console.error('加载个性化内容失败:', error)
      }
    },
    
    /**
     * 重置用户偏好设置
     */
    resetUserPreferences(): void {
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
})

export default userPersonalizationMixin

export { userPersonalizationMixin }

// 导出类型
export type {
  UserPreferences,
  PersonalizedContent,
  Achievement,
  ElementPosition,
  ElementSize,
  ElementConfig,
  MoveOperations,
  PredefinedElementConfigs
}