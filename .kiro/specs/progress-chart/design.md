# Design Document

## Overview

基于需求分析，我们将创建一个纯HTML/CSS/JavaScript的九宫格进程图表组件，用于在Django项目中展示学习进度数据。该组件将采用圆形布局，中心显示主要信息，周围8个扇形区域显示不同类别的数据。

## Architecture

### 技术栈选择
- **前端框架**: 纯HTML/CSS/JavaScript（不依赖Vue.js）
- **样式框架**: Bootstrap 5（项目已集成）
- **图表实现**: 纯CSS + JavaScript（使用CSS Grid和Flexbox布局）
- **动画效果**: CSS3 Transitions和Animations
- **数据交互**: 原生JavaScript

### 组件架构
```
ProgressChart/
├── HTML结构层
│   ├── 容器元素
│   ├── 中心圆形区域
│   └── 8个扇形区域
├── CSS样式层
│   ├── 布局样式（Grid/Flexbox）
│   ├── 视觉效果（颜色、阴影、动画）
│   └── 响应式设计
└── JavaScript逻辑层
    ├── 数据处理
    ├── 动态渲染
    └── 交互事件
```

## Components and Interfaces

### 1. HTML结构设计

#### 主容器结构
```html
<div class="progress-chart-container">
  <div class="progress-chart">
    <!-- 中心圆形区域 -->
    <div class="center-circle">
      <div class="center-content">
        <h3 class="center-title">九宫格进程</h3>
        <p class="center-subtitle">学习进度</p>
      </div>
    </div>
    
    <!-- 8个扇形区域 -->
    <div class="grid-items">
      <div class="grid-item" data-position="1" data-category="掌握">
        <div class="item-content">
          <div class="item-label">掌握</div>
          <div class="item-value">49</div>
        </div>
      </div>
      <!-- 其他7个区域... -->
    </div>
  </div>
</div>
```

#### 区域定位系统
使用CSS Grid和绝对定位实现8个区域的精确布局：
- 位置1: 上方中央（掌握）
- 位置2: 右上角（遗忘）
- 位置3: 右方中央（学习中）
- 位置4: 右下角（测试）
- 位置5: 下方中央（口音文本）
- 位置6: 左下角（口音文件）
- 位置7: 左方中央（区域化任务）
- 位置8: 左上角（解决方案）

### 2. CSS样式设计

#### 布局系统
```css
.progress-chart {
  position: relative;
  width: 320px;
  height: 320px;
  margin: 0 auto;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.center-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: #fff;
  border: 3px solid #e9ecef;
  z-index: 10;
}

.grid-item {
  position: absolute;
  width: 85px;
  height: 85px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}
```

#### 颜色系统
- **绿色系**: 正面状态（掌握、测试等）
  - 主色: `#4CAF50`
  - 渐变: `linear-gradient(135deg, #4CAF50, #45a049)`
- **红色系**: 负面状态（遗忘）
  - 主色: `#f44336`
  - 渐变: `linear-gradient(135deg, #f44336, #d32f2f)`
- **黄色系**: 中性状态（学习中）
  - 主色: `#FFC107`
  - 渐变: `linear-gradient(135deg, #FFC107, #FF8F00)`

#### 响应式设计
```css
/* 平板设备 */
@media (max-width: 768px) {
  .progress-chart { width: 280px; height: 280px; }
  .center-circle { width: 100px; height: 100px; }
  .grid-item { width: 70px; height: 70px; }
}

/* 手机设备 */
@media (max-width: 480px) {
  .progress-chart { width: 240px; height: 240px; }
  .center-circle { width: 80px; height: 80px; }
  .grid-item { width: 55px; height: 55px; }
}
```

### 3. JavaScript功能设计

#### 核心类结构
```javascript
class ProgressChart {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.options = this.mergeOptions(options);
    this.data = [];
    this.init();
  }
  
  // 初始化方法
  init() {
    this.render();
    this.bindEvents();
  }
  
  // 渲染图表
  render() {
    this.container.innerHTML = this.generateHTML();
    this.applyStyles();
    this.animateIn();
  }
  
  // 更新数据
  updateData(newData) {
    this.data = newData;
    this.render();
  }
  
  // 事件绑定
  bindEvents() {
    // 点击事件、悬停效果等
  }
}
```

#### 数据接口设计
```javascript
const chartData = {
  title: "九宫格进程",
  subtitle: "学习进度分析",
  items: [
    {
      position: 1,
      category: "掌握",
      label: "掌握",
      value: 49,
      color: "linear-gradient(135deg, #4CAF50, #45a049)",
      textColor: "#fff"
    },
    // 其他数据项...
  ]
};
```

## Data Models

### 图表配置模型
```javascript
interface ChartConfig {
  title: string;           // 中心标题
  subtitle?: string;       // 中心副标题
  width?: number;          // 图表宽度
  height?: number;         // 图表高度
  animated?: boolean;      // 是否启用动画
  responsive?: boolean;    // 是否响应式
  theme?: string;          // 主题色彩
}
```

### 数据项模型
```javascript
interface ChartItem {
  position: number;        // 位置编号 1-8
  category: string;        // 类别标识
  label: string;          // 显示标签
  value: number;          // 数值
  color: string;          // 背景颜色/渐变
  textColor?: string;     // 文字颜色
  icon?: string;          // 可选图标
  clickable?: boolean;    // 是否可点击
}
```

### Django模型集成
```python
# 在Django中的数据模型
class ProgressData(models.Model):
    category = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    value = models.IntegerField()
    color = models.CharField(max_length=100)
    position = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def to_chart_data(self):
        return {
            'position': self.position,
            'category': self.category,
            'label': self.label,
            'value': self.value,
            'color': self.color
        }
```

## Error Handling

### 1. 数据验证
- **空数据处理**: 当数据为空时显示默认占位符
- **数据格式验证**: 确保数据符合预期格式
- **数值范围检查**: 验证数值在合理范围内

### 2. 渲染错误处理
```javascript
try {
  this.render();
} catch (error) {
  console.error('图表渲染失败:', error);
  this.showErrorMessage('图表加载失败，请刷新页面重试');
}
```

### 3. 兼容性处理
- **浏览器兼容**: 检测CSS Grid支持，提供降级方案
- **设备适配**: 检测屏幕尺寸，自动调整布局
- **性能优化**: 防抖处理窗口resize事件

## Testing Strategy

### 1. 单元测试
- **数据处理函数测试**: 验证数据转换和验证逻辑
- **渲染函数测试**: 确保HTML生成正确
- **事件处理测试**: 验证用户交互响应

### 2. 集成测试
- **Django视图测试**: 测试数据传递和模板渲染
- **前端集成测试**: 验证组件在页面中的正常工作
- **API接口测试**: 测试数据获取和更新接口

### 3. 视觉测试
- **响应式测试**: 在不同设备尺寸下的显示效果
- **浏览器兼容测试**: 主流浏览器的兼容性验证
- **性能测试**: 大数据量下的渲染性能

### 4. 用户体验测试
- **交互测试**: 点击、悬停等用户操作
- **可访问性测试**: 键盘导航、屏幕阅读器支持
- **加载性能测试**: 首次加载和数据更新速度

## Implementation Approach

### 阶段1: 基础结构搭建
1. 创建HTML模板文件
2. 实现基础CSS样式
3. 搭建JavaScript类框架

### 阶段2: 核心功能实现
1. 数据渲染逻辑
2. 响应式布局
3. 基础交互功能

### 阶段3: 高级特性
1. 动画效果
2. 主题系统
3. 配置选项

### 阶段4: Django集成
1. 创建Django视图
2. 模板集成
3. 数据接口开发

### 阶段5: 测试和优化
1. 功能测试
2. 性能优化
3. 兼容性调试

## File Structure

```
templates/components/
├── progress_chart.html          # 主模板文件
└── progress_chart_demo.html     # 演示页面

static/css/
└── progress_chart.css           # 样式文件

static/js/
└── progress_chart.js            # JavaScript逻辑

apps/reports/
├── views.py                     # Django视图
├── urls.py                      # URL配置
└── models.py                    # 数据模型（如需要）
```

## Integration Points

### 1. Django模板系统
- 使用Django模板标签传递数据
- 集成CSRF保护
- 支持国际化

### 2. 现有样式系统
- 继承Bootstrap 5样式
- 与现有主题保持一致
- 复用现有CSS变量

### 3. JavaScript生态
- 不与Vue.js冲突
- 可选择性集成到现有页面
- 支持模块化加载

这个设计确保了组件的独立性、可维护性和与现有系统的良好集成。