/**
 * UI性能监控模块
 * 负责用户界面相关的性能指标收集和分析
 */

export class UIMonitor {
    constructor() {
        this.metrics = {
            renderTime: [],
            interactionLatency: [],
            scrollPerformance: [],
            animationFrames: [],
            domMutations: [],
            clickEvents: [],
            inputEvents: []
        };
        
        this.maxHistorySize = 300;
        this.observers = [];
        this.isMonitoring = false;
        
        this.initializeMonitoring();
    }

    /**
     * 初始化UI监控
     */
    initializeMonitoring() {
        this.setupRenderMonitoring();
        this.setupInteractionMonitoring();
        this.setupScrollMonitoring();
        this.setupDOMMonitoring();
        this.setupAnimationMonitoring();
        
        this.isMonitoring = true;
    }

    /**
     * 设置渲染监控
     */
    setupRenderMonitoring() {
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    list.getEntries().forEach(entry => {
                        if (entry.entryType === 'paint') {
                            this.recordPaintTiming(entry);
                        } else if (entry.entryType === 'largest-contentful-paint') {
                            this.recordLCPTiming(entry);
                        }
                    });
                });
                
                observer.observe({ entryTypes: ['paint', 'largest-contentful-paint'] });
                this.observers.push(observer);
            } catch (error) {
                console.warn('[UIMonitor] 渲染监控设置失败:', error);
            }
        }
    }

    /**
     * 设置交互监控
     */
    setupInteractionMonitoring() {
        // 监听点击事件
        document.addEventListener('click', (event) => {
            this.recordClickEvent(event);
        }, { passive: true });
        
        // 监听输入事件
        document.addEventListener('input', (event) => {
            this.recordInputEvent(event);
        }, { passive: true });
        
        // 监听键盘事件
        document.addEventListener('keydown', (event) => {
            this.recordKeyboardEvent(event);
        }, { passive: true });
    }

    /**
     * 设置滚动监控
     */
    setupScrollMonitoring() {
        let scrollStartTime = null;
        let isScrolling = false;
        
        document.addEventListener('scroll', () => {
            if (!isScrolling) {
                scrollStartTime = performance.now();
                isScrolling = true;
            }
        }, { passive: true });
        
        // 使用防抖来检测滚动结束
        let scrollTimeout;
        document.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                if (isScrolling && scrollStartTime) {
                    this.recordScrollPerformance(performance.now() - scrollStartTime);
                    isScrolling = false;
                    scrollStartTime = null;
                }
            }, 150);
        }, { passive: true });
    }

    /**
     * 设置DOM监控
     */
    setupDOMMonitoring() {
        if ('MutationObserver' in window) {
            const observer = new MutationObserver((mutations) => {
                this.recordDOMMutations(mutations);
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeOldValue: true
            });
            
            this.observers.push(observer);
        }
    }

    /**
     * 设置动画监控
     */
    setupAnimationMonitoring() {
        let frameCount = 0;
        let lastTime = performance.now();
        
        const measureFrameRate = () => {
            const currentTime = performance.now();
            frameCount++;
            
            if (currentTime - lastTime >= 1000) {
                this.recordAnimationFrame(frameCount, currentTime - lastTime);
                frameCount = 0;
                lastTime = currentTime;
            }
            
            if (this.isMonitoring) {
                requestAnimationFrame(measureFrameRate);
            }
        };
        
        requestAnimationFrame(measureFrameRate);
    }

    /**
     * 记录绘制时间
     */
    recordPaintTiming(entry) {
        this.metrics.renderTime.push({
            type: entry.name,
            startTime: entry.startTime,
            timestamp: Date.now()
        });
        
        this.limitHistorySize(this.metrics.renderTime);
    }

    /**
     * 记录最大内容绘制时间
     */
    recordLCPTiming(entry) {
        this.metrics.renderTime.push({
            type: 'largest-contentful-paint',
            startTime: entry.startTime,
            size: entry.size,
            timestamp: Date.now()
        });
        
        this.limitHistorySize(this.metrics.renderTime);
    }

    /**
     * 记录点击事件
     */
    recordClickEvent(event) {
        const startTime = performance.now();
        
        // 使用requestAnimationFrame来测量响应时间
        requestAnimationFrame(() => {
            const responseTime = performance.now() - startTime;
            
            this.metrics.clickEvents.push({
                target: event.target.tagName,
                className: event.target.className,
                responseTime,
                timestamp: Date.now()
            });
            
            this.metrics.interactionLatency.push({
                type: 'click',
                latency: responseTime,
                timestamp: Date.now()
            });
            
            this.limitHistorySize(this.metrics.clickEvents);
            this.limitHistorySize(this.metrics.interactionLatency);
        });
    }

    /**
     * 记录输入事件
     */
    recordInputEvent(event) {
        const startTime = performance.now();
        
        requestAnimationFrame(() => {
            const responseTime = performance.now() - startTime;
            
            this.metrics.inputEvents.push({
                type: event.target.type,
                tagName: event.target.tagName,
                responseTime,
                timestamp: Date.now()
            });
            
            this.metrics.interactionLatency.push({
                type: 'input',
                latency: responseTime,
                timestamp: Date.now()
            });
            
            this.limitHistorySize(this.metrics.inputEvents);
            this.limitHistorySize(this.metrics.interactionLatency);
        });
    }

    /**
     * 记录键盘事件
     */
    recordKeyboardEvent(event) {
        const startTime = performance.now();
        
        requestAnimationFrame(() => {
            const responseTime = performance.now() - startTime;
            
            this.metrics.interactionLatency.push({
                type: 'keyboard',
                key: event.key,
                latency: responseTime,
                timestamp: Date.now()
            });
            
            this.limitHistorySize(this.metrics.interactionLatency);
        });
    }

    /**
     * 记录滚动性能
     */
    recordScrollPerformance(duration) {
        this.metrics.scrollPerformance.push({
            duration,
            timestamp: Date.now()
        });
        
        this.limitHistorySize(this.metrics.scrollPerformance);
    }

    /**
     * 记录DOM变化
     */
    recordDOMMutations(mutations) {
        const mutationCount = mutations.length;
        const addedNodes = mutations.reduce((count, mutation) => count + mutation.addedNodes.length, 0);
        const removedNodes = mutations.reduce((count, mutation) => count + mutation.removedNodes.length, 0);
        
        this.metrics.domMutations.push({
            mutationCount,
            addedNodes,
            removedNodes,
            timestamp: Date.now()
        });
        
        this.limitHistorySize(this.metrics.domMutations);
    }

    /**
     * 记录动画帧率
     */
    recordAnimationFrame(frameCount, duration) {
        const fps = Math.round((frameCount * 1000) / duration);
        
        this.metrics.animationFrames.push({
            fps,
            frameCount,
            duration,
            timestamp: Date.now()
        });
        
        this.limitHistorySize(this.metrics.animationFrames);
    }

    /**
     * 限制历史记录大小
     */
    limitHistorySize(history) {
        if (history.length > this.maxHistorySize) {
            history.splice(0, history.length - this.maxHistorySize);
        }
    }

    /**
     * 获取UI性能指标
     */
    getMetrics() {
        return {
            ...this.metrics,
            renderStats: this.getRenderStats(),
            interactionStats: this.getInteractionStats(),
            scrollStats: this.getScrollStats(),
            animationStats: this.getAnimationStats(),
            domStats: this.getDOMStats()
        };
    }

    /**
     * 获取渲染统计
     */
    getRenderStats() {
        if (this.metrics.renderTime.length === 0) return null;
        
        const paintTimes = this.metrics.renderTime.filter(entry => entry.type.includes('paint'));
        const avgRenderTime = paintTimes.reduce((sum, entry) => sum + entry.startTime, 0) / paintTimes.length;
        
        return {
            totalRenders: paintTimes.length,
            averageRenderTime: avgRenderTime,
            lastRenderTime: paintTimes[paintTimes.length - 1]?.startTime || 0
        };
    }

    /**
     * 获取交互统计
     */
    getInteractionStats() {
        if (this.metrics.interactionLatency.length === 0) return null;
        
        const latencies = this.metrics.interactionLatency.map(entry => entry.latency);
        const avgLatency = latencies.reduce((sum, latency) => sum + latency, 0) / latencies.length;
        const maxLatency = Math.max(...latencies);
        
        return {
            totalInteractions: this.metrics.interactionLatency.length,
            averageLatency: avgLatency,
            maxLatency,
            clickCount: this.metrics.clickEvents.length,
            inputCount: this.metrics.inputEvents.length
        };
    }

    /**
     * 获取滚动统计
     */
    getScrollStats() {
        if (this.metrics.scrollPerformance.length === 0) return null;
        
        const durations = this.metrics.scrollPerformance.map(entry => entry.duration);
        const avgDuration = durations.reduce((sum, duration) => sum + duration, 0) / durations.length;
        
        return {
            totalScrolls: this.metrics.scrollPerformance.length,
            averageDuration: avgDuration,
            maxDuration: Math.max(...durations)
        };
    }

    /**
     * 获取动画统计
     */
    getAnimationStats() {
        if (this.metrics.animationFrames.length === 0) return null;
        
        const recentFrames = this.metrics.animationFrames.slice(-10); // 最近10个记录
        const avgFPS = recentFrames.reduce((sum, frame) => sum + frame.fps, 0) / recentFrames.length;
        const minFPS = Math.min(...recentFrames.map(frame => frame.fps));
        
        return {
            currentFPS: recentFrames[recentFrames.length - 1]?.fps || 0,
            averageFPS: avgFPS,
            minFPS,
            frameDrops: recentFrames.filter(frame => frame.fps < 30).length
        };
    }

    /**
     * 获取DOM统计
     */
    getDOMStats() {
        if (this.metrics.domMutations.length === 0) return null;
        
        const totalMutations = this.metrics.domMutations.reduce((sum, entry) => sum + entry.mutationCount, 0);
        const totalAdded = this.metrics.domMutations.reduce((sum, entry) => sum + entry.addedNodes, 0);
        const totalRemoved = this.metrics.domMutations.reduce((sum, entry) => sum + entry.removedNodes, 0);
        
        return {
            totalMutations,
            totalAddedNodes: totalAdded,
            totalRemovedNodes: totalRemoved,
            mutationEvents: this.metrics.domMutations.length
        };
    }

    /**
     * 重置统计数据
     */
    reset() {
        Object.keys(this.metrics).forEach(key => {
            this.metrics[key] = [];
        });
    }

    /**
     * 清理过期数据
     */
    cleanup(maxAge = 10 * 60 * 1000) { // 默认10分钟
        const cutoff = Date.now() - maxAge;
        
        Object.keys(this.metrics).forEach(key => {
            if (Array.isArray(this.metrics[key])) {
                this.metrics[key] = this.metrics[key].filter(
                    entry => entry.timestamp > cutoff
                );
            }
        });
    }

    /**
     * 停止监控
     */
    stopMonitoring() {
        this.isMonitoring = false;
        
        // 断开所有观察者
        this.observers.forEach(observer => {
            if (observer.disconnect) {
                observer.disconnect();
            }
        });
        
        this.observers = [];
    }

    /**
     * 销毁监控器
     */
    destroy() {
        this.stopMonitoring();
        this.reset();
    }
}