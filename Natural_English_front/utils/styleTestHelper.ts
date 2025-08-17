/**
 * 样式测试辅助工具
 * 用于验证样式修复是否有效
 */

// 类型定义
interface StyleTestResult {
  xpath: string;
  found: boolean;
  message?: string;
  error?: string;
  element?: string;
  position?: string;
  zIndex?: string;
  transform?: string;
  display?: string;
  visibility?: string;
  hasProblems?: boolean;
  problems?: string[];
}

interface StyleProblem {
  type: string;
  description: string;
}

class StyleTestHelper {
  private testResults: StyleTestResult[] = [];

  constructor() {
    this.testResults = [];
  }

  /**
   * 测试特定XPath元素的样式
   * @param xpath - XPath表达式
   * @returns 测试结果
   */
  testElementStyle(xpath: string): StyleTestResult {
    try {
      const element = document.evaluate(
        xpath,
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
      ).singleNodeValue as Element | null;

      if (!element) {
        return {
          xpath,
          found: false,
          message: '元素未找到'
        };
      }

      const computedStyle = window.getComputedStyle(element);
      const hasProblematicStyles = this.checkProblematicStyles(computedStyle);
      
      return {
        xpath,
        found: true,
        element: element.tagName,
        position: computedStyle.position,
        zIndex: computedStyle.zIndex,
        transform: computedStyle.transform,
        display: computedStyle.display,
        visibility: computedStyle.visibility,
        hasProblems: hasProblematicStyles.length > 0,
        problems: hasProblematicStyles
      };
    } catch (error: any) {
      return {
        xpath,
        found: false,
        error: error.message
      };
    }
  }

  /**
   * 检查是否有问题样式
   * @param style - 计算样式
   * @returns 问题列表
   */
  private checkProblematicStyles(style: CSSStyleDeclaration): string[] {
    const problems: string[] = [];
    
    // 检查位置相关问题
    if (style.position === 'fixed' || style.position === 'absolute') {
      problems.push(`问题定位: ${style.position}`);
    }
    
    // 检查z-index问题
    if (style.zIndex && parseInt(style.zIndex) > 1000) {
      problems.push(`高z-index: ${style.zIndex}`);
    }
    
    // 检查transform问题
    if (style.transform && style.transform !== 'none') {
      problems.push(`transform变换: ${style.transform}`);
    }
    
    // 检查显示问题
    if (style.display === 'none') {
      problems.push('元素隐藏: display: none');
    }
    
    if (style.visibility === 'hidden') {
      problems.push('元素隐藏: visibility: hidden');
    }
    
    return problems;
  }

  /**
   * 测试所有已知的问题XPath
   * @returns 所有测试结果
   */
  testAllKnownElements(): StyleTestResult[] {
    const knownXPaths: string[] = [
      '//*[@id="app"]/div[2]/div/div[3]',
      '//*[@id="app"]/div[2]/div/div[2]/div[1]',
      '//*[@id="app"]/div[3]/div[2]/div[1]',
      '//*[@id="app"]/div[3]/div[2]/div[1]/div[5]',
      '//*[@id="app"]/div[3]/div/div[1]/div[1]'
    ];

    this.testResults = knownXPaths.map(xpath => this.testElementStyle(xpath));
    return this.testResults;
  }

  /**
   * 生成测试报告
   * @returns 格式化的测试报告
   */
  generateReport(): string {
    if (this.testResults.length === 0) {
      this.testAllKnownElements();
    }

    let report = '\n=== 样式测试报告 ===\n';
    
    this.testResults.forEach((result, index) => {
      report += `\n${index + 1}. XPath: ${result.xpath}\n`;
      
      if (!result.found) {
        report += `   状态: ❌ ${result.message || result.error}\n`;
        return;
      }
      
      report += `   状态: ✅ 元素找到 (${result.element})\n`;
      report += `   位置: ${result.position}\n`;
      report += `   z-index: ${result.zIndex}\n`;
      report += `   显示: ${result.display}\n`;
      report += `   可见: ${result.visibility}\n`;
      
      if (result.hasProblems) {
        report += `   问题: ⚠️  ${result.problems?.join(', ')}\n`;
      } else {
        report += `   问题: ✅ 无问题\n`;
      }
    });
    
    const problemCount = this.testResults.filter(r => r.hasProblems).length;
    const foundCount = this.testResults.filter(r => r.found).length;
    
    report += `\n=== 总结 ===\n`;
    report += `找到元素: ${foundCount}/${this.testResults.length}\n`;
    report += `有问题的元素: ${problemCount}\n`;
    report += `修复状态: ${problemCount === 0 ? '✅ 全部修复' : '⚠️  仍有问题'}\n`;
    
    return report;
  }

  /**
   * 在控制台输出测试报告
   */
  logReport(): void {
    console.log(this.generateReport());
  }

  /**
   * 获取测试结果
   */
  getTestResults(): StyleTestResult[] {
    return this.testResults;
  }

  /**
   * 清除测试结果
   */
  clearResults(): void {
    this.testResults = [];
  }
}

// 创建全局实例
const styleTestHelper = new StyleTestHelper();

// 导出供其他模块使用
if (typeof window !== 'undefined') {
  (window as any).styleTestHelper = styleTestHelper;
}

export type { StyleTestResult, StyleProblem };
export default styleTestHelper;
export { StyleTestHelper };