/**
 * 九宫格进度图表组件
 * 基于纯JavaScript实现的圆形布局进度图表
 */
class ProgressChart {
    constructor(containerOrId, options = {}) {
        // 支持传入DOM元素或字符串ID
        if (typeof containerOrId === 'string') {
            this.container = document.getElementById(containerOrId);
            if (!this.container) {
                throw new Error(`Container with id '${containerOrId}' not found`);
            }
        } else if (containerOrId instanceof HTMLElement) {
            this.container = containerOrId;
        } else {
            throw new Error('Container must be a DOM element or a valid element ID string');
        }
        
        this.options = this.mergeOptions(options);
        this.data = [];
        this.isLoading = false;
        
        this.init();
    }
    
    /**
     * 合并默认选项和用户选项
     */
    mergeOptions(userOptions) {
        const defaultOptions = {
            title: '九宫格',
            subtitle: '进程',
            width: 360,
            height: 360,
            animated: true,
            responsive: true,
            theme: 'light',
            clickable: true,
            showTooltip: true,
            colors: {
                1: 'linear-gradient(135deg, #4CAF50, #45a049)', // 掌握
                2: 'linear-gradient(135deg, #f44336, #d32f2f)',   // 遗忘
                3: 'linear-gradient(135deg, #FFC107, #FF8F00)',   // 学习中
                4: 'linear-gradient(135deg, #2196F3, #1976D2)',   // 测试
                5: 'linear-gradient(135deg, #9C27B0, #7B1FA2)',   // 口音文本
                6: 'linear-gradient(135deg, #00BCD4, #0097A7)',   // 口音文件
                7: 'linear-gradient(135deg, #8BC34A, #689F38)',   // 区域化任务
                8: 'linear-gradient(135deg, #FF5722, #D84315)'    // 解决方案
            },
            onItemClick: null,
            onItemHover: null,
            enableAccessibility: true,
            enableAnimations: true
        };
        
        return { ...defaultOptions, ...userOptions };
    }
    
    /**
     * 初始化组件
     */
    init() {
        this.createStructure();
        this.bindEvents();
        
        if (this.options.responsive) {
            this.setupResponsive();
        }
    }
    
    /**
     * 创建HTML结构
     */
    createStructure() {
        const themeClass = this.options.theme === 'dark' ? 'theme-dark' : '';
        
        this.container.innerHTML = `
            <div class="progress-chart-container ${themeClass}">
                <div class="progress-chart ${themeClass}">
                    <div class="center-circle">
                        <div class="center-content">
                            <h3 class="center-title">${this.options.title}</h3>
                            <p class="center-subtitle">${this.options.subtitle}</p>
                        </div>
                    </div>
                    <div class="grid-items" role="group" aria-label="学习进度数据"></div>
                </div>
            </div>
        `;
        
        this.chartElement = this.container.querySelector('.progress-chart');
        this.gridContainer = this.container.querySelector('.grid-items');
        this.containerElement = this.container.querySelector('.progress-chart-container');
    }
    
    /**
     * 更新数据并重新渲染
     */
    updateData(newData) {
        try {
            this.data = this.validateAndProcessData(newData);
            this.render();
        } catch (error) {
            console.error('数据更新失败:', error);
            this.showError('数据格式错误');
        }
    }
    
    /**
     * 验证和处理数据
     */
    validateAndProcessData(data) {
        if (!Array.isArray(data)) {
            throw new Error('数据必须是数组格式');
        }
        
        return data.map((item, index) => {
            // 确保item不为null或undefined
            if (!item) {
                item = {};
            }
            
            const processedItem = {
                position: item.position || (index + 1),
                category: item.category || `类别${index + 1}`,
                label: item.label || item.category || `项目${index + 1}`,
                value: this.formatValue(item.value || 0),
                rawValue: item.value || 0,
                color: item.color || this.options.colors[item.position] || this.options.colors[index + 1],
                textColor: item.textColor || '#fff',
                clickable: item.clickable !== false && this.options.clickable
            };
            
            // 验证位置范围
            if (processedItem.position < 1 || processedItem.position > 8) {
                console.warn(`位置 ${processedItem.position} 超出范围，将调整为 ${Math.max(1, Math.min(8, processedItem.position))}`);
                processedItem.position = Math.max(1, Math.min(8, processedItem.position));
            }
            
            return processedItem;
        });
    }
    
    /**
     * 格式化数值显示
     */
    formatValue(value) {
        if (typeof value !== 'number') {
            return '0';
        }
        
        if (value >= 1000000) {
            return (value / 1000000).toFixed(1) + 'M';
        } else if (value >= 1000) {
            return (value / 1000).toFixed(1) + 'K';
        }
        
        return value.toString();
    }
    
    /**
     * 渲染图表
     */
    render() {
        if (this.isLoading) return;
        
        this.setLoading(true);
        
        // 清空现有内容
        this.gridContainer.innerHTML = '';
        
        // 渲染数据项
        this.data.forEach(item => {
            if (item) {
                const gridItem = this.createGridItem(item);
                this.gridContainer.appendChild(gridItem);
            }
        });
        
        // 应用主题
        if (this.options.theme) {
            this.setTheme(this.options.theme);
        }
        
        // 添加动画效果
        if (this.options.animated) {
            setTimeout(() => {
                this.animateIn();
            }, 100);
        }
        
        this.setLoading(false);
        
        console.log('ProgressChart rendered successfully');
    }
    
    /**
     * 创建单个网格项
     */
    createGridItem(item) {
        if (!item) {
            console.warn('createGridItem: item is null or undefined');
            return document.createElement('div');
        }
        
        const div = document.createElement('div');
        div.className = 'grid-item';
        div.setAttribute('data-position', item.position || '');
        div.setAttribute('data-category', item.category || '');
        div.setAttribute('data-value', item.rawValue || item.value || '');
        
        if (item.clickable) {
            div.setAttribute('tabindex', '0');
            div.setAttribute('role', 'button');
            div.setAttribute('aria-label', `${item.label || '未知项目'}: ${item.value || '0'}`);
        }
        
        // 设置背景色
        div.style.background = item.color || '#f8f9fa';
        div.style.color = item.textColor || '#333';
        
        // 创建内容
        div.innerHTML = `
            <div class="item-content">
                <div class="item-label">${this.escapeHtml(item.label || '未知项目')}</div>
                <div class="item-value">${this.escapeHtml(item.value || '0')}</div>
            </div>
        `;
        
        // 绑定事件
        if (item.clickable) {
            div.addEventListener('click', (e) => this.handleItemClick(e, item));
            div.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.handleItemClick(e, item);
                }
            });
        }
        
        if (this.options.showTooltip) {
            div.addEventListener('mouseenter', (e) => this.showTooltip(e, item));
            div.addEventListener('mouseleave', () => this.hideTooltip());
        }
        
        return div;
    }
    
    /**
     * 处理项目点击事件
     */
    handleItemClick(event, item) {
        event.preventDefault();
        
        if (this.options.onItemClick && typeof this.options.onItemClick === 'function') {
            this.options.onItemClick(item, event);
        }
        
        // 触发自定义事件
        this.container.dispatchEvent(new CustomEvent('chartItemClick', {
            detail: { item, event }
        }));
    }
    
    /**
     * 显示工具提示
     */
    showTooltip(event, item) {
        if (!item) {
            console.warn('showTooltip: item is null or undefined');
            return;
        }
        
        if (this.options.onItemHover && typeof this.options.onItemHover === 'function') {
            this.options.onItemHover(item, event);
        }
        
        // 简单的工具提示实现
        const tooltip = document.createElement('div');
        tooltip.className = 'progress-chart-tooltip';
        tooltip.innerHTML = `
            <strong>${this.escapeHtml(item.label || '未知项目')}</strong><br>
            数值: ${this.escapeHtml(item.value || '0')}<br>
            类别: ${this.escapeHtml(item.category || '未知类别')}
        `;
        
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            line-height: 1.4;
            z-index: 1000;
            pointer-events: none;
            white-space: nowrap;
        `;
        
        document.body.appendChild(tooltip);
        
        const rect = event.target.getBoundingClientRect();
        tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
        
        this.currentTooltip = tooltip;
    }
    
    /**
     * 隐藏工具提示
     */
    hideTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }
    
    /**
     * 转义HTML字符
     */
    escapeHtml(text) {
        if (text === null || text === undefined) {
            return '';
        }
        const div = document.createElement('div');
        div.textContent = String(text);
        return div.innerHTML;
    }
    
    /**
     * 设置加载状态
     */
    setLoading(loading) {
        this.isLoading = loading;
        
        if (loading) {
            this.chartElement.classList.add('loading');
        } else {
            this.chartElement.classList.remove('loading');
        }
    }
    
    /**
     * 显示加载状态
     */
    showLoading() {
        this.setLoading(true);
        
        // 显示加载动画
        const themeClass = this.options.theme === 'dark' ? 'theme-dark' : '';
        this.container.innerHTML = `
            <div class="progress-chart-container ${themeClass}" style="
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 360px;
                color: ${this.options.theme === 'dark' ? '#a0aec0' : '#666'};
            ">
                <div style="
                    width: 50px;
                    height: 50px;
                    border: 4px solid ${this.options.theme === 'dark' ? '#4a5568' : '#f3f3f3'};
                    border-top: 4px solid #007bff;
                    border-radius: 50%;
                    animation: spin 1.2s linear infinite;
                    margin-bottom: 20px;
                "></div>
                <p style="font-size: 1.1rem; font-weight: 500;">正在加载数据...</p>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
    }
    
    /**
     * 隐藏加载状态
     */
    hideLoading() {
        this.setLoading(false);
        
        // 重新创建结构
        this.createStructure();
        
        // 如果有数据，重新渲染
        if (this.data.length > 0) {
            this.render();
        }
    }
    
    /**
     * 显示错误信息
     */
    showError(message) {
        console.error('ProgressChart Error:', message);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'progress-chart-error';
        errorDiv.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #dc3545;">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 10px;"></i><br>
                <strong>加载失败</strong><br>
                <small>${this.escapeHtml(message)}</small>
            </div>
        `;
        
        this.container.innerHTML = '';
        this.container.appendChild(errorDiv);
    }
    
    /**
     * 动画效果
     */
    animateIn() {
        const items = this.gridContainer.querySelectorAll('.grid-item');
        items.forEach((item, index) => {
            item.style.animation = 'fadeInScale 0.6s ease-out forwards';
            item.style.animationDelay = `${(index + 1) * 0.1}s`;
            item.style.opacity = '0';
        });
    }
    
    /**
     * 设置主题
     */
    setTheme(theme) {
        this.options.theme = theme;
        
        // 移除所有主题类
        this.chartElement.classList.remove('theme-light', 'theme-dark');
        this.containerElement.classList.remove('theme-light', 'theme-dark');
        
        // 添加新主题类
        if (theme && theme !== 'default') {
            this.chartElement.classList.add(`theme-${theme}`);
            this.containerElement.classList.add(`theme-${theme}`);
        }
    }
    
    /**
     * 切换主题
     */
    toggleTheme() {
        const currentTheme = this.options.theme || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
        return newTheme;
    }
    
    /**
     * 添加脉冲动画效果
     */
    addPulseEffect(position) {
        const item = this.gridContainer.querySelector(`[data-position="${position}"]`);
        if (item) {
            item.style.animation = 'pulse 1s ease-in-out 3';
            setTimeout(() => {
                item.style.animation = '';
            }, 3000);
        }
    }
    
    /**
     * 高亮特定项目
     */
    highlightItem(position, duration = 2000) {
        const item = this.gridContainer.querySelector(`[data-position="${position}"]`);
        if (item) {
            item.classList.add('highlighted');
            
            // 添加高亮样式
            const style = document.createElement('style');
            style.textContent = `
                .grid-item.highlighted {
                    transform: scale(1.12) !important;
                    box-shadow: 0 0 25px rgba(0, 123, 255, 0.8), 0 0 50px rgba(0, 123, 255, 0.4) !important;
                    z-index: 15 !important;
                    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
                    filter: brightness(1.2) saturate(1.2) !important;
                }
            `;
            document.head.appendChild(style);
            
            setTimeout(() => {
                item.classList.remove('highlighted');
                document.head.removeChild(style);
            }, duration);
        }
    }
    
    /**
     * 设置响应式
     */
    setupResponsive() {
        const resizeHandler = this.debounce(() => {
            this.handleResize();
        }, 250);
        
        window.addEventListener('resize', resizeHandler);
        
        // 保存引用以便清理
        this.resizeHandler = resizeHandler;
    }
    
    /**
     * 处理窗口大小变化
     */
    handleResize() {
        // 响应式逻辑已通过CSS媒体查询处理
        // 这里可以添加额外的JavaScript响应式逻辑
    }
    
    /**
     * 防抖函数
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 键盘导航支持
        this.container.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                // Tab键导航已由浏览器处理
                return;
            }
        });
    }
    
    /**
     * 更新配置
     */
    updateOptions(newOptions) {
        this.options = this.mergeOptions({ ...this.options, ...newOptions });
        
        // 更新标题
        const titleElement = this.container.querySelector('.center-title');
        const subtitleElement = this.container.querySelector('.center-subtitle');
        
        if (titleElement) titleElement.textContent = this.options.title;
        if (subtitleElement) subtitleElement.textContent = this.options.subtitle;
        
        // 重新渲染
        if (this.data.length > 0) {
            this.render();
        }
    }
    
    /**
     * 获取当前数据
     */
    getData() {
        return [...this.data];
    }
    
    /**
     * 清理资源
     */
    destroy() {
        // 移除事件监听器
        if (this.resizeHandler) {
            window.removeEventListener('resize', this.resizeHandler);
        }
        
        // 清理工具提示
        this.hideTooltip();
        
        // 清空容器
        this.container.innerHTML = '';
        
        // 清理引用
        this.container = null;
        this.chartElement = null;
        this.gridContainer = null;
        this.data = [];
    }
}

// 导出类（如果使用模块系统）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProgressChart;
}

// 全局注册（用于直接在HTML中使用）
if (typeof window !== 'undefined') {
    window.ProgressChart = ProgressChart;
}