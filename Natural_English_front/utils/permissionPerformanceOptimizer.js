/**
 * 权限性能优化模块
 * 根据实际使用情况优化权限缓存策略和性能
 */

/**
 * 权限性能监控器
 */
class PermissionPerformanceMonitor {
  constructor() {
    this.metrics = {
      cacheHits: 0,
      cacheMisses: 0,
      apiCalls: 0,
      averageResponseTime: 0,
      totalResponseTime: 0,
      permissionChecks: 0,
      slowQueries: [],
      memoryUsage: 0,
      cacheSize: 0
    };
    
    this.performanceThresholds = {
      slowQueryTime: 100, // ms
      maxCacheSize: 1000, // 条目数
      maxMemoryUsage: 50 * 1024 * 1024, // 50MB
      cacheHitRateTarget: 0.8 // 80%
    };
    
    this.startTime = Date.now();
    this.isMonitoring = false;
  }

  /**
   * 开始性能监控
   */
  startMonitoring() {
    this.isMonitoring = true;
    this.startTime = Date.now();
    
    // 定期收集性能指标
    this.monitoringInterval = setInterval(() => {
      this.collectMetrics();
    }, 5000); // 每5秒收集一次
    
    console.log('权限性能监控已启动');
  }

  /**
   * 停止性能监控
   */
  stopMonitoring() {
    this.isMonitoring = false;
    
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    
    console.log('权限性能监控已停止');
  }

  /**
   * 记录缓存命中
   */
  recordCacheHit() {
    this.metrics.cacheHits++;
  }

  /**
   * 记录缓存未命中
   */
  recordCacheMiss() {
    this.metrics.cacheMisses++;
  }

  /**
   * 记录API调用
   */
  recordApiCall(responseTime) {
    this.metrics.apiCalls++;
    this.metrics.totalResponseTime += responseTime;
    this.metrics.averageResponseTime = this.metrics.totalResponseTime / this.metrics.apiCalls;
    
    // 记录慢查询
    if (responseTime > this.performanceThresholds.slowQueryTime) {
      this.metrics.slowQueries.push({
        timestamp: Date.now(),
        responseTime,
        type: 'api_call'
      });
      
      // 只保留最近100个慢查询
      if (this.metrics.slowQueries.length > 100) {
        this.metrics.slowQueries = this.metrics.slowQueries.slice(-100);
      }
    }
  }

  /**
   * 记录权限检查
   */
  recordPermissionCheck(checkTime) {
    this.metrics.permissionChecks++;
    
    if (checkTime > this.performanceThresholds.slowQueryTime) {
      this.metrics.slowQueries.push({
        timestamp: Date.now(),
        responseTime: checkTime,
        type: 'permission_check'
      });
    }
  }

  /**
   * 收集性能指标
   */
  collectMetrics() {
    // 收集内存使用情况
    if (performance.memory) {
      this.metrics.memoryUsage = performance.memory.usedJSHeapSize;
    }
    
    // 收集缓存大小
    if (window.permissionCache) {
      this.metrics.cacheSize = window.permissionCache.getSize();
    }
  }

  /**
   * 获取缓存命中率
   */
  getCacheHitRate() {
    const total = this.metrics.cacheHits + this.metrics.cacheMisses;
    return total > 0 ? this.metrics.cacheHits / total : 0;
  }

  /**
   * 获取性能报告
   */
  getPerformanceReport() {
    const uptime = Date.now() - this.startTime;
    const cacheHitRate = this.getCacheHitRate();
    
    return {
      uptime,
      metrics: { ...this.metrics },
      cacheHitRate,
      performance: {
        isHealthy: this.isPerformanceHealthy(),
        recommendations: this.getPerformanceRecommendations()
      }
    };
  }

  /**
   * 检查性能是否健康
   */
  isPerformanceHealthy() {
    const cacheHitRate = this.getCacheHitRate();
    
    return (
      cacheHitRate >= this.performanceThresholds.cacheHitRateTarget &&
      this.metrics.averageResponseTime < this.performanceThresholds.slowQueryTime &&
      this.metrics.memoryUsage < this.performanceThresholds.maxMemoryUsage &&
      this.metrics.cacheSize < this.performanceThresholds.maxCacheSize
    );
  }

  /**
   * 获取性能优化建议
   */
  getPerformanceRecommendations() {
    const recommendations = [];
    const cacheHitRate = this.getCacheHitRate();
    
    if (cacheHitRate < this.performanceThresholds.cacheHitRateTarget) {
      recommendations.push({
        type: 'cache_optimization',
        message: `缓存命中率较低 (${(cacheHitRate * 100).toFixed(1)}%)，建议增加缓存时间或预加载常用权限`,
        priority: 'high'
      });
    }
    
    if (this.metrics.averageResponseTime > this.performanceThresholds.slowQueryTime) {
      recommendations.push({
        type: 'api_optimization',
        message: `API响应时间较慢 (${this.metrics.averageResponseTime.toFixed(1)}ms)，建议优化后端接口或增加缓存`,
        priority: 'high'
      });
    }
    
    if (this.metrics.memoryUsage > this.performanceThresholds.maxMemoryUsage) {
      recommendations.push({
        type: 'memory_optimization',
        message: `内存使用过高 (${(this.metrics.memoryUsage / 1024 / 1024).toFixed(1)}MB)，建议清理缓存或减少缓存大小`,
        priority: 'medium'
      });
    }
    
    if (this.metrics.cacheSize > this.performanceThresholds.maxCacheSize) {
      recommendations.push({
        type: 'cache_size_optimization',
        message: `缓存条目过多 (${this.metrics.cacheSize})，建议实施LRU清理策略`,
        priority: 'medium'
      });
    }
    
    if (this.metrics.slowQueries.length > 10) {
      recommendations.push({
        type: 'query_optimization',
        message: `检测到${this.metrics.slowQueries.length}个慢查询，建议优化权限检查逻辑`,
        priority: 'medium'
      });
    }
    
    return recommendations;
  }
}

/**
 * 智能缓存策略优化器
 */
class SmartCacheOptimizer {
  constructor() {
    this.accessPatterns = new Map(); // 访问模式统计
    this.cacheStrategy = 'lru'; // 默认LRU策略
    this.preloadRules = new Set(); // 预加载规则
    this.optimizationInterval = null;
  }

  /**
   * 开始智能优化
   */
  startOptimization() {
    // 每分钟分析一次访问模式
    this.optimizationInterval = setInterval(() => {
      this.analyzeAccessPatterns();
      this.optimizeCacheStrategy();
      this.updatePreloadRules();
    }, 60000);
    
    console.log('智能缓存优化已启动');
  }

  /**
   * 停止智能优化
   */
  stopOptimization() {
    if (this.optimizationInterval) {
      clearInterval(this.optimizationInterval);
      this.optimizationInterval = null;
    }
    
    console.log('智能缓存优化已停止');
  }

  /**
   * 记录权限访问
   */
  recordAccess(permission, context = {}) {
    const key = permission;
    const now = Date.now();
    
    if (!this.accessPatterns.has(key)) {
      this.accessPatterns.set(key, {
        count: 0,
        lastAccess: now,
        firstAccess: now,
        contexts: new Set(),
        frequency: 0
      });
    }
    
    const pattern = this.accessPatterns.get(key);
    pattern.count++;
    pattern.lastAccess = now;
    pattern.contexts.add(context.page || 'unknown');
    
    // 计算访问频率 (次/小时)
    const timeSpan = now - pattern.firstAccess;
    pattern.frequency = timeSpan > 0 ? (pattern.count / timeSpan) * 3600000 : 0;
  }

  /**
   * 分析访问模式
   */
  analyzeAccessPatterns() {
    const now = Date.now();
    const hotPermissions = [];
    const coldPermissions = [];
    
    for (const [permission, pattern] of this.accessPatterns) {
      const timeSinceLastAccess = now - pattern.lastAccess;
      
      if (pattern.frequency > 10 && timeSinceLastAccess < 3600000) { // 1小时内高频访问
        hotPermissions.push({ permission, pattern });
      } else if (timeSinceLastAccess > 86400000) { // 24小时未访问
        coldPermissions.push({ permission, pattern });
      }
    }
    
    // 清理冷数据
    coldPermissions.forEach(({ permission }) => {
      this.accessPatterns.delete(permission);
      if (window.permissionCache) {
        window.permissionCache.remove(permission);
      }
    });
    
    console.log(`访问模式分析: 热点权限 ${hotPermissions.length} 个，清理冷数据 ${coldPermissions.length} 个`);
  }

  /**
   * 优化缓存策略
   */
  optimizeCacheStrategy() {
    const totalAccess = Array.from(this.accessPatterns.values())
      .reduce((sum, pattern) => sum + pattern.count, 0);
    
    if (totalAccess > 1000) {
      // 高访问量，使用LFU策略
      this.cacheStrategy = 'lfu';
    } else {
      // 低访问量，使用LRU策略
      this.cacheStrategy = 'lru';
    }
    
    // 应用新策略到缓存
    if (window.permissionCache && window.permissionCache.setStrategy) {
      window.permissionCache.setStrategy(this.cacheStrategy);
    }
  }

  /**
   * 更新预加载规则
   */
  updatePreloadRules() {
    this.preloadRules.clear();
    
    // 基于访问频率确定预加载权限
    const sortedPatterns = Array.from(this.accessPatterns.entries())
      .sort(([, a], [, b]) => b.frequency - a.frequency)
      .slice(0, 20); // 取前20个高频权限
    
    sortedPatterns.forEach(([permission]) => {
      this.preloadRules.add(permission);
    });
    
    console.log(`更新预加载规则: ${this.preloadRules.size} 个权限`);
  }

  /**
   * 获取预加载权限列表
   */
  getPreloadPermissions() {
    return Array.from(this.preloadRules);
  }

  /**
   * 获取优化建议
   */
  getOptimizationSuggestions() {
    const suggestions = [];
    
    // 分析访问模式
    const patterns = Array.from(this.accessPatterns.values());
    const avgFrequency = patterns.reduce((sum, p) => sum + p.frequency, 0) / patterns.length;
    
    if (avgFrequency > 50) {
      suggestions.push({
        type: 'high_frequency',
        message: '检测到高频权限访问，建议增加缓存时间',
        action: 'increase_cache_ttl'
      });
    }
    
    if (patterns.length > 500) {
      suggestions.push({
        type: 'large_dataset',
        message: '权限数据量较大，建议实施分页加载',
        action: 'implement_pagination'
      });
    }
    
    return suggestions;
  }
}

/**
 * 权限批量处理优化器
 */
class PermissionBatchOptimizer {
  constructor() {
    this.batchQueue = [];
    this.batchSize = 10;
    this.batchTimeout = 100; // ms
    this.processingTimer = null;
  }

  /**
   * 添加权限检查到批处理队列
   */
  addToBatch(permission, callback) {
    this.batchQueue.push({ permission, callback, timestamp: Date.now() });
    
    // 如果队列达到批处理大小，立即处理
    if (this.batchQueue.length >= this.batchSize) {
      this.processBatch();
    } else {
      // 否则设置定时器
      this.scheduleProcessing();
    }
  }

  /**
   * 调度批处理
   */
  scheduleProcessing() {
    if (this.processingTimer) {
      clearTimeout(this.processingTimer);
    }
    
    this.processingTimer = setTimeout(() => {
      this.processBatch();
    }, this.batchTimeout);
  }

  /**
   * 处理批次
   */
  async processBatch() {
    if (this.batchQueue.length === 0) return;
    
    const batch = this.batchQueue.splice(0, this.batchSize);
    const permissions = batch.map(item => item.permission);
    
    try {
      // 批量检查权限
      const results = await this.batchCheckPermissions(permissions);
      
      // 调用回调函数
      batch.forEach((item, index) => {
        item.callback(results[index]);
      });
      
    } catch (error) {
      console.error('批量权限检查失败:', error);
      
      // 失败时单独处理每个权限
      batch.forEach(async (item) => {
        try {
          const result = await this.singleCheckPermission(item.permission);
          item.callback(result);
        } catch (err) {
          item.callback(false);
        }
      });
    }
    
    // 如果还有待处理的项目，继续处理
    if (this.batchQueue.length > 0) {
      this.scheduleProcessing();
    }
  }

  /**
   * 批量检查权限
   */
  async batchCheckPermissions(permissions) {
    // 这里应该调用实际的批量权限检查API
    // 暂时使用模拟实现
    return permissions.map(permission => {
      if (window.permissionCache) {
        return window.permissionCache.getPermission(permission) !== null;
      }
      return false;
    });
  }

  /**
   * 单个权限检查
   */
  async singleCheckPermission(permission) {
    if (window.permissionCache) {
      return window.permissionCache.getPermission(permission) !== null;
    }
    return false;
  }
}

/**
 * 权限性能优化管理器
 */
class PermissionPerformanceOptimizer {
  constructor() {
    this.monitor = new PermissionPerformanceMonitor();
    this.cacheOptimizer = new SmartCacheOptimizer();
    this.batchOptimizer = new PermissionBatchOptimizer();
    this.isOptimizing = false;
  }

  /**
   * 启动性能优化
   */
  start() {
    if (this.isOptimizing) return;
    
    this.isOptimizing = true;
    this.monitor.startMonitoring();
    this.cacheOptimizer.startOptimization();
    
    console.log('权限性能优化器已启动');
  }

  /**
   * 停止性能优化
   */
  stop() {
    if (!this.isOptimizing) return;
    
    this.isOptimizing = false;
    this.monitor.stopMonitoring();
    this.cacheOptimizer.stopOptimization();
    
    console.log('权限性能优化器已停止');
  }

  /**
   * 优化权限检查
   */
  optimizePermissionCheck(permission, callback, options = {}) {
    const startTime = performance.now();
    
    // 记录访问模式
    this.cacheOptimizer.recordAccess(permission, options.context);
    
    // 检查缓存
    if (window.permissionCache) {
      const cached = window.permissionCache.getPermission(permission);
      if (cached !== null) {
        this.monitor.recordCacheHit();
        const endTime = performance.now();
        this.monitor.recordPermissionCheck(endTime - startTime);
        callback(cached);
        return;
      }
    }
    
    this.monitor.recordCacheMiss();
    
    // 使用批处理优化
    if (options.batch !== false) {
      this.batchOptimizer.addToBatch(permission, (result) => {
        const endTime = performance.now();
        this.monitor.recordPermissionCheck(endTime - startTime);
        callback(result);
      });
    } else {
      // 直接检查
      this.directPermissionCheck(permission).then(result => {
        const endTime = performance.now();
        this.monitor.recordPermissionCheck(endTime - startTime);
        callback(result);
      });
    }
  }

  /**
   * 直接权限检查
   */
  async directPermissionCheck(permission) {
    // 这里应该调用实际的权限检查逻辑
    return false;
  }

  /**
   * 预加载权限
   */
  async preloadPermissions() {
    const permissions = this.cacheOptimizer.getPreloadPermissions();
    
    if (permissions.length > 0) {
      console.log(`预加载 ${permissions.length} 个权限`);
      
      // 批量加载权限
      try {
        const results = await this.batchOptimizer.batchCheckPermissions(permissions);
        
        // 更新缓存
        if (window.permissionCache) {
          permissions.forEach((permission, index) => {
            window.permissionCache.setPermission(permission, results[index]);
          });
        }
      } catch (error) {
        console.error('预加载权限失败:', error);
      }
    }
  }

  /**
   * 获取性能报告
   */
  getPerformanceReport() {
    const monitorReport = this.monitor.getPerformanceReport();
    const optimizationSuggestions = this.cacheOptimizer.getOptimizationSuggestions();
    
    return {
      ...monitorReport,
      optimization: {
        cacheStrategy: this.cacheOptimizer.cacheStrategy,
        preloadRules: this.cacheOptimizer.preloadRules.size,
        suggestions: optimizationSuggestions
      }
    };
  }
}

// 创建全局实例
const permissionPerformanceOptimizer = new PermissionPerformanceOptimizer();

// 自动启动优化
if (typeof window !== 'undefined') {
  window.addEventListener('load', () => {
    permissionPerformanceOptimizer.start();
  });
}

export {
  PermissionPerformanceMonitor,
  SmartCacheOptimizer,
  PermissionBatchOptimizer,
  PermissionPerformanceOptimizer,
  permissionPerformanceOptimizer
};

export default permissionPerformanceOptimizer;