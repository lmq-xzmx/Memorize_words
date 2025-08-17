/**
 * 系统性能监控模块
 * 负责系统级别的性能指标收集和分析
 */

// 设备信息接口
interface DeviceInfo {
  userAgent: string;
  platform: string;
  language: string;
  cookieEnabled: boolean;
  onLine: boolean;
  hardwareConcurrency: number | string;
  maxTouchPoints: number;
  screen: {
    width: number;
    height: number;
    colorDepth: number;
    pixelDepth: number;
  };
  viewport: {
    width: number;
    height: number;
  };
}

// 内存使用信息接口
interface MemoryUsage {
  used: number;
  total: number;
  limit: number;
  percentage: number;
  timestamp: number;
}

// 电池信息接口
interface BatteryInfo {
  level: number;
  charging: boolean;
  chargingTime: number;
  dischargingTime: number;
  timestamp: number;
}

// 性能条目接口
interface PerformanceEntry {
  type: string;
  timestamp: number;
  [key: string]: any;
}

// 网络性能条目接口
interface NetworkPerformanceEntry extends PerformanceEntry {
  type: 'network';
  status: string;
}

// 连接性能条目接口
interface ConnectionPerformanceEntry extends PerformanceEntry {
  type: 'connection';
  effectiveType: string;
  downlink: number;
  rtt: number;
}

// 导航性能条目接口
interface NavigationPerformanceEntry extends PerformanceEntry {
  type: 'navigation';
  loadTime: number;
  domContentLoaded: number;
  firstPaint: number;
}

// 自定义性能条目接口
interface CustomPerformanceEntry extends PerformanceEntry {
  type: 'measure' | 'mark';
  name: string;
  duration: number;
}

// 资源时间记录接口
interface ResourceTiming {
  name: string;
  duration: number;
  size: number;
  type: string;
  timestamp: number;
}

// 资源统计接口
interface ResourceStats {
  totalResources: number;
  totalSize: number;
  averageDuration: number;
  slowestResource: number;
}

// 性能统计接口
interface PerformanceStats {
  pageLoadTime: number;
  domContentLoadedTime: number;
  firstPaintTime: number;
}

// 系统指标接口
interface SystemMetrics {
  memoryUsage: MemoryUsage | number;
  networkStatus: string;
  batteryLevel: BatteryInfo | null;
  connectionType: string;
  deviceInfo: DeviceInfo | {};
  performanceEntries: PerformanceEntry[];
  resourceTiming: ResourceTiming[];
}

// 系统指标报告接口
interface SystemMetricsReport extends SystemMetrics {
  resourceStats: ResourceStats | null;
  performanceStats: PerformanceStats | null;
}

// 扩展Navigator接口
declare global {
  interface Navigator {
    connection?: {
      effectiveType?: string;
      downlink?: number;
      rtt?: number;
      addEventListener(type: string, listener: EventListener): void;
    };
    getBattery?: () => Promise<{
      level: number;
      charging: boolean;
      chargingTime: number;
      dischargingTime: number;
      addEventListener(type: string, listener: EventListener): void;
    }>;
  }

  interface Performance {
    memory?: {
      usedJSHeapSize: number;
      totalJSHeapSize: number;
      jsHeapSizeLimit: number;
    };
  }
}

export class SystemMonitor {
  private metrics: SystemMetrics;
  private maxHistorySize: number;
  private monitoringInterval: NodeJS.Timeout | null;

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
  private initializeMonitoring(): void {
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
  private detectDeviceInfo(): void {
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
  private setupNetworkMonitoring(): void {
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
    if ('connection' in navigator && navigator.connection) {
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
  private setupBatteryMonitoring(): void {
    if ('getBattery' in navigator && navigator.getBattery) {
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
  private setupPerformanceMonitoring(): void {
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
  private startPeriodicMonitoring(): void {
    this.monitoringInterval = setInterval(() => {
      this.updateMemoryUsage();
      this.updatePerformanceMetrics();
    }, 30000); // 每30秒更新一次
  }

  /**
   * 停止定期监控
   */
  private stopPeriodicMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }

  /**
   * 更新内存使用情况
   */
  private updateMemoryUsage(): void {
    if ('memory' in performance && performance.memory) {
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
  private updatePerformanceMetrics(): void {
    if ('performance' in window) {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (navigation) {
        this.recordNavigationTiming(navigation);
      }
    }
  }

  /**
   * 更新电池信息
   */
  private updateBatteryInfo(battery: any): void {
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
  private recordNetworkChange(status: string): void {
    const entry: NetworkPerformanceEntry = {
      type: 'network',
      status,
      timestamp: Date.now()
    };
    
    this.metrics.performanceEntries.push(entry);
    this.limitHistorySize(this.metrics.performanceEntries);
  }

  /**
   * 记录连接变化
   */
  private recordConnectionChange(connection: any): void {
    const entry: ConnectionPerformanceEntry = {
      type: 'connection',
      effectiveType: connection.effectiveType,
      downlink: connection.downlink,
      rtt: connection.rtt,
      timestamp: Date.now()
    };
    
    this.metrics.performanceEntries.push(entry);
    this.limitHistorySize(this.metrics.performanceEntries);
  }

  /**
   * 记录导航时间
   */
  private recordNavigationTiming(navigation: PerformanceNavigationTiming): void {
    const entry: NavigationPerformanceEntry = {
      type: 'navigation',
      loadTime: navigation.loadEventEnd - navigation.fetchStart,
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.fetchStart,
      firstPaint: navigation.responseEnd - navigation.requestStart,
      timestamp: Date.now()
    };
    
    this.metrics.performanceEntries.push(entry);
    this.limitHistorySize(this.metrics.performanceEntries);
  }

  /**
   * 处理性能条目
   */
  private processPerformanceEntries(entries: PerformanceEntryList): void {
    Array.from(entries).forEach(entry => {
      if (entry.entryType === 'resource') {
        this.recordResourceTiming(entry as unknown as PerformanceResourceTiming);
      } else if (entry.entryType === 'measure' || entry.entryType === 'mark') {
        this.recordCustomTiming(entry);
      }
    });
  }

  /**
   * 记录资源时间
   */
  private recordResourceTiming(entry: PerformanceResourceTiming): void {
    const resourceEntry: ResourceTiming = {
      name: entry.name,
      duration: entry.duration,
      size: entry.transferSize || 0,
      type: entry.initiatorType,
      timestamp: Date.now()
    };
    
    this.metrics.resourceTiming.push(resourceEntry);
    this.limitHistorySize(this.metrics.resourceTiming);
  }

  /**
   * 记录自定义时间
   */
  private recordCustomTiming(entry: globalThis.PerformanceEntry): void {
    const customEntry: CustomPerformanceEntry = {
      type: entry.entryType as 'measure' | 'mark',
      name: entry.name,
      duration: entry.duration,
      timestamp: Date.now()
    };
    
    this.metrics.performanceEntries.push(customEntry);
    this.limitHistorySize(this.metrics.performanceEntries);
  }

  /**
   * 限制历史记录大小
   */
  private limitHistorySize(history: any[]): void {
    if (history.length > this.maxHistorySize) {
      history.splice(0, history.length - this.maxHistorySize);
    }
  }

  /**
   * 获取系统性能指标
   */
  public getMetrics(): SystemMetricsReport {
    return {
      ...this.metrics,
      resourceStats: this.getResourceStats(),
      performanceStats: this.getPerformanceStats()
    };
  }

  /**
   * 获取资源统计
   */
  public getResourceStats(): ResourceStats | null {
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
  public getPerformanceStats(): PerformanceStats | null {
    const navigationEntries = this.metrics.performanceEntries.filter(
      (entry): entry is NavigationPerformanceEntry => entry.type === 'navigation'
    );
    
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
  public reset(): void {
    this.metrics.performanceEntries = [];
    this.metrics.resourceTiming = [];
    this.metrics.memoryUsage = 0;
  }

  /**
   * 清理过期数据
   */
  public cleanup(maxAge: number = 24 * 60 * 60 * 1000): void { // 默认24小时
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
  public destroy(): void {
    this.stopPeriodicMonitoring();
    this.reset();
  }
}

// 导出类型
export type {
  DeviceInfo,
  MemoryUsage,
  BatteryInfo,
  PerformanceEntry,
  NetworkPerformanceEntry,
  ConnectionPerformanceEntry,
  NavigationPerformanceEntry,
  CustomPerformanceEntry,
  ResourceTiming,
  ResourceStats,
  PerformanceStats,
  SystemMetrics,
  SystemMetricsReport
};

// 导出实例
export const systemMonitor = new SystemMonitor();