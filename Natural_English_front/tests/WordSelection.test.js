// WordSelection.vue 组件单元测试
import { mount, createLocalVue } from '@vue/test-utils'
import axios from 'axios'
import WordSelection from '@/pages/WordSelection.vue'

// Mock axios
jest.mock('axios')
const mockedAxios = axios

// Mock Vue Router
const mockRouter = {
  push: jest.fn(),
  go: jest.fn()
}

// Mock $message
const mockMessage = {
  error: jest.fn(),
  warning: jest.fn(),
  success: jest.fn()
}

describe('WordSelection.vue', () => {
  let wrapper
  const localVue = createLocalVue()

  beforeEach(() => {
    // 重置所有 mock
    jest.clearAllMocks()
    
    // Mock 学习目标数据
    mockedAxios.get.mockResolvedValue({
      data: {
        results: [
          { id: 1, name: '基础词汇', description: '基础英语词汇学习' },
          { id: 2, name: '高级词汇', description: '高级英语词汇学习' }
        ]
      }
    })

    wrapper = mount(WordSelection, {
      localVue,
      mocks: {
        $router: mockRouter,
        $message: mockMessage
      }
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  describe('组件初始化', () => {
    test('应该正确渲染组件', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.enhanced-word-practice-container').exists()).toBe(true)
    })

    test('应该加载学习目标', async () => {
      await wrapper.vm.$nextTick()
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/teaching/learning-goals/', {
        params: { is_active: true },
        timeout: 10000
      })
      expect(wrapper.vm.learningGoals).toHaveLength(2)
    })

    test('初始状态应该正确', () => {
      expect(wrapper.vm.practiceStarted).toBe(false)
      expect(wrapper.vm.practiceCompleted).toBe(false)
      expect(wrapper.vm.loading).toBe(false)
      expect(wrapper.vm.currentIndex).toBe(0)
    })
  })

  describe('练习配置', () => {
    test('应该验证练习配置', async () => {
      // 未选择学习目标和练习模式
      await wrapper.vm.startPractice()
      expect(mockMessage.warning).toHaveBeenCalledWith('请完成练习配置')
    })

    test('应该正确设置练习参数', () => {
      wrapper.setData({
        selectedGoalId: '1',
        practiceMode: 'meaning',
        wordsCount: 20
      })
      
      expect(wrapper.vm.selectedGoalId).toBe('1')
      expect(wrapper.vm.practiceMode).toBe('meaning')
      expect(wrapper.vm.wordsCount).toBe(20)
    })
  })

  describe('练习流程', () => {
    beforeEach(() => {
      // 设置练习配置
      wrapper.setData({
        selectedGoalId: '1',
        practiceMode: 'meaning',
        practiceWords: [
          { id: 1, word: 'hello', meaning: '你好' },
          { id: 2, word: 'world', meaning: '世界' }
        ]
      })
    })

    test('应该正确计算进度百分比', () => {
      wrapper.setData({ currentIndex: 1 })
      expect(wrapper.vm.progressPercentage).toBe(50)
    })

    test('应该正确记录答题结果', async () => {
      mockedAxios.post.mockResolvedValue({ data: { id: 1 } })
      
      wrapper.setData({
        learningSession: { id: 1 },
        questionStartTime: Date.now() - 1000
      })
      
      await wrapper.vm.answerWord(true)
      
      expect(wrapper.vm.wordRecords).toHaveLength(1)
      expect(wrapper.vm.wordRecords[0].is_correct).toBe(true)
      expect(wrapper.vm.showMeaning).toBe(true)
    })

    test('应该正确处理下一个单词', () => {
      wrapper.setData({ currentIndex: 0, showMeaning: true })
      wrapper.vm.nextWord()
      
      expect(wrapper.vm.currentIndex).toBe(1)
      expect(wrapper.vm.showMeaning).toBe(false)
    })

    test('应该在最后一个单词后完成练习', () => {
      wrapper.setData({ currentIndex: 1 }) // 最后一个单词
      const completePracticeSpy = jest.spyOn(wrapper.vm, 'completePractice')
      
      wrapper.vm.nextWord()
      
      expect(completePracticeSpy).toHaveBeenCalled()
    })
  })

  describe('错误处理', () => {
    test('应该处理网络错误', async () => {
      const networkError = new Error('Network Error')
      networkError.code = 'ECONNABORTED'
      
      await wrapper.vm.handleApiError(networkError, '测试错误')
      
      expect(wrapper.vm.networkError).toBe(true)
      expect(mockMessage.warning).toHaveBeenCalled()
    })

    test('应该处理会话过期', async () => {
      const sessionError = {
        response: { status: 401 }
      }
      
      await wrapper.vm.handleApiError(sessionError, '会话过期')
      
      expect(wrapper.vm.sessionExpired).toBe(true)
      expect(mockMessage.error).toHaveBeenCalledWith('登录已过期，请重新登录')
    })

    test('应该处理离线模式', async () => {
      // Mock navigator.onLine
      Object.defineProperty(navigator, 'onLine', {
        writable: true,
        value: false
      })
      
      const offlineError = new Error('Network Error')
      await wrapper.vm.handleApiError(offlineError, '离线错误')
      
      expect(wrapper.vm.offlineMode).toBe(true)
      expect(wrapper.vm.networkError).toBe(true)
    })
  })

  describe('音频功能', () => {
    test('应该处理音频播放错误', async () => {
      wrapper.setData({
        currentWord: { id: 1, word: 'test' }
      })
      
      // Mock speechSynthesis 不可用
      Object.defineProperty(window, 'speechSynthesis', {
        value: undefined
      })
      
      mockedAxios.get.mockRejectedValue(new Error('Audio Error'))
      
      await wrapper.vm.playAudio()
      
      expect(wrapper.vm.audioError).toBe(true)
    })
  })

  describe('数据同步', () => {
    test('应该同步待处理记录', async () => {
      wrapper.setData({
        pendingRecords: [
          { session: 1, word: 1, is_correct: true }
        ]
      })
      
      mockedAxios.post.mockResolvedValue({ data: { id: 1 } })
      
      await wrapper.vm.syncPendingRecords()
      
      expect(wrapper.vm.pendingRecords).toHaveLength(0)
      expect(wrapper.vm.offlineMode).toBe(false)
      expect(mockMessage.success).toHaveBeenCalledWith('学习记录已同步')
    })

    test('应该处理同步失败', async () => {
      wrapper.setData({
        pendingRecords: [
          { session: 1, word: 1, is_correct: true }
        ]
      })
      
      mockedAxios.post.mockRejectedValue(new Error('Sync Error'))
      
      await wrapper.vm.syncPendingRecords()
      
      expect(mockMessage.warning).toHaveBeenCalledWith('部分学习记录同步失败，将在下次练习时重试')
    })
  })

  describe('计算属性', () => {
    test('应该正确计算统计数据', () => {
      wrapper.setData({
        wordRecords: [
          { is_correct: true, word: { id: 1, word: 'test1' } },
          { is_correct: false, word: { id: 2, word: 'test2' } },
          { is_correct: true, word: { id: 3, word: 'test3' } }
        ]
      })
      
      expect(wrapper.vm.answeredCount).toBe(3)
      expect(wrapper.vm.correctCount).toBe(2)
      expect(wrapper.vm.incorrectCount).toBe(1)
      expect(wrapper.vm.accuracyPercentage).toBe(67)
    })

    test('应该正确分类掌握和复习单词', () => {
      wrapper.setData({
        wordRecords: [
          { is_correct: true, word: { id: 1, word: 'mastered' } },
          { is_correct: false, word: { id: 2, word: 'review' } }
        ]
      })
      
      expect(wrapper.vm.masteredWords).toHaveLength(1)
      expect(wrapper.vm.reviewWords).toHaveLength(1)
      expect(wrapper.vm.masteredWords[0].word).toBe('mastered')
      expect(wrapper.vm.reviewWords[0].word).toBe('review')
    })
  })
})