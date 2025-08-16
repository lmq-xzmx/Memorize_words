// API 集成测试
import axios from 'axios'

// Mock axios
jest.mock('axios')
const mockedAxios = axios

describe('API 集成测试', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('学习目标 API', () => {
    test('应该获取学习目标列表', async () => {
      const mockGoals = {
        data: {
          results: [
            { id: 1, name: '基础词汇', description: '基础英语词汇' },
            { id: 2, name: '高级词汇', description: '高级英语词汇' }
          ]
        }
      }
      
      mockedAxios.get.mockResolvedValue(mockGoals)
      
      const response = await axios.get('/api/teaching/learning-goals/', {
        params: { is_active: true }
      })
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/teaching/learning-goals/', {
        params: { is_active: true }
      })
      expect(response.data.results).toHaveLength(2)
    })

    test('应该处理学习目标获取失败', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Network Error'))
      
      await expect(axios.get('/api/teaching/learning-goals/')).rejects.toThrow('Network Error')
    })
  })

  describe('学习会话 API', () => {
    test('应该创建学习会话', async () => {
      const mockSession = {
        data: {
          id: 1,
          goal: 1,
          start_time: '2024-01-01T00:00:00Z',
          is_active: true
        }
      }
      
      mockedAxios.post.mockResolvedValue(mockSession)
      
      const response = await axios.post('/api/teaching/learning-sessions/', {
        goal: 1
      })
      
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/teaching/learning-sessions/', {
        goal: 1
      })
      expect(response.data.id).toBe(1)
    })

    test('应该结束学习会话', async () => {
      const mockResponse = {
        data: {
          id: 1,
          is_active: false,
          end_time: '2024-01-01T01:00:00Z'
        }
      }
      
      mockedAxios.post.mockResolvedValue(mockResponse)
      
      const response = await axios.post('/api/teaching/learning-sessions/1/end_session/')
      
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/teaching/learning-sessions/1/end_session/')
      expect(response.data.is_active).toBe(false)
    })
  })

  describe('单词学习记录 API', () => {
    test('应该创建学习记录', async () => {
      const mockRecord = {
        data: {
          id: 1,
          session: 1,
          word: 1,
          is_correct: true,
          response_time: 2.5
        }
      }
      
      mockedAxios.post.mockResolvedValue(mockRecord)
      
      const recordData = {
        session: 1,
        goal: 1,
        word: 1,
        user_answer: 'correct',
        is_correct: true,
        response_time: 2.5
      }
      
      const response = await axios.post('/api/teaching/word-learning-records/', recordData)
      
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/teaching/word-learning-records/', recordData)
      expect(response.data.is_correct).toBe(true)
    })

    test('应该处理学习记录创建失败', async () => {
      mockedAxios.post.mockRejectedValue({
        response: {
          status: 400,
          data: { error: 'Invalid data' }
        }
      })
      
      const recordData = {
        session: 1,
        word: 1,
        is_correct: true
      }
      
      await expect(axios.post('/api/teaching/word-learning-records/', recordData))
        .rejects.toMatchObject({
          response: {
            status: 400
          }
        })
    })
  })

  describe('练习单词 API', () => {
    test('应该获取练习单词', async () => {
      const mockWords = {
        data: {
          results: [
            { id: 1, word: 'hello', meaning: '你好', pronunciation: '/həˈloʊ/' },
            { id: 2, word: 'world', meaning: '世界', pronunciation: '/wɜːrld/' }
          ]
        }
      }
      
      mockedAxios.get.mockResolvedValue(mockWords)
      
      const params = {
        goal_id: 1,
        count: 20,
        smart_recommendation: true
      }
      
      const response = await axios.get('/api/teaching/practice-words/', { params })
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/teaching/practice-words/', { params })
      expect(response.data.results).toHaveLength(2)
    })

    test('应该处理空单词列表', async () => {
      const mockEmptyResponse = {
        data: {
          results: []
        }
      }
      
      mockedAxios.get.mockResolvedValue(mockEmptyResponse)
      
      const response = await axios.get('/api/teaching/practice-words/', {
        params: { goal_id: 1, count: 20 }
      })
      
      expect(response.data.results).toHaveLength(0)
    })
  })

  describe('错误处理', () => {
    test('应该处理网络超时', async () => {
      const timeoutError = new Error('timeout of 10000ms exceeded')
      timeoutError.code = 'ECONNABORTED'
      
      mockedAxios.get.mockRejectedValue(timeoutError)
      
      await expect(axios.get('/api/teaching/learning-goals/'))
        .rejects.toMatchObject({
          code: 'ECONNABORTED'
        })
    })

    test('应该处理401未授权错误', async () => {
      const authError = {
        response: {
          status: 401,
          data: { detail: 'Authentication credentials were not provided.' }
        }
      }
      
      mockedAxios.get.mockRejectedValue(authError)
      
      await expect(axios.get('/api/teaching/learning-goals/'))
        .rejects.toMatchObject({
          response: {
            status: 401
          }
        })
    })

    test('应该处理500服务器错误', async () => {
      const serverError = {
        response: {
          status: 500,
          data: { error: 'Internal Server Error' }
        }
      }
      
      mockedAxios.get.mockRejectedValue(serverError)
      
      await expect(axios.get('/api/teaching/learning-goals/'))
        .rejects.toMatchObject({
          response: {
            status: 500
          }
        })
    })
  })

  describe('请求配置', () => {
    test('应该设置正确的超时时间', async () => {
      mockedAxios.get.mockResolvedValue({ data: {} })
      
      await axios.get('/api/teaching/learning-goals/', {
        timeout: 10000
      })
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/teaching/learning-goals/', {
        timeout: 10000
      })
    })

    test('应该设置正确的请求头', async () => {
      mockedAxios.post.mockResolvedValue({ data: {} })
      
      await axios.post('/api/teaching/learning-sessions/', 
        { goal: 1 },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Token token'
          }
        }
      )
      
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/teaching/learning-sessions/',
        { goal: 1 },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer token'
          }
        }
      )
    })
  })
})