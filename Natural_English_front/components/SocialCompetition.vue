<template>
  <div class="social-competition">
    <!-- 竞争模式选择 -->
    <div class="mode-selector">
      <button 
        v-for="mode in competitionModes" 
        :key="mode.id"
        class="mode-btn"
        :class="{ active: currentMode === mode.id }"
        @click="switchMode(mode.id)"
      >
        <div class="mode-icon">{{ mode.icon }}</div>
        <div class="mode-name">{{ mode.name }}</div>
      </button>
    </div>
    
    <!-- PvP 对战模式 -->
    <div v-if="currentMode === 'pvp'" class="pvp-section">
      <div class="pvp-header">
        <h3>实时对战</h3>
        <div class="online-count">在线用户: {{ onlineUsers }}</div>
      </div>
      
      <!-- 匹配状态 -->
      <div v-if="!isInBattle" class="matching-section">
        <div v-if="!isMatching" class="match-controls">
          <button class="btn btn-primary btn-large" @click="startMatching">
            <span class="btn-icon">⚔️</span>
            开始匹配
          </button>
          <div class="difficulty-selector">
            <label>难度选择:</label>
            <select v-model="selectedDifficulty">
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="hard">困难</option>
            </select>
          </div>
        </div>
        
        <div v-else class="matching-status">
          <div class="matching-animation">
            <div class="spinner"></div>
            <div class="matching-text">正在匹配对手...</div>
            <div class="matching-time">{{ matchingTime }}s</div>
          </div>
          <button class="btn btn-secondary" @click="cancelMatching">
            取消匹配
          </button>
        </div>
      </div>
      
      <!-- 对战界面 -->
      <div v-else class="battle-interface">
        <div class="battle-header">
          <div class="player-info">
            <div class="player-avatar">{{ currentUser.avatar }}</div>
            <div class="player-details">
              <div class="player-name">{{ currentUser.name }}</div>
              <div class="player-level">Lv.{{ currentUser.level }}</div>
            </div>
            <div class="player-score">{{ battleState.playerScore }}</div>
          </div>
          
          <div class="battle-timer">
            <div class="timer-circle">
              <div class="timer-text">{{ battleTimeLeft }}</div>
            </div>
          </div>
          
          <div class="opponent-info">
            <div class="player-score">{{ battleState.opponentScore }}</div>
            <div class="player-details">
              <div class="player-name">{{ opponent.name }}</div>
              <div class="player-level">Lv.{{ opponent.level }}</div>
            </div>
            <div class="player-avatar">{{ opponent.avatar }}</div>
          </div>
        </div>
        
        <div class="battle-progress">
          <div class="progress-bar">
            <div 
              class="progress-fill player" 
              :style="{ width: playerProgressPercentage + '%' }"
            ></div>
            <div 
              class="progress-fill opponent" 
              :style="{ width: opponentProgressPercentage + '%' }"
            ></div>
          </div>
        </div>
        
        <div class="battle-actions">
          <button class="btn btn-danger" @click="surrenderBattle">
            投降
          </button>
        </div>
      </div>
    </div>
    
    <!-- 排行榜模式 -->
    <div v-if="currentMode === 'leaderboard'" class="leaderboard-section">
      <div class="leaderboard-tabs">
        <button 
          v-for="tab in leaderboardTabs" 
          :key="tab.id"
          class="tab-btn"
          :class="{ active: currentLeaderboardTab === tab.id }"
          @click="switchLeaderboardTab(tab.id)"
        >
          {{ tab.name }}
        </button>
      </div>
      
      <div class="leaderboard-content">
        <div class="my-rank">
          <div class="rank-card">
            <div class="rank-position">#{{ myRank.position }}</div>
            <div class="rank-info">
              <div class="rank-name">{{ myRank.name }}</div>
              <div class="rank-score">{{ myRank.score }} 分</div>
            </div>
            <div class="rank-change" :class="myRank.changeClass">
              {{ myRank.change }}
            </div>
          </div>
        </div>
        
        <div class="leaderboard-list">
          <div 
            v-for="(player, index) in leaderboardData" 
            :key="player.id"
            class="leaderboard-item"
            :class="{ 
              'top-1': index === 0,
              'top-3': index < 3,
              'current-user': player.id === currentUser.id
            }"
          >
            <div class="rank-number">
              <span v-if="index < 3" class="medal">{{ getMedal(index) }}</span>
              <span v-else class="rank-text">#{{ index + 1 }}</span>
            </div>
            
            <div class="player-avatar">{{ player.avatar }}</div>
            
            <div class="player-info">
              <div class="player-name">{{ player.name }}</div>
              <div class="player-level">Lv.{{ player.level }}</div>
            </div>
            
            <div class="player-stats">
              <div class="stat-value">{{ player.score }}</div>
              <div class="stat-label">{{ getScoreLabel() }}</div>
            </div>
            
            <div class="rank-change" :class="player.changeClass">
              {{ player.change }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 团队挑战模式 -->
    <div v-if="currentMode === 'team'" class="team-section">
      <div class="team-header">
        <h3>团队挑战</h3>
        <button v-if="!currentTeam" class="btn btn-primary" @click="createTeam">
          创建团队
        </button>
      </div>
      
      <!-- 当前团队信息 -->
      <div v-if="currentTeam" class="current-team">
        <div class="team-info">
          <div class="team-name">{{ currentTeam.name }}</div>
          <div class="team-stats">
            <span>成员: {{ currentTeam.memberCount }}/{{ currentTeam.maxMembers }}</span>
            <span>等级: {{ currentTeam.level }}</span>
            <span>积分: {{ currentTeam.points }}</span>
          </div>
        </div>
        
        <div class="team-members">
          <div 
            v-for="member in currentTeam.members" 
            :key="member.id"
            class="member-item"
          >
            <div class="member-avatar">{{ member.avatar }}</div>
            <div class="member-info">
              <div class="member-name">{{ member.name }}</div>
              <div class="member-role">{{ member.role }}</div>
            </div>
            <div class="member-status" :class="member.status">
              {{ getStatusText(member.status) }}
            </div>
          </div>
        </div>
        
        <div class="team-actions">
          <button class="btn btn-primary" @click="startTeamChallenge">
            开始团队挑战
          </button>
          <button class="btn btn-secondary" @click="inviteMembers">
            邀请成员
          </button>
          <button class="btn btn-danger" @click="leaveTeam">
            离开团队
          </button>
        </div>
      </div>
      
      <!-- 团队列表 -->
      <div v-else class="team-list">
        <div class="team-search">
          <input 
            v-model="teamSearchQuery" 
            type="text" 
            placeholder="搜索团队..."
            class="search-input"
          >
        </div>
        
        <div class="teams-grid">
          <div 
            v-for="team in filteredTeams" 
            :key="team.id"
            class="team-card"
            @click="joinTeam(team)"
          >
            <div class="team-header">
              <div class="team-name">{{ team.name }}</div>
              <div class="team-level">Lv.{{ team.level }}</div>
            </div>
            
            <div class="team-stats">
              <div class="stat">
                <span class="stat-value">{{ team.memberCount }}</span>
                <span class="stat-label">成员</span>
              </div>
              <div class="stat">
                <span class="stat-value">{{ team.points }}</span>
                <span class="stat-label">积分</span>
              </div>
              <div class="stat">
                <span class="stat-value">{{ team.winRate }}%</span>
                <span class="stat-label">胜率</span>
              </div>
            </div>
            
            <div class="team-description">{{ team.description }}</div>
            
            <div class="team-requirements">
              <span v-if="team.minLevel" class="requirement">
                最低等级: {{ team.minLevel }}
              </span>
              <span class="team-type" :class="team.type">
                {{ getTeamTypeText(team.type) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 活动挑战模式 -->
    <div v-if="currentMode === 'events'" class="events-section">
      <div class="events-header">
        <h3>限时活动</h3>
        <div class="events-timer">距离活动结束: {{ eventTimeLeft }}</div>
      </div>
      
      <div class="events-list">
        <div 
          v-for="event in activeEvents" 
          :key="event.id"
          class="event-card"
          :class="event.difficulty"
        >
          <div class="event-header">
            <div class="event-icon">{{ event.icon }}</div>
            <div class="event-info">
              <div class="event-name">{{ event.name }}</div>
              <div class="event-description">{{ event.description }}</div>
            </div>
            <div class="event-difficulty">{{ getDifficultyText(event.difficulty) }}</div>
          </div>
          
          <div class="event-progress">
            <div class="progress-info">
              <span>进度: {{ event.currentProgress }}/{{ event.totalProgress }}</span>
              <span>{{ Math.round((event.currentProgress / event.totalProgress) * 100) }}%</span>
            </div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: (event.currentProgress / event.totalProgress) * 100 + '%' }"
              ></div>
            </div>
          </div>
          
          <div class="event-rewards">
            <div class="rewards-title">奖励:</div>
            <div class="rewards-list">
              <span 
                v-for="reward in event.rewards" 
                :key="reward.id"
                class="reward-item"
              >
                {{ reward.icon }} {{ reward.amount }}
              </span>
            </div>
          </div>
          
          <div class="event-actions">
            <button 
              class="btn btn-primary"
              :disabled="event.completed"
              @click="joinEvent(event)"
            >
              {{ event.completed ? '已完成' : '参加活动' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SocialCompetition',
  props: {
    currentUser: {
      type: Object,
      required: true
    },
    gameState: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      currentMode: 'pvp',
      competitionModes: [
        { id: 'pvp', name: 'PvP对战', icon: '⚔️' },
        { id: 'leaderboard', name: '排行榜', icon: '🏆' },
        { id: 'team', name: '团队挑战', icon: '👥' },
        { id: 'events', name: '限时活动', icon: '🎯' }
      ],
      
      // PvP 相关
      isMatching: false,
      isInBattle: false,
      matchingTime: 0,
      selectedDifficulty: 'medium',
      onlineUsers: 1247,
      opponent: null,
      battleState: {
        playerScore: 0,
        opponentScore: 0,
        timeLeft: 300
      },
      
      // 排行榜相关
      currentLeaderboardTab: 'weekly',
      leaderboardTabs: [
        { id: 'daily', name: '今日' },
        { id: 'weekly', name: '本周' },
        { id: 'monthly', name: '本月' },
        { id: 'alltime', name: '总榜' }
      ],
      
      // 团队相关
      currentTeam: null,
      teamSearchQuery: '',
      
      // 活动相关
      eventTimeLeft: '2天 14:32:15'
    }
  },
  computed: {
    battleTimeLeft() {
      const minutes = Math.floor(this.battleState.timeLeft / 60)
      const seconds = this.battleState.timeLeft % 60
      return `${minutes}:${seconds.toString().padStart(2, '0')}`
    },
    
    playerProgressPercentage() {
      const total = this.battleState.playerScore + this.battleState.opponentScore
      return total > 0 ? (this.battleState.playerScore / total) * 100 : 50
    },
    
    opponentProgressPercentage() {
      const total = this.battleState.playerScore + this.battleState.opponentScore
      return total > 0 ? (this.battleState.opponentScore / total) * 100 : 50
    },
    
    myRank() {
      return {
        position: 42,
        name: this.currentUser.name,
        score: 2847,
        change: '+3',
        changeClass: 'positive'
      }
    },
    
    leaderboardData() {
      // 模拟排行榜数据
      return [
        { id: 1, name: '学霸小王', avatar: '👑', level: 25, score: 5420, change: '=', changeClass: 'neutral' },
        { id: 2, name: '英语达人', avatar: '🎓', level: 23, score: 5180, change: '+1', changeClass: 'positive' },
        { id: 3, name: '单词王者', avatar: '📚', level: 22, score: 4950, change: '-1', changeClass: 'negative' },
        { id: 4, name: '语言天才', avatar: '🌟', level: 21, score: 4720, change: '+2', changeClass: 'positive' },
        { id: 5, name: '学习狂人', avatar: '🔥', level: 20, score: 4500, change: '-1', changeClass: 'negative' }
      ]
    },
    
    filteredTeams() {
      const teams = [
        {
          id: 1,
          name: '英语精英团',
          level: 15,
          memberCount: 8,
          maxMembers: 10,
          points: 15420,
          winRate: 85,
          description: '专注高级英语学习，欢迎有经验的学习者加入',
          minLevel: 10,
          type: 'competitive'
        },
        {
          id: 2,
          name: '快乐学习组',
          level: 8,
          memberCount: 12,
          maxMembers: 15,
          points: 8750,
          winRate: 72,
          description: '轻松愉快的学习氛围，适合初学者',
          minLevel: 1,
          type: 'casual'
        }
      ]
      
      if (!this.teamSearchQuery) return teams
      
      return teams.filter(team => 
        team.name.toLowerCase().includes(this.teamSearchQuery.toLowerCase()) ||
        team.description.toLowerCase().includes(this.teamSearchQuery.toLowerCase())
      )
    },
    
    activeEvents() {
      return [
        {
          id: 1,
          name: '单词马拉松',
          description: '在24小时内学习100个新单词',
          icon: '🏃‍♂️',
          difficulty: 'hard',
          currentProgress: 67,
          totalProgress: 100,
          completed: false,
          rewards: [
            { id: 1, icon: '💎', amount: 500 },
            { id: 2, icon: '🏆', amount: '专属称号' }
          ]
        },
        {
          id: 2,
          name: '完美连击',
          description: '连续答对50题不出错',
          icon: '🎯',
          difficulty: 'medium',
          currentProgress: 32,
          totalProgress: 50,
          completed: false,
          rewards: [
            { id: 1, icon: '⭐', amount: 200 },
            { id: 2, icon: '🎨', amount: '新头像' }
          ]
        }
      ]
    }
  },
  mounted() {
    this.initializeWebSocket()
  },
  methods: {
    switchMode(mode) {
      this.currentMode = mode
    },
    
    // PvP 方法
    startMatching() {
      this.isMatching = true
      this.matchingTime = 0
      
      const matchingInterval = setInterval(() => {
        this.matchingTime++
        
        // 模拟匹配成功
        if (this.matchingTime >= 5) {
          clearInterval(matchingInterval)
          this.matchFound()
        }
      }, 1000)
    },
    
    cancelMatching() {
      this.isMatching = false
      this.matchingTime = 0
    },
    
    matchFound() {
      this.isMatching = false
      this.isInBattle = true
      
      // 模拟对手数据
      this.opponent = {
        id: 'opponent_1',
        name: '挑战者',
        avatar: '🤖',
        level: this.currentUser.level + Math.floor(Math.random() * 3) - 1
      }
      
      this.battleState = {
        playerScore: 0,
        opponentScore: 0,
        timeLeft: 300
      }
      
      this.startBattleTimer()
    },
    
    startBattleTimer() {
      const timer = setInterval(() => {
        this.battleState.timeLeft--
        
        if (this.battleState.timeLeft <= 0) {
          clearInterval(timer)
          this.endBattle()
        }
      }, 1000)
    },
    
    surrenderBattle() {
      this.endBattle(false)
    },
    
    endBattle(victory = null) {
      this.isInBattle = false
      this.opponent = null
      
      // 触发战斗结束事件
      this.$emit('battle-end', {
        victory,
        playerScore: this.battleState.playerScore,
        opponentScore: this.battleState.opponentScore
      })
    },
    
    // 排行榜方法
    switchLeaderboardTab(tab) {
      this.currentLeaderboardTab = tab
    },
    
    getMedal(index) {
      const medals = ['🥇', '🥈', '🥉']
      return medals[index] || ''
    },
    
    getScoreLabel() {
      const labels = {
        daily: '今日积分',
        weekly: '周积分',
        monthly: '月积分',
        alltime: '总积分'
      }
      return labels[this.currentLeaderboardTab] || '积分'
    },
    
    // 团队方法
    createTeam() {
      // 实现创建团队逻辑
      this.$emit('create-team')
    },
    
    joinTeam(team) {
      // 实现加入团队逻辑
      this.$emit('join-team', team)
    },
    
    leaveTeam() {
      this.currentTeam = null
      this.$emit('leave-team')
    },
    
    startTeamChallenge() {
      this.$emit('start-team-challenge')
    },
    
    inviteMembers() {
      this.$emit('invite-members')
    },
    
    getStatusText(status) {
      const statusMap = {
        online: '在线',
        offline: '离线',
        busy: '忙碌'
      }
      return statusMap[status] || '未知'
    },
    
    getTeamTypeText(type) {
      const typeMap = {
        competitive: '竞技',
        casual: '休闲',
        educational: '教育'
      }
      return typeMap[type] || '普通'
    },
    
    // 活动方法
    joinEvent(event) {
      this.$emit('join-event', event)
    },
    
    getDifficultyText(difficulty) {
      const difficultyMap = {
        easy: '简单',
        medium: '中等',
        hard: '困难'
      }
      return difficultyMap[difficulty] || '未知'
    },
    
    // WebSocket 初始化
    initializeWebSocket() {
      // 实现 WebSocket 连接逻辑
      // this.socket = new WebSocket('ws://localhost:3001/competition')
    }
  }
}
</script>

<style scoped>
.social-competition {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.mode-selector {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  justify-content: center;
}

.mode-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.mode-btn:hover {
  border-color: #007aff;
  transform: translateY(-2px);
}

.mode-btn.active {
  border-color: #007aff;
  background: #007aff;
  color: white;
}

.mode-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.mode-name {
  font-size: 14px;
  font-weight: 500;
}

/* PvP 样式 */
.pvp-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.pvp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.online-count {
  color: #4CAF50;
  font-weight: 500;
}

.match-controls {
  text-align: center;
}

.btn-large {
  padding: 20px 40px;
  font-size: 18px;
  margin-bottom: 20px;
}

.difficulty-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.matching-status {
  text-align: center;
  padding: 40px;
}

.matching-animation {
  margin-bottom: 30px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007aff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.battle-interface {
  space-y: 20px;
}

.battle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.player-info, .opponent-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.player-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.player-score {
  font-size: 24px;
  font-weight: bold;
  color: #007aff;
}

.timer-circle {
  width: 80px;
  height: 80px;
  border: 4px solid #e0e0e0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
}

.timer-text {
  font-size: 16px;
  font-weight: bold;
}

.battle-progress {
  margin-bottom: 20px;
}

.progress-bar {
  height: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.progress-fill.player {
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  float: left;
}

.progress-fill.opponent {
  background: linear-gradient(90deg, #f44336, #ff7043);
  float: right;
}

/* 排行榜样式 */
.leaderboard-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.leaderboard-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 2px solid #f0f0f0;
}

.tab-btn {
  padding: 12px 24px;
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.tab-btn.active {
  color: #007aff;
  border-bottom-color: #007aff;
}

.my-rank {
  margin-bottom: 30px;
}

.rank-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.rank-position {
  font-size: 32px;
  font-weight: bold;
  margin-right: 20px;
}

.rank-info {
  flex: 1;
}

.rank-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 5px;
}

.rank-score {
  font-size: 14px;
  opacity: 0.9;
}

.rank-change {
  font-size: 16px;
  font-weight: bold;
}

.rank-change.positive {
  color: #4CAF50;
}

.rank-change.negative {
  color: #f44336;
}

.rank-change.neutral {
  color: #999;
}

.leaderboard-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  transition: all 0.3s ease;
}

.leaderboard-item:hover {
  background: #f8f9fa;
  transform: translateX(5px);
}

.leaderboard-item.top-1 {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
}

.leaderboard-item.top-3 {
  background: linear-gradient(135deg, #e8f5e8, #f0f8f0);
}

.leaderboard-item.current-user {
  border: 2px solid #007aff;
  background: #e3f2fd;
}

.rank-number {
  width: 50px;
  text-align: center;
  font-weight: bold;
}

.medal {
  font-size: 24px;
}

.player-stats {
  text-align: right;
  margin-left: auto;
  margin-right: 20px;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

/* 团队样式 */
.team-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.team-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.current-team {
  space-y: 20px;
}

.team-info {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 20px;
}

.team-name {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.team-stats {
  display: flex;
  gap: 20px;
  color: #666;
}

.team-members {
  margin-bottom: 20px;
}

.member-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 10px;
}

.member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.member-info {
  flex: 1;
}

.member-name {
  font-weight: 500;
  margin-bottom: 2px;
}

.member-role {
  font-size: 12px;
  color: #666;
}

.member-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.member-status.online {
  background: #e8f5e8;
  color: #4CAF50;
}

.member-status.offline {
  background: #f5f5f5;
  color: #999;
}

.team-actions {
  display: flex;
  gap: 10px;
}

.team-search {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
}

.teams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.team-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.team-card:hover {
  border-color: #007aff;
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 122, 255, 0.15);
}

.team-requirements {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
}

.requirement {
  font-size: 12px;
  color: #666;
}

.team-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.team-type.competitive {
  background: #ffebee;
  color: #f44336;
}

.team-type.casual {
  background: #e8f5e8;
  color: #4CAF50;
}

/* 活动样式 */
.events-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.events-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.events-timer {
  color: #f44336;
  font-weight: 500;
}

.event-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.event-card.hard {
  border-left: 4px solid #f44336;
}

.event-card.medium {
  border-left: 4px solid #ff9800;
}

.event-card.easy {
  border-left: 4px solid #4CAF50;
}

.event-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.event-icon {
  font-size: 32px;
  margin-right: 15px;
}

.event-info {
  flex: 1;
}

.event-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 5px;
}

.event-description {
  color: #666;
  font-size: 14px;
}

.event-difficulty {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: #f0f0f0;
}

.event-progress {
  margin-bottom: 15px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;
}

.event-rewards {
  margin-bottom: 15px;
}

.rewards-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #333;
}

.rewards-list {
  display: flex;
  gap: 15px;
}

.reward-item {
  font-size: 12px;
  padding: 4px 8px;
  background: #f8f9fa;
  border-radius: 4px;
  color: #666;
}

/* 通用按钮样式 */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: #007aff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #d32f2f;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .mode-selector {
    flex-wrap: wrap;
  }
  
  .mode-btn {
    min-width: 100px;
    padding: 12px 15px;
  }
  
  .battle-header {
    flex-direction: column;
    gap: 20px;
  }
  
  .teams-grid {
    grid-template-columns: 1fr;
  }
  
  .team-actions {
    flex-direction: column;
  }
}
</style>