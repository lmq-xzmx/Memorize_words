/**
 * 权限性能监控器
 * 提供权限检查性能监控、统计分析和性能优化建议
 */

interface PermissionCheckMetrics {
  total: number;
  successful: number;
  failed: number;
  cached: number;
  uncached: number;
}

interface TimingMetrics {
  totalTime: number;
  averageTime: number;
  minTime: number;
  maxTime: number;
  p95Time: number;
  p99Time: number;
}

interface CacheMetrics {
  hits: number;
  misses: number;
  hitRate: number;
  evictions: number;
}

interface ApiMetrics {
  requests: number;
  responses: number;
  errors: number;
  timeouts: number;
  averageResponseTime: number;
}

interface MemoryMetrics {
  cacheSize: number;
  memoryUsage: number;
  peakMemoryUsage: number;
}

interface PerformanceMetrics {
  permissionChecks: PermissionCheckMetrics;
  timing: TimingMetrics;
  cache: CacheMetrics;
  api: ApiMetrics;
  memory: MemoryMetrics;
}

interface PerformanceThresholds {
  slowPermissionCheck: number;
  cacheHitRateWarning: number;
  memoryUsageWarning: number;
  apiErrorRateWarning: number;
}

interface SamplingConfig {
  enabled: boolean;
  rate: number;
  detailedLogging: boolean;
}

interface CheckData {
  id: string;
  startTime: number;
  context: Record<string, any>;
  timestamp: number;
}

interface CheckResult {
  success?: boolean;
  fromCache?: boolean;
  error?: any;
}

interface CheckRecord extends CheckData {
  endTime: number;
  duration: number;
  result: CheckResult;
  slow: boolean;
}

interface ApiRequestData {
  url: string;
  method: string;
  startTime: number;
  timestamp: number;
}

interface ApiResponse {
  error?: any;
  timeout?: boolean;
  status?: number;
}

interface PerformanceAlert {
  type: string;
  severity: 'info' | 'warning' | 'error';
  message: string;
  data: any;
  timestamp: number;
}

interface PerformanceRecommendation {
  type: string;
  priority: 'low' | 'medium' | 'high';
  message: string;
  impact: string;
}

interface PerformanceTrends {
  insufficient_data?: boolean;
  performance_trend?: 'increasing' | 'decreasing';
  change_magnitude?: number;
  significant?: boolean;
}

interface PerformanceAnalysis {
  timestamp: number;
  summary: {
    totalChecks: number;
    averageTime: number;
    cacheHitRate: number;
    errorRate: number;
  };
  recommendations: PerformanceRecommendation[];
  trends: PerformanceTrends;
}

interface PerformanceReport {
  metrics: PerformanceMetrics & {
    alerts: PerformanceAlert[];
    isMonitoring: boolean;
    samplingRate: number;
  };
  analysis: PerformanceAnalysis;
  recentAlerts: PerformanceAlert[];
  timingHistory: CheckRecord[];
}

type PerformanceListener = (event: string, data: any) => void;

class PermissionPerformanceMonitor {
    private metrics: PerformanceMetrics;
    private timingHistory: CheckRecord[];
    private maxHistorySize: number;
    private performanceThresholds: PerformanceThresholds;
    private alerts: PerformanceAlert[];
    private listeners: Set<PerformanceListener>;
    private isMonitoring: boolean;
    private samplingConfig: SamplingConfig;

    constructor() {
        this.metrics = {
            permissionChecks: {
                total: 0,
                successful: 0,
                failed: 0,
                cached: 0,
                uncached: 0
            },
            timing: {
                totalTime: 0,
                averageTime: 0,
                minTime: Infinity,
                maxTime: 0,
                p95Time: 0,
                p99Time: 0
            },
            cache: {
                hits: 0,
                misses: 0,
                hitRate: 0,
                evictions: 0
            },
            api: {
                requests: 0,
                responses: 0,
                errors: 0,
                timeouts: 0,
                averageResponseTime: 0
            },
            memory: {
                cacheSize: 0,
                memoryUsage: 0,
                peakMemoryUsage: 0
            }
        };
        
        this.timingHistory = [];
        this.maxHistorySize = 1000;
        this.performanceThresholds = {
            slowPermissionCheck: 100, // 100ms
            cacheHitRateWarning: 0.8, // 80%
            memoryUsageWarning: 50 * 1024 * 1024, // 50MB
            apiErrorRateWarning: 0.05 // 5%
        };
        
        this.alerts = [];
        this.listeners = new Set();
        this.isMonitoring = false;
        
        // 性能采样配置
        this.samplingConfig = {
            enabled: true,
            rate: 0.1, // 10%采样率
            detailedLogging: false
        };
        
        this.init();
    }

    /**
     * 初始化监控器
     */
    init(): void {
        this.startMonitoring();
        this.setupPerformanceObserver();
        this.schedulePeriodicAnalysis();
    }

    /**
     * 开始监控
     */
    startMonitoring(): void {
        this.isMonitoring = true;
        console.log('[PermissionPerformanceMonitor] 性能监控已启动');
    }

    /**
     * 停止监控
     */
    stopMonitoring(): void {
        this.isMonitoring = false;
        console.log('[PermissionPerformanceMonitor] 性能监控已停止');
    }

    /**
     * 记录权限检查开始
     */
    startPermissionCheck(checkId: string, context: Record<string, any> = {}): CheckData | null {
        if (!this.isMonitoring || !this.shouldSample()) {
            return null;
        }
        
        const startTime = performance.now();
        const checkData: CheckData = {
            id: checkId,
            startTime,
            context,
            timestamp: Date.now()
        };
        
        return checkData;
    }

    /**
     * 记录权限检查结束
     */
    endPermissionCheck(checkData: CheckData | null, result: CheckResult = {}): void {
        if (!checkData || !this.isMonitoring) {
            return;
        }
        
        const endTime = performance.now();
        const duration = endTime - checkData.startTime;
        
        // 更新基础指标
        this.metrics.permissionChecks.total++;
        
        if (result.success) {
            this.metrics.permissionChecks.successful++;
        } else {
            this.metrics.permissionChecks.failed++;
        }
        
        if (result.fromCache) {
            this.metrics.permissionChecks.cached++;
            this.metrics.cache.hits++;
        } else {
            this.metrics.permissionChecks.uncached++;
            this.metrics.cache.misses++;
        }
        
        // 更新时间指标
        this.updateTimingMetrics(duration);
        
        // 记录详细信息
        const checkRecord: CheckRecord = {
            ...checkData,
            endTime,
            duration,
            result,
            slow: duration > this.performanceThresholds.slowPermissionCheck
        };
        
        this.addTimingRecord(checkRecord);
        
        // 检查性能警告
        this.checkPerformanceAlerts(checkRecord);
        
        // 详细日志
        if (this.samplingConfig.detailedLogging) {
            console.log('[PermissionPerformanceMonitor] 权限检查完成:', checkRecord);
        }
        
        // 通知监听器
        this.notifyListeners('permissionCheckCompleted', checkRecord);
    }

    /**
     * 记录API请求
     */
    recordApiRequest(url: string, method: string = 'GET'): ApiRequestData | null {
        if (!this.isMonitoring) return null;
        
        this.metrics.api.requests++;
        
        return {
            url,
            method,
            startTime: performance.now(),
            timestamp: Date.now()
        };
    }

    /**
     * 记录API响应
     */
    recordApiResponse(requestData: ApiRequestData | null, response: ApiResponse = {}): void {
        if (!requestData || !this.isMonitoring) return;
        
        const duration = performance.now() - requestData.startTime;
        
        this.metrics.api.responses++;
        
        if (response.error) {
            this.metrics.api.errors++;
        }
        
        if (response.timeout) {
            this.metrics.api.timeouts++;
        }
        
        // 更新平均响应时间
        const totalResponseTime = this.metrics.api.averageResponseTime * (this.metrics.api.responses - 1) + duration;
        this.metrics.api.averageResponseTime = totalResponseTime / this.metrics.api.responses;
        
        // 检查API性能警告
        this.checkApiPerformanceAlerts({
            ...requestData,
            duration,
            response
        });
    }

    /**
     * 记录缓存操作
     */
    recordCacheOperation(operation: 'hit' | 'miss' | 'eviction', _details: Record<string, any> = {}): void {
        if (!this.isMonitoring) return;
        
        switch (operation) {
            case 'hit':
                this.metrics.cache.hits++;
                break;
            case 'miss':
                this.metrics.cache.misses++;
                break;
            case 'eviction':
                this.metrics.cache.evictions++;
                break;
        }
        
        // 更新缓存命中率
        const totalCacheRequests = this.metrics.cache.hits + this.metrics.cache.misses;
        if (totalCacheRequests > 0) {
            this.metrics.cache.hitRate = this.metrics.cache.hits / totalCacheRequests;
        }
        
        // 检查缓存性能警告
        this.checkCachePerformanceAlerts();
    }

    /**
     * 更新内存使用情况
     */
    updateMemoryUsage(cacheSize: number, memoryUsage: number): void {
        if (!this.isMonitoring) return;
        
        this.metrics.memory.cacheSize = cacheSize;
        this.metrics.memory.memoryUsage = memoryUsage;
        
        if (memoryUsage > this.metrics.memory.peakMemoryUsage) {
            this.metrics.memory.peakMemoryUsage = memoryUsage;
        }
        
        // 检查内存使用警告
        this.checkMemoryAlerts();
    }

    /**
     * 更新时间指标
     */
    private updateTimingMetrics(duration: number): void {
        this.metrics.timing.totalTime += duration;
        this.metrics.timing.averageTime = this.metrics.timing.totalTime / this.metrics.permissionChecks.total;
        
        if (duration < this.metrics.timing.minTime) {
            this.metrics.timing.minTime = duration;
        }
        
        if (duration > this.metrics.timing.maxTime) {
            this.metrics.timing.maxTime = duration;
        }
        
        // 计算百分位数
        this.calculatePercentiles();
    }

    /**
     * 添加时间记录
     */
    private addTimingRecord(record: CheckRecord): void {
        this.timingHistory.push(record);
        
        // 保持历史记录大小
        if (this.timingHistory.length > this.maxHistorySize) {
            this.timingHistory.shift();
        }
    }

    /**
     * 计算百分位数
     */
    private calculatePercentiles(): void {
        if (this.timingHistory.length === 0) return;
        
        const durations = this.timingHistory.map(record => record.duration).sort((a, b) => a - b);
        
        const p95Index = Math.floor(durations.length * 0.95);
        const p99Index = Math.floor(durations.length * 0.99);
        
        this.metrics.timing.p95Time = durations[p95Index] || 0;
        this.metrics.timing.p99Time = durations[p99Index] || 0;
    }

    /**
     * 检查性能警告
     */
    private checkPerformanceAlerts(checkRecord: CheckRecord): void {
        const alerts: PerformanceAlert[] = [];
        
        // 慢权限检查警告
        if (checkRecord.slow) {
            alerts.push({
                type: 'slow_permission_check',
                severity: 'warning',
                message: `权限检查耗时过长: ${checkRecord.duration.toFixed(2)}ms`,
                data: checkRecord,
                timestamp: Date.now()
            });
        }
        
        // 连续失败警告
        const recentFailures = this.getRecentFailures();
        if (recentFailures.length >= 5) {
            alerts.push({
                type: 'consecutive_failures',
                severity: 'error',
                message: `连续权限检查失败: ${recentFailures.length}次`,
                data: { failures: recentFailures },
                timestamp: Date.now()
            });
        }
        
        alerts.forEach(alert => this.addAlert(alert));
    }

    /**
     * 检查API性能警告
     */
    private checkApiPerformanceAlerts(_requestData: any): void {
        const errorRate = this.metrics.api.errors / this.metrics.api.requests;
        
        if (errorRate > this.performanceThresholds.apiErrorRateWarning) {
            this.addAlert({
                type: 'high_api_error_rate',
                severity: 'warning',
                message: `API错误率过高: ${(errorRate * 100).toFixed(2)}%`,
                data: { errorRate, totalRequests: this.metrics.api.requests },
                timestamp: Date.now()
            });
        }
    }

    /**
     * 检查缓存性能警告
     */
    private checkCachePerformanceAlerts(): void {
        if (this.metrics.cache.hitRate < this.performanceThresholds.cacheHitRateWarning) {
            this.addAlert({
                type: 'low_cache_hit_rate',
                severity: 'warning',
                message: `缓存命中率过低: ${(this.metrics.cache.hitRate * 100).toFixed(2)}%`,
                data: { hitRate: this.metrics.cache.hitRate },
                timestamp: Date.now()
            });
        }
    }

    /**
     * 检查内存警告
     */
    private checkMemoryAlerts(): void {
        if (this.metrics.memory.memoryUsage > this.performanceThresholds.memoryUsageWarning) {
            this.addAlert({
                type: 'high_memory_usage',
                severity: 'warning',
                message: `内存使用过高: ${(this.metrics.memory.memoryUsage / 1024 / 1024).toFixed(2)}MB`,
                data: { memoryUsage: this.metrics.memory.memoryUsage },
                timestamp: Date.now()
            });
        }
    }

    /**
     * 添加警告
     */
    private addAlert(alert: PerformanceAlert): void {
        this.alerts.push(alert);
        
        // 保持警告数量
        if (this.alerts.length > 100) {
            this.alerts.shift();
        }
        
        console.warn('[PermissionPerformanceMonitor] 性能警告:', alert);
        this.notifyListeners('performanceAlert', alert);
    }

    /**
     * 获取最近的失败记录
     */
    private getRecentFailures(): CheckRecord[] {
        const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
        return this.timingHistory.filter(record => 
            record.timestamp > fiveMinutesAgo && !record.result.success
        );
    }

    /**
     * 是否应该采样
     */
    private shouldSample(): boolean {
        if (!this.samplingConfig.enabled) return false;
        return Math.random() < this.samplingConfig.rate;
    }

    /**
     * 设置性能观察器
     */
    private setupPerformanceObserver(): void {
        if (typeof PerformanceObserver === 'undefined') {
            console.warn('[PermissionPerformanceMonitor] PerformanceObserver不可用');
            return;
        }
        
        try {
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    if (entry.name.includes('permission')) {
                        this.recordPerformanceEntry(entry);
                    }
                });
            });
            
            observer.observe({ entryTypes: ['measure', 'navigation', 'resource'] });
        } catch (error) {
            console.warn('[PermissionPerformanceMonitor] 设置PerformanceObserver失败:', error);
        }
    }

    /**
     * 记录性能条目
     */
    private recordPerformanceEntry(entry: PerformanceEntry): void {
        if (this.samplingConfig.detailedLogging) {
            console.log('[PermissionPerformanceMonitor] 性能条目:', entry);
        }
    }

    /**
     * 安排定期分析
     */
    private schedulePeriodicAnalysis(): void {
        setInterval(() => {
            this.performPeriodicAnalysis();
        }, 60000); // 每分钟分析一次
    }

    /**
     * 执行定期分析
     */
    private performPeriodicAnalysis(): void {
        if (!this.isMonitoring) return;
        
        const analysis = this.generatePerformanceAnalysis();
        
        if (analysis.recommendations.length > 0) {
            console.log('[PermissionPerformanceMonitor] 性能分析建议:', analysis.recommendations);
            this.notifyListeners('performanceAnalysis', analysis);
        }
    }

    /**
     * 生成性能分析报告
     */
    generatePerformanceAnalysis(): PerformanceAnalysis {
        const analysis: PerformanceAnalysis = {
            timestamp: Date.now(),
            summary: {
                totalChecks: this.metrics.permissionChecks.total,
                averageTime: this.metrics.timing.averageTime,
                cacheHitRate: this.metrics.cache.hitRate,
                errorRate: this.metrics.api.errors / Math.max(this.metrics.api.requests, 1)
            },
            recommendations: [],
            trends: this.analyzeTrends()
        };
        
        // 生成优化建议
        if (this.metrics.cache.hitRate < 0.8) {
            analysis.recommendations.push({
                type: 'cache_optimization',
                priority: 'high',
                message: '缓存命中率较低，建议优化缓存策略或增加缓存时间',
                impact: 'performance'
            });
        }
        
        if (this.metrics.timing.averageTime > 50) {
            analysis.recommendations.push({
                type: 'performance_optimization',
                priority: 'medium',
                message: '权限检查平均耗时较长，建议优化权限检查逻辑',
                impact: 'user_experience'
            });
        }
        
        if (this.metrics.api.errors / Math.max(this.metrics.api.requests, 1) > 0.05) {
            analysis.recommendations.push({
                type: 'error_handling',
                priority: 'high',
                message: 'API错误率较高，建议检查网络连接和错误处理机制',
                impact: 'reliability'
            });
        }
        
        return analysis;
    }

    /**
     * 分析趋势
     */
    private analyzeTrends(): PerformanceTrends {
        const recentRecords = this.timingHistory.slice(-100); // 最近100条记录
        
        if (recentRecords.length < 10) {
            return { insufficient_data: true };
        }
        
        const firstHalf = recentRecords.slice(0, Math.floor(recentRecords.length / 2));
        const secondHalf = recentRecords.slice(Math.floor(recentRecords.length / 2));
        
        const firstHalfAvg = firstHalf.reduce((sum, r) => sum + r.duration, 0) / firstHalf.length;
        const secondHalfAvg = secondHalf.reduce((sum, r) => sum + r.duration, 0) / secondHalf.length;
        
        const trend = secondHalfAvg > firstHalfAvg ? 'increasing' : 'decreasing';
        const change = Math.abs(secondHalfAvg - firstHalfAvg);
        
        return {
            performance_trend: trend,
            change_magnitude: change,
            significant: change > 10 // 变化超过10ms认为是显著变化
        };
    }

    /**
     * 获取性能指标
     */
    getMetrics(): PerformanceMetrics & {
        alerts: PerformanceAlert[];
        isMonitoring: boolean;
        samplingRate: number;
    } {
        return {
            ...this.metrics,
            alerts: this.alerts.slice(-10), // 最近10个警告
            isMonitoring: this.isMonitoring,
            samplingRate: this.samplingConfig.rate
        };
    }

    /**
     * 获取性能报告
     */
    getPerformanceReport(): PerformanceReport {
        return {
            metrics: this.getMetrics(),
            analysis: this.generatePerformanceAnalysis(),
            recentAlerts: this.alerts.slice(-20),
            timingHistory: this.timingHistory.slice(-50)
        };
    }

    /**
     * 重置指标
     */
    resetMetrics(): void {
        this.metrics = {
            permissionChecks: { total: 0, successful: 0, failed: 0, cached: 0, uncached: 0 },
            timing: { totalTime: 0, averageTime: 0, minTime: Infinity, maxTime: 0, p95Time: 0, p99Time: 0 },
            cache: { hits: 0, misses: 0, hitRate: 0, evictions: 0 },
            api: { requests: 0, responses: 0, errors: 0, timeouts: 0, averageResponseTime: 0 },
            memory: { cacheSize: 0, memoryUsage: 0, peakMemoryUsage: 0 }
        };
        
        this.timingHistory = [];
        this.alerts = [];
        
        console.log('[PermissionPerformanceMonitor] 性能指标已重置');
    }

    /**
     * 添加监听器
     */
    addListener(listener: PerformanceListener): void {
        this.listeners.add(listener);
    }

    /**
     * 移除监听器
     */
    removeListener(listener: PerformanceListener): void {
        this.listeners.delete(listener);
    }

    /**
     * 通知监听器
     */
    private notifyListeners(event: string, data: any): void {
        this.listeners.forEach(listener => {
            try {
                listener(event, data);
            } catch (error) {
                console.error('[PermissionPerformanceMonitor] 监听器错误:', error);
            }
        });
    }

    /**
     * 配置采样
     */
    configureSampling(config: Partial<SamplingConfig>): void {
        this.samplingConfig = { ...this.samplingConfig, ...config };
        console.log('[PermissionPerformanceMonitor] 采样配置已更新:', this.samplingConfig);
    }

    /**
     * 导出性能数据
     */
    exportData(): {
        metrics: PerformanceMetrics;
        timingHistory: CheckRecord[];
        alerts: PerformanceAlert[];
        config: SamplingConfig;
        timestamp: number;
    } {
        return {
            metrics: this.metrics,
            timingHistory: this.timingHistory,
            alerts: this.alerts,
            config: this.samplingConfig,
            timestamp: Date.now()
        };
    }
}

// 创建全局性能监控器实例
const performanceMonitor = new PermissionPerformanceMonitor();

export { performanceMonitor, PermissionPerformanceMonitor };
export default performanceMonitor;