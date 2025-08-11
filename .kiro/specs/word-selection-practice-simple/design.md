# 设计文档

## 概述

word-selection-practice2（简洁模式）是一个专注于高效学习的单词选择练习系统。设计理念强调简洁性、响应性和任务导向，为用户提供无干扰的学习体验。系统采用Vue.js前端框架，与现有Django后端API集成，确保数据一致性和功能复用。

## 架构

### 整体架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 Vue.js   │    │   Django API    │    │   数据库层      │
│                 │    │                 │    │                 │
│ - 练习组件      │◄──►│ - 单词API       │◄──►│ - Word模型      │
│ - 状态管理      │    │ - 学习记录API   │    │ - LearningSession│
│ - 音频播放      │    │ - 用户进度API   │    │ - WordLearningRecord│
│ - 响应式布局    │    │ - 音频服务      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 前端架构层次
```
WordSelectionPractice2.vue (主容器)
├── PracticeHeader.vue (标题和进度)
├── WordDisplay.vue (单词展示区)
├── OptionsPanel.vue (选项面板)
├── ProgressBar.vue (进度条)
├── ResultModal.vue (结果弹窗)
└── AudioPlayer.vue (音频播放器)
```

## 组件和接口

### 核心组件设计

#### 1. WordSelectionPractice2.vue (主组件)
**职责：** 整体状态管理、API调用协调、用户交互流程控制

**状态管理：**
```javascript
data() {
  return {
    // 练习状态
    currentWordIndex: 0,
    words: [],
    userAnswers: [],
    isLoading: false,
    isCompleted: false,
    
    // 当前题目状态
    currentWord: null,
    selectedOption: null,
    showResult: false,
    isCorrect: false,
    
    // 统计信息
    correctCount: 0,
    totalTime: 0,
    startTime: null,
    
    // UI状态
    showResultModal: false,
    audioLoading: false
  }
}
```

**关键方法：**
- `initializePractice()`: 初始化练习，加载单词数据
- `loadNextWord()`: 加载下一个单词
- `submitAnswer(option)`: 提交答案并处理结果
- `completeSession()`: 完成练习会话
- `restartPractice()`: 重新开始练习

#### 2. WordDisplay.vue (单词展示组件)
**职责：** 展示当前单词、音标、音频播放控制

**Props：**
```javascript
props: {
  word: Object, // { text, phonetic, audio_url, meaning }
  showResult: Boolean,
  isCorrect: Boolean
}
```

**功能：**
- 单词文本展示（大字体，居中）
- 音标显示（IPA格式）
- 音频播放按钮和状态指示
- 答题结果的视觉反馈

#### 3. OptionsPanel.vue (选项面板组件)
**职责：** 展示选择选项，处理用户选择

**Props：**
```javascript
props: {
  options: Array, // [{ id, text, is_correct }]
  selectedOption: Number,
  showResult: Boolean,
  disabled: Boolean
}
```

**功能：**
- 4个选项的网格布局
- 选中状态的视觉反馈
- 正确/错误答案的颜色标识
- 触摸友好的按钮设计

#### 4. ProgressBar.vue (进度条组件)
**职责：** 显示学习进度和统计信息

**Props：**
```javascript
props: {
  current: Number,
  total: Number,
  correctCount: Number
}
```

**功能：**
- 线性进度条（百分比显示）
- 当前题目数/总题目数
- 实时正确率显示
- 简洁的数字统计

#### 5. ResultModal.vue (结果弹窗组件)
**职责：** 显示练习完成结果和操作选项

**Props：**
```javascript
props: {
  visible: Boolean,
  totalWords: Number,
  correctCount: Number,
  totalTime: Number,
  incorrectWords: Array
}
```

**功能：**
- 总体成绩展示（正确率、用时）
- 错误题目回顾列表
- 重新开始按钮
- 返回主页按钮

### API接口设计

#### 1. 获取练习单词
```
GET /api/teaching/words/practice/
Query Parameters:
- count: 练习题目数量 (默认20)
- difficulty: 难度级别 (可选)
- category: 单词分类 (可选)

Response:
{
  "words": [
    {
      "id": 1,
      "text": "example",
      "phonetic": "/ɪɡˈzæmpəl/",
      "audio_url": "/media/audio/example.mp3",
      "meaning": "例子",
      "options": [
        {"id": 1, "text": "例子", "is_correct": true},
        {"id": 2, "text": "练习", "is_correct": false},
        {"id": 3, "text": "测试", "is_correct": false},
        {"id": 4, "text": "问题", "is_correct": false}
      ]
    }
  ]
}
```

#### 2. 提交学习记录
```
POST /api/teaching/learning-sessions/
Request Body:
{
  "session_type": "word_selection_simple",
  "total_words": 20,
  "correct_count": 16,
  "total_time": 180,
  "word_records": [
    {
      "word_id": 1,
      "is_correct": true,
      "response_time": 3.2,
      "selected_option": 1
    }
  ]
}

Response:
{
  "session_id": 123,
  "created_at": "2024-01-01T10:00:00Z"
}
```

## 数据模型

### 前端数据模型

#### Word对象
```javascript
{
  id: Number,
  text: String,        // 单词文本
  phonetic: String,    // 音标
  audio_url: String,   // 音频文件URL
  meaning: String,     // 中文释义
  options: Array       // 选项数组
}
```

#### Option对象
```javascript
{
  id: Number,
  text: String,        // 选项文本
  is_correct: Boolean  // 是否为正确答案
}
```

#### UserAnswer对象
```javascript
{
  word_id: Number,
  selected_option_id: Number,
  is_correct: Boolean,
  response_time: Number,  // 响应时间（秒）
  timestamp: Date
}
```

#### SessionResult对象
```javascript
{
  total_words: Number,
  correct_count: Number,
  accuracy_rate: Number,    // 正确率
  total_time: Number,       // 总用时（秒）
  average_time: Number,     // 平均每题用时
  incorrect_words: Array    // 错误的单词列表
}
```

### 后端数据模型复用

系统复用现有的Django模型：
- `Word`: 单词基础信息
- `LearningSession`: 学习会话记录
- `WordLearningRecord`: 单词学习记录
- `User`: 用户信息

## 错误处理

### 前端错误处理策略

#### 1. 网络错误
```javascript
// API调用错误处理
async function fetchWords() {
  try {
    const response = await api.get('/words/practice/');
    return response.data;
  } catch (error) {
    if (error.response?.status === 404) {
      showError('没有找到合适的练习内容');
    } else if (error.code === 'NETWORK_ERROR') {
      showError('网络连接失败，请检查网络设置');
    } else {
      showError('加载失败，请稍后重试');
    }
    throw error;
  }
}
```

#### 2. 音频播放错误
```javascript
// 音频播放错误处理
async function playAudio(audioUrl) {
  try {
    await audio.play();
  } catch (error) {
    console.warn('音频播放失败:', error);
    showToast('音频暂时无法播放');
  }
}
```

#### 3. 数据验证错误
```javascript
// 数据完整性检查
function validateWordData(word) {
  if (!word.text || !word.options || word.options.length !== 4) {
    throw new Error('单词数据不完整');
  }
  
  const correctOptions = word.options.filter(opt => opt.is_correct);
  if (correctOptions.length !== 1) {
    throw new Error('单词选项配置错误');
  }
}
```

### 用户体验优化

#### 1. 加载状态管理
- 初始加载：显示骨架屏
- 音频加载：显示加载图标
- 提交答案：按钮禁用状态

#### 2. 离线处理
- 检测网络状态
- 本地缓存已加载的单词
- 离线时显示友好提示

#### 3. 错误恢复
- 自动重试机制
- 手动刷新选项
- 降级到基础功能

## 测试策略

### 单元测试

#### 1. 组件测试
```javascript
// WordDisplay.vue 测试
describe('WordDisplay', () => {
  test('正确显示单词信息', () => {
    const word = {
      text: 'example',
      phonetic: '/ɪɡˈzæmpəl/',
      meaning: '例子'
    };
    
    const wrapper = mount(WordDisplay, {
      props: { word }
    });
    
    expect(wrapper.text()).toContain('example');
    expect(wrapper.text()).toContain('/ɪɡˈzæmpəl/');
  });
  
  test('音频播放按钮功能', async () => {
    const wrapper = mount(WordDisplay, {
      props: { word: mockWord }
    });
    
    await wrapper.find('.audio-button').trigger('click');
    expect(wrapper.emitted('play-audio')).toBeTruthy();
  });
});
```

#### 2. 状态管理测试
```javascript
// 练习流程测试
describe('Practice Flow', () => {
  test('答题流程完整性', async () => {
    const wrapper = mount(WordSelectionPractice2);
    
    // 模拟加载单词
    await wrapper.vm.initializePractice();
    expect(wrapper.vm.words.length).toBeGreaterThan(0);
    
    // 模拟答题
    await wrapper.vm.submitAnswer(1);
    expect(wrapper.vm.currentWordIndex).toBe(1);
    expect(wrapper.vm.userAnswers.length).toBe(1);
  });
});
```

### 集成测试

#### 1. API集成测试
- 单词数据获取
- 学习记录提交
- 错误响应处理

#### 2. 用户流程测试
- 完整练习流程
- 重新开始功能
- 结果查看功能

### 性能测试

#### 1. 加载性能
- 首屏加载时间 < 2秒
- 题目切换时间 < 300ms
- 音频播放响应 < 500ms

#### 2. 内存使用
- 长时间使用无内存泄漏
- 音频资源及时释放
- 组件销毁清理

### 兼容性测试

#### 1. 浏览器兼容
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

#### 2. 设备兼容
- 桌面端（1920x1080, 1366x768）
- 平板端（768x1024, 1024x768）
- 手机端（375x667, 414x896）

#### 3. 网络环境
- 高速网络（4G/WiFi）
- 慢速网络（3G）
- 间歇性网络中断

## 性能优化

### 前端优化策略

#### 1. 资源优化
```javascript
// 图片懒加载
const imageObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      imageObserver.unobserve(img);
    }
  });
});

// 音频预加载
function preloadAudio(audioUrls) {
  audioUrls.slice(0, 3).forEach(url => {
    const audio = new Audio();
    audio.preload = 'metadata';
    audio.src = url;
  });
}
```

#### 2. 状态优化
```javascript
// 使用computed优化计算
computed: {
  progressPercentage() {
    return Math.round((this.currentWordIndex / this.words.length) * 100);
  },
  
  accuracyRate() {
    return this.userAnswers.length > 0 
      ? Math.round((this.correctCount / this.userAnswers.length) * 100)
      : 0;
  }
}
```

#### 3. 渲染优化
```vue
<!-- 使用v-show代替v-if减少重渲染 -->
<div v-show="!isLoading" class="practice-content">
  <!-- 内容 -->
</div>

<!-- 使用key优化列表渲染 -->
<div 
  v-for="option in currentWord.options" 
  :key="`${currentWord.id}-${option.id}`"
  class="option-item"
>
  {{ option.text }}
</div>
```

### 网络优化

#### 1. 请求优化
- 单词数据批量获取
- 音频文件CDN加速
- 请求去重和缓存

#### 2. 数据压缩
- API响应gzip压缩
- 音频文件格式优化
- 图片资源WebP格式

## 部署和维护

### 构建配置
```javascript
// vue.config.js
module.exports = {
  publicPath: '/static/teaching/',
  outputDir: 'dist/word-selection-practice2',
  assetsDir: 'assets',
  
  configureWebpack: {
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            name: 'vendor',
            test: /[\\/]node_modules[\\/]/,
            chunks: 'all'
          }
        }
      }
    }
  }
};
```

### 监控和日志
```javascript
// 错误监控
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
  // 发送错误报告到监控系统
});

// 性能监控
const observer = new PerformanceObserver((list) => {
  list.getEntries().forEach((entry) => {
    if (entry.entryType === 'navigation') {
      console.log('Page load time:', entry.loadEventEnd - entry.fetchStart);
    }
  });
});
observer.observe({ entryTypes: ['navigation'] });
```

### 维护策略
1. **版本管理**: 语义化版本控制
2. **代码质量**: ESLint + Prettier
3. **文档更新**: 组件文档和API文档
4. **性能监控**: 定期性能审计
5. **用户反馈**: 错误收集和用户体验改进