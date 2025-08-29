// 模拟数据文件
import { imageConfig } from '@/config/imageConfig'

// 单词数据
export const mockWords = [
  {
    id: 1,
    word: 'apple',
    pronunciation: '/ˈæpəl/',
    meaning: '苹果',
    partOfSpeech: 'n.',
    example: 'I eat an apple every day.',
    exampleTranslation: '我每天吃一个苹果。',
    difficulty: 1,
    category: 'food',
    image: imageConfig.getWordImage('apple'),
    audioUrl: '/audio/apple.mp3',
    synonyms: ['fruit'],
    antonyms: [],
    derivations: ['apples', 'apple-like']
  },
  {
    id: 2,
    word: 'book',
    pronunciation: '/bʊk/',
    meaning: '书',
    partOfSpeech: 'n.',
    example: 'She is reading a book.',
    exampleTranslation: '她正在读一本书。',
    difficulty: 1,
    category: 'education',
    image: imageConfig.getWordImage('book'),
    audioUrl: '/audio/book.mp3',
    synonyms: ['volume', 'publication'],
    antonyms: [],
    derivations: ['books', 'bookish', 'booking']
  },
  {
    id: 3,
    word: 'cat',
    pronunciation: '/kæt/',
    meaning: '猫',
    partOfSpeech: 'n.',
    example: 'The cat is sleeping on the sofa.',
    exampleTranslation: '猫正在沙发上睡觉。',
    difficulty: 1,
    category: 'animals',
    image: imageConfig.getWordImage('cat'),
    audioUrl: '/audio/cat.mp3',
    synonyms: ['feline', 'kitty'],
    antonyms: ['dog'],
    derivations: ['cats', 'catlike']
  },
  {
    id: 4,
    word: 'elephant',
    pronunciation: '/ˈeləfənt/',
    meaning: '大象',
    partOfSpeech: 'n.',
    example: 'The elephant is the largest land animal.',
    exampleTranslation: '大象是最大的陆地动物。',
    difficulty: 2,
    category: 'animals',
    image: imageConfig.getWordImage('elephant'),
    audioUrl: '/audio/elephant.mp3',
    synonyms: ['pachyderm'],
    antonyms: ['mouse'],
    derivations: ['elephants', 'elephantine']
  },
  {
    id: 5,
    word: 'guitar',
    pronunciation: '/ɡɪˈtɑːr/',
    meaning: '吉他',
    partOfSpeech: 'n.',
    example: 'He plays the guitar very well.',
    exampleTranslation: '他吉他弹得很好。',
    difficulty: 2,
    category: 'music',
    image: imageConfig.getWordImage('guitar'),
    audioUrl: '/audio/guitar.mp3',
    synonyms: ['instrument'],
    antonyms: [],
    derivations: ['guitars', 'guitarist']
  }
]

// 挑战题目数据
export const mockChallengeQuestions = [
  {
    id: 1,
    type: 'multiple_choice',
    question: 'What does "apple" mean?',
    word: 'apple',
    options: ['苹果', '香蕉', '橙子', '葡萄'],
    correctAnswer: 0,
    explanation: 'Apple means 苹果 in Chinese.',
    difficulty: 1,
    points: 10
  },
  {
    id: 2,
    type: 'fill_blank',
    question: 'I eat an _____ every day.',
    word: 'apple',
    correctAnswer: 'apple',
    explanation: 'The sentence means "我每天吃一个苹果".',
    difficulty: 1,
    points: 15
  },
  {
    id: 3,
    type: 'pronunciation',
    question: 'Choose the correct pronunciation of "elephant"',
    word: 'elephant',
    options: ['/ˈeləfənt/', '/ˈelɪfænt/', '/ˈeləfænt/', '/ˈelɪfənt/'],
    correctAnswer: 0,
    explanation: 'The correct pronunciation is /ˈeləfənt/.',
    difficulty: 2,
    points: 20
  },
  {
    id: 4,
    type: 'translation',
    question: 'Translate: "The cat is sleeping."',
    word: 'cat',
    correctAnswer: '猫正在睡觉',
    alternatives: ['猫在睡觉', '这只猫在睡觉', '猫咪在睡觉'],
    explanation: 'This sentence describes a cat that is currently sleeping.',
    difficulty: 2,
    points: 25
  }
]

// 用户学习统计数据
export const mockUserStats = {
  totalWords: 156,
  masteredWords: 89,
  learningWords: 45,
  newWords: 22,
  studyDays: 28,
  totalStudyTime: 1680, // 分钟
  averageAccuracy: 85.6,
  currentStreak: 7,
  longestStreak: 15,
  weeklyProgress: [
    { day: '周一', words: 12, time: 45 },
    { day: '周二', words: 8, time: 30 },
    { day: '周三', words: 15, time: 60 },
    { day: '周四', words: 10, time: 40 },
    { day: '周五', words: 18, time: 75 },
    { day: '周六', words: 20, time: 90 },
    { day: '周日', words: 14, time: 55 }
  ],
  categoryProgress: [
    { category: '食物', total: 25, mastered: 20, accuracy: 92 },
    { category: '动物', total: 30, mastered: 18, accuracy: 88 },
    { category: '教育', total: 35, mastered: 25, accuracy: 85 },
    { category: '音乐', total: 20, mastered: 12, accuracy: 78 },
    { category: '运动', total: 28, mastered: 14, accuracy: 82 }
  ]
}

// 复习数据
export const mockReviewData = {
  todayReview: {
    total: 25,
    completed: 18,
    accuracy: 88.9,
    timeSpent: 45 // 分钟
  },
  weeklyReview: {
    total: 156,
    completed: 134,
    accuracy: 85.2,
    timeSpent: 320 // 分钟
  },
  reviewWords: [
    {
      id: 1,
      word: 'apple',
      lastReview: '2024-01-15',
      nextReview: '2024-01-18',
      reviewCount: 5,
      accuracy: 95,
      difficulty: 1,
      status: 'mastered'
    },
    {
      id: 2,
      word: 'elephant',
      lastReview: '2024-01-14',
      nextReview: '2024-01-17',
      reviewCount: 3,
      accuracy: 75,
      difficulty: 2,
      status: 'learning'
    },
    {
      id: 3,
      word: 'guitar',
      lastReview: '2024-01-13',
      nextReview: '2024-01-16',
      reviewCount: 2,
      accuracy: 60,
      difficulty: 2,
      status: 'difficult'
    }
  ]
}

// 用户信息
export const mockUserInfo = {
  id: 1,
  username: 'demo_user',
  nickname: 'Demo用户',
  avatar: imageConfig.defaultImages.userAvatar,
  email: 'demo@example.com',
  level: 5,
  experience: 2580,
  nextLevelExp: 3000,
  joinDate: '2023-12-01',
  lastLoginDate: '2024-01-16',
  preferences: {
    dailyGoal: 20, // 每日学习单词数目标
    reminderTime: '20:00',
    soundEnabled: true,
    vibrationEnabled: true,
    theme: 'auto' // auto, light, dark
  },
  achievements: [
    {
      id: 1,
      name: '初学者',
      description: '学习第一个单词',
      icon: '🎯',
      unlockedAt: '2023-12-01'
    },
    {
      id: 2,
      name: '坚持者',
      description: '连续学习7天',
      icon: '🔥',
      unlockedAt: '2023-12-08'
    },
    {
      id: 3,
      name: '单词达人',
      description: '掌握100个单词',
      icon: '📚',
      unlockedAt: '2024-01-10'
    }
  ]
}

// 获取随机单词
export function getRandomWord() {
  return mockWords[Math.floor(Math.random() * mockWords.length)]
}

// 获取随机挑战题目
export function getRandomChallenge() {
  return mockChallengeQuestions[Math.floor(Math.random() * mockChallengeQuestions.length)]
}

// 根据难度获取单词
export function getWordsByDifficulty(difficulty) {
  return mockWords.filter(word => word.difficulty === difficulty)
}

// 根据分类获取单词
export function getWordsByCategory(category) {
  return mockWords.filter(word => word.category === category)
}

// 模拟API延迟
export function simulateApiDelay(ms = 500) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// 获取用户统计数据
export function getUserStats() {
  return mockUserStats
}

export default {
  mockWords,
  mockChallengeQuestions,
  mockUserStats,
  mockReviewData,
  mockUserInfo,
  getRandomWord,
  getRandomChallenge,
  getWordsByDifficulty,
  getWordsByCategory,
  simulateApiDelay,
  getUserStats
}