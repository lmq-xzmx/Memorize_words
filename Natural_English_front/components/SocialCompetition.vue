<template>
  <div class="particle-container" v-if="show">
    <div 
      v-for="particle in particles" 
      :key="particle.id"
      class="particle"
      :style="{
        left: particle.x + 'px',
        top: particle.y + 'px',
        backgroundColor: particle.color,
        animationDelay: particle.delay + 'ms',
        animationDuration: particle.duration + 'ms'
      }"
    >
      {{ particle.emoji }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'ParticleEffect',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'success', // success, combo, levelup
      validator: value => ['success', 'combo', 'levelup', 'achievement'].includes(value)
    },
    intensity: {
      type: Number,
      default: 10
    }
  },
  data() {
    return {
      particles: []
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        this.generateParticles()
        // 自动隐藏
        setTimeout(() => {
          this.$emit('hide')
        }, 2000)
      } else {
        this.particles = []
      }
    }
  },
  methods: {
    generateParticles() {
      this.particles = []
      const config = this.getParticleConfig()
      
      for (let i = 0; i < this.intensity; i++) {
        this.particles.push({
          id: i,
          x: Math.random() * window.innerWidth,
          y: Math.random() * window.innerHeight,
          color: config.colors[Math.floor(Math.random() * config.colors.length)],
          emoji: config.emojis[Math.floor(Math.random() * config.emojis.length)],
          delay: Math.random() * 500,
          duration: 1000 + Math.random() * 1000
        })
      }
    },
    getParticleConfig() {
      const configs = {
        success: {
          colors: ['#4CAF50', '#8BC34A', '#CDDC39'],
          emojis: ['✨', '⭐', '💫', '🌟']
        },
        combo: {
          colors: ['#FF9800', '#FF5722', '#F44336'],
          emojis: ['🔥', '⚡', '💥', '🎯']
        },
        levelup: {
          colors: ['#9C27B0', '#673AB7', '#3F51B5'],
          emojis: ['🎉', '🎊', '👑', '🏆']
        },
        achievement: {
          colors: ['#FFD700', '#FFA500', '#FF6347'],
          emojis: ['🏆', '🥇', '🎖️', '👑']
        }
      }
      return configs[this.type] || configs.success
    }
  }
}
</script>

<style scoped>
.particle-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 9999;
  overflow: hidden;
}

.particle {
  position: absolute;
  font-size: 1.5rem;
  font-weight: bold;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: particleFloat linear forwards;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
  text-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
}

@keyframes particleFloat {
  0% {
    opacity: 1;
    transform: translateY(0) scale(0.5) rotate(0deg);
  }
  50% {
    opacity: 1;
    transform: translateY(-50px) scale(1) rotate(180deg);
  }
  100% {
    opacity: 0;
    transform: translateY(-100px) scale(0.3) rotate(360deg);
  }
}

/* 成功效果 */
.particle-container[data-type="success"] .particle {
  animation: successParticle linear forwards;
}

@keyframes successParticle {
  0% {
    opacity: 1;
    transform: translateY(0) scale(0.8);
    filter: brightness(1);
  }
  25% {
    opacity: 1;
    transform: translateY(-20px) scale(1.2);
    filter: brightness(1.5);
  }
  50% {
    opacity: 1;
    transform: translateY(-40px) scale(1);
    filter: brightness(1.2);
  }
  100% {
    opacity: 0;
    transform: translateY(-80px) scale(0.5);
    filter: brightness(0.8);
  }
}

/* 连击效果 */
.particle-container[data-type="combo"] .particle {
  animation: comboParticle linear forwards;
}

@keyframes comboParticle {
  0% {
    opacity: 1;
    transform: translateY(0) scale(0.5) rotate(0deg);
    filter: hue-rotate(0deg);
  }
  25% {
    opacity: 1;
    transform: translateY(-15px) scale(1.3) rotate(90deg);
    filter: hue-rotate(45deg);
  }
  50% {
    opacity: 1;
    transform: translateY(-30px) scale(1.1) rotate(180deg);
    filter: hue-rotate(90deg);
  }
  75% {
    opacity: 0.8;
    transform: translateY(-45px) scale(0.9) rotate(270deg);
    filter: hue-rotate(135deg);
  }
  100% {
    opacity: 0;
    transform: translateY(-60px) scale(0.3) rotate(360deg);
    filter: hue-rotate(180deg);
  }
}

/* 升级效果 */
.particle-container[data-type="levelup"] .particle {
  animation: levelupParticle linear forwards;
}

@keyframes levelupParticle {
  0% {
    opacity: 1;
    transform: translateY(0) scale(0.3);
    box-shadow: 0 0 5px currentColor;
  }
  20% {
    opacity: 1;
    transform: translateY(-10px) scale(1.5);
    box-shadow: 0 0 15px currentColor;
  }
  40% {
    opacity: 1;
    transform: translateY(-25px) scale(1.2);
    box-shadow: 0 0 20px currentColor;
  }
  60% {
    opacity: 1;
    transform: translateY(-40px) scale(1);
    box-shadow: 0 0 15px currentColor;
  }
  80% {
    opacity: 0.7;
    transform: translateY(-55px) scale(0.8);
    box-shadow: 0 0 10px currentColor;
  }
  100% {
    opacity: 0;
    transform: translateY(-70px) scale(0.4);
    box-shadow: 0 0 5px currentColor;
  }
}

/* 成就效果 */
.particle-container[data-type="achievement"] .particle {
  animation: achievementParticle linear forwards;
}

@keyframes achievementParticle {
  0% {
    opacity: 1;
    transform: translateY(0) scale(0.6) rotate(0deg);
    box-shadow: 0 0 10px gold;
    filter: brightness(1);
  }
  15% {
    opacity: 1;
    transform: translateY(-5px) scale(1.4) rotate(45deg);
    box-shadow: 0 0 20px gold;
    filter: brightness(1.5);
  }
  30% {
    opacity: 1;
    transform: translateY(-15px) scale(1.2) rotate(90deg);
    box-shadow: 0 0 25px gold;
    filter: brightness(1.3);
  }
  50% {
    opacity: 1;
    transform: translateY(-30px) scale(1) rotate(180deg);
    box-shadow: 0 0 20px gold;
    filter: brightness(1.2);
  }
  70% {
    opacity: 0.8;
    transform: translateY(-45px) scale(0.8) rotate(270deg);
    box-shadow: 0 0 15px gold;
    filter: brightness(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-60px) scale(0.4) rotate(360deg);
    box-shadow: 0 0 5px gold;
    filter: brightness(0.8);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .particle {
    font-size: 1.2rem;
    width: 25px;
    height: 25px;
  }
}

@media (max-width: 480px) {
  .particle {
    font-size: 1rem;
    width: 20px;
    height: 20px;
  }
}

/* 性能优化 */
.particle {
  will-change: transform, opacity;
  backface-visibility: hidden;
  transform-style: preserve-3d;
}

/* 减少动画在低性能设备上的影响 */
@media (prefers-reduced-motion: reduce) {
  .particle {
    animation-duration: 0.5s !important;
  }
  
  @keyframes particleFloat {
    0% {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
    100% {
      opacity: 0;
      transform: translateY(-20px) scale(0.8);
    }
  }
}
</style>

