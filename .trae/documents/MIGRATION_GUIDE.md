# CSS 架构迁移指南

本指南将帮助您将现有组件从传统 CSS 架构迁移到新的 SCSS + BEM 架构。

## 📋 迁移检查清单

### 1. 准备工作
- [x] 新的 SCSS 架构已创建
- [x] 设计令牌 (`tokens.scss`) 已定义
- [x] Mixins 库 (`mixins.scss`) 已创建
- [x] 组件样式库 (`components.scss`) 已创建
- [x] 工具类 (`utilities.scss`) 已创建
- [x] Vite 配置已更新
- [x] 主入口文件已更新

### 2. 组件迁移步骤
- [x] 识别需要迁移的组件
- [x] 更新组件样式语法
- [x] 替换硬编码值为设计令牌
- [x] 应用 BEM 命名规范
- [x] 使用 Mixins 简化代码
- [x] 测试组件功能
- [x] 清理旧的 CSS 文件

### 3. Sass 现代化迁移
- [x] 更新 Vite 配置使用现代 Sass API
- [x] 将 @import 语句迁移为 @use 语法
- [x] 修复变量命名空间问题
- [x] 消除 legacy-js-api 弃用警告
- [x] 验证构建和开发服务器正常运行

## 🔄 迁移步骤详解

### 步骤 1: 分析现有组件

首先，识别项目中需要迁移的组件：

```bash
# 查找所有 Vue 组件
find ./components -name "*.vue" -type f

# 查找使用了 <style> 标签的组件
grep -r "<style" ./components
```

### 步骤 2: 组件样式迁移

#### 2.1 更新 `<style>` 标签

**迁移前：**
```vue
<style scoped>
/* 传统 CSS */
</style>
```

**迁移后：**
```vue
<style lang="scss" scoped>
// 使用新的 SCSS + BEM 架构
</style>
```

#### 2.2 应用 BEM 命名规范

**迁移前：**
```vue
<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title">标题</h3>
    </div>
    <div class="card-body">
      内容
    </div>
  </div>
</template>

<style scoped>
.card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
}

.card-header {
  margin-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 8px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.card-body {
  color: #6b7280;
}
</style>
```

**迁移后：**
```vue
<template>
  <div class="modern-card">
    <div class="modern-card__header">
      <h3 class="modern-card__title">标题</h3>
    </div>
    <div class="modern-card__body">
      内容
    </div>
  </div>
</template>

<style lang="scss" scoped>
.modern-card {
  // 使用设计令牌替换硬编码值
  border: 1px solid $color-gray-200;
  border-radius: $border-radius-lg;
  padding: $spacing-4;
  
  // 使用 BEM 元素选择器
  @include bem-element('header') {
    margin-bottom: $spacing-3;
    border-bottom: 1px solid $color-gray-200;
    padding-bottom: $spacing-2;
  }
  
  @include bem-element('title') {
    @include heading(3);
    margin: 0;
  }
  
  @include bem-element('body') {
    color: $color-gray-600;
  }
}
</style>
```

#### 2.3 使用 Mixins 简化代码

**迁移前：**
```scss
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}
```

**迁移后：**
```scss
.modern-button {
  @include button-base;
  @include transition();
  
  &:hover {
    @include hover-lift;
  }
}
```

### 步骤 3: 替换硬编码值

创建一个查找和替换的映射表：

| 旧值 | 新值 | 说明 |
|------|------|------|
| `#3b82f6` | `$color-primary-500` | 主色调 |
| `#6b7280` | `$color-gray-600` | 文本颜色 |
| `16px` | `$spacing-4` | 间距 |
| `8px` | `$border-radius-lg` | 圆角 |
| `font-weight: 600` | `$font-weight-semibold` | 字体粗细 |

### 步骤 4: 更新响应式设计

**迁移前：**
```scss
@media (min-width: 768px) {
  .component {
    padding: 24px;
  }
}
```

**迁移后：**
```scss
.component {
  @include respond-to('md') {
    padding: $spacing-6;
  }
}
```

## 🛠️ 实用工具

### 自动化迁移脚本

创建一个简单的脚本来帮助迁移：

```bash
#!/bin/bash
# migrate-styles.sh

# 替换常见的硬编码值
sed -i 's/#3b82f6/$color-primary-500/g' $1
sed -i 's/#6b7280/$color-gray-600/g' $1
sed -i 's/16px/$spacing-4/g' $1
sed -i 's/8px/$spacing-2/g' $1

echo "已完成 $1 的基础迁移"
```

### VS Code 代码片段

在 `.vscode/snippets.json` 中添加：

```json
{
  "BEM Element": {
    "prefix": "bem-el",
    "body": [
      "@include bem-element('$1') {",
      "  $2",
      "}"
    ],
    "description": "BEM 元素选择器"
  },
  "BEM Modifier": {
    "prefix": "bem-mod",
    "body": [
      "@include bem-modifier('$1') {",
      "  $2",
      "}"
    ],
    "description": "BEM 修饰符选择器"
  }
}
```

## 📝 迁移示例

### 示例 1: 简单按钮组件

**原始组件 (`OldButton.vue`)：**
```vue
<template>
  <button class="btn" :class="[size, variant]">
    <slot></slot>
  </button>
</template>

<style scoped>
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.primary {
  background: #3b82f6;
  color: white;
}

.small {
  padding: 4px 8px;
  font-size: 14px;
}
</style>
```

**迁移后 (`ModernButton.vue`)：**
```vue
<template>
  <button :class="buttonClasses">
    <slot></slot>
  </button>
</template>

<script setup>
const props = defineProps({
  variant: { type: String, default: 'primary' },
  size: { type: String, default: 'md' }
})

const buttonClasses = computed(() => [
  'modern-button',
  `modern-button--${props.variant}`,
  `modern-button--${props.size}`
])
</script>

<style lang="scss" scoped>
.modern-button {
  @include button-base;
  
  @include bem-modifier('primary') {
    @include button-variant($color-primary-500, $color-white);
  }
  
  @include bem-modifier('small') {
    padding: $spacing-1 $spacing-2;
    @include text-style($font-size-sm);
  }
}
</style>
```

### 示例 2: 复杂卡片组件

查看 `components/examples/ModernCard.vue` 获取完整的迁移示例。

## ⚠️ 注意事项

### 1. 向后兼容性
- 保持旧的 CSS 文件导入，直到所有组件迁移完成
- 逐步迁移，避免一次性修改所有组件
- 在迁移过程中保持功能测试

### 2. 性能考虑
- 新架构可能会增加 CSS 包大小，使用 PurgeCSS 优化
- 监控构建时间变化
- 考虑按需加载组件样式

### 3. 团队协作
- 更新团队的编码规范文档
- 提供培训和示例
- 建立代码审查检查点

## 🧪 测试策略

### 1. 视觉回归测试
```bash
# 使用 Playwright 进行视觉测试
npm run test:visual
```

### 2. 组件测试
```bash
# 测试组件功能
npm run test:unit
```

### 3. 样式一致性检查
```bash
# 使用 Stylelint 检查样式
npm run lint:style
```

## 📚 参考资源

- [BEM 官方文档](http://getbem.com/)
- [SCSS 官方文档](https://sass-lang.com/)
- [CSS 架构指南](./CSS_ARCHITECTURE_GUIDE.md)
- [设计系统文档](./pages/examples/StyleGuide.vue)

## 🎯 迁移完成后的清理

1. **删除未使用的 CSS 文件**
   ```bash
   # 检查哪些 CSS 文件不再被使用
   find ./assets/css -name "*.css" -type f
   ```

2. **更新导入语句**
   ```bash
   # 移除旧的 CSS 导入
   grep -r "import.*\.css" ./
   ```

3. **运行最终测试**
   ```bash
   npm run build
   npm run test
   npm run lint
   ```

---

**迁移完成！** 🎉

您的项目现在使用现代化的 SCSS + BEM 架构，具有更好的可维护性、可扩展性和开发体验。