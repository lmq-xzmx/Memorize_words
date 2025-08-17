/**
 * 性能监控和诊断模块
 * 提供全面的性能监控、实时状态检查和诊断功能
 */

import { APIMonitor } from './performance/apiMonitor.js';
import { WebSocketMonitor } from './performance/websocketMonitor.js';
import { UIMonitor } from './performance/uiMonitor.js';
import { SystemMonitor } from './performance/systemMonitor.js';
import globalErrorHandler from './globalErrorHandler';
import configManager from './configManager';

// 类型定义
interface APIMetrics {
  requests: any[];
  responseTimes: number[];
  errorRates: number[];
  averageResponseTime: number;
  errorRate: number;
  totalRequests: number;
  failedRequests: number;
}

interface WebSocketMetrics {
  connections: any[];
  averageLatency: number;
  reconnectCount: number;
  messagesSent: number;
  messagesReceived: number;
}

interface UIMetrics {
  pageLoadTime: number;
  renderTime: number;
  interactionLatency: number;
  componentRenders: any[];
  memoryUsage?: number;
  componentRenderCount?: number;
}

interface SystemMetrics {
  memoryUsage: number;
  networkStatus: string;
  connectionType: string;
  batteryLevel: number;
}

interface PerformanceMetrics {
  api: APIMetrics;
  websocket: WebSocketMetrics;
  ui: UIMetrics;
  system: SystemMetrics;
}

interface Alert {
  type: string;
  severity: 'info' | 'warning' | 'error';
  message: string;
  timestamp: number;
}

interface Thresholds {
  api: {
    responseTime: number;
    errorRate: number;
  };
  websocket: {
    latency: number;
    reconnectThreshold: number;
  };
  ui: {
    renderTime: number;
    interactionLatency: number;
  };
  system: {
    memoryUsage: number;
    batteryLevel: number;
  };
  apiResponseTime?: number;
  errorRate?: number;
  wsLatency?: number;
  memoryUsage?: number;
}

interface Recommendation {
  type: string;
  priority: 'low' | 'medium' | 'high';
  message: string;
}

interface PerformanceReport {
  timestamp: string;
  summary: any;
  details: any;
  alerts: Alert[];
  recommendations: Recommendation[];
}

class PerformanceMonitor {
  private apiMonitor: APIMonitor;
  private websocketMonitor: WebSocketMonitor;
  private uiMonitor: UIMonitor;
  private systemMonitor: SystemMonitor;
  private metrics: PerformanceMetrics;
  private alerts: Alert[];
  private thresholds: Thresholds;
  private monitoring: boolean;
  private monitoringInterval: NodeJS.Timeout | null;
  private observers: PerformanceObserver[];

  constructor() {
    // 初始化各个监控模块
    this.apiMonitor = new APIMonitor();
    this.websocketMonitor = new WebSocketMonitor();
    this.uiMonitor = new UIMonitor();
    this.systemMonitor = new SystemMonitor();
    
    // 初始化metrics对象
    this.metrics = {
      api: {
        requests: [],
        responseTimes: [],
        errorRates: [],
        averageResponseTime: 0,
        errorRate: 0,
        totalRequests: 0,
        failedRequests: 0
      },
      websocket: {
        connections: [],
        averageLatency: 0,
        reconnectCount: 0,
        messagesSent: 0,
        messagesReceived: 0
      },
      ui: {
        pageLoadTime: 0,
        renderTime: 0,
        interactionLatency: 0,
        componentRenders: []
      },
      system: {
        memoryUsage: 0,
        networkStatus: 'unknown',
        connectionType: 'unknown',
        batteryLevel: 100
      }
    };
    
    this.alerts = [];
    this.thresholds = {
      api: {
        responseTime: 3000, // 3秒
        errorRate: 5 // 5%
      },
      websocket: {
        latency: 1000, // 1秒
        reconnectThreshold: 3
      },
      ui: {
        renderTime: 16, // 60fps
        interactionLatency: 100
      },
      system: {
        memoryUsage: 80, // 80%
        batteryLevel: 20 // 20%
      },
      apiResponseTime: 3000,
      errorRate: 0.05,
      wsLatency: 1000,
      memoryUsage: 80
    };
    
    this.monitoring = false;
    this.monitoringInterval = null;
    this.observers = [];
    
    this.init();
  }

  /**
   * 初始化性能监控
   */
  init(): void {
    // 监听页面性能
    this.setupPagePerformanceMonitoring();
    
    // 监听网络状态
    this.setupNetworkMonitoring();
    
    // 监听内存使用
    this.setupMemoryMonitoring();
    
    // 设置定期检查
    this.startMonitoring();
    
    console.log('[性能监控] 初始化完成');
  }

  /**
   * 设置页面性能监控
   */
  setupPagePerformanceMonitoring(): void {
    // 监听页面加载性能
    if (typeof window !== 'undefined' && window.performance) {
      window.addEventListener('load', () => {
        setTimeout(() => {
          const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
          if (navigation) {
            this.metrics.ui.pageLoadTime = navigation.loadEventEnd - navigation.fetchStart;
            this.metrics.ui.renderTime = navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart;
          }
        }, 0);
      });
    }
    
    // 监听长任务
    if (typeof PerformanceObserver !== 'undefined') {
      try {
        const longTaskObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.duration > 50) { // 长于50ms的任务
              this.addAlert({
                type: 'performance',
                severity: 'warning',
                message: `检测到长任务: ${entry.duration.toFixed(2)}ms`,
                timestamp: Date.now()
              });
            }
          }
        });
        
        longTaskObserver.observe({ entryTypes: ['longtask'] });
        this.observers.push(longTaskObserver);
      } catch (error) {
        console.warn('[性能监控] 长任务监控不支持:', error);
      }
    }
  }

  /**
   * 设置网络监控
   */
  setupNetworkMonitoring(): void {
    // 监听网络状态变化
    window.addEventListener('online', () => {
      this.metrics.system.networkStatus = 'online';
      this.addAlert({
        type: 'network',
        severity: 'info',
        message: '网络连接已恢复',
        timestamp: Date.now()
      });
    });
    
    window.addEventListener('offline', () => {
      this.metrics.system.networkStatus = 'offline';
      this.addAlert({
        type: 'network',
        severity: 'error',
        message: '网络连接已断开',
        timestamp: Date.now()
      });
    });
    
    // 获取连接信息
    if ((navigator as any).connection) {
      this.metrics.system.connectionType = (navigator as any).connection.effectiveType || 'unknown';
      
      (navigator as any).connection.addEventListener('change', () => {
        this.metrics.system.connectionType = (navigator as any).connection.effectiveType || 'unknown';
      });
    }
    
    // 获取电池信息
    if ((navigator as any).getBattery) {
      (navigator as any).getBattery().then((battery: any) => {
        this.metrics.system.batteryLevel = battery.level;
        
        battery.addEventListener('levelchange', () => {
          this.metrics.system.batteryLevel = battery.level;
        });
      });
    }
  }

  /**
   * 设置内存监控
   */
  setupMemoryMonitoring(): void {
    if ((performance as any).memory) {
      setInterval(() => {
        this.metrics.ui.memoryUsage = (performance as any).memory.usedJSHeapSize;
        
        // 检查内存使用阈值
        if (this.metrics.ui.memoryUsage! > this.thresholds.memoryUsage!) {
          this.addAlert({
            type: 'memory',
            severity: 'warning',
            message: `内存使用过高: ${(this.metrics.ui.memoryUsage! / 1024 / 1024).toFixed(2)}MB`,
            timestamp: Date.now()
          });
        }
      }, 30000); // 每30秒检查一次
    }
  }

  /**
   * 开始监控
   */
  startMonitoring(): void {
    if (this.monitoring) {
      return;
    }
    
    this.monitoring = true;
    const interval = configManager.get('performance', 'metricsInterval', 30000);
    
    this.monitoringInterval = setInterval(() => {
      this.collectMetrics();
      this.checkThresholds();
      this.cleanupOldData();
    }, interval);
    
    console.log('[性能监控] 开始监控');
  }

  /**
   * 停止监控
   */
  stopMonitoring(): void {
    if (!this.monitoring) {
      return;
    }
    
    this.monitoring = false;
    
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    
    console.log('[性能监控] 停止监控');
  }

  /**
   * 收集指标
   */
  collectMetrics(): void {
    // 收集API性能指标
    this.updateAPIMetrics();
    
    // 收集UI性能指标
    this.updateUIMetrics();
    
    // 收集系统指标
    this.updateSystemMetrics();
  }

  /**
   * 更新API指标
   */
  updateAPIMetrics(): void {
    const apiMetrics = this.metrics.api;
    
    // 计算平均响应时间
    if (apiMetrics.responseTimes.length > 0) {
      const sum = apiMetrics.responseTimes.reduce((a, b) => a + b, 0);
      apiMetrics.averageResponseTime = sum / apiMetrics.responseTimes.length;
    }
    
    // 计算错误率
    if (apiMetrics.totalRequests > 0) {
      const errorRate = apiMetrics.failedRequests / apiMetrics.totalRequests;
      apiMetrics.errorRates.push(errorRate);
      
      // 保持最近100个错误率记录
      if (apiMetrics.errorRates.length > 100) {
        apiMetrics.errorRates.shift();
      }
    }
  }

  /**
   * 更新UI指标
   */
  updateUIMetrics(): void {
    if ((performance as any).memory) {
      this.metrics.ui.memoryUsage = (performance as any).memory.usedJSHeapSize;
    }
  }

  /**
   * 更新系统指标
   */
  updateSystemMetrics(): void {
    this.metrics.system.networkStatus = navigator.onLine ? 'online' : 'offline';
    
    if ((navigator as any).connection) {
      this.metrics.system.connectionType = (navigator as any).connection.effectiveType || 'unknown';
    }
  }

  /**
   * 检查阈值
   */
  checkThresholds(): void {
    const { api, ui, websocket } = this.metrics;
    
    // 检查API响应时间
    if (api.averageResponseTime > this.thresholds.apiResponseTime!) {
      this.addAlert({
        type: 'api',
        severity: 'warning',
        message: `API响应时间过慢: ${api.averageResponseTime.toFixed(2)}ms`,
        timestamp: Date.now()
      });
    }
    
    // 检查错误率
    if (api.errorRates.length > 0) {
      const recentErrorRate = api.errorRates.slice(-10).reduce((a, b) => a + b, 0) / Math.min(10, api.errorRates.length);
      if (recentErrorRate > this.thresholds.errorRate!) {
        this.addAlert({
          type: 'api',
          severity: 'error',
          message: `API错误率过高: ${(recentErrorRate * 100).toFixed(2)}%`,
          timestamp: Date.now()
        });
      }
    }
    
    // 检查WebSocket延迟
    if (websocket.averageLatency > this.thresholds.wsLatency!) {
      this.addAlert({
        type: 'websocket',
        severity: 'warning',
        message: `WebSocket延迟过高: ${websocket.averageLatency}ms`,
        timestamp: Date.now()
      });
    }
  }

  /**
   * 清理旧数据
   */
  cleanupOldData(): void {
    const maxAge = 60 * 60 * 1000; // 1小时
    
    this.apiMonitor.cleanup(maxAge);
    this.websocketMonitor.cleanup(maxAge);
    this.uiMonitor.cleanup(maxAge);
    this.systemMonitor.cleanup(maxAge);
    
    // 清理旧警报
    this.alerts = this.alerts.filter(alert => alert.timestamp > Date.now() - maxAge);
  }

  /**
   * 记录API请求
   */
  recordAPIRequest(url: string, method: string, responseTime: number, success: boolean = true): void {
    try {
      this.apiMonitor.recordRequest(url, method, responseTime);
      
      // 更新本地metrics
      this.metrics.api.responseTimes.push(responseTime);
      this.metrics.api.totalRequests++;
      if (!success) {
        this.metrics.api.failedRequests++;
      }
      
      // 保持最近100个响应时间记录
      if (this.metrics.api.responseTimes.length > 100) {
        this.metrics.api.responseTimes.shift();
      }
      
      // 获取当前指标进行阈值检查
      const metrics = this.apiMonitor.getMetrics();
      this.checkAPIThresholds(responseTime, metrics.errorRate);
      
    } catch (error) {
      globalErrorHandler.handleError(error, 'PerformanceMonitor.recordAPIRequest');
    }
  }

  /**
   * 检查API阈值
   */
  private checkAPIThresholds(responseTime: number, errorRate: number): void {
    if (responseTime > this.thresholds.api.responseTime) {
      this.addAlert({
        type: 'api',
        severity: 'warning',
        message: `API响应时间过慢: ${responseTime.toFixed(2)}ms`,
        timestamp: Date.now()
      });
    }
    
    if (errorRate > this.thresholds.api.errorRate / 100) {
      this.addAlert({
        type: 'api',
        severity: 'error',
        message: `API错误率过高: ${(errorRate * 100).toFixed(2)}%`,
        timestamp: Date.now()
      });
    }
  }

  /**
   * 检查WebSocket阈值
   */
  private checkWebSocketThresholds(latency: number): void {
    if (latency > this.thresholds.websocket.latency) {
      this.addAlert({
        type: 'websocket',
        severity: 'warning',
        message: `WebSocket延迟过高: ${latency}ms`,
        timestamp: Date.now()
      });
    }
  }

  /**
   * 记录WebSocket事件
   */
  recordWebSocketEvent(eventType: string, data: any = {}): void {
    try {
      this.websocketMonitor.recordEvent(eventType);
      
      // 获取当前指标进行阈值检查
      const metrics = this.websocketMonitor.getMetrics();
      if (eventType === 'latency' && data.latency) {
        this.checkWebSocketThresholds(data.latency);
      }
      
    } catch (error) {
      globalErrorHandler.handleError(error, 'PerformanceMonitor.recordWebSocketEvent');
    }
  }

  /**
   * 记录组件渲染
   */
  recordComponentRender(componentName: string, renderTime: number): void {
    if (!this.metrics.ui.componentRenderCount) {
      this.metrics.ui.componentRenderCount = 0;
    }
    this.metrics.ui.componentRenderCount++;
    
    if (renderTime > 16) { // 超过一帧的时间
      this.addAlert({
        type: 'ui',
        severity: 'info',
        message: `组件渲染较慢: ${componentName} (${renderTime.toFixed(2)}ms)`,
        timestamp: Date.now()
      });
    }
  }

  /**
   * 添加警报
   */
  addAlert(alert: Alert): void {
    this.alerts.push(alert);
    
    // 限制警报数量
    if (this.alerts.length > 100) {
      this.alerts.shift();
    }
    
    // 发送到全局错误处理器
    if (alert.severity === 'error') {
      globalErrorHandler.handleBusinessError(alert.message, alert.type, {
        performanceAlert: true,
        metrics: this.getMetricsSummary()
      });
    }
    
    console.log(`[性能监控] ${alert.severity.toUpperCase()}: ${alert.message}`);
  }

  /**
   * 获取所有性能指标
   */
  getMetrics(): any {
    return {
      api: this.apiMonitor.getMetrics(),
      websocket: this.websocketMonitor.getMetrics(),
      ui: this.uiMonitor.getMetrics(),
      system: this.systemMonitor.getMetrics(),
      alerts: this.alerts,
      timestamp: Date.now()
    };
  }

  /**
   * 获取API性能指标
   */
  getAPIMetrics(): any {
    return this.apiMonitor.getMetrics();
  }

  /**
   * 获取WebSocket性能指标
   */
  getWebSocketMetrics(): any {
    return this.websocketMonitor.getMetrics();
  }

  /**
   * 获取UI性能指标
   */
  getUIMetrics(): any {
    return this.uiMonitor.getMetrics();
  }

  /**
   * 获取系统性能指标
   */
  getSystemMetrics(): any {
    return this.systemMonitor.getMetrics();
  }

  /**
   * 获取指标摘要
   */
  getMetricsSummary(): any {
    const apiMetrics = this.apiMonitor.getMetrics();
    const websocketMetrics = this.websocketMonitor.getMetrics();
    const uiMetrics = this.uiMonitor.getMetrics();
    const systemMetrics = this.systemMonitor.getMetrics();
    
    return {
      api: {
        totalRequests: apiMetrics.totalRequests,
        successRate: apiMetrics.totalRequests > 0 ? 
          (apiMetrics.successfulRequests / apiMetrics.totalRequests * 100).toFixed(2) + '%' : '0%',
        averageResponseTime: apiMetrics.averageResponseTime.toFixed(2) + 'ms'
      },
      websocket: {
        connections: websocketMetrics.connections,
        reconnections: websocketMetrics.reconnections,
        averageLatency: websocketMetrics.averageLatency + 'ms'
      },
      ui: {
        memoryUsage: (uiMetrics.memoryUsage / 1024 / 1024).toFixed(2) + 'MB',
        componentRenderCount: uiMetrics.componentRenderCount
      },
      system: {
        networkStatus: systemMetrics.networkStatus,
        connectionType: systemMetrics.connectionType
      }
    };
  }

  /**
   * 获取详细指标
   */
  getDetailedMetrics(): any {
    return {
      api: this.apiMonitor.getDetailedMetrics(),
      websocket: this.websocketMonitor.getDetailedMetrics(),
      ui: this.uiMonitor.getDetailedMetrics(),
      system: this.systemMonitor.getDetailedMetrics()
    };
  }

  /**
   * 获取警报
   */
  getAlerts(severity: string | null = null): Alert[] {
    if (severity) {
      return this.alerts.filter(alert => alert.severity === severity);
    }
    return [...this.alerts];
  }

  /**
   * 清除警报
   */
  clearAlerts(): void {
    this.alerts = [];
  }

  /**
   * 生成性能报告
   */
  generateReport(): PerformanceReport {
    const report: PerformanceReport = {
      timestamp: new Date().toISOString(),
      summary: this.getMetricsSummary(),
      details: this.getDetailedMetrics(),
      alerts: this.getAlerts(),
      recommendations: this.generateRecommendations()
    };
    
    return report;
  }

  /**
   * 生成优化建议
   */
  generateRecommendations(): Recommendation[] {
    const recommendations: Recommendation[] = [];
    const { api, ui, websocket } = this.metrics;
    
    // API优化建议
    if (api.averageResponseTime > 3000) {
      recommendations.push({
        type: 'api',
        priority: 'high',
        message: '考虑启用请求缓存或优化后端响应时间'
      });
    }
    
    if (api.totalRequests > 0 && api.failedRequests / api.totalRequests > 0.05) {
      recommendations.push({
        type: 'api',
        priority: 'medium',
        message: '检查网络连接稳定性和错误处理机制'
      });
    }
    
    // UI优化建议
    if (ui.memoryUsage && ui.memoryUsage > 50 * 1024 * 1024) {
      recommendations.push({
        type: 'ui',
        priority: 'medium',
        message: '考虑优化内存使用，清理不必要的数据缓存'
      });
    }
    
    // WebSocket优化建议
    if (websocket.reconnectCount > 5) {
      recommendations.push({
        type: 'websocket',
        priority: 'medium',
        message: '检查WebSocket连接稳定性，可能需要优化重连策略'
      });
    }
    
    return recommendations;
  }

  /**
   * 重置指标
   */
  resetMetrics(): void {
    this.apiMonitor.reset();
    this.websocketMonitor.reset();
    this.uiMonitor.reset();
    this.systemMonitor.reset();
    
    this.clearAlerts();
    console.log('[性能监控] 指标已重置');
  }

  /**
   * 销毁监控器
   */
  destroy(): void {
    this.stopMonitoring();
    
    // 销毁各个监控模块
    this.apiMonitor.destroy();
    this.websocketMonitor.destroy();
    this.uiMonitor.destroy();
    this.systemMonitor.destroy();
    
    // 清理观察者
    this.observers.forEach(observer => {
      try {
        observer.disconnect();
      } catch (error) {
        console.warn('[性能监控] 清理观察者失败:', error);
      }
    });
    
    this.observers = [];
    this.alerts = [];
    
    console.log('[性能监控] 已销毁');
  }
}

// 创建全局实例
const performanceMonitor = new PerformanceMonitor();

export { PerformanceMonitor, performanceMonitor };
export default performanceMonitor;

// 导出类型
export type {
  APIMetrics,
  WebSocketMetrics,
  UIMetrics,
  SystemMetrics,
  PerformanceMetrics,
  Alert,
  Thresholds,
  Recommendation,
  PerformanceReport
};