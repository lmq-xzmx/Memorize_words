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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
}

.header {
  text-align: center;
  margin-bottom: 30px;
  color: white;
}

.header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.header p {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0;
}

.content {
  max-width: 800px;
  margin: 0 auto;
}

.tabs {
  display: flex;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 20px;
  backdrop-filter: blur(10px);
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.tab-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.tab-item.active {
  background: white;
  color: #667eea;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tab-content {
  min-height: 400px;
}

/* 话题卡片 */
.topic-card, .share-card, .qa-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.topic-card:hover, .share-card:hover, .qa-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.topic-header, .share-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 16px;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.time {
  font-size: 12px;
  color: #666;
}

.level {
  font-size: 12px;
  color: #667eea;
  font-weight: 500;
}

.topic-tag {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.topic-content h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.topic-content p, .share-content p {
  margin: 0;
  color: #666;
  line-height: 1.6;
}

.topic-stats {
  display: flex;
  gap: 20px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-size: 14px;
}

.stat-item .icon {
  font-size: 16px;
}

/* 分享内容 */
.share-content {
  margin: 15px 0;
}

.share-image {
  margin-top: 12px;
  border-radius: 8px;
  overflow: hidden;
}

.share-image img {
  width: 100%;
  height: auto;
  display: block;
}

.share-actions {
  display: flex;
  gap: 12px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  background: #f8f9fa;
  border-radius: 20px;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: #667eea;
  color: white;
}

/* 问答区 */
.question {
  margin-bottom: 15px;
}

.q-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.q-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #ff6b6b;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.q-title {
  font-weight: 600;
  color: #333;
  font-size: 16px;
}

.q-author {
  font-size: 12px;
  color: #666;
  margin-left: 32px;
}

.answer {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
}

.a-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.a-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #51cf66;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.a-author {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.a-content {
  color: #666;
  line-height: 1.6;
  margin-left: 32px;
}

.qa-actions {
  display: flex;
  gap: 12px;
  margin-top: 15px;
}

/* 悬浮按钮 */
.fab {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 1000;
}

.fab-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.fab-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
}

/* 弹窗 */
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
  backdrop-filter: blur(4px);
}

.modal {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.3s ease;
}

.close-btn:hover {
  background: #f0f0f0;
}

.modal-body {
  padding: 20px;
}

.modal-body textarea {
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

.modal-body textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #f0f0f0;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary {
  background: #f8f9fa;
  color: #666;
}

.btn-secondary:hover {
  background: #e9ecef;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .community {
    padding: 15px;
  }
  
  .header h1 {
    font-size: 2rem;
  }
  
  .tabs {
    flex-direction: column;
    gap: 4px;
  }
  
  .tab-item {
    padding: 10px 15px;
  }
  
  .topic-card, .share-card, .qa-card {
    padding: 15px;
  }
  
  .topic-stats {
    gap: 15px;
  }
  
  .share-actions, .qa-actions {
    flex-wrap: wrap;
  }
  
  .fab {
    bottom: 20px;
    right: 20px;
  }
  
  .fab-btn {
    width: 50px;
    height: 50px;
    font-size: 18px;
  }
  
  .modal {
    width: 95%;
    margin: 20px;
  }
}
</style>

