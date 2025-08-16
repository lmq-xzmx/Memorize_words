/**
 * 系统性能监控模块
 * 负责系统级别的性能指标收集和分析
 */

export class SystemMonitor {
    constructor() {
        this.metrics = {
            memoryUsage: 0,
            networkStatus: 'online',
            batteryLevel: null,
            connectionType: 'unknown',
            deviceInfo: {},
            performanceEntries: [],
            resourceTiming: []
        };
        
        this.maxHistorySize = 500;
        this.monitoringInterval = null;
        
        this.initializeMonitoring();
    }

    /**
     * 初始化系统监控
     */
    initializeMonitoring() {
        this.detectDeviceInfo();
        this.setupNetworkMonitoring();
        this.setupBatteryMonitoring();
        this.setupPerformanceMonitoring();
        
        // 定期更新系统指标
        this.startPeriodicMonitoring();
    }

    /**
     * 检测设备信息
     */
    detectDeviceInfo() {
        this.metrics.deviceInfo = {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine,
            hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
            maxTouchPoints: navigator.maxTouchPoints || 0,
            screen: {
                width: screen.width,
                height: screen.height,
                colorDepth: screen.colorDepth,
                pixelDepth: screen.pixelDepth
            },
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            }
        };
    }

    /**
     * 设置网络监控
     */
    setupNetworkMonitoring() {
        // 监听网络状态变化
        window.addEventListener('online', () => {
            this.metrics.networkStatus = 'online';
            this.recordNetworkChange('online');
        });
        
        window.addEventListener('offline', () => {
            this.metrics.networkStatus = 'offline';
            this.recordNetworkChange('offline');
        });
        
        // 检测连接类型
        if ('connection' in navigator) {
            const connection = navigator.connection;
            this.metrics.connectionType = connection.effectiveType || 'unknown';
            
            connection.addEventListener('change', () => {
                this.metrics.connectionType = connection.effectiveType || 'unknown';
                this.recordConnectionChange(connection);
            });
        }
    }

    /**
     * 设置电池监控
     */
    setupBatteryMonitoring() {
        if ('getBattery' in navigator) {
            navigator.getBattery().then(battery => {
                this.updateBatteryInfo(battery);
                
                battery.addEventListener('levelchange', () => {
                    this.updateBatteryInfo(battery);
                });
                
                battery.addEventListener('chargingchange', () => {
                    this.updateBatteryInfo(battery);
                });
            }).catch(error => {
                console.warn('[SystemMonitor] 无法获取电池信息:', error);
            });
        }
    }

    /**
     * 设置性能监控
     */
    setupPerformanceMonitoring() {
        if ('performance' in window) {
            // 监听性能条目
            if ('PerformanceObserver' in window) {
                try {
                    const observer = new PerformanceObserver((list) => {
                        this.processPerformanceEntries(list.getEntries());
                    });
                    
                    observer.observe({ entryTypes: ['navigation', 'resource', 'measure', 'mark'] });
                } catch (error) {
                    console.warn('[SystemMonitor] PerformanceObserver不支持:', error);
                }
            }
        }
    }

    /**
     * 开始定期监控
     */
    startPeriodicMonitoring() {
        this.monitoringInterval = setInterval(() => {
            this.updateMemoryUsage();
            this.updatePerformanceMetrics();
        }, 30000); // 每30秒更新一次
    }

    /**
     * 停止定期监控
     */
    stopPeriodicMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
    }

    /**
     * 更新内存使用情况
     */
    updateMemoryUsage() {
        if ('memory' in performance) {
            const memory = performance.memory;
            this.metrics.memoryUsage = {
                used: memory.usedJSHeapSize,
                total: memory.totalJSHeapSize,
                limit: memory.jsHeapSizeLimit,
                percentage: (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100,
                timestamp: Date.now()
            };
        }
    }

    /**
     * 更新性能指标
     */
    updatePerformanceMetrics() {
        if ('performance' in window) {
            const navigation = performance.getEntriesByType('navigation')[0];
            if (navigation) {
                this.recordNavigationTiming(navigation);
            }
        }
    }

    /**
     * 更新电池信息
     */
    updateBatteryInfo(battery) {
        this.metrics.batteryLevel = {
            level: battery.level,
            charging: battery.charging,
            chargingTime: battery.chargingTime,
            dischargingTime: battery.dischargingTime,
            timestamp: Date.now()
        };
    }

    /**
     * 记录网络状态变化
     */
    recordNetworkChange(status) {
        this.metrics.performanceEntries.push({
            type: 'network',
            status,
            timestamp: Date.now()
        });
        
        this.limitHistorySize(this.metrics.performanceEntries);
    }

    /**
     * 记录连接变化
     */
    recordConnectionChange(connection) {
        this.metrics.performanceEntries.push({
            type: 'connection',
            effectiveType: connection.effectiveType,
            downlink: connection.downlink,
            rtt: connection.rtt,
            timestamp: Date.now()
        });
        
        this.limitHistorySize(this.metrics.performanceEntries);
    }

    /**
     * 记录导航时间
     */
    recordNavigationTiming(navigation) {
        this.metrics.performanceEntries.push({
            type: 'navigation',
            loadTime: navigation.loadEventEnd - navigation.navigationStart,
            domContentLoaded: navigation.domContentLoadedEventEnd - navigation.navigationStart,
            firstPaint: navigation.responseEnd - navigation.requestStart,
            timestamp: Date.now()
        });
        
        this.limitHistorySize(this.metrics.performanceEntries);
    }

    /**
     * 处理性能条目
     */
    processPerformanceEntries(entries) {
        entries.forEach(entry => {
            if (entry.entryType === 'resource') {
                this.recordResourceTiming(entry);
            } else if (entry.entryType === 'measure' || entry.entryType === 'mark') {
                this.recordCustomTiming(entry);
            }
        });
    }

    /**
     * 记录资源时间
     */
    recordResourceTiming(entry) {
        this.metrics.resourceTiming.push({
            name: entry.name,
            duration: entry.duration,
            size: entry.transferSize || 0,
            type: entry.initiatorType,
            timestamp: Date.now()
        });
        
        this.limitHistorySize(this.metrics.resourceTiming);
    }

    /**
     * 记录自定义时间
     */
    recordCustomTiming(entry) {
        this.metrics.performanceEntries.push({
            type: entry.entryType,
            name: entry.name,
            duration: entry.duration,
            timestamp: Date.now()
        });
        
        this.limitHistorySize(this.metrics.performanceEntries);
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
     * 获取系统性能指标
     */
    getMetrics() {
        return {
            ...this.metrics,
            resourceStats: this.getResourceStats(),
            performanceStats: this.getPerformanceStats()
        };
    }

    /**
     * 获取资源统计
     */
    getResourceStats() {
        if (this.metrics.resourceTiming.length === 0) return null;
        
        const totalSize = this.metrics.resourceTiming.reduce((sum, resource) => sum + resource.size, 0);
        const avgDuration = this.metrics.resourceTiming.reduce((sum, resource) => sum + resource.duration, 0) / this.metrics.resourceTiming.length;
        
        return {
            totalResources: this.metrics.resourceTiming.length,
            totalSize,
            averageDuration: avgDuration,
            slowestResource: Math.max(...this.metrics.resourceTiming.map(r => r.duration))
        };
    }

    /**
     * 获取性能统计
     */
    getPerformanceStats() {
        const navigationEntries = this.metrics.performanceEntries.filter(entry => entry.type === 'navigation');
        if (navigationEntries.length === 0) return null;
        
        const latest = navigationEntries[navigationEntries.length - 1];
        return {
            pageLoadTime: latest.loadTime,
            domContentLoadedTime: latest.domContentLoaded,
            firstPaintTime: latest.firstPaint
        };
    }

    /**
     * 重置统计数据
     */
    reset() {
        this.metrics.performanceEntries = [];
        this.metrics.resourceTiming = [];
        this.metrics.memoryUsage = 0;
    }

    /**
     * 清理过期数据
     */
    cleanup(maxAge = 24 * 60 * 60 * 1000) { // 默认24小时
        const cutoff = Date.now() - maxAge;
        
        this.metrics.performanceEntries = this.metrics.performanceEntries.filter(
            entry => entry.timestamp > cutoff
        );
        
        this.metrics.resourceTiming = this.metrics.resourceTiming.filter(
            entry => entry.timestamp > cutoff
        );
    }

    /**
     * 销毁监控器
     */
    destroy() {
        this.stopPeriodicMonitoring();
        this.reset();
    }
}