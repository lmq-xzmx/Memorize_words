// 图片配置文件
export const imageConfig = {
  // 默认图片
  defaultImages: {
    wordCard: 'https://picsum.photos/300/200?random=1',
    userAvatar: 'https://picsum.photos/100/100?random=2',
    placeholder: 'https://picsum.photos/200/150?random=3'
  },
  
  // 单词图片映射
  wordImages: {
    'apple': 'https://picsum.photos/300/200?random=10',
    'book': 'https://picsum.photos/300/200?random=11',
    'cat': 'https://picsum.photos/300/200?random=12',
    'dog': 'https://picsum.photos/300/200?random=13',
    'elephant': 'https://picsum.photos/300/200?random=14',
    'flower': 'https://picsum.photos/300/200?random=15',
    'guitar': 'https://picsum.photos/300/200?random=16',
    'house': 'https://picsum.photos/300/200?random=17',
    'ice': 'https://picsum.photos/300/200?random=18',
    'jungle': 'https://picsum.photos/300/200?random=19'
  },
  
  // 获取单词图片
  getWordImage(word) {
    return this.wordImages[word.toLowerCase()] || this.defaultImages.wordCard
  },
  
  // 获取随机图片
  getRandomImage() {
    const randomId = Math.floor(Math.random() * 1000) + 20
    return `https://picsum.photos/300/200?random=${randomId}`
  },
  
  // 图片预加载
  preloadImages(urls) {
    return Promise.all(
      urls.map(url => {
        return new Promise((resolve, reject) => {
          const img = new Image()
          img.onload = () => resolve(url)
          img.onerror = () => reject(new Error(`Failed to load image: ${url}`))
          img.src = url
        })
      })
    )
  }
}

export default imageConfig