# 九宫格进度报告模板使用指南

## 概述

本项目提供了一个通用的九宫格进度报告UI模板，支持数据导入、可视化展示和报告导出功能。该模板同时支持Django+Bootstrap5（后台）和Vue3（前台）两种技术栈。

## 功能特性

### 🎯 核心功能
- **数据导入**: 支持CSV、Excel、JSON格式文件上传
- **可视化展示**: 九宫格布局展示进度数据
- **统计分析**: 自动计算完成率、进行中项目等统计信息
- **报告导出**: 支持PDF、Excel、图片格式导出
- **响应式设计**: 适配桌面端和移动端

### 🎨 UI特性
- **现代化设计**: 使用渐变色和阴影效果
- **交互动画**: 悬停效果和加载动画
- **用户友好**: 拖拽上传和进度提示
- **可定制**: 支持自定义颜色和标签

## 技术架构

### Django后台版本
```
templates/
├── components/
│   └── progress_grid.html          # 九宫格组件
├── reports/
│   └── progress_report.html        # 完整报告页面
apps/
└── reports/
    ├── views.py                     # 视图逻辑
    ├── urls.py                      # URL配置
    └── __init__.py
```

### Vue3前台版本
```
static/vue/
├── components/
│   ├── ProgressGrid.vue            # 九宫格组件
│   └── ProgressReport.vue          # 完整报告页面
└── examples/
    └── report-usage.js             # 使用示例
```

## 快速开始

### Django版本使用

1. **添加应用到设置**
```python
# settings.py
INSTALLED_APPS = [
    # ... 其他应用
    'apps.reports',
]
```

2. **配置URL路由**
```python
# urls.py
urlpatterns = [
    # ... 其他路由
    path('reports/', include('apps.reports.urls')),
]
```

3. **在模板中使用**
```html
<!-- 使用九宫格组件 -->
{% include 'components/progress_grid.html' with grid_title="学习进度" grid_items=progress_data %}

<!-- 或访问完整报告页面 -->
<!-- /reports/ -->
```

### Vue3版本使用

1. **导入组件**
```javascript
import ProgressGrid from '@/components/ProgressGrid.vue'
import ProgressReport from '@/components/ProgressReport.vue'
```

2. **使用九宫格组件**
```vue
<template>
  <ProgressGrid 
    :grid-items="progressData"
    grid-title="学习进度"
    @item-click="handleClick"
  />
</template>

<script setup>
const progressData = [
  { label: '掌握', value: 49, color: '#4CAF50', category: '掌握' },
  { label: '学习中', value: 15, color: '#FFC107', category: '学习中' },
  // ... 更多数据
]

const handleClick = (detail) => {
  console.log('点击了:', detail)
}
</script>
```

3. **使用完整报告组件**
```vue
<template>
  <ProgressReport />
</template>
```

## 数据格式

### 输入数据格式

支持以下格式的数据文件：

**CSV格式示例：**
```csv
category,value,label
掌握,49,已掌握单词
学习中,15,正在学习
遗忘,0,已遗忘
```

**JSON格式示例：**
```json
[
  {
    "category": "掌握",
    "value": 49,
    "label": "已掌握单词"
  },
  {
    "category": "学习中",
    "value": 15,
    "label": "正在学习"
  }
]
```

### 九宫格数据结构

```javascript
const gridItems = [
  {
    label: '掌握',           // 显示标签
    value: 49,              // 数值
    color: '#4CAF50',       // 颜色（支持渐变）
    category: '掌握'        // 类别（用于点击事件）
  },
  // ... 最多8个项目
]
```

## API接口

### Django API端点

```python
# 报告仪表板
GET /reports/

# 数据上传
POST /reports/api/upload/
Content-Type: multipart/form-data
Body: files[]

# 生成报告
POST /reports/api/generate/
Content-Type: application/json
Body: { "data": [...] }

# 导出报告
POST /reports/api/export/
Content-Type: application/json
Body: { "format": "pdf", "report_data": [...] }
```

### 响应格式

```json
{
  "success": true,
  "data": {
    "report_data": [...],
    "stats": {
      "total_records": 64,
      "completed_items": 49,
      "pending_items": 15,
      "completion_rate": 76.6
    }
  },
  "message": "操作成功"
}
```

## 自定义配置

### 颜色主题

```css
/* 自定义颜色变量 */
:root {
  --primary-color: #667eea;
  --success-color: #4CAF50;
  --warning-color: #FFC107;
  --danger-color: #f44336;
}
```

### 九宫格布局

可以通过修改CSS类来调整九宫格的位置和样式：

```css
.grid-item-1 { /* 第一个位置 */ }
.grid-item-2 { /* 第二个位置 */ }
/* ... 最多8个位置 */
```

### 动画效果

```css
/* 自定义动画 */
@keyframes customFadeIn {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}

.grid-item {
  animation: customFadeIn 0.6s ease;
}
```

## 最佳实践

### 1. 数据准备
- 确保数据格式正确，包含必需字段
- 数值应为数字类型
- 类别名称保持一致

### 2. 性能优化
- 大文件上传时显示进度条
- 使用防抖处理用户交互
- 适当使用缓存减少API调用

### 3. 用户体验
- 提供清晰的错误提示
- 支持拖拽上传
- 响应式设计适配移动端

### 4. 安全考虑
- 验证上传文件类型和大小
- 使用CSRF保护
- 对用户输入进行验证

## 故障排除

### 常见问题

**Q: 文件上传失败**
A: 检查文件格式是否支持，文件大小是否超限

**Q: 九宫格显示异常**
A: 确认数据格式正确，检查CSS样式是否冲突

**Q: API调用失败**
A: 检查CSRF token，确认用户权限

**Q: 导出功能不工作**
A: 确认服务器端导出库已安装（如pandas、reportlab）

### 调试模式

```javascript
// 开启调试模式
const DEBUG = true

if (DEBUG) {
  console.log('报告数据:', reportData)
  console.log('统计信息:', stats)
}
```

## 扩展开发

### 添加新的图表类型

1. 创建新的Vue组件
2. 实现数据处理逻辑
3. 添加到报告页面

### 支持新的文件格式

1. 在Django视图中添加处理逻辑
2. 更新前端文件验证
3. 测试新格式的解析

### 自定义导出格式

1. 实现新的导出处理器
2. 添加到API端点
3. 更新前端导出选项

## 版本历史

- **v1.0.0**: 初始版本，支持基本的九宫格展示
- **v1.1.0**: 添加数据导入功能
- **v1.2.0**: 支持Vue3前台版本
- **v1.3.0**: 添加导出功能和统计分析

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献指南

欢迎提交Issue和Pull Request来改进这个模板。请确保：

1. 代码符合项目规范
2. 添加适当的测试
3. 更新相关文档
4. 遵循语义化版本控制

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues: [GitHub Issues]
- 邮箱: [项目邮箱]
- 文档: [在线文档地址]