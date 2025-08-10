<template>
  <div class="community">
    <div class="header">
      <h1>社区互动</h1>
      <p>与其他学习者一起交流进步</p>
    </div>
    
    <div class="content">
      <div class="tabs">
        <div 
          v-for="tab in tabs" 
          :key="tab.key"
          class="tab-item"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.name }}
        </div>
      </div>
      
      <div class="tab-content">
        <!-- 热门话题 -->
        <div v-if="activeTab === 'hot'" class="topic-list">
          <div v-for="topic in hotTopics" :key="topic.id" class="topic-card">
            <div class="topic-header">
              <div class="user-info">
                <div class="avatar">{{ topic.author.charAt(0) }}</div>
                <div class="user-details">
                  <div class="username">{{ topic.author }}</div>
                  <div class="time">{{ topic.time }}</div>
                </div>
              </div>
              <div class="topic-tag">{{ topic.tag }}</div>
            </div>
            <div class="topic-content">
              <h3>{{ topic.title }}</h3>
              <p>{{ topic.content }}</p>
            </div>
            <div class="topic-stats">
              <span class="stat-item">
                <span class="icon">👍</span>
                {{ topic.likes }}
              </span>
              <span class="stat-item">
                <span class="icon">💬</span>
                {{ topic.comments }}
              </span>
              <span class="stat-item">
                <span class="icon">👁</span>
                {{ topic.views }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- 学习分享 -->
        <div v-if="activeTab === 'share'" class="share-list">
          <div v-for="share in shareList" :key="share.id" class="share-card">
            <div class="share-header">
              <div class="user-info">
                <div class="avatar">{{ share.author.charAt(0) }}</div>
                <div class="user-details">
                  <div class="username">{{ share.author }}</div>
                  <div class="level">{{ share.level }}</div>
                </div>
              </div>
            </div>
            <div class="share-content">
              <p>{{ share.content }}</p>
              <div v-if="share.image" class="share-image">
                <img :src="share.image" alt="分享图片">
              </div>
            </div>
            <div class="share-actions">
              <button class="action-btn">
                <span class="icon">❤️</span>
                点赞
              </button>
              <button class="action-btn">
                <span class="icon">💬</span>
                评论
              </button>
              <button class="action-btn">
                <span class="icon">📤</span>
                分享
              </button>
            </div>
          </div>
        </div>
        
        <!-- 问答区 -->
        <div v-if="activeTab === 'qa'" class="qa-list">
          <div v-for="qa in qaList" :key="qa.id" class="qa-card">
            <div class="question">
              <div class="q-header">
                <span class="q-icon">Q</span>
                <span class="q-title">{{ qa.question }}</span>
              </div>
              <div class="q-author">提问者：{{ qa.questioner }}</div>
            </div>
            <div v-if="qa.answer" class="answer">
              <div class="a-header">
                <span class="a-icon">A</span>
                <span class="a-author">{{ qa.answerer }}</span>
              </div>
              <div class="a-content">{{ qa.answer }}</div>
            </div>
            <div class="qa-actions">
              <button class="action-btn">
                <span class="icon">👍</span>
                有用 {{ qa.helpful }}
              </button>
              <button class="action-btn">
                <span class="icon">💬</span>
                回答
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 发布按钮 -->
    <div class="fab">
      <button class="fab-btn" @click="showPublishModal = true">
        <span class="icon">✏️</span>
      </button>
    </div>
    
    <!-- 发布弹窗 -->
    <div v-if="showPublishModal" class="modal-overlay" @click="showPublishModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>发布内容</h3>
          <button class="close-btn" @click="showPublishModal = false">×</button>
        </div>
        <div class="modal-body">
          <textarea 
            v-model="publishContent" 
            placeholder="分享你的学习心得或提出问题..."
            rows="4"
          ></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showPublishModal = false">取消</button>
          <button class="btn btn-primary" @click="publishPost">发布</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Community',
  data() {
    return {
      activeTab: 'hot',
      showPublishModal: false,
      publishContent: '',
      tabs: [
        { key: 'hot', name: '热门话题' },
        { key: 'share', name: '学习分享' },
        { key: 'qa', name: '问答区' }
      ],
      hotTopics: [
        {
          id: 1,
          title: '如何快速记忆英语单词？',
          content: '最近在背单词，总是记了忘，忘了记，有什么好的方法吗？',
          author: '学习小白',
          time: '2小时前',
          tag: '学习方法',
          likes: 23,
          comments: 15,
          views: 156
        },
        {
          id: 2,
          title: '分享一个超好用的单词记忆法',
          content: '联想记忆法真的很有效，把单词和生活场景联系起来...',
          author: '英语达人',
          time: '5小时前',
          tag: '经验分享',
          likes: 45,
          comments: 28,
          views: 234
        }
      ],
      shareList: [
        {
          id: 1,
          content: '今天学会了10个新单词，感觉很有成就感！坚持就是胜利 💪',
          author: '努力学习中',
          level: 'Lv.5',
          image: null
        },
        {
          id: 2,
          content: '分享一下我的单词本，这样整理单词真的很有效果！',
          author: '学霸小王',
          level: 'Lv.8',
          image: '/images/wordbook.jpg'
        }
      ],
      qaList: [
        {
          id: 1,
          question: 'affect 和 effect 有什么区别？',
          questioner: '初学者',
          answer: 'affect是动词，表示影响；effect是名词，表示效果、结果。记忆方法：A for Action (affect是动作)，E for End result (effect是结果)。',
          answerer: '英语老师',
          helpful: 12
        },
        {
          id: 2,
          question: '如何提高英语听力？',
          questioner: '听力困难户',
          answer: null,
          helpful: 0
        }
      ]
    }
  },
  methods: {
    publishPost() {
      if (this.publishContent.trim()) {
        alert('发布成功！')
        this.publishContent = ''
        this.showPublishModal = false
      }
    }
  }
}
</script>

<style scoped>
.community {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 80px;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  padding: 30px 20px;
}

.header h1 {
  font-size: 24px;
  margin-bottom: 8px;
}

.header p {
  font-size: 14px;
  opacity: 0.9;
}

.content {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.tabs {
  display: flex;
  background: white;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  color: #666;
}

.tab-item.active {
  background: #007aff;
  color: white;
}

.topic-card,
.share-card,
.qa-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.topic-header,
.share-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.user-info {
  display: flex;
  align-items: center;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #007aff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 12px;
}

.username {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.time,
.level {
  font-size: 12px;
  color: #666;
}

.topic-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.topic-content h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
}

.topic-content p,
.share-content p {
  color: #666;
  line-height: 1.5;
  margin-bottom: 12px;
}

.topic-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.share-image img {
  width: 100%;
  border-radius: 8px;
  margin-top: 8px;
}

.share-actions,
.qa-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  background: white;
  color: #666;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: #f5f5f5;
  border-color: #007aff;
}

.question {
  margin-bottom: 12px;
}

.q-header,
.a-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.q-icon,
.a-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 12px;
}

.q-icon {
  background: #ff9800;
  color: white;
}

.a-icon {
  background: #4caf50;
  color: white;
}

.q-title {
  font-weight: 600;
  color: #333;
}

.q-author,
.a-author {
  font-size: 12px;
  color: #666;
}

.answer {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.a-content {
  color: #333;
  line-height: 1.5;
}

.fab {
  position: fixed;
  bottom: 80px;
  right: 20px;
  z-index: 1000;
}

.fab-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #007aff;
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
}

.fab-btn:hover {
  transform: scale(1.1);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  max-height: 80vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #666;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
}

.modal-body textarea {
  width: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  resize: vertical;
  min-height: 100px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
}

.btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-primary {
  background: #007aff;
  color: white;
}

.btn:hover {
  opacity: 0.8;
}
</style>