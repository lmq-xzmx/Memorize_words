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
}

.particle {
  position: absolute;
  font-size: 20px;
  animation: particleFloat 2s ease-out forwards;
  opacity: 0;
}

@keyframes particleFloat {
  0% {
    opacity: 1;
    transform: translateY(0) scale(0.5) rotate(0deg);
  }
  50% {
    opacity: 1;
    transform: translateY(-100px) scale(1) rotate(180deg);
  }
  100% {
    opacity: 0;
    transform: translateY(-200px) scale(0.5) rotate(360deg);
  }
}

/* 不同类型的特殊动画 */
.particle-container[data-type="combo"] .particle {
  animation: comboParticle 1.5s ease-out forwards;
}

@keyframes comboParticle {
  0% {
    opacity: 1;
    transform: scale(0) rotate(0deg);
  }
  50% {
    opacity: 1;
    transform: scale(1.5) rotate(180deg);
  }
  100% {
    opacity: 0;
    transform: scale(0.5) rotate(360deg);
  }
}

.particle-container[data-type="levelup"] .particle {
  animation: levelupParticle 2.5s ease-out forwards;
}

@keyframes levelupParticle {
  0% {
    opacity: 1;
    transform: translateY(100px) scale(0) rotate(0deg);
  }
  30% {
    opacity: 1;
    transform: translateY(0) scale(1.2) rotate(120deg);
  }
  70% {
    opacity: 1;
    transform: translateY(-50px) scale(1) rotate(240deg);
  }
  100% {
    opacity: 0;
    transform: translateY(-150px) scale(0.3) rotate(360deg);
  }
}
</style>