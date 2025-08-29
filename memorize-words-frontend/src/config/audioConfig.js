// 音频配置文件
export const audioConfig = {
  // 音频API配置
  ttsConfig: {
    // 使用Web Speech API进行文本转语音
    enabled: typeof window !== 'undefined' && 'speechSynthesis' in window,
    defaultVoice: 'en-US',
    rate: 0.8,
    pitch: 1,
    volume: 1
  },
  
  // 预设音频文件映射（可选）
  audioFiles: {
    'apple': '/audio/apple.mp3',
    'book': '/audio/book.mp3',
    'cat': '/audio/cat.mp3',
    'dog': '/audio/dog.mp3',
    'elephant': '/audio/elephant.mp3'
  },
  
  // 播放单词发音
  playWordAudio(word, options = {}) {
    return new Promise((resolve, reject) => {
      try {
        // 优先使用预设音频文件
        if (this.audioFiles[word.toLowerCase()]) {
          const audio = new Audio(this.audioFiles[word.toLowerCase()])
          audio.onended = () => resolve()
          audio.onerror = () => {
            // 如果音频文件加载失败，回退到TTS
            this.playTTS(word, options).then(resolve).catch(reject)
          }
          audio.play()
          return
        }
        
        // 使用TTS
        this.playTTS(word, options).then(resolve).catch(reject)
      } catch (error) {
        reject(error)
      }
    })
  },
  
  // 使用Web Speech API播放TTS
  playTTS(text, options = {}) {
    return new Promise((resolve, reject) => {
      if (!this.ttsConfig.enabled) {
        reject(new Error('Speech synthesis not supported'))
        return
      }
      
      try {
        const utterance = new SpeechSynthesisUtterance(text)
        
        // 设置语音参数
        utterance.rate = options.rate || this.ttsConfig.rate
        utterance.pitch = options.pitch || this.ttsConfig.pitch
        utterance.volume = options.volume || this.ttsConfig.volume
        utterance.lang = options.lang || this.ttsConfig.defaultVoice
        
        // 事件监听
        utterance.onend = () => resolve()
        utterance.onerror = (event) => reject(new Error(`Speech synthesis error: ${event.error}`))
        
        // 播放
        window.speechSynthesis.speak(utterance)
      } catch (error) {
        reject(error)
      }
    })
  },
  
  // 停止当前播放
  stopAudio() {
    if (this.ttsConfig.enabled) {
      window.speechSynthesis.cancel()
    }
  },
  
  // 获取可用语音列表
  getAvailableVoices() {
    if (!this.ttsConfig.enabled) {
      return []
    }
    
    return window.speechSynthesis.getVoices().filter(voice => 
      voice.lang.startsWith('en')
    )
  },
  
  // 播放提示音
  playNotificationSound(type = 'success') {
    const frequencies = {
      success: [523, 659, 784], // C5, E5, G5
      error: [392, 311, 247],   // G4, Eb4, B3
      warning: [440, 554, 659], // A4, C#5, E5
      info: [523, 523, 523]     // C5, C5, C5
    }
    
    const freq = frequencies[type] || frequencies.info
    this.playBeep(freq, 200)
  },
  
  // 播放蜂鸣音
  playBeep(frequencies, duration = 200) {
    if (typeof window === 'undefined' || !window.AudioContext) {
      return
    }
    
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)()
      
      frequencies.forEach((freq, index) => {
        const oscillator = audioContext.createOscillator()
        const gainNode = audioContext.createGain()
        
        oscillator.connect(gainNode)
        gainNode.connect(audioContext.destination)
        
        oscillator.frequency.setValueAtTime(freq, audioContext.currentTime)
        oscillator.type = 'sine'
        
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime)
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration / 1000)
        
        const startTime = audioContext.currentTime + (index * duration / 1000)
        oscillator.start(startTime)
        oscillator.stop(startTime + duration / 1000)
      })
    } catch (error) {
      console.warn('Audio playback failed:', error)
    }
  }
}

export default audioConfig