# CSS 架构升级指南

## 概述

本项目已从传统的 CSS 架构升级为现代化的 **SCSS + BEM** 架构，结合设计令牌系统，提供更好的可维护性、可扩展性和开发体验。

## 为什么选择 SCSS + BEM 而不是 CSS Modules？

### SCSS + BEM 的优势

1. **更好的设计系统集成**：通过 SCSS 变量和 mixins，可以轻松实现设计令牌系统
2. **团队协作友好**：BEM 命名规范清晰，易于理解和维护
3. **渐进式迁移**：可以逐步迁移现有代码，不需要大规模重构
4. **工具链成熟**：SCSS 生态系统完善，工具支持良好
5. **运行时主题切换**：支持 CSS 变量，便于实现深色模式等主题功能

### CSS Modules 的局限性

1. **学习成本高**：需要改变现有的开发习惯
2. **工具链复杂**：需要额外的构建配置和类型定义
3. **设计系统集成困难**：难以实现全局设计令牌系统
4. **调试困难**：生成的类名不直观，调试时难以定位

## 新架构结构

```
styles/
├── index.scss          # 主入口文件
├── tokens.scss         # 设计令牌（颜色、间距、字体等）
├── mixins.scss         # SCSS mixins 和工具函数
├── variables.scss      # CSS 变量定义（支持主题切换）
├── base.scss          # 全局重置和基础样式
├── components.scss    # 组件样式库
└── utilities.scss     # 工具类样式
```

## 使用指南

### 1. 设计令牌使用

```scss
// ✅ 推荐：使用设计令牌
.my-component {
  color: $color-primary-600;
  padding: $spacing-4;
  border-radius: $border-radius-md;
  box-shadow: $shadow-lg;
}

// ❌ 避免：硬编码值
.my-component {
  color: #2563eb;
  padding: 16px;
  border-radius: 6px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
```

### 2. BEM 命名规范

```scss
// 块 (Block)
.card {
  @include card();
  
  // 元素 (Element)
  @include bem-element('header') {
    padding-bottom: $spacing-4;
    border-bottom: 1px solid $color-gray-200;
  }
  
  @include bem-element('title') {
    @include heading(3);
    margin: 0;
  }
  
  @include bem-element('content') {
    padding: $spacing-4 0;
  }
  
  // 修饰符 (Modifier)
  @include bem-modifier('highlighted') {
    border: 2px solid $color-primary-500;
  }
  
  @include bem-modifier('compact') {
    padding: $spacing-2;
  }
}
```

对应的 HTML：

```html
<div class="card card--highlighted">
  <div class="card__header">
    <h3 class="card__title">标题</h3>
  </div>
  <div class="card__content">
    内容
  </div>
</div>
```

### 3. Mixins 使用

```scss
// 布局 mixins
.header {
  @include flex-between;
  @include container();
}

// 按钮状态 mixins
.btn-primary {
  @include button-states($color-primary-500);
  @include focus-ring();
}

// 响应式 mixins
.sidebar {
  display: none;
  
  @include respond-to('md') {
    display: block;
    width: 250px;
  }
}

// 文本样式 mixins
.heading {
  @include heading(2);
  @include text-truncate;
}
```

### 4. 工具类使用

```html
<!-- 布局工具类 -->
<div class="flex items-center justify-between p-4">
  <h1 class="text-2xl font-bold text-gray-900">标题</h1>
  <button class="btn btn--primary">按钮</button>
</div>

<!-- 响应式工具类 -->
<div class="hidden md:block lg:flex">
  响应式内容
</div>

<!-- 间距工具类 -->
<div class="mt-4 mb-6 px-4">
  内容
</div>
```

### 5. 主题切换支持

```scss
// 使用 CSS 变量支持主题切换
.theme-toggle {
  background-color: var(--primary-500);
  color: var(--white);
  
  &:hover {
    background-color: var(--primary-600);
  }
}
```

```javascript
// JavaScript 主题切换
function toggleTheme() {
  document.documentElement.classList.toggle('dark-theme');
}
```

## 组件开发最佳实践

### 1. 组件样式结构

```scss
// components/UserCard.vue
<style lang="scss" scoped>
.user-card {
  @include card();
  @include transition();
  
  @include bem-element('avatar') {
    width: 3rem;
    height: 3rem;
    @include rounded('full');
    @include img-responsive;
  }
  
  @include bem-element('info') {
    flex: 1;
    margin-left: $spacing-3;
  }
  
  @include bem-element('name') {
    @include text-style($font-size-lg, $font-weight-semibold);
    color: $color-gray-900;
    margin-bottom: $spacing-1;
  }
  
  @include bem-element('email') {
    @include text-style($font-size-sm);
    color: $color-gray-600;
  }
  
  @include bem-modifier('interactive') {
    @include hover-lift;
    cursor: pointer;
  }
  
  // 响应式设计
  @include respond-to('sm') {
    @include bem-element('avatar') {
      width: 4rem;
      height: 4rem;
    }
  }
}
</style>
```

### 2. 状态管理

```scss
.form-field {
  @include bem-element('input') {
    @include input-base;
    
    // 状态修饰符
    @include bem-modifier('error') {
      border-color: $color-error-500;
      
      &:focus {
        @include focus-ring($color-error-500);
      }
    }
    
    @include bem-modifier('success') {
      border-color: $color-success-500;
    }
    
    @include bem-modifier('disabled') {
      background-color: $color-gray-100;
      cursor: not-allowed;
    }
  }
}
```

### 3. 动画和过渡

```scss
.modal {
  @include transition(opacity, transform);
  
  &.modal--entering {
    opacity: 0;
    transform: scale(0.95);
  }
  
  &.modal--entered {
    opacity: 1;
    transform: scale(1);
  }
}

.loading-spinner {
  @include bem-element('icon') {
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
```

## 迁移指南

### 1. 现有组件迁移

```scss
// 旧代码
.tab-bar {
  background: #ffffff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 16px;
}

.tab-bar .tab-item {
  color: #666;
  padding: 8px 16px;
}

.tab-bar .tab-item.active {
  color: #3b82f6;
  border-bottom: 2px solid #3b82f6;
}

// 新代码
.tab-bar {
  background-color: $color-white;
  @include shadow('base');
  padding: $spacing-4;
  
  @include bem-element('item') {
    color: $color-gray-600;
    padding: $spacing-2 $spacing-4;
    @include transition();
    
    @include bem-modifier('active') {
      color: $color-primary-600;
      border-bottom: 2px solid $color-primary-600;
    }
  }
}
```

### 2. 逐步迁移策略

1. **第一阶段**：更新 Vite 配置，引入新的 SCSS 架构
2. **第二阶段**：将硬编码值替换为设计令牌
3. **第三阶段**：重构组件样式，采用 BEM 命名规范
4. **第四阶段**：添加响应式设计和主题支持
5. **第五阶段**：优化性能，移除冗余样式

## 性能优化

### 1. 样式拆分

```scss
// 按需导入组件样式
@import './components/button';
@import './components/card';
@import './components/modal';
```

### 2. 工具类优化

```scss
// 使用 PurgeCSS 移除未使用的工具类
// vite.config.ts
export default {
  css: {
    postcss: {
      plugins: [
        require('@fullhuman/postcss-purgecss')({
          content: ['./src/**/*.{vue,js,ts}'],
          defaultExtractor: content => content.match(/[\w-/:]+(?<!:)/g) || []
        })
      ]
    }
  }
}
```

## 开发工具

### 1. VS Code 扩展推荐

- **SCSS IntelliSense**：SCSS 语法高亮和自动完成
- **BEM Helper**：BEM 命名规范辅助
- **CSS Peek**：快速查看 CSS 定义

### 2. Stylelint 配置

```json
{
  "extends": [
    "stylelint-config-standard-scss",
    "stylelint-config-prettier"
  ],
  "rules": {
    "selector-class-pattern": "^[a-z]([a-z0-9-]+)?(__([a-z0-9]+-?)+)?(--([a-z0-9]+-?)+){0,2}$",
    "scss/at-import-partial-extension": null,
    "scss/at-import-no-partial-leading-underscore": null
  }
}
```

## 总结

新的 SCSS + BEM 架构为项目提供了：

1. **更好的可维护性**：清晰的命名规范和模块化结构
2. **更强的可扩展性**：设计令牌系统支持快速主题定制
3. **更优的开发体验**：丰富的 mixins 和工具类提高开发效率
4. **更好的性能**：优化的样式结构和按需加载
5. **更强的一致性**：统一的设计系统确保视觉一致性

通过遵循本指南，团队可以高效地开发和维护高质量的用户界面。