# CSS 架构开发规范

本文档定义了项目中 SCSS + BEM 架构的开发规范和最佳实践。

## 📋 目录

1. [BEM 命名规范](#bem-命名规范)
2. [SCSS 使用指南](#scss-使用指南)
3. [设计令牌使用](#设计令牌使用)
4. [Mixins 使用规范](#mixins-使用规范)
5. [组件开发规范](#组件开发规范)
6. [响应式设计规范](#响应式设计规范)
7. [性能优化指南](#性能优化指南)
8. [代码审查检查点](#代码审查检查点)

## 🎯 BEM 命名规范

### 基本语法

```scss
// Block（块）
.component-name { }

// Element（元素）
.component-name__element { }

// Modifier（修饰符）
.component-name--modifier { }
.component-name__element--modifier { }
```

### 命名约定

#### 1. Block 命名
- 使用 kebab-case（短横线分隔）
- 描述组件的功能，而非外观
- 避免使用缩写

```scss
// ✅ 正确
.modern-button { }
.user-profile { }
.navigation-menu { }

// ❌ 错误
.btn { }           // 缩写
.red-button { }    // 描述外观
.userProfile { }   // camelCase
```

#### 2. Element 命名
- 使用双下划线 `__` 分隔
- 描述元素在组件中的作用
- 只能是 Block 的直接子元素

```scss
// ✅ 正确
.modern-button__icon { }
.modern-button__text { }
.user-profile__avatar { }
.user-profile__name { }

// ❌ 错误
.modern-button__icon__svg { }  // 嵌套过深
.modern-button__redIcon { }    // camelCase
```

#### 3. Modifier 命名
- 使用双短横线 `--` 分隔
- 描述状态或变体
- 可以应用于 Block 或 Element

```scss
// ✅ 正确
.modern-button--primary { }
.modern-button--disabled { }
.modern-button__icon--large { }

// ❌ 错误
.modern-button-primary { }     // 单短横线
.modern-button--bluePrimary { } // camelCase
```

### BEM Mixins 使用

```scss
.modern-card {
  // 基础样式
  @include card($spacing-6);
  
  // Element
  @include bem-element('header') {
    padding-bottom: $spacing-4;
    border-bottom: 1px solid $color-gray-200;
  }
  
  @include bem-element('title') {
    @include heading(3);
    margin: 0;
  }
  
  @include bem-element('body') {
    color: $color-gray-600;
  }
  
  // Modifier
  @include bem-modifier('highlighted') {
    border-color: $color-primary-500;
    box-shadow: 0 0 0 1px $color-primary-100;
  }
  
  @include bem-modifier('compact') {
    padding: $spacing-4;
    
    @include bem-element('header') {
      padding-bottom: $spacing-2;
    }
  }
}
```

## 🎨 SCSS 使用指南

### 文件组织

```
styles/
├── index.scss          # 主入口文件
├── tokens.scss         # 设计令牌
├── variables.scss      # SCSS 变量
├── mixins.scss         # Mixins 库
├── base.scss          # 基础样式
├── components.scss    # 组件样式
└── utilities.scss     # 工具类
```

### 导入顺序

```scss
// 1. 设计令牌和变量
@import 'tokens';
@import 'variables';

// 2. Mixins 和函数
@import 'mixins';

// 3. 基础样式
@import 'base';

// 4. 组件样式
@import 'components';

// 5. 工具类
@import 'utilities';
```

### 嵌套规则

```scss
// ✅ 正确：最多 3 层嵌套
.modern-card {
  padding: $spacing-4;
  
  @include bem-element('header') {
    margin-bottom: $spacing-3;
    
    @include bem-element('title') {
      font-weight: $font-weight-semibold;
    }
  }
}

// ❌ 错误：嵌套过深
.modern-card {
  .header {
    .title {
      .text {
        .span {
          color: red; // 5 层嵌套
        }
      }
    }
  }
}
```

### 变量命名

```scss
// ✅ 正确：语义化命名
$color-primary-500: #3b82f6;
$spacing-4: 16px;
$font-size-lg: 18px;
$border-radius-md: 6px;

// ❌ 错误：非语义化命名
$blue: #3b82f6;
$size-16: 16px;
$large: 18px;
```

## 🎯 设计令牌使用

### 颜色系统

```scss
// 主色调
$color-primary-50: #eff6ff;
$color-primary-100: #dbeafe;
$color-primary-500: #3b82f6;
$color-primary-900: #1e3a8a;

// 语义化颜色
$color-success: $color-green-500;
$color-warning: $color-yellow-500;
$color-error: $color-red-500;
$color-info: $color-blue-500;

// 使用示例
.alert {
  &--success {
    background-color: $color-success;
    border-color: $color-green-600;
  }
  
  &--error {
    background-color: $color-error;
    border-color: $color-red-600;
  }
}
```

### 间距系统

```scss
// 间距令牌
$spacing-1: 4px;
$spacing-2: 8px;
$spacing-3: 12px;
$spacing-4: 16px;
$spacing-6: 24px;
$spacing-8: 32px;

// 使用示例
.modern-button {
  padding: $spacing-2 $spacing-4;
  margin-bottom: $spacing-3;
  
  &--large {
    padding: $spacing-3 $spacing-6;
  }
}
```

### 字体系统

```scss
// 字体大小
$font-size-xs: 12px;
$font-size-sm: 14px;
$font-size-base: 16px;
$font-size-lg: 18px;
$font-size-xl: 20px;

// 字体粗细
$font-weight-light: 300;
$font-weight-normal: 400;
$font-weight-medium: 500;
$font-weight-semibold: 600;
$font-weight-bold: 700;

// 使用示例
.heading {
  &--h1 {
    font-size: $font-size-2xl;
    font-weight: $font-weight-bold;
  }
  
  &--h3 {
    font-size: $font-size-lg;
    font-weight: $font-weight-semibold;
  }
}
```

## 🔧 Mixins 使用规范

### 常用 Mixins

#### 1. 按钮 Mixin

```scss
@mixin button-base {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: $border-radius-md;
  font-weight: $font-weight-medium;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:focus {
    outline: 2px solid $color-primary-500;
    outline-offset: 2px;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

@mixin button-variant($bg-color, $text-color, $hover-bg: null) {
  background-color: $bg-color;
  color: $text-color;
  
  @if $hover-bg {
    &:hover:not(:disabled) {
      background-color: $hover-bg;
    }
  } @else {
    &:hover:not(:disabled) {
      background-color: darken($bg-color, 10%);
    }
  }
}

// 使用示例
.modern-button {
  @include button-base;
  
  &--primary {
    @include button-variant($color-primary-500, $color-white);
  }
  
  &--secondary {
    @include button-variant($color-gray-200, $color-gray-900);
  }
}
```

#### 2. 卡片 Mixin

```scss
@mixin card($padding: $spacing-6) {
  background-color: $color-white;
  border: 1px solid $color-gray-200;
  border-radius: $border-radius-lg;
  padding: $padding;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

// 使用示例
.modern-card {
  @include card($spacing-6);
  
  &--compact {
    @include card($spacing-4);
  }
}
```

#### 3. 响应式 Mixin

```scss
@mixin respond-to($breakpoint) {
  @if $breakpoint == 'sm' {
    @media (min-width: 640px) { @content; }
  }
  @if $breakpoint == 'md' {
    @media (min-width: 768px) { @content; }
  }
  @if $breakpoint == 'lg' {
    @media (min-width: 1024px) { @content; }
  }
  @if $breakpoint == 'xl' {
    @media (min-width: 1280px) { @content; }
  }
}

// 使用示例
.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: $spacing-4;
  
  @include respond-to('md') {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @include respond-to('lg') {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

## 🧩 组件开发规范

### Vue 组件样式结构

```vue
<template>
  <div :class="componentClasses">
    <div class="modern-component__header">
      <h3 class="modern-component__title">{{ title }}</h3>
    </div>
    <div class="modern-component__body">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  variant: { type: String, default: 'default' },
  size: { type: String, default: 'md' }
})

const componentClasses = computed(() => [
  'modern-component',
  `modern-component--${props.variant}`,
  `modern-component--${props.size}`
])
</script>

<style lang="scss" scoped>
.modern-component {
  @include card($spacing-6);
  
  @include bem-element('header') {
    margin-bottom: $spacing-4;
    padding-bottom: $spacing-3;
    border-bottom: 1px solid $color-gray-200;
  }
  
  @include bem-element('title') {
    @include heading(3);
    margin: 0;
  }
  
  @include bem-element('body') {
    color: $color-gray-700;
  }
  
  @include bem-modifier('compact') {
    padding: $spacing-4;
    
    @include bem-element('header') {
      margin-bottom: $spacing-2;
      padding-bottom: $spacing-2;
    }
  }
  
  @include bem-modifier('large') {
    padding: $spacing-8;
    
    @include bem-element('title') {
      @include heading(2);
    }
  }
}
</style>
```

### 组件变体管理

```scss
// ✅ 正确：使用修饰符管理变体
.modern-button {
  @include button-base;
  
  // 颜色变体
  @include bem-modifier('primary') {
    @include button-variant($color-primary-500, $color-white);
  }
  
  @include bem-modifier('secondary') {
    @include button-variant($color-gray-200, $color-gray-900);
  }
  
  @include bem-modifier('danger') {
    @include button-variant($color-red-500, $color-white);
  }
  
  // 尺寸变体
  @include bem-modifier('small') {
    padding: $spacing-1 $spacing-3;
    font-size: $font-size-sm;
  }
  
  @include bem-modifier('large') {
    padding: $spacing-3 $spacing-6;
    font-size: $font-size-lg;
  }
  
  // 状态变体
  @include bem-modifier('loading') {
    position: relative;
    color: transparent;
    
    &::after {
      content: '';
      position: absolute;
      width: 16px;
      height: 16px;
      border: 2px solid currentColor;
      border-radius: 50%;
      border-top-color: transparent;
      animation: spin 1s linear infinite;
    }
  }
}
```

## 📱 响应式设计规范

### 断点系统

```scss
// 断点定义
$breakpoints: (
  'sm': 640px,
  'md': 768px,
  'lg': 1024px,
  'xl': 1280px,
  '2xl': 1536px
);

// 移动优先设计
.grid {
  // 移动端：单列
  display: grid;
  grid-template-columns: 1fr;
  gap: $spacing-4;
  
  // 平板：双列
  @include respond-to('md') {
    grid-template-columns: repeat(2, 1fr);
    gap: $spacing-6;
  }
  
  // 桌面：三列
  @include respond-to('lg') {
    grid-template-columns: repeat(3, 1fr);
    gap: $spacing-8;
  }
}
```

### 响应式组件

```scss
.modern-card {
  @include card($spacing-4);
  
  // 平板及以上：增加内边距
  @include respond-to('md') {
    padding: $spacing-6;
  }
  
  @include bem-element('header') {
    margin-bottom: $spacing-3;
    
    @include respond-to('md') {
      margin-bottom: $spacing-4;
    }
  }
  
  @include bem-element('title') {
    font-size: $font-size-lg;
    
    @include respond-to('md') {
      font-size: $font-size-xl;
    }
  }
}
```

## ⚡ 性能优化指南

### 1. 避免深层嵌套

```scss
// ❌ 错误：深层嵌套影响性能
.component {
  .header {
    .title {
      .text {
        .span {
          color: $color-primary-500;
        }
      }
    }
  }
}

// ✅ 正确：使用 BEM 扁平化结构
.component {
  @include bem-element('header') { }
  @include bem-element('title') { }
  @include bem-element('text') { }
  @include bem-element('span') {
    color: $color-primary-500;
  }
}
```

### 2. 合理使用 @extend

```scss
// ✅ 正确：使用 mixin 而非 @extend
@mixin button-base {
  display: inline-flex;
  align-items: center;
  padding: $spacing-2 $spacing-4;
}

.modern-button {
  @include button-base;
}

.icon-button {
  @include button-base;
  padding: $spacing-2;
}
```

### 3. 优化选择器

```scss
// ❌ 错误：复杂选择器
.sidebar .menu .item.active .link:hover {
  color: $color-primary-500;
}

// ✅ 正确：简化选择器
.menu-item {
  @include bem-modifier('active') {
    @include bem-element('link') {
      &:hover {
        color: $color-primary-500;
      }
    }
  }
}
```

## 🔍 代码审查检查点

### 命名规范检查

- [ ] 是否使用了正确的 BEM 命名规范？
- [ ] 类名是否语义化，避免描述外观？
- [ ] 是否避免了缩写和非标准命名？

### 结构检查

- [ ] 嵌套层级是否超过 3 层？
- [ ] 是否正确使用了 BEM mixins？
- [ ] 是否避免了不必要的选择器复杂度？

### 设计令牌检查

- [ ] 是否使用设计令牌而非硬编码值？
- [ ] 颜色、间距、字体是否来自令牌系统？
- [ ] 是否正确使用了语义化令牌？

### 响应式检查

- [ ] 是否采用移动优先的设计方法？
- [ ] 是否正确使用了响应式 mixins？
- [ ] 断点使用是否合理？

### 性能检查

- [ ] 是否避免了深层嵌套？
- [ ] 选择器是否足够简洁？
- [ ] 是否合理使用了 mixins 而非 @extend？

### 可维护性检查

- [ ] 代码是否易于理解和修改？
- [ ] 是否遵循了项目的编码规范？
- [ ] 是否添加了必要的注释？

---

## 📚 相关文档

- [CSS 架构指南](./CSS_ARCHITECTURE_GUIDE.md)
- [迁移指南](./MIGRATION_GUIDE.md)
- [设计系统展示](./pages/examples/StyleGuide.vue)
- [BEM 官方文档](http://getbem.com/)
- [SCSS 官方文档](https://sass-lang.com/)

---

**遵循这些规范，确保代码的一致性、可维护性和性能！** 🚀