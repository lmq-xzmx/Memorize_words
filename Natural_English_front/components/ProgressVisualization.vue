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

<style lang="scss" scoped>
@use '../styles/index.scss';

@include bem-block('combo-indicator') {
  position: fixed;
  top: var(--spacing-6);
  right: var(--spacing-6);
  z-index: 1000;
  pointer-events: none;
  animation: slideInRight 0.5s ease-out;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@include bem-element('combo-content') {
  @include flex-center;
  gap: var(--spacing-3);
  background: linear-gradient(135deg, var(--color-orange-500) 0%, var(--color-red-500) 100%);
   color: var(--color-white);
  padding: var(--spacing-4) var(--spacing-6);
  border-radius: var(--border-radius-2xl);
   box-shadow: var(--shadow-2xl);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(var(--color-white), 0.2);
  transition: all 0.2s ease;
  transform-origin: center;

  @include bem-modifier('combo-pulse') {
    animation: comboPulse 0.6s ease-out;
  }
}

@keyframes comboPulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
    box-shadow: 0 0 30px rgba($color-orange-500, 0.8);
  }
  100% {
    transform: scale(1);
  }
}

@include bem-element('combo-icon') {
  font-size: 2rem;
  animation: iconBounce 2s infinite;
}

@keyframes iconBounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-8px);
  }
  60% {
    transform: translateY(-4px);
  }
}

@include bem-element('combo-text') {
  @include flex-column;
  align-items: center;
  gap: $spacing-1;
}

@include bem-element('combo-number') {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  line-height: 1;
  text-shadow: 2px 2px 4px rgba($color-black, 0.3);
}

@include bem-element('combo-label') {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 1px;
}

@include bem-element('combo-multiplier') {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  background: rgba($color-white, 0.2);
  padding: $spacing-1 $spacing-2;
  border-radius: $border-radius-md;
  border: 1px solid rgba($color-white, 0.3);
  animation: multiplierGlow 1.5s ease-in-out infinite alternate;
}

@keyframes multiplierGlow {
  from {
    box-shadow: 0 0 5px rgba($color-white, 0.5);
  }
  to {
    box-shadow: 0 0 15px rgba($color-white, 0.8);
  }
}

@include bem-element('combo-level') {
  margin-top: $spacing-2;
  text-align: center;
  padding: $spacing-2 $spacing-4;
  border-radius: $border-radius-lg;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  animation: levelPulse 2s ease-in-out infinite;

  @include bem-modifier('common') {
    background: linear-gradient(135deg, $color-gray-500 0%, $color-gray-600 100%);
    color: $color-white;
  }

  @include bem-modifier('uncommon') {
    background: linear-gradient(135deg, $color-green-500 0%, $color-green-600 100%);
    color: $color-white;
  }

  @include bem-modifier('rare') {
    background: linear-gradient(135deg, $color-blue-500 0%, $color-blue-600 100%);
    color: $color-white;
  }

  @include bem-modifier('epic') {
    background: linear-gradient(135deg, $color-purple-500 0%, $color-purple-600 100%);
    color: $color-white;
  }

  @include bem-modifier('legendary') {
    background: linear-gradient(135deg, $color-yellow-400 0%, $color-orange-500 100%);
    color: $color-black;
    box-shadow: 0 0 20px rgba($color-yellow-400, 0.6);
  }
}

@keyframes levelPulse {
  0%, 100% {
    opacity: 0.8;
  }
  50% {
    opacity: 1;
  }
}

@include bem-element('combo-level-text') {
  text-shadow: 1px 1px 2px rgba($color-black, 0.3);
}

// 响应式设计
@media (max-width: 768px) {
  @include bem-block('combo-indicator') {
    top: var(--spacing-4);
    right: var(--spacing-4);
  }
  
  .combo-indicator__combo-content {
    padding: var(--spacing-3) var(--spacing-4);
    gap: var(--spacing-2);
  }
  
  .combo-indicator__combo-icon {
    font-size: 1.5rem;
  }
  
  .combo-indicator__combo-number {
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-bold);
  }
  
  .combo-indicator__combo-multiplier {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-bold);
  }
}

@media (max-width: 576px) {
  .combo-indicator {
    top: $spacing-3;
    right: $spacing-3;
  }
  
  .combo-indicator__combo-content {
    padding: $spacing-2 $spacing-3;
  }
  
  .combo-indicator__combo-icon {
    font-size: 1.25rem;
  }
  
  .combo-indicator__combo-number {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
  }
  
  .combo-indicator__combo-label {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
  }
}
</style>

