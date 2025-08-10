<template>
  <div class="combo-indicator" v-if="combo > 1">
    <div class="combo-content" :class="{ 'combo-pulse': isPulsing }">
      <div class="combo-icon">🔥</div>
      <div class="combo-text">
        <span class="combo-number">{{ combo }}</span>
        <span class="combo-label">连击</span>
      </div>
      <div class="combo-multiplier" v-if="multiplier > 1">
        x{{ multiplier }}
      </div>
    </div>
    
    <!-- 连击等级指示器 -->>
    <div class="combo-level" :class="comboLevelClass">
      <div class="combo-level-text">{{ comboLevelText }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ComboIndicator',
  props: {
    combo: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      isPulsing: false,
      lastCombo: 0
    }
  },
  computed: {
    multiplier() {
      if (this.combo >= 20) return 3
      if (this.combo >= 10) return 2.5
      if (this.combo >= 5) return 2
      return 1
    },
    comboLevelClass() {
      if (this.combo >= 20) return 'legendary'
      if (this.combo >= 15) return 'epic'
      if (this.combo >= 10) return 'rare'
      if (this.combo >= 5) return 'uncommon'
      return 'common'
    },
    comboLevelText() {
      if (this.combo >= 20) return '传奇连击！'
      if (this.combo >= 15) return '史诗连击！'
      if (this.combo >= 10) return '稀有连击！'
      if (this.combo >= 5) return '优秀连击！'
      return '连击开始！'
    }
  },
  watch: {
    combo(newVal, oldVal) {
      if (newVal > oldVal && newVal > 1) {
        this.triggerPulse()
        this.playComboSound()
      }
      this.lastCombo = oldVal
    }
  },
  methods: {
    triggerPulse() {
      this.isPulsing = true
      setTimeout(() => {
        this.isPulsing = false
      }, 600)
    },
    playComboSound() {
      // 简单的音效提示（可以替换为真实音频）
      if (this.combo % 5 === 0) {
        // 每5连击播放特殊音效
        console.log('🎵 特殊连击音效')
      } else {
        console.log('🎵 连击音效')
      }
    }
  }
}
</script>

<style scoped>
.combo-indicator {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  animation: comboAppear 0.3s ease-out;
}

.combo-content {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #FF6B6B, #FF8E53);
  color: white;
  padding: 12px 16px;
  border-radius: 25px;
  box-shadow: 0 4px 20px rgba(255, 107, 107, 0.4);
  transition: all 0.3s ease;
  min-width: 120px;
}

.combo-content.combo-pulse {
  animation: comboPulse 0.6s ease-out;
}

.combo-icon {
  font-size: 24px;
  margin-right: 8px;
  animation: iconSpin 0.6s ease-out;
}

.combo-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.combo-number {
  font-size: 20px;
  font-weight: bold;
  line-height: 1;
}

.combo-label {
  font-size: 12px;
  opacity: 0.9;
  line-height: 1;
}

.combo-multiplier {
  font-size: 14px;
  font-weight: bold;
  margin-left: 8px;
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

.combo-level {
  text-align: center;
  margin-top: 8px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  animation: levelGlow 0.5s ease-out;
}

.combo-level-text {
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 连击等级样式 */
.combo-level.common {
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  color: white;
}

.combo-level.uncommon {
  background: linear-gradient(135deg, #00b894, #00a085);
  color: white;
}

.combo-level.rare {
  background: linear-gradient(135deg, #fdcb6e, #e17055);
  color: white;
}

.combo-level.epic {
  background: linear-gradient(135deg, #a29bfe, #6c5ce7);
  color: white;
}

.combo-level.legendary {
  background: linear-gradient(135deg, #fd79a8, #e84393);
  color: white;
  animation: legendaryGlow 1s ease-in-out infinite alternate;
}

/* 动画效果 */
@keyframes comboAppear {
  0% {
    opacity: 0;
    transform: translateX(100px) scale(0.5);
  }
  100% {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

@keyframes comboPulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
    box-shadow: 0 6px 25px rgba(255, 107, 107, 0.6);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes iconSpin {
  0% {
    transform: rotate(0deg) scale(1);
  }
  50% {
    transform: rotate(180deg) scale(1.2);
  }
  100% {
    transform: rotate(360deg) scale(1);
  }
}

@keyframes levelGlow {
  0% {
    opacity: 0;
    transform: translateY(10px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes legendaryGlow {
  0% {
    box-shadow: 0 0 10px rgba(253, 121, 168, 0.5);
  }
  100% {
    box-shadow: 0 0 20px rgba(253, 121, 168, 0.8), 0 0 30px rgba(232, 67, 147, 0.3);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .combo-indicator {
    top: 10px;
    right: 10px;
  }
  
  .combo-content {
    padding: 8px 12px;
    min-width: 100px;
  }
  
  .combo-icon {
    font-size: 20px;
  }
  
  .combo-number {
    font-size: 18px;
  }
  
  .combo-label {
    font-size: 10px;
  }
}
</style>