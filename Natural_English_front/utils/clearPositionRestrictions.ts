/**
 * 清除位置限制工具
 * 动态清除所有可能影响元素正常显示的样式限制
 */

// 扩展Window接口
declare global {
  interface Window {
    positionCleaner: PositionRestrictionCleaner;
    clearPositionRestrictions: () => void;
  }
}

class PositionRestrictionCleaner {
  private targetXPaths: string[];
  private restrictiveStyles: string[];
  private restrictiveClasses: string[];
  private intervalId: number | null = null;
  private isManualCall: boolean = false;

  constructor() {
    this.targetXPaths = [
      '//*[@id="app"]/div[3]/div[2]'
    ];
    
    this.restrictiveStyles = [
      'position', 'top', 'left', 'right', 'bottom', 
      'z-index', 'transform', 'position'
    ];
    
    this.restrictiveClasses = [
      'pinned', 'sticky', 'fixed-top', 'position-fixed',
      'position-sticky', 'position-absolute', 'top-0'
    ];
  }
  
  /**
   * 清除所有位置限制
   */
  clearAllRestrictions(): void {
    // 移除频繁的控制台输出，只在手动调用时输出
    if (this.isManualCall) {
      console.log('开始清除位置限制...');
    }
    
    // 清除XPath指定的元素
    this.clearXPathElements();
    
    // 清除词汇阅读中心相关元素
    this.clearVocabularyElements();
    
    // 清除所有可能的限制性样式
    this.clearRestrictiveStyles();
    
    // 清除内联样式
    this.clearInlineStyles();
    
    if (this.isManualCall) {
      console.log('位置限制清除完成');
      this.isManualCall = false;
    }
  }
  
  /**
   * 清除XPath指定的元素限制
   */
  private clearXPathElements(): void {
    this.targetXPaths.forEach(xpath => {
      try {
        const element = document.evaluate(
          xpath,
          document,
          null,
          XPathResult.FIRST_ORDERED_NODE_TYPE,
          null
        ).singleNodeValue as HTMLElement;
        
        if (element) {
          this.resetElementStyles(element);
          console.log(`✅ 已清除XPath元素限制: ${xpath}`);
        }
      } catch (error) {
        console.error(`❌ 清除XPath元素失败: ${xpath}`, error);
      }
    });
  }
  
  /**
   * 清除词汇阅读中心相关元素
   */
  private clearVocabularyElements(): void {
    try {
      // 通过文本内容查找
      const allElements = document.querySelectorAll('*');
      
      allElements.forEach(element => {
        if (element.textContent && element.textContent.includes('词汇阅读中心')) {
          this.resetElementStyles(element as HTMLElement);
        }
      });
      
      // 通过属性查找
      const attributeSelectors = [
        '[data-navigation-url*="learning-modes"]',
        '[title*="词汇阅读中心"]',
        '[data-navigation-url*="dev-index"]'
      ];
      
      attributeSelectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
          this.resetElementStyles(element as HTMLElement);
        });
      });
      
      // 移除频繁的控制台输出
    } catch (error) {
      console.error('❌ 清除词汇阅读中心元素失败:', error);
    }
  }
  
  /**
   * 清除限制性样式
   */
  private clearRestrictiveStyles(): void {
    try {
      const selectors = [
        '[style*="position: fixed"]',
        '[style*="position: sticky"]',
        '[style*="position: absolute"]',
        '[style*="top: 0"]',
        '.pinned', '.sticky', '.fixed-top',
        '.position-fixed', '.position-sticky'
      ];
      
      selectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
          // 跳过必要的导航元素
          if (this.isNavigationElement(element as HTMLElement)) {
            return;
          }
          
          this.resetElementStyles(element as HTMLElement);
        });
      });
      
      // 移除频繁的控制台输出
    } catch (error) {
      console.error('❌ 清除限制性样式失败:', error);
    }
  }
  
  /**
   * 清除内联样式
   */
  private clearInlineStyles(): void {
    try {
      const allElements = document.querySelectorAll('*[style]');
      
      allElements.forEach(element => {
        if (this.isNavigationElement(element as HTMLElement)) {
          return;
        }
        
        const style = element.getAttribute('style');
        if (style && this.hasRestrictiveStyles(style)) {
          this.resetElementStyles(element as HTMLElement);
        }
      });
      
      // 移除频繁的控制台输出
    } catch (error) {
      console.error('❌ 清除内联样式失败:', error);
    }
  }
  
  /**
   * 重置元素样式
   * @param element - HTML元素
   */
  private resetElementStyles(element: HTMLElement): void {
    if (!element) return;
    
    // 重置位置样式
    element.style.position = 'static';
    element.style.top = 'auto';
    element.style.left = 'auto';
    element.style.right = 'auto';
    element.style.bottom = 'auto';
    element.style.zIndex = 'auto';
    element.style.transform = 'none';
    
    // 移除限制性类名
    this.restrictiveClasses.forEach(className => {
      element.classList.remove(className);
    });
  }
  
  /**
   * 检查是否为导航元素（需要保留定位）
   * @param element - HTML元素
   * @returns 是否为导航元素
   */
  private isNavigationElement(element: HTMLElement): boolean {
    const navigationClasses = [
      'tab-bar-container', 'bottom-navigation', 'top-nav-bar',
      'popup-menu', 'overlay', 'popup-container'
    ];
    
    return navigationClasses.some(className => 
      element.classList.contains(className) ||
      element.closest(`.${className}`)
    );
  }
  
  /**
   * 检查样式是否包含限制性属性
   * @param style - 样式字符串
   * @returns 是否包含限制性样式
   */
  private hasRestrictiveStyles(style: string): boolean {
    return style.includes('position: fixed') ||
           style.includes('position: sticky') ||
           style.includes('position: absolute') ||
           style.includes('top: 0');
  }
  
  /**
   * 开始监听DOM变化并自动清除限制（已禁用自动执行）
   */
  startAutoClearing(): null {
    // 禁用自动执行，避免无限循环的控制台输出
    // 只在手动调用时执行
    console.log('位置限制清理器已初始化，使用 window.clearPositionRestrictions() 手动执行清理');
    
    // 注释掉自动执行的代码
    /*
    // 立即执行一次
    this.clearAllRestrictions();
    
    // 设置定时清理 - 降低频率
    this.intervalId = setInterval(() => {
      this.clearAllRestrictions();
    }, 5000); // 每5秒清理一次，降低频率
    
    // 监听DOM变化 - 添加防抖
    let debounceTimer: number | null = null;
    const observer = new MutationObserver((mutations) => {
      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }
      
      debounceTimer = setTimeout(() => {
        let shouldClear = false;
        mutations.forEach(mutation => {
          if (mutation.type === 'childList' || 
              mutation.type === 'attributes') {
            shouldClear = true;
          }
        });
        
        if (shouldClear) {
          this.clearAllRestrictions();
        }
      }, 500); // 500ms 防抖
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['style', 'class']
    });
    */
    
    return null;
  }
  
  /**
   * 手动触发清除（用于调试）
   */
  manualClear(): void {
    this.isManualCall = true;
    this.clearAllRestrictions();
  }
  
  /**
   * 停止自动清理
   */
  stopAutoClearing(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
      console.log('已停止自动位置限制清理');
    }
  }
}

// 创建全局实例
const positionCleaner = new PositionRestrictionCleaner();

// 页面加载完成后自动启动
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    positionCleaner.startAutoClearing();
  });
} else {
  positionCleaner.startAutoClearing();
}

// 暴露到全局，方便调试
if (typeof window !== 'undefined') {
  window.positionCleaner = positionCleaner;
  window.clearPositionRestrictions = () => positionCleaner.manualClear();
}

export default positionCleaner;