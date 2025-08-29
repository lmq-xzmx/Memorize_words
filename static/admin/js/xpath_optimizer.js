// XPath表达式优化工具
// 针对Django Admin表单元素定位的优化方案

(function() {
    'use strict';
    
    // XPath优化器类
    class XPathOptimizer {
        constructor() {
            this.selectors = {
                // CustomUser表单的优化选择器
                customUserForm: {
                    // 更新的XPath: /html/body/div/div[2]/div/div[1]/div/form/div/fieldset/div[1]/div/div/select
                    // 优化后的多重选择器策略
                    permissions: {
                        // 策略1: 基于fieldset标题定位
                        byFieldsetTitle: '//fieldset[contains(.//h2, "权限")]//div[@class="form-row"]//select',
                        
                        // 策略2: 基于字段名定位
                        byFieldName: '//div[contains(@class, "field-is_active") or contains(@class, "field-is_staff") or contains(@class, "field-is_superuser")]//select',
                        
                        // 策略3: 基于表单ID和相对位置
                        byFormStructure: '#customuser_form fieldset:nth-child(1) .form-row select',
                        
                        // 策略4: 更稳定的CSS选择器
                        byCSS: '#customuser_form .fieldset:has(h2:contains("权限")) .form-row select',
                        
                        // 策略5: 新的XPath路径
                        byNewXPath: '/html/body/div/div[2]/div/div[1]/div/form/div/fieldset/div[1]/div/div/select'
                    }
                }
            };
        }
        
        /**
         * 获取元素的优化选择器
         * @param {string} formType - 表单类型
         * @param {string} section - 表单区域
         * @returns {Object} 包含多种选择器策略的对象
         */
        getOptimizedSelectors(formType, section) {
            if (this.selectors[formType] && this.selectors[formType][section]) {
                return this.selectors[formType][section];
            }
            return null;
        }
        
        /**
         * 尝试使用多种策略定位元素
         * @param {Object} selectors - 选择器策略对象
         * @returns {Element|null} 找到的元素
         */
        findElementWithFallback(selectors) {
            const strategies = [
                'byNewXPath',
                'byFieldName',
                'byFieldsetTitle', 
                'byFormStructure',
                'byCSS'
            ];
            
            for (const strategy of strategies) {
                if (selectors[strategy]) {
                    try {
                        let element;
                        
                        if (strategy === 'byFormStructure' || strategy === 'byCSS') {
                            // CSS选择器
                            element = document.querySelector(selectors[strategy]);
                        } else if (strategy === 'byNewXPath') {
                            // 新的XPath选择器 - 使用绝对路径
                            const result = document.evaluate(
                                selectors[strategy],
                                document,
                                null,
                                XPathResult.FIRST_ORDERED_NODE_TYPE,
                                null
                            );
                            element = result.singleNodeValue;
                        } else {
                            // 其他XPath选择器
                            const result = document.evaluate(
                                selectors[strategy],
                                document,
                                null,
                                XPathResult.FIRST_ORDERED_NODE_TYPE,
                                null
                            );
                            element = result.singleNodeValue;
                        }
                        
                        if (element) {
                            if (typeof console !== 'undefined' && console.debug) {
                                console.debug(`XPath优化: 使用策略 ${strategy} 成功定位元素`);
                            }
                            return element;
                        }
                    } catch (error) {
                        if (typeof console !== 'undefined' && console.debug) {
                            console.debug(`XPath优化: 策略 ${strategy} 失败:`, error.message);
                        }
                    }
                }
            }
            
            if (typeof console !== 'undefined' && console.warn) {
                console.warn('XPath优化: 所有定位策略都失败了');
            }
            return null;
        }
        
        /**
         * 获取权限字段区域的文本内容
         * @returns {string|null} 文本内容
         */
        getPermissionsFieldText() {
            const selectors = this.getOptimizedSelectors('customUserForm', 'permissions');
            if (!selectors) return null;
            
            const element = this.findElementWithFallback(selectors);
            if (element) {
                return element.textContent || element.innerText || null;
            }
            return null;
        }
        
        /**
         * 监听表单变化并更新元素定位
         */
        observeFormChanges() {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList' || mutation.type === 'attributes') {
                        // 表单结构发生变化时重新定位
                        this.refreshElementCache();
                    }
                });
            });
            
            const form = document.getElementById('customuser_form');
            if (form) {
                observer.observe(form, {
                    childList: true,
                    subtree: true,
                    attributes: true,
                    attributeFilter: ['class', 'id']
                });
            }
        }
        
        /**
         * 刷新元素缓存
         */
        refreshElementCache() {
            // 清除可能的缓存
            this.cachedElements = {};
            
            if (typeof console !== 'undefined' && console.debug) {
                console.debug('XPath优化: 元素缓存已刷新');
            }
        }
        
        /**
         * 生成更好的XPath表达式建议
         * @param {string} originalXPath - 原始XPath
         * @returns {Object} 优化建议
         */
        generateOptimizationSuggestions(originalXPath) {
            const suggestions = {
                original: originalXPath,
                issues: [],
                recommendations: []
            };
            
            // 分析原始XPath的问题
            if (originalXPath.includes('/div[2]/div/div[1]/input')) {
                suggestions.issues.push('旧的input元素路径已过时，应更新为select元素');
                suggestions.recommendations.push('使用新的select元素路径: /html/body/div/div[2]/div/div[1]/div/form/div/fieldset/div[1]/div/div/select');
            }
            
            if (originalXPath.includes('/div[2]/') || originalXPath.includes('/div[1]/')) {
                suggestions.issues.push('使用了硬编码的位置索引，容易因DOM结构变化而失效');
                suggestions.recommendations.push('使用基于内容或属性的定位方式');
            }
            
            if (originalXPath.includes('/text()')) {
                suggestions.issues.push('直接获取text()节点，可能获取不到完整内容');
                suggestions.recommendations.push('使用textContent或innerText属性获取文本');
            }
            
            if (originalXPath.startsWith('//*[@id=')) {
                suggestions.recommendations.push('考虑使用CSS选择器替代XPath以提高性能');
            }
            
            return suggestions;
        }
    }
    
    // 创建全局实例
    window.XPathOptimizer = new XPathOptimizer();
    
    // 自动初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            window.XPathOptimizer.observeFormChanges();
        });
    } else {
        window.XPathOptimizer.observeFormChanges();
    }
    
    // 提供便捷的全局方法
    window.getPermissionsText = function() {
        return window.XPathOptimizer.getPermissionsFieldText();
    };
    
    window.analyzeXPath = function(xpath) {
        return window.XPathOptimizer.generateOptimizationSuggestions(xpath);
    };
    
})();

// 使用示例和测试代码
if (typeof console !== 'undefined' && console.info) {
    console.info('XPath优化器已加载。使用方法:');
    console.info('1. getPermissionsText() - 获取权限字段文本');
    console.info('2. analyzeXPath(xpath) - 分析XPath表达式');
    console.info('3. window.XPathOptimizer - 访问完整的优化器实例');
}