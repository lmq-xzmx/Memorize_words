/**
 * UI性能监控模块
 * 负责用户界面相关的性能指标收集和分析
 */

// 渲染时间记录接口
interface RenderTimeEntry {
  type: string;
  startTime: number;
  size?: number;
  timestamp: number;
}

// 交互延迟记录接口
interface InteractionLatencyEntry {
  type: 'click' | 'input' | 'keyboard';
  latency: number;
  key?: string;
  timestamp: number;
}

// 滚动性能记录接口
interface ScrollPerformanceEntry {
  duration: number;
  timestamp: number;
}

// 动画帧记录接口
interface AnimationFrameEntry {
  fps: number;
  frameCount: number;
  duration: number;
  timestamp: number;
}

// DOM变化记录接口
interface DOMMutationEntry {
  mutationCount: number;
  addedNodes: number;
  removedNodes: number;
  timestamp: number;
}

// 点击事件记录接口
interface ClickEventEntry {
  target: string;
  className: string;
  responseTime: number;
  timestamp: number;
}

// 输入事件记录接口
interface InputEventEntry {
  type: string;
  tagName: string;
  responseTime: number;
  timestamp: number;
}

// UI指标接口
interface UIMetrics {
  renderTime: RenderTimeEntry[];
  interactionLatency: InteractionLatencyEntry[];
  scrollPerformance: ScrollPerformanceEntry[];
  animationFrames: AnimationFrameEntry[];
  domMutations: DOMMutationEntry[];
  clickEvents: ClickEventEntry[];
  inputEvents: InputEventEntry[];
}

// 渲染统计接口
interface RenderStats {
  totalRenders: number;
  averageRenderTime: number;
  lastRenderTime: number;
}

// 交互统计接口
interface InteractionStats {
  totalInteractions: number;
  averageLatency: number;
  maxLatency: number;
  clickCount: number;
  inputCount: number;
}

// 滚动统计接口
interface ScrollStats {
  totalScrolls: number;
  averageDuration: number;
  maxDuration: number;
}

// 动画统计接口
interface AnimationStats {
  currentFPS: number;
  averageFPS: number;
  minFPS: number;
  frameDrops: number;
}

// DOM统计接口
interface DOMStats {
  totalMutations: number;
  totalAddedNodes: number;
  totalRemovedNodes: number;
  mutationEvents: number;
}

// UI指标报告接口
interface UIMetricsReport extends UIMetrics {
  renderStats: RenderStats | null;
  interactionStats: InteractionStats | null;
  scrollStats: ScrollStats | null;
  animationStats: AnimationStats | null;
  domStats: DOMStats | null;
}

export class UIMonitor {
  private metrics: UIMetrics;
  private maxHistorySize: number;
  private observers: (PerformanceObserver | MutationObserver)[];
  private isMonitoring: boolean;

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
  private initializeMonitoring(): void {
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
  private setupRenderMonitoring(): void {
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          Array.from(list.getEntries()).forEach(entry => {
            if (entry.entryType === 'paint') {
              this.recordPaintTiming(entry);
            } else if (entry.entryType === 'largest-contentful-paint') {
              this.recordLCPTiming(entry as PerformanceEntry & { size: number });
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
  private setupInteractionMonitoring(): void {
    // 监听点击事件
    document.addEventListener('click', (event: MouseEvent) => {
      this.recordClickEvent(event);
    }, { passive: true });
    
    // 监听输入事件
    document.addEventListener('input', (event: Event) => {
      this.recordInputEvent(event);
    }, { passive: true });
    
    // 监听键盘事件
    document.addEventListener('keydown', (event: KeyboardEvent) => {
      this.recordKeyboardEvent(event);
    }, { passive: true });
  }

  /**
   * 设置滚动监控
   */
  private setupScrollMonitoring(): void {
    let scrollStartTime: number | null = null;
    let isScrolling = false;
    
    document.addEventListener('scroll', () => {
      if (!isScrolling) {
        scrollStartTime = performance.now();
        isScrolling = true;
      }
    }, { passive: true });
    
    // 使用防抖来检测滚动结束
    let scrollTimeout: NodeJS.Timeout;
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
  private setupDOMMonitoring(): void {
    if ('MutationObserver' in window) {
      const observer = new MutationObserver((mutations: MutationRecord[]) => {
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
  private setupAnimationMonitoring(): void {
    let frameCount = 0;
    let lastTime = performance.now();
    
    const measureFrameRate = (): void => {
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
  private recordPaintTiming(entry: PerformanceEntry): void {
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
  private recordLCPTiming(entry: PerformanceEntry & { size: number }): void {
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
  private recordClickEvent(event: MouseEvent): void {
    const startTime = performance.now();
    
    // 使用requestAnimationFrame来测量响应时间
    requestAnimationFrame(() => {
      const responseTime = performance.now() - startTime;
      const target = event.target as HTMLElement;
      
      this.metrics.clickEvents.push({
        target: target.tagName,
        className: target.className,
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
  private recordInputEvent(event: Event): void {
    const startTime = performance.now();
    
    requestAnimationFrame(() => {
      const responseTime = performance.now() - startTime;
      const target = event.target as HTMLInputElement;
      
      this.metrics.inputEvents.push({
        type: target.type || 'unknown',
        tagName: target.tagName,
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
  private recordKeyboardEvent(event: KeyboardEvent): void {
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
  private recordScrollPerformance(duration: number): void {
    this.metrics.scrollPerformance.push({
      duration,
      timestamp: Date.now()
    });
    
    this.limitHistorySize(this.metrics.scrollPerformance);
  }

  /**
   * 记录DOM变化
   */
  private recordDOMMutations(mutations: MutationRecord[]): void {
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
  private recordAnimationFrame(frameCount: number, duration: number): void {
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
  private limitHistorySize(history: any[]): void {
    if (history.length > this.maxHistorySize) {
      history.splice(0, history.length - this.maxHistorySize);
    }
  }

  /**
   * 获取UI性能指标
   */
  public getMetrics(): UIMetricsReport {
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
  public getRenderStats(): RenderStats | null {
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
  public getInteractionStats(): InteractionStats | null {
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
  public getScrollStats(): ScrollStats | null {
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
  public getAnimationStats(): AnimationStats | null {
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
  public getDOMStats(): DOMStats | null {
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
  public reset(): void {
    Object.keys(this.metrics).forEach(key => {
      (this.metrics as any)[key] = [];
    });
  }

  /**
   * 清理过期数据
   */
  public cleanup(maxAge: number = 10 * 60 * 1000): void { // 默认10分钟
    const cutoff = Date.now() - maxAge;
    
    Object.keys(this.metrics).forEach(key => {
      const metricArray = (this.metrics as any)[key];
      if (Array.isArray(metricArray)) {
        (this.metrics as any)[key] = metricArray.filter(
          (entry: any) => entry.timestamp > cutoff
        );
      }
    });
  }

  /**
   * 停止监控
   */
  public stopMonitoring(): void {
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
  public destroy(): void {
    this.stopMonitoring();
    this.reset();
  }
}

// 导出类型
export type {
  RenderTimeEntry,
  InteractionLatencyEntry,
  ScrollPerformanceEntry,
  AnimationFrameEntry,
  DOMMutationEntry,
  ClickEventEntry,
  InputEventEntry,
  UIMetrics,
  RenderStats,
  InteractionStats,
  ScrollStats,
  AnimationStats,
  DOMStats,
  UIMetricsReport
};

// 导出实例
export const uiMonitor = new UIMonitor();