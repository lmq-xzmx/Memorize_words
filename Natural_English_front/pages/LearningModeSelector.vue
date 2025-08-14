<template>
  <div class="learning-mode-selector">
    <div class="header">
      <h1>英语学习中心</h1>
      <p class="subtitle">选择您的学习模式</p>
    </div>
    
    <!-- 分类标题 -->
    <div class="category-section">
      <h2 class="category-title">📚 学习模块</h2>
      <div class="mode-grid">
        <!-- 单词阅读 -->
        <div v-if="canUseMode('word-reading')" class="mode-card" @click="navigateToMode('word-reading')">
          <div class="mode-header">
            <div class="mode-icon">📖</div>
            <div class="mode-title">单词阅读</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="word-reading"
                v-model="selectedHomepage"
                @change="setHomepage('word-reading')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>H5版单词阅读页面，支持音频播放和进度跟踪</p>
            <div class="mode-features">
              <span class="feature-tag">音频播放</span>
              <span class="feature-tag">进度跟踪</span>
              <span class="feature-tag">发音练习</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">发音练习</span>
            </div>
          </div>
        </div>

        <!-- 单词学习 -->
        <div v-if="canUseMode('word-learning')" class="mode-card" @click="navigateToMode('word-learning')">
          <div class="mode-header">
            <div class="mode-icon">📚</div>
            <div class="mode-title">单词学习</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="word-learning"
                v-model="selectedHomepage"
                @change="setHomepage('word-learning')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>H5版单词学习页面，展示单词详情和多种释义</p>
            <div class="mode-features">
              <span class="feature-tag">详细释义</span>
              <span class="feature-tag">例句展示</span>
              <span class="feature-tag">词汇积累</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">系统学习</span>
            </div>
          </div>
        </div>

        <!-- 单词详情 -->
        <div v-if="canUseMode('word-detail')" class="mode-card" @click="navigateToMode('word-detail')">
          <div class="mode-header">
            <div class="mode-icon">📝</div>
            <div class="mode-title">单词详情</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="word-detail"
                v-model="selectedHomepage"
                @change="setHomepage('word-detail')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>单词详情页面，包含音标、释义、例句、词根词缀等完整信息</p>
            <div class="mode-features">
              <span class="feature-tag">音标标注</span>
              <span class="feature-tag">词根分析</span>
              <span class="feature-tag">例句丰富</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">深度学习</span>
            </div>
          </div>
        </div>

        <!-- 词根分解 -->
        <div v-if="canUseMode('word-root-analysis')" class="mode-card" @click="navigateToMode('word-root-analysis')">
          <div class="mode-header">
            <div class="mode-icon">🌱</div>
            <div class="mode-title">词根分解</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="word-root-analysis"
                v-model="selectedHomepage"
                @change="setHomepage('word-root-analysis')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>词根拆解展示页面，支持词根分析和学习进度管理</p>
            <div class="mode-features">
              <span class="feature-tag">词根拆解</span>
              <span class="feature-tag">词缀分析</span>
              <span class="feature-tag">记忆技巧</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">词汇扩展</span>
            </div>
          </div>
        </div>

        <!-- 故事阅读 -->
        <div v-if="canUseMode('story-reading')" class="mode-card" @click="navigateToMode('story-reading')">
          <div class="mode-header">
            <div class="mode-icon">📚</div>
            <div class="mode-title">故事阅读</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="story-reading"
                v-model="selectedHomepage"
                @change="setHomepage('story-reading')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>交互式故事阅读页面，支持词性标注和生词收集功能</p>
            <div class="mode-features">
              <span class="feature-tag">词性标注</span>
              <span class="feature-tag">生词收集</span>
              <span class="feature-tag">情境学习</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">阅读提升</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 练习模块 -->
    <div class="category-section">
      <h2 class="category-title">✍️ 练习模块</h2>
      <div class="mode-grid">

        <!-- 拼写练习 -->
        <div v-if="canUseMode('spelling')" class="mode-card" @click="navigateToMode('spelling')">
          <div class="mode-header">
            <div class="mode-icon">✍️</div>
            <div class="mode-title">拼写练习</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="spelling"
                v-model="selectedHomepage"
                @change="setHomepage('spelling')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>听音拼写练习页面，提升单词记忆</p>
            <div class="mode-features">
              <span class="feature-tag">听音练习</span>
              <span class="feature-tag">拖拽拼写</span>
              <span class="feature-tag">记忆强化</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">拼写练习</span>
            </div>
          </div>
        </div>

        <!-- 闪卡学习 -->
        <div v-if="canUseMode('flashcard')" class="mode-card" @click="navigateToMode('flashcard')">
          <div class="mode-header">
            <div class="mode-icon">🃏</div>
            <div class="mode-title">闪卡学习</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="flashcard"
                v-model="selectedHomepage"
                @change="setHomepage('flashcard')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>翻转卡片学习单词页面</p>
            <div class="mode-features">
              <span class="feature-tag">卡片翻转</span>
              <span class="feature-tag">快速记忆</span>
              <span class="feature-tag">重复练习</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">快速记忆</span>
            </div>
          </div>
        </div>

        <!-- 模式匹配记忆 -->
        <div v-if="canUseMode('pattern-memory')" class="mode-card" @click="navigateToMode('pattern-memory')">
          <div class="mode-header">
            <div class="mode-icon">🧠</div>
            <div class="mode-title">模式匹配记忆</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="pattern-memory"
                v-model="selectedHomepage"
                @change="setHomepage('pattern-memory')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>三级学习模式：图片选择、选择题、单词补全，支持多种记忆方式</p>
            <div class="mode-features">
              <span class="feature-tag">图片选择</span>
              <span class="feature-tag">选择题</span>
              <span class="feature-tag">单词补全</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">系统学习</span>
            </div>
          </div>
        </div>

        <!-- 单词挑战 -->
        <div v-if="canUseMode('word-challenge')" class="mode-card" @click="navigateToMode('word-challenge')">
          <div class="mode-header">
            <div class="mode-icon">⚔️</div>
            <div class="mode-title">单词挑战</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="word-challenge"
                v-model="selectedHomepage"
                @change="setHomepage('word-challenge')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>单词挑战游戏页面</p>
            <div class="mode-features">
              <span class="feature-tag">游戏化</span>
              <span class="feature-tag">挑战模式</span>
              <span class="feature-tag">竞技对战</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">竞技挑战</span>
            </div>
          </div>
        </div>

        <!-- 单词复习 -->
        <div v-if="canUseMode('word-review')" class="mode-card" @click="navigateToMode('word-review')">
          <div class="mode-header">
            <div class="mode-icon">🔄</div>
            <div class="mode-title">单词复习</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="word-review"
                v-model="selectedHomepage"
                @change="setHomepage('word-review')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>单词复习页面</p>
            <div class="mode-features">
              <span class="feature-tag">复习计划</span>
              <span class="feature-tag">遗忘曲线</span>
              <span class="feature-tag">智能推荐</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">巩固复习</span>
            </div>
          </div>
        </div>

        <!-- 单词选择 -->
        <div v-if="canUseMode('word-selection')" class="mode-card" @click="navigateToMode('word-selection')">
          <div class="mode-header">
            <div class="mode-icon">✅</div>
            <div class="mode-title">单词选择</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="word-selection"
                v-model="selectedHomepage"
                @change="setHomepage('word-selection')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>单词选择练习页面</p>
            <div class="mode-features">
              <span class="feature-tag">选择题</span>
              <span class="feature-tag">快速判断</span>
              <span class="feature-tag">准确率统计</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">快速练习</span>
            </div>
          </div>
        </div>

        <!-- 师生互动 -->
        <div v-if="canUseMode('teacher-student-interaction')" class="mode-card" @click="navigateToMode('teacher-student-interaction')">
          <div class="mode-header">
            <div class="mode-icon">👥</div>
            <div class="mode-title">师生互动</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="teacher-student-interaction"
                v-model="selectedHomepage"
                @change="setHomepage('teacher-student-interaction')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>师生互动练习模式，支持单词选择和实时反馈</p>
            <div class="mode-features">
              <span class="feature-tag">师生互动</span>
              <span class="feature-tag">实时反馈</span>
              <span class="feature-tag">协作学习</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">课堂教学</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 特色模块 -->
    <div class="category-section">
      <h2 class="category-title">🏆 特色模块</h2>
      <div class="mode-grid">
        <!-- 竞技模式 -->
        <div v-if="canUseMode('competition')" class="mode-card" @click="navigateToMode('competition')">
          <div class="mode-header">
            <div class="mode-icon">🏆</div>
            <div class="mode-title">竞技模式</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="competition"
                v-model="selectedHomepage"
                @change="setHomepage('competition')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>与其他学习者竞技对战，团队挑战</p>
            <div class="mode-features">
              <span class="feature-tag">实时对战</span>
              <span class="feature-tag">团队挑战</span>
              <span class="feature-tag">排行榜</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">竞技挑战</span>
            </div>
          </div>
        </div>

        <!-- 快刷模式 -->
        <div v-if="canUseMode('quick-brush')" class="mode-card" @click="navigateToMode('quick-brush')">
          <div class="mode-header">
            <div class="mode-icon">⚡</div>
            <div class="mode-title">快刷模式</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="quick-brush"
                v-model="selectedHomepage"
                @change="setHomepage('quick-brush')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>快速刷题模式，自动跳转下一题，提升学习效率</p>
            <div class="mode-features">
              <span class="feature-tag">实时计时</span>
              <span class="feature-tag">自动跳转</span>
              <span class="feature-tag">快速反馈</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">快速复习</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 当前首页设置提示 -->
    <div v-if="selectedHomepage" class="homepage-tip">
      <div class="tip-content">
        <span class="tip-icon">🏠</span>
        <span class="tip-text">当前首页：{{ getModeName(selectedHomepage) }}</span>
        <button @click="clearHomepage" class="clear-btn">清除设置</button>
      </div>
    </div>
  </div>
</template>

<script>
import { UserSettingsManager } from '../utils/userSettings.js'
import userPersonalizationMixin, { predefinedElementConfigs } from '../mixins/userPersonalization.js'
import permissionMixin from '../mixins/permissionMixin.js'
import { homepageManager } from '../utils/homepageManager.js'

export default {
  name: 'LearningModeSelector',
  mixins: [userPersonalizationMixin, permissionMixin],
  data() {
    return {
      selectedHomepage: '',
      userId: 'default',
      userSettings: new UserSettingsManager(),
      // 学习模式权限映射
      modePermissions: {
        'word-reading': 'practice_reading',
        'word-learning': 'view_word_learning',
        'word-detail': 'view_word_detail',
        'word-root-analysis': 'analyze_word_roots',
        'story-reading': 'practice_story_reading',
        'spelling': 'practice_spelling',
        'flashcard': 'use_flashcard',
        'pattern-memory': 'use_pattern_memory',
        'word-challenge': 'participate_challenge',
        'word-review': 'review_words',
        'word-selection': 'practice_word_selection',
        'teacher-student-interaction': 'practice_word_selection',
        'competition': 'participate_challenge',
        'quick-brush': 'review_words'
      }
    }
  },
  
  computed: {
    /**
     * 根据用户权限过滤可用的学习模式
     */
    availableModes() {
      const allModes = Object.keys(this.modePermissions)
      return allModes.filter(mode => {
        const permission = this.modePermissions[mode]
        return this.$hasPermission(permission)
      })
    }
  },
  methods: {
    /**
     * 检查用户是否有权限使用指定模式
     */
    canUseMode(mode) {
      const permission = this.modePermissions[mode]
      return permission ? this.$hasPermission(permission) : false
    },
    
    /**
     * 导航到指定模式（带权限检查）
     */
    navigateToMode(mode) {
      // 权限检查
      if (!this.canUseMode(mode)) {
        this.$showError(`您没有权限使用${homepageManager.getModeName(mode)}功能`)
        return
      }
      
      // 执行导航
      switch(mode) {
        case 'word-reading':
          this.$router.push('/word-reading')
          break
        case 'word-learning':
          this.$router.push('/word-learning')
          break
        case 'word-detail':
          this.$router.push('/word-detail/institution')
          break
        case 'word-root-analysis':
          this.$router.push('/word-root-analysis')
          break
        case 'story-reading':
          this.$router.push('/story-reading')
          break
        case 'spelling':
          this.$router.push('/word-learning/spelling')
          break
        case 'flashcard':
          this.$router.push('/word-learning/flashcard')
          break
        case 'pattern-memory':
          this.$router.push('/pattern-memory')
          break
        case 'word-challenge':
          this.$router.push('/word-challenge')
          break
        case 'word-review':
          this.$router.push('/word-review')
          break
        case 'word-selection':
          this.$router.push('/word-selection')
          break
        case 'teacher-student-interaction':
          this.$router.push('/word-selection-practice2')
          break
        case 'competition':
          this.$router.push('/competition')
          break
        case 'quick-brush':
          this.$router.push('/quick-brush')
          break
        default:
          console.log('未知模式:', mode)
      }
    },
    
    setHomepage(mode) {
      // 检查权限
      if (!this.canUseMode(mode)) {
        this.$showError(`您没有权限将${homepageManager.getModeName(mode)}设置为首页`)
        return
      }
      
      const success = homepageManager.setHomepage(mode)
      if (success) {
        this.selectedHomepage = mode
        
        // 显示设置成功提示
        this.$nextTick(() => {
          this.$showSuccess(`已将"${homepageManager.getModeName(mode)}"设置为首页`)
        })
      } else {
        this.$showError('设置首页失败，请重试')
      }
    },
    
    clearHomepage() {
      const success = homepageManager.clearHomepage()
      if (success) {
        this.selectedHomepage = ''
      }
    },
    
    getModeName(mode) {
      return homepageManager.getModeName(mode)
    },
    
    // 获取用户ID
    getUserId() {
      this.userId = this.userSettings.userId
    },
    
    // 加载用户的首页设置
    loadUserHomepageSettings() {
      this.selectedHomepage = homepageManager.getHomepage() || ''
    }
  },
  
  mounted() {
    // 获取用户ID
    this.getUserId()
    
    // 加载用户的首页设置
    this.loadUserHomepageSettings()
    
    // 应用竞技模式元素配置
    this.$nextTick(() => {
      const competitionConfigs = predefinedElementConfigs.competitionElements
      if (competitionConfigs && typeof competitionConfigs === 'object') {
        // competitionConfigs 是对象，不是数组，所以使用 Object.entries 遍历
        Object.entries(competitionConfigs).forEach(([key, config]) => {
          if (config && config.position && config.size) {
            // 应用元素配置
            console.log(`Applying config for ${key}:`, config)
          }
        })
      }
    })
    
    // 检查是否禁用重定向
    const noRedirect = this.$route.query['no-redirect'] === 'true'
    
    // 只有在根路径（/）或首页相关路径时才执行重定向
    // 避免在学习模式页面中触发不必要的重定向
    const shouldCheckRedirect = ['/', '/index', '/dashboard', '/home'].includes(this.$route.path)
    
    // 如果没有禁用重定向且在合适的路径下，则检查并执行首页重定向
    if (!noRedirect && shouldCheckRedirect) {
      const redirected = homepageManager.performHomepageRedirect(this.$router, this.$route)
      if (redirected) {
        return
      }
    }
  }
}
</script>

<style scoped>
.learning-mode-selector {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  padding-bottom: 120px; /* 增加底部内边距，确保内容不被遮挡 */
}

.category-section {
  margin-bottom: 40px;
}

.category-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 20px;
  text-align: center;
  background: linear-gradient(45deg, #fff, #f0f8ff, #fff);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 3s ease-in-out infinite;
  text-shadow: 2px 2px 8px rgba(0,0,0,0.4);
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

.header {
  text-align: center;
  color: white;
  margin-bottom: 30px;
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 700;
}

.subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
}

.mode-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.mode-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.mode-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.mode-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.mode-icon {
  font-size: 2.5rem;
  margin-right: 12px;
}

.mode-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: #333;
  flex: 1;
}

.homepage-selector {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  color: #666;
}

.homepage-selector input[type="radio"] {
  margin: 0;
}

.mode-description p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 12px;
}

.mode-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.feature-tag {
  background: #f0f4ff;
  color: #4f46e5;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.mode-stats {
  border-top: 1px solid #eee;
  padding-top: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: #888;
  font-size: 0.9rem;
}

.stat-value {
  color: #333;
  font-weight: 600;
}

.homepage-tip {
  position: fixed;
  bottom: 80px; /* 调整为80px，确保不被底部菜单栏遮挡 */
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 12px 20px;
  border-radius: 25px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
}

.tip-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tip-icon {
  font-size: 1.2rem;
}

.tip-text {
  color: #333;
  font-weight: 500;
}

.clear-btn {
  background: #ff4757;
  color: white;
  border: none;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.2s;
}

.clear-btn:hover {
  background: #ff3742;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .mode-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .header h1 {
    font-size: 2rem;
  }
  
  .mode-card {
    padding: 20px;
  }
  
  .mode-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .homepage-selector {
    align-self: flex-end;
  }
}
</style>