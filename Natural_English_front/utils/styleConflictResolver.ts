/**
 * 样式冲突解决器
 * 专门处理项目中的样式冲突和位置问题
 */

// 类型定义
interface ConflictElement {
  xpath: string;
  position: string;
  zIndex: string;
  transform: string;
}

interface HighZIndexElement {
  tagName: string;
  className: string;
  zIndex: number;
}

interface ConflictReport {
  conflictingElements: ConflictElement[];
  highZIndexElements: HighZIndexElement[];
  fixedPositionElements: any[];
  timestamp: string;
}

class StyleConflictResolver {
  private conflictingXPaths: string[];
  private problematicStyles: string[];
  private safeNavigationSelectors: string[];

  constructor() {
    this.conflictingXPaths = [
      '//*[@id="app"]/div[2]/div/div[3]',
      '//*[@id="app"]/div[2]/div/div[2]/div[1]',
      '//*[@id="app"]/div[3]/div[2]/div[1]',
      '//*[@id="app"]/div[3]/div[2]/div[1]/div[5]',
      '//*[@id="app"]/div[3]/div/div[1]/div[1]'
    ];
    
    this.problematicStyles = [
      'position: fixed',
      'position: absolute', 
      'position: sticky',
      'z-index: 9999',
      'z-index: 1000',
      'transform: translate'
    ];
    
    this.safeNavigationSelectors = [
      '.top-nav',
      '.bottom-nav',
      '.nav-bar',
      '.modal',
      '.dropdown',
      '.tooltip',
      '.popup',
      '.menu-overlay'
    ];
  }

  /**
   * 解决所有样式冲突
   */
  resolveAllConflicts(): void {
    try {
      console.log('🔧 开始解决样式冲突...');
      
      // 1. 重置问题XPath元素
      this.resetConflictingElements();
      
      // 2. 修复高z-index元素
      this.fixHighZIndexElements();
      
      // 3. 重置固定定位元素
      this.resetFixedPositionElements();
      
      // 4. 清理内联样式冲突
      this.cleanInlineStyleConflicts();
      
      console.log('✅ 样式冲突解决完成');
    } catch (error) {
      console.error('❌ 样式冲突解决失败:', error);
    }
  }

  /**
   * 重置冲突的XPath元素
   */
  private resetConflictingElements(): void {
    this.conflictingXPaths.forEach(xpath => {
      try {
        const element = document.evaluate(
          xpath,
          document,
          null,
          XPathResult.FIRST_ORDERED_NODE_TYPE,
          null
        ).singleNodeValue as Element;
        
        if (element) {
          this.resetElementStyle(element as HTMLElement);
          console.log(`🔄 已重置元素: ${xpath}`);
        }
      } catch (error) {
        console.warn(`⚠️ 重置XPath元素失败: ${xpath}`, error);
      }
    });
  }

  /**
   * 修复高z-index元素
   */
  private fixHighZIndexElements(): void {
    const highZIndexSelectors = [
      '[style*="z-index: 9999"]',
      '[style*="z-index: 1000"]',
      '[style*="z-index: 2000"]'
    ];
    
    highZIndexSelectors.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(element => {
        if (!this.isNavigationElement(element as HTMLElement)) {
          (element as HTMLElement).style.zIndex = 'auto';
          console.log('🔧 已修复高z-index元素');
        }
      });
    });
  }

  /**
   * 重置固定定位元素
   */
  private resetFixedPositionElements(): void {
    const fixedElements = document.querySelectorAll('[style*="position: fixed"], [style*="position: absolute"]');
    
    fixedElements.forEach(element => {
      if (!this.isNavigationElement(element as HTMLElement)) {
        this.resetElementStyle(element as HTMLElement);
        console.log('🔄 已重置固定定位元素');
      }
    });
  }

  /**
   * 清理内联样式冲突
   */
  private cleanInlineStyleConflicts(): void {
    const allElements = document.querySelectorAll('*[style]');
    
    allElements.forEach(element => {
      if (this.isNavigationElement(element as HTMLElement)) return;
      
      const style = element.getAttribute('style');
      if (style && this.hasConflictingStyles(style)) {
        this.resetElementStyle(element as HTMLElement);
        console.log('🧹 已清理内联样式冲突');
      }
    });
  }

  /**
   * 重置单个元素样式
   */
  private resetElementStyle(element: HTMLElement): void {
    if (!element) return;
    
    // 重置位置相关样式
    element.style.position = 'static';
    element.style.top = 'auto';
    element.style.left = 'auto';
    element.style.right = 'auto';
    element.style.bottom = 'auto';
    element.style.zIndex = 'auto';
    element.style.transform = 'none';
    
    // 移除问题类名
    const problematicClasses = [
      'pinned', 'sticky', 'fixed-top', 'position-fixed',
      'position-sticky', 'position-absolute', 'top-0'
    ];
    
    problematicClasses.forEach(className => {
      element.classList.remove(className);
    });
  }

  /**
   * 检查是否为导航元素
   */
  private isNavigationElement(element: HTMLElement): boolean {
    return this.safeNavigationSelectors.some(selector => {
      return element.matches(selector) || element.closest(selector);
    });
  }

  /**
   * 检查是否有冲突样式
   */
  private hasConflictingStyles(style: string): boolean {
    return this.problematicStyles.some(problematicStyle => 
      style.includes(problematicStyle)
    );
  }

  /**
   * 监听DOM变化并自动修复
   */
  startAutoFix(): MutationObserver {
    const observer = new MutationObserver((mutations) => {
      let needsFix = false;
      
      mutations.forEach(mutation => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
          const element = mutation.target as HTMLElement;
          if (!this.isNavigationElement(element)) {
            const style = element.getAttribute('style');
            if (style && this.hasConflictingStyles(style)) {
              needsFix = true;
            }
          }
        }
      });
      
      if (needsFix) {
        setTimeout(() => this.resolveAllConflicts(), 100);
      }
    });
    
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['style'],
      subtree: true
    });
    
    console.log('🤖 自动样式修复已启动');
    return observer;
  }

  /**
   * 生成样式冲突报告
   */
  generateConflictReport(): ConflictReport {
    const report: ConflictReport = {
      conflictingElements: [],
      highZIndexElements: [],
      fixedPositionElements: [],
      timestamp: new Date().toISOString()
    };
    
    // 检查冲突元素
    this.conflictingXPaths.forEach(xpath => {
      const element = document.evaluate(
        xpath,
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
      ).singleNodeValue as HTMLElement;
      
      if (element) {
        const computedStyle = window.getComputedStyle(element);
        report.conflictingElements.push({
          xpath,
          position: computedStyle.position,
          zIndex: computedStyle.zIndex,
          transform: computedStyle.transform
        });
      }
    });
    
    // 检查高z-index元素
    const highZElements = document.querySelectorAll('[style*="z-index"]');
    highZElements.forEach(element => {
      const htmlElement = element as HTMLElement;
      const zIndex = parseInt(htmlElement.style.zIndex);
      if (zIndex > 100 && !this.isNavigationElement(htmlElement)) {
        report.highZIndexElements.push({
          tagName: htmlElement.tagName,
          className: htmlElement.className,
          zIndex: zIndex
        });
      }
    });
    
    console.log('📊 样式冲突报告:', report);
    return report;
  }
}

// 创建全局实例
const styleConflictResolver = new StyleConflictResolver();

// 导出到全局作用域
if (typeof window !== 'undefined') {
  (window as any).styleConflictResolver = styleConflictResolver;
  (window as any).resolveStyleConflicts = () => styleConflictResolver.resolveAllConflicts();
}

export default styleConflictResolver;

// 导出类型
export type {
  ConflictElement,
  HighZIndexElement,
  ConflictReport
};

export { StyleConflictResolver };