import { reactive, readonly, computed, Ref, ComputedRef } from 'vue'

// 类型定义
interface User {
  level: number;
  experience: number;
  coins: number;
  character: string;
  title: string;
}

interface Progress {
  wordsLearned: number;
  currentStreak: number;
  totalSessions: number;
  averageAccuracy: number;
  bestStreak: number;
}

interface Collections {
  characters: string[];
  pets: string[];
  themes: string[];
}

interface Session {
  currentScore: number;
  combo: number;
  maxCombo: number;
  correctAnswers: number;
  totalAnswers: number;
  startTime: number | null;
}

interface GameState {
  user: User;
  progress: Progress;
  achievements: string[];
  collections: Collections;
  session: Session;
}

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  reward: { coins: number };
}

interface GameStateReturn {
  gameState: GameState;
  experienceToNextLevel: ComputedRef<number>;
  experienceProgress: ComputedRef<number>;
  sessionAccuracy: ComputedRef<number>;
  updateExperience: (points: number) => void;
  levelUp: () => void;
  triggerLevelUpEffect: () => void;
  unlockAchievement: (achievementId: string) => void;
  triggerAchievementEffect: (achievementId: string) => void;
  handleAnswer: (isCorrect: boolean, responseTime?: number) => void;
  startSession: () => void;
  endSession: () => void;
  resetSession: () => void;
  updateProgress: () => void;
  checkAchievements: () => void;
  saveGameState: () => void;
  loadGameState: () => void;
}

// 游戏状态管理
export function useGameState(): GameStateReturn {
  const gameState: GameState = reactive({
    user: {
      level: 1,
      experience: 0,
      coins: 100,
      character: 'default',
      title: 'Beginner'
    },
    progress: {
      wordsLearned: 0,
      currentStreak: 0,
      totalSessions: 0,
      averageAccuracy: 0,
      bestStreak: 0
    },
    achievements: [],
    collections: {
      characters: ['default'],
      pets: [],
      themes: ['classic']
    },
    session: {
      currentScore: 0,
      combo: 0,
      maxCombo: 0,
      correctAnswers: 0,
      totalAnswers: 0,
      startTime: null
    }
  })

  // 计算属性
  const experienceToNextLevel = computed(() => {
    return gameState.user.level * 100
  })

  const experienceProgress = computed(() => {
    return (gameState.user.experience / experienceToNextLevel.value) * 100
  })

  const sessionAccuracy = computed(() => {
    if (gameState.session.totalAnswers === 0) return 0
    return Math.round((gameState.session.correctAnswers / gameState.session.totalAnswers) * 100)
  })

  // 经验值更新
  const updateExperience = (points: number): void => {
    gameState.user.experience += points
    
    // 检查是否升级
    while (gameState.user.experience >= experienceToNextLevel.value) {
      levelUp()
    }
  }

  // 升级处理
  const levelUp = (): void => {
    gameState.user.experience -= experienceToNextLevel.value
    gameState.user.level++
    gameState.user.coins += gameState.user.level * 10
    
    // 触发升级动画和奖励
    triggerLevelUpEffect()
  }

  // 升级效果
  const triggerLevelUpEffect = (): void => {
    // 这里可以触发升级动画
    console.log(`🎉 升级到 ${gameState.user.level} 级！获得 ${gameState.user.level * 10} 金币！`)
  }

  // 解锁成就
  const unlockAchievement = (achievementId: string): void => {
    if (!gameState.achievements.includes(achievementId)) {
      gameState.achievements.push(achievementId)
      // 触发成就解锁动画
      triggerAchievementEffect(achievementId)
    }
  }

  // 成就解锁效果
  const triggerAchievementEffect = (achievementId: string): void => {
    console.log(`🏆 解锁成就: ${achievementId}`)
  }

  // 答题处理
  const handleAnswer = (isCorrect: boolean, responseTime: number = 1000): void => {
    gameState.session.totalAnswers++
    
    if (isCorrect) {
      gameState.session.correctAnswers++
      gameState.session.combo++
      gameState.session.maxCombo = Math.max(gameState.session.maxCombo, gameState.session.combo)
      
      // 计算得分（基于准确性、速度和连击）
      const baseScore = 10
      const speedBonus = Math.max(0, 5 - Math.floor(responseTime / 1000))
      const comboBonus = Math.min(gameState.session.combo * 2, 20)
      const totalScore = baseScore + speedBonus + comboBonus
      
      gameState.session.currentScore += totalScore
      updateExperience(totalScore)
      
      // 检查连击成就
      checkComboAchievements()
    } else {
      gameState.session.combo = 0
    }
    
    // 更新平均准确率
    updateAverageAccuracy()
  }

  // 检查连击成就
  const checkComboAchievements = () => {
    const combo = gameState.session.combo
    if (combo === 5) unlockAchievement('combo_5')
    if (combo === 10) unlockAchievement('combo_10')
    if (combo === 20) unlockAchievement('combo_20')
  }

  // 更新平均准确率
  const updateAverageAccuracy = () => {
    const currentAccuracy = sessionAccuracy.value
    const totalSessions = gameState.progress.totalSessions
    const previousAverage = gameState.progress.averageAccuracy
    
    gameState.progress.averageAccuracy = Math.round(
      (previousAverage * totalSessions + currentAccuracy) / (totalSessions + 1)
    )
  }

  // 开始新会话
  const startSession = () => {
    gameState.session = {
      currentScore: 0,
      combo: 0,
      maxCombo: 0,
      correctAnswers: 0,
      totalAnswers: 0,
      startTime: Date.now()
    }
  }

  // 结束会话
  const endSession = () => {
    gameState.progress.totalSessions++
    gameState.progress.wordsLearned += gameState.session.correctAnswers
    
    // 更新最佳连击
    gameState.progress.bestStreak = Math.max(
      gameState.progress.bestStreak, 
      gameState.session.maxCombo
    )
    
    // 更新当前连续学习天数（简化版）
    gameState.progress.currentStreak++
    
    // 检查会话成就
    checkSessionAchievements()
  }

  // 检查会话成就
  const checkSessionAchievements = () => {
    const accuracy = sessionAccuracy.value
    const score = gameState.session.currentScore
    
    if (accuracy === 100) unlockAchievement('perfect_session')
    if (accuracy >= 90) unlockAchievement('excellent_session')
    if (score >= 200) unlockAchievement('high_scorer')
    if (gameState.progress.totalSessions === 1) unlockAchievement('first_session')
    if (gameState.progress.totalSessions === 10) unlockAchievement('dedicated_learner')
  }

  // 购买物品
  const purchaseItem = (itemId, cost) => {
    if (gameState.user.coins >= cost) {
      gameState.user.coins -= cost
      
      // 根据物品类型添加到收集中
      if (itemId.startsWith('character_')) {
        gameState.collections.characters.push(itemId)
      } else if (itemId.startsWith('pet_')) {
        gameState.collections.pets.push(itemId)
      } else if (itemId.startsWith('theme_')) {
        gameState.collections.themes.push(itemId)
      }
      
      return true
    }
    return false
  }

  // 保存到本地存储
  const saveToLocalStorage = () => {
    localStorage.setItem('gameState', JSON.stringify(gameState))
  }

  // 从本地存储加载
  const loadFromLocalStorage = () => {
    const saved = localStorage.getItem('gameState')
    if (saved) {
      const savedState = JSON.parse(saved)
      Object.assign(gameState, savedState)
    }
  }

  // 初始化时加载数据
  loadFromLocalStorage()

  return {
    gameState: readonly(gameState),
    experienceToNextLevel,
    experienceProgress,
    sessionAccuracy,
    updateExperience,
    levelUp,
    unlockAchievement,
    handleAnswer,
    startSession,
    endSession,
    purchaseItem,
    saveToLocalStorage,
    loadFromLocalStorage
  }
}

// 成就定义
export const ACHIEVEMENTS = {
  first_session: {
    id: 'first_session',
    name: '初次尝试',
    description: '完成第一次练习',
    icon: '🎯',
    reward: { coins: 20 }
  },
  combo_5: {
    id: 'combo_5',
    name: '连击新手',
    description: '连续答对5题',
    icon: '🔥',
    reward: { coins: 30 }
  },
  combo_10: {
    id: 'combo_10',
    name: '连击高手',
    description: '连续答对10题',
    icon: '⚡',
    reward: { coins: 50 }
  },
  combo_20: {
    id: 'combo_20',
    name: '连击大师',
    description: '连续答对20题',
    icon: '💫',
    reward: { coins: 100 }
  },
  perfect_session: {
    id: 'perfect_session',
    name: '完美表现',
    description: '单次练习100%正确率',
    icon: '👑',
    reward: { coins: 80 }
  },
  excellent_session: {
    id: 'excellent_session',
    name: '优秀表现',
    description: '单次练习90%以上正确率',
    icon: '⭐',
    reward: { coins: 40 }
  },
  high_scorer: {
    id: 'high_scorer',
    name: '高分达人',
    description: '单次练习得分超过200',
    icon: '🎖️',
    reward: { coins: 60 }
  },
  dedicated_learner: {
    id: 'dedicated_learner',
    name: '坚持学习',
    description: '完成10次练习',
    icon: '📚',
    reward: { coins: 100 }
  }
}