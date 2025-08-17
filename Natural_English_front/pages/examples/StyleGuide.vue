<template>
  <div class="style-guide">
    <!-- 页面头部 -->
    <header class="style-guide__header">
      <div class="container">
        <h1 class="style-guide__title">设计系统样式指南</h1>
        <p class="style-guide__description">
          展示新的 SCSS + BEM 架构的设计令牌、组件和工具类使用示例
        </p>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="style-guide__content">
      <div class="container">
        
        <!-- 颜色系统 -->
        <section class="style-guide__section">
          <h2 class="style-guide__section-title">颜色系统</h2>
          <div class="color-palette">
            <div class="color-palette__group">
              <h3 class="color-palette__title">主色调</h3>
              <div class="color-palette__swatches">
                <div class="color-swatch color-swatch--primary-50">50</div>
                <div class="color-swatch color-swatch--primary-100">100</div>
                <div class="color-swatch color-swatch--primary-200">200</div>
                <div class="color-swatch color-swatch--primary-300">300</div>
                <div class="color-swatch color-swatch--primary-400">400</div>
                <div class="color-swatch color-swatch--primary-500">500</div>
                <div class="color-swatch color-swatch--primary-600">600</div>
                <div class="color-swatch color-swatch--primary-700">700</div>
                <div class="color-swatch color-swatch--primary-800">800</div>
                <div class="color-swatch color-swatch--primary-900">900</div>
              </div>
            </div>
            
            <div class="color-palette__group">
              <h3 class="color-palette__title">中性色</h3>
              <div class="color-palette__swatches">
                <div class="color-swatch color-swatch--gray-50">50</div>
                <div class="color-swatch color-swatch--gray-100">100</div>
                <div class="color-swatch color-swatch--gray-200">200</div>
                <div class="color-swatch color-swatch--gray-300">300</div>
                <div class="color-swatch color-swatch--gray-400">400</div>
                <div class="color-swatch color-swatch--gray-500">500</div>
                <div class="color-swatch color-swatch--gray-600">600</div>
                <div class="color-swatch color-swatch--gray-700">700</div>
                <div class="color-swatch color-swatch--gray-800">800</div>
                <div class="color-swatch color-swatch--gray-900">900</div>
              </div>
            </div>
          </div>
        </section>

        <!-- 按钮组件 -->
        <section class="style-guide__section">
          <h2 class="style-guide__section-title">按钮组件</h2>
          <div class="component-showcase">
            <div class="component-showcase__group">
              <h3 class="component-showcase__title">按钮变体</h3>
              <div class="component-showcase__items">
                <ModernButton variant="primary">主要按钮</ModernButton>
                <ModernButton variant="secondary">次要按钮</ModernButton>
                <ModernButton variant="outline">轮廓按钮</ModernButton>
                <ModernButton variant="ghost">幽灵按钮</ModernButton>
                <ModernButton variant="danger">危险按钮</ModernButton>
              </div>
            </div>
            
            <div class="component-showcase__group">
              <h3 class="component-showcase__title">按钮尺寸</h3>
              <div class="component-showcase__items">
                <ModernButton size="sm">小按钮</ModernButton>
                <ModernButton size="md">中按钮</ModernButton>
                <ModernButton size="lg">大按钮</ModernButton>
              </div>
            </div>
            
            <div class="component-showcase__group">
              <h3 class="component-showcase__title">按钮状态</h3>
              <div class="component-showcase__items">
                <ModernButton>正常状态</ModernButton>
                <ModernButton loading loadingText="加载中...">加载状态</ModernButton>
                <ModernButton disabled>禁用状态</ModernButton>
              </div>
            </div>
            
            <div class="component-showcase__group">
              <h3 class="component-showcase__title">带图标按钮</h3>
              <div class="component-showcase__items">
                <ModernButton prefix-icon="icon-plus">添加</ModernButton>
                <ModernButton suffix-icon="icon-arrow-right">下一步</ModernButton>
                <ModernButton prefix-icon="icon-download" suffix-icon="icon-external">下载</ModernButton>
              </div>
            </div>
          </div>
        </section>

        <!-- 卡片组件 -->
        <section class="style-guide__section">
          <h2 class="style-guide__section-title">卡片组件</h2>
          <div class="component-showcase">
            <div class="component-showcase__grid">
              <ModernCard 
                title="默认卡片" 
                subtitle="这是一个默认样式的卡片组件"
              >
                <p>卡片内容区域，可以放置任何内容。支持文本、图片、按钮等各种元素。</p>
                <template #footer>
                  <ModernButton size="sm" variant="outline">取消</ModernButton>
                  <ModernButton size="sm">确认</ModernButton>
                </template>
              </ModernCard>
              
              <ModernCard 
                title="高亮卡片" 
                subtitle="重要信息展示"
                variant="highlighted"
                interactive
              >
                <p>这是一个高亮样式的交互式卡片，点击时会有悬停效果。</p>
                <template #footer>
                  <span class="text-sm text-gray-500">点击查看详情</span>
                </template>
              </ModernCard>
              
              <ModernCard 
                title="紧凑卡片" 
                variant="compact"
              >
                <p>紧凑样式的卡片，适合在空间有限的地方使用。</p>
              </ModernCard>
              
              <ModernCard 
                title="加载状态" 
                loading
              >
                <p>这个卡片正在加载中...</p>
              </ModernCard>
            </div>
          </div>
        </section>

        <!-- 工具类展示 -->
        <section class="style-guide__section">
          <h2 class="style-guide__section-title">工具类示例</h2>
          <div class="utility-showcase">
            <div class="utility-showcase__group">
              <h3 class="utility-showcase__title">间距工具类</h3>
              <div class="utility-showcase__demo">
                <div class="p-4 bg-blue-50 border border-blue-200 rounded">
                  <div class="mb-2 text-sm font-medium">padding: 1rem (p-4)</div>
                  <div class="p-2 bg-white border border-gray-200 rounded">
                    <div class="text-xs">padding: 0.5rem (p-2)</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="utility-showcase__group">
              <h3 class="utility-showcase__title">Flexbox 工具类</h3>
              <div class="utility-showcase__demo">
                <div class="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded">
                  <span class="text-sm">flex items-center justify-between</span>
                  <ModernButton size="sm">按钮</ModernButton>
                </div>
              </div>
            </div>
            
            <div class="utility-showcase__group">
              <h3 class="utility-showcase__title">文本工具类</h3>
              <div class="utility-showcase__demo">
                <div class="space-y-2">
                  <p class="text-xs text-gray-500">超小文本 (text-xs)</p>
                  <p class="text-sm text-gray-600">小文本 (text-sm)</p>
                  <p class="text-base text-gray-700">基础文本 (text-base)</p>
                  <p class="text-lg text-gray-800">大文本 (text-lg)</p>
                  <p class="text-xl font-semibold text-gray-900">超大文本 (text-xl font-semibold)</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 响应式展示 -->
        <section class="style-guide__section">
          <h2 class="style-guide__section-title">响应式设计</h2>
          <div class="responsive-demo">
            <div class="responsive-demo__item">
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div class="p-4 bg-purple-50 border border-purple-200 rounded text-center">
                  <div class="text-sm font-medium">移动端: 1列</div>
                  <div class="text-xs text-gray-500">平板: 2列</div>
                  <div class="text-xs text-gray-500">桌面: 3列</div>
                </div>
                <div class="p-4 bg-purple-50 border border-purple-200 rounded text-center hidden md:block">
                  <div class="text-sm font-medium">平板及以上可见</div>
                </div>
                <div class="p-4 bg-purple-50 border border-purple-200 rounded text-center hidden lg:block">
                  <div class="text-sm font-medium">桌面端可见</div>
                </div>
              </div>
            </div>
          </div>
        </section>

      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import ModernButton from '@/components/examples/ModernButton.vue'
import ModernCard from '@/components/examples/ModernCard.vue'

// 页面元数据
defineOptions({
  name: 'StyleGuide'
})
</script>

<style lang="scss" scoped>
@use '../../styles/variables.scss' as *;
@use '../../styles/mixins.scss' as *;

// 使用新的 SCSS + BEM 架构
.style-guide {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--color-gray-50) 0%, var(--color-white) 100%);
  
  // 页面头部
  @include bem-element('header') {
    background: linear-gradient(135deg, var(--color-primary-600) 0%, var(--color-primary-700) 100%);
  color: var(--color-white);
  padding: var(--spacing-12) 0;
    
    @include respond-to('sm') {
      padding: var(--spacing-16) 0;
    }
  }
  
  @include bem-element('title') {
    @include heading(1);
    margin: 0 0 var(--spacing-4) 0;
    
    @include respond-to('sm') {
      @include heading(1, 3.5rem);
    }
  }
  
  @include bem-element('description') {
    @include text-style(var(--font-size-lg), var(--font-weight-normal));
    margin: 0;
    opacity: 0.9;
    max-width: 600px;
  }
  
  // 主要内容
  @include bem-element('content') {
    padding: var(--spacing-12) 0;
  }
  
  // 章节样式
  @include bem-element('section') {
    margin-bottom: var(--spacing-16);
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  @include bem-element('section-title') {
    @include heading(2);
    margin: 0 0 var(--spacing-8) 0;
    color: var(--color-gray-900);
    border-bottom: 2px solid var(--color-primary-200);
    padding-bottom: var(--spacing-4);
  }
}

// 颜色调色板
.color-palette {
  @include bem-element('group') {
    margin-bottom: var(--spacing-8);
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  @include bem-element('title') {
    @include heading(3);
    margin: 0 0 var(--spacing-4) 0;
    color: var(--color-gray-800);
  }
  
  @include bem-element('swatches') {
    @include grid(10, var(--spacing-2));
    
    @include respond-to('sm') {
      @include grid(5, var(--spacing-3));
    }
  }
}

.color-swatch {
  @include flex-center;
  height: 4rem;
  border-radius: var(--border-radius-lg);
  @include text-style(var(--font-size-xs), var(--font-weight-semibold));
  @include shadow('sm');
  @include transition();
  
  &:hover {
    @include shadow('md');
    transform: translateY(-2px);
  }
  
  // 主色调色板
  @include bem-modifier('primary-50') { background-color: var(--color-primary-50); color: var(--color-primary-900); }
  @include bem-modifier('primary-100') { background-color: var(--color-primary-100); color: var(--color-primary-900); }
  @include bem-modifier('primary-200') { background-color: var(--color-primary-200); color: var(--color-primary-900); }
  @include bem-modifier('primary-300') { background-color: var(--color-primary-300); color: var(--color-primary-900); }
  @include bem-modifier('primary-400') { background-color: var(--color-primary-400); color: var(--color-white); }
  @include bem-modifier('primary-500') { background-color: var(--color-primary-500); color: var(--color-white); }
  @include bem-modifier('primary-600') { background-color: var(--color-primary-600); color: var(--color-white); }
  @include bem-modifier('primary-700') { background-color: var(--color-primary-700); color: var(--color-white); }
  @include bem-modifier('primary-800') { background-color: var(--color-primary-800); color: var(--color-white); }
  @include bem-modifier('primary-900') { background-color: var(--color-primary-900); color: var(--color-white); }
  
  // 中性色调色板
  @include bem-modifier('gray-50') { background-color: var(--color-gray-50); color: var(--color-gray-900); }
  &--gray-100 { background-color: var(--color-gray-100); color: var(--color-gray-900); }
  &--gray-200 { background-color: var(--color-gray-200); color: var(--color-gray-900); }
  &--gray-300 { background-color: var(--color-gray-300); color: var(--color-gray-900); }
  &--gray-400 { background-color: var(--color-gray-400); color: var(--color-white); }
  &--gray-500 { background-color: var(--color-gray-500); color: var(--color-white); }
  &--gray-600 { background-color: var(--color-gray-600); color: var(--color-white); }
  &--gray-700 { background-color: var(--color-gray-700); color: var(--color-white); }
  &--gray-800 { background-color: var(--color-gray-800); color: var(--color-white); }
  &--gray-900 { background-color: var(--color-gray-900); color: var(--color-white); }
}

// 组件展示
.component-showcase {
  .component-showcase__group {
    margin-bottom: var(--spacing-8);
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  .component-showcase__title {
    @include heading(4);
    margin: 0 0 var(--spacing-4) 0;
    color: var(--color-gray-700);
  }
  
  .component-showcase__items {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-3);
  }
  
  .component-showcase__grid {
    display: grid;
    grid-template-columns: repeat(1, 1fr);
    gap: var(--spacing-6);
    
    @media (min-width: 768px) {
      grid-template-columns: repeat(2, 1fr);
    }
  }
}

// 工具类展示
.utility-showcase {
  .utility-showcase__group {
    margin-bottom: var(--spacing-6);
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  @include bem-element('title') {
    @include heading(4);
    margin: 0 0 var(--spacing-3) 0;
    color: var(--color-gray-700);
  }
  
  .style-guide__demo {
    padding: var(--spacing-4);
  background-color: var(--color-gray-50);
  border: 1px solid var(--color-gray-200);
    border-radius: var(--border-radius-lg);
  }
}

// 响应式演示
.responsive-demo {
  .responsive-demo__item {
    padding: var(--spacing-6);
  background-color: var(--color-white);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--border-radius-xl);
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  }
}

// 容器样式
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-4);
  
  @media (min-width: 640px) {
    padding: 0 var(--spacing-6);
  }
  
  @media (min-width: 1024px) {
    padding: 0 var(--spacing-8);
  }
}
</style>