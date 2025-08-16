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

