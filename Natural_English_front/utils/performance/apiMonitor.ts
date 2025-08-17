/**
 * API性能监控模块
 * 负责API请求的性能指标收集和分析
 */

// 类型定义
interface ResponseTimeRecord {
  time: number;
  timestamp: number;
}

interface ErrorRateRecord {
  rate: number;
  timestamp: number;
}

interface EndpointStats {
  requests: number;
  successes: number;
  failures: number;
  totalTime: number;
  averageTime: number;
  slowestTime: number;
  fastestTime: number;
}

interface EndpointWithStats extends EndpointStats {
  endpoint: string;
  errorRate?: number;
}

interface APIMetrics {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  slowestRequest: number;
  fastestRequest: number;
  responseTimes: ResponseTimeRecord[];
  errorRates: ErrorRateRecord[];
  endpointStats: Map<string, EndpointStats>;
}

interface APIMetricsReport extends APIMetrics {
  currentErrorRate: number;
  topSlowEndpoints: EndpointWithStats[];
  topErrorEndpoints: EndpointWithStats[];
}

export class APIMonitor {
  private metrics: APIMetrics;
  private maxHistorySize: number;

  constructor() {
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0,
      slowestRequest: 0,
      fastestRequest: Infinity,
      responseTimes: [],
      errorRates: [],
      endpointStats: new Map<string, EndpointStats>()
    };
    
    this.maxHistorySize = 1000;
  }

  /**
   * 记录API请求
   */
  recordRequest(url: string, method: string, responseTime: number, success: boolean): void {
    this.metrics.totalRequests++;
    
    if (success) {
      this.metrics.successfulRequests++;
    } else {
      this.metrics.failedRequests++;
    }
    
    // 更新响应时间统计
    this.updateResponseTimeStats(responseTime);
    
    // 更新端点统计
    this.updateEndpointStats(url, method, responseTime, success);
    
    // 计算错误率
    this.updateErrorRate();
  }

  /**
   * 更新响应时间统计
   */
  private updateResponseTimeStats(responseTime: number): void {
    this.metrics.responseTimes.push({
      time: responseTime,
      timestamp: Date.now()
    });
    
    // 限制历史记录大小
    if (this.metrics.responseTimes.length > this.maxHistorySize) {
      this.metrics.responseTimes.shift();
    }
    
    // 更新最快/最慢请求
    this.metrics.slowestRequest = Math.max(this.metrics.slowestRequest, responseTime);
    this.metrics.fastestRequest = Math.min(this.metrics.fastestRequest, responseTime);
    
    // 计算平均响应时间
    const recentTimes = this.metrics.responseTimes.slice(-100); // 最近100个请求
    this.metrics.averageResponseTime = recentTimes.reduce((sum, item) => sum + item.time, 0) / recentTimes.length;
  }

  /**
   * 更新端点统计
   */
  private updateEndpointStats(url: string, method: string, responseTime: number, success: boolean): void {
    const key = `${method} ${url}`;
    
    if (!this.metrics.endpointStats.has(key)) {
      this.metrics.endpointStats.set(key, {
        requests: 0,
        successes: 0,
        failures: 0,
        totalTime: 0,
        averageTime: 0,
        slowestTime: 0,
        fastestTime: Infinity
      });
    }
    
    const stats = this.metrics.endpointStats.get(key)!;
    stats.requests++;
    stats.totalTime += responseTime;
    stats.averageTime = stats.totalTime / stats.requests;
    stats.slowestTime = Math.max(stats.slowestTime, responseTime);
    stats.fastestTime = Math.min(stats.fastestTime, responseTime);
    
    if (success) {
      stats.successes++;
    } else {
      stats.failures++;
    }
  }

  /**
   * 更新错误率
   */
  private updateErrorRate(): void {
    const errorRate = this.metrics.totalRequests > 0 
      ? this.metrics.failedRequests / this.metrics.totalRequests 
      : 0;
        
    this.metrics.errorRates.push({
      rate: errorRate,
      timestamp: Date.now()
    });
    
    // 限制历史记录大小
    if (this.metrics.errorRates.length > this.maxHistorySize) {
      this.metrics.errorRates.shift();
    }
  }

  /**
   * 获取API性能指标
   */
  getMetrics(): APIMetricsReport {
    return {
      ...this.metrics,
      currentErrorRate: this.getCurrentErrorRate(),
      topSlowEndpoints: this.getTopSlowEndpoints(5),
      topErrorEndpoints: this.getTopErrorEndpoints(5)
    };
  }

  /**
   * 获取当前错误率
   */
  getCurrentErrorRate(): number {
    if (this.metrics.errorRates.length === 0) return 0;
    return this.metrics.errorRates[this.metrics.errorRates.length - 1].rate;
  }

  /**
   * 获取最慢的端点
   */
  getTopSlowEndpoints(limit: number = 5): EndpointWithStats[] {
    return Array.from(this.metrics.endpointStats.entries())
      .map(([endpoint, stats]) => ({ endpoint, ...stats }))
      .sort((a, b) => b.averageTime - a.averageTime)
      .slice(0, limit);
  }

  /**
   * 获取错误最多的端点
   */
  getTopErrorEndpoints(limit: number = 5): EndpointWithStats[] {
    return Array.from(this.metrics.endpointStats.entries())
      .map(([endpoint, stats]) => ({ 
        endpoint, 
        ...stats, 
        errorRate: stats.requests > 0 ? stats.failures / stats.requests : 0 
      }))
      .sort((a, b) => (b.errorRate || 0) - (a.errorRate || 0))
      .slice(0, limit);
  }

  /**
   * 重置统计数据
   */
  reset(): void {
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0,
      slowestRequest: 0,
      fastestRequest: Infinity,
      responseTimes: [],
      errorRates: [],
      endpointStats: new Map<string, EndpointStats>()
    };
  }

  /**
   * 清理过期数据
   */
  cleanup(maxAge: number = 24 * 60 * 60 * 1000): void { // 默认24小时
    const cutoff = Date.now() - maxAge;
    
    this.metrics.responseTimes = this.metrics.responseTimes.filter(
      item => item.timestamp > cutoff
    );
    
    this.metrics.errorRates = this.metrics.errorRates.filter(
      item => item.timestamp > cutoff
    );
  }

  /**
   * 获取历史响应时间数据
   */
  getResponseTimeHistory(): ResponseTimeRecord[] {
    return [...this.metrics.responseTimes];
  }

  /**
   * 获取历史错误率数据
   */
  getErrorRateHistory(): ErrorRateRecord[] {
    return [...this.metrics.errorRates];
  }

  /**
   * 获取特定端点的统计信息
   */
  getEndpointStats(url: string, method: string): EndpointStats | null {
    const key = `${method} ${url}`;
    return this.metrics.endpointStats.get(key) || null;
  }
}

export type {
  ResponseTimeRecord,
  ErrorRateRecord,
  EndpointStats,
  EndpointWithStats,
  APIMetrics,
  APIMetricsReport
};

// 创建默认实例
export const apiMonitor = new APIMonitor();
export default APIMonitor;