/**
 * WebSocket性能监控模块
 * 负责WebSocket连接的性能指标收集和分析
 */

// 连接历史记录接口
interface ConnectionHistoryEntry {
  type: 'connect' | 'reconnect' | 'disconnect';
  timestamp: number;
}

// 延迟历史记录接口
interface LatencyHistoryEntry {
  latency: number;
  timestamp: number;
}

// 消息历史记录接口
interface MessageHistoryEntry {
  type: 'sent' | 'received';
  timestamp: number;
  size: number;
}

// WebSocket指标接口
interface WebSocketMetrics {
  connections: number;
  reconnections: number;
  messagesReceived: number;
  messagesSent: number;
  averageLatency: number;
  connectionUptime: number;
  lastConnectionTime: number | null;
  connectionHistory: ConnectionHistoryEntry[];
  latencyHistory: LatencyHistoryEntry[];
  messageHistory: MessageHistoryEntry[];
}

// 消息吞吐量接口
interface MessageThroughput {
  sent: number;
  received: number;
  total: number;
}

// 最近延迟统计接口
interface RecentLatencyStats {
  min: number;
  max: number;
  average: number;
}

// WebSocket指标报告接口
interface WebSocketMetricsReport extends WebSocketMetrics {
  currentUptime: number;
  connectionStability: number;
  messageThroughput: MessageThroughput;
  recentLatency: RecentLatencyStats | null;
}

// 事件数据接口
interface EventData {
  latency?: number;
  [key: string]: any;
}

export class WebSocketMonitor {
  private metrics: WebSocketMetrics;
  private maxHistorySize: number;
  private connectionStartTime: number | null;

  constructor() {
    this.metrics = {
      connections: 0,
      reconnections: 0,
      messagesReceived: 0,
      messagesSent: 0,
      averageLatency: 0,
      connectionUptime: 0,
      lastConnectionTime: null,
      connectionHistory: [],
      latencyHistory: [],
      messageHistory: []
    };
    
    this.maxHistorySize = 1000;
    this.connectionStartTime = null;
  }

  /**
   * 记录WebSocket事件
   */
  public recordEvent(eventType: string, data: EventData = {}): void {
    const timestamp = Date.now();
    
    switch (eventType) {
      case 'connect':
        this.recordConnection(timestamp);
        break;
      case 'reconnect':
        this.recordReconnection(timestamp);
        break;
      case 'message_sent':
        this.recordMessageSent(timestamp, data);
        break;
      case 'message_received':
        this.recordMessageReceived(timestamp, data);
        break;
      case 'disconnect':
        this.recordDisconnection(timestamp);
        break;
      case 'latency':
        if (data.latency !== undefined) {
          this.recordLatency(timestamp, data.latency);
        }
        break;
    }
  }

  /**
   * 记录连接事件
   */
  private recordConnection(timestamp: number): void {
    this.metrics.connections++;
    this.metrics.lastConnectionTime = timestamp;
    this.connectionStartTime = timestamp;
    
    this.metrics.connectionHistory.push({
      type: 'connect',
      timestamp
    });
    
    this.limitHistorySize(this.metrics.connectionHistory);
  }

  /**
   * 记录重连事件
   */
  private recordReconnection(timestamp: number): void {
    this.metrics.reconnections++;
    this.metrics.lastConnectionTime = timestamp;
    this.connectionStartTime = timestamp;
    
    this.metrics.connectionHistory.push({
      type: 'reconnect',
      timestamp
    });
    
    this.limitHistorySize(this.metrics.connectionHistory);
  }

  /**
   * 记录消息发送
   */
  private recordMessageSent(timestamp: number, data: EventData): void {
    this.metrics.messagesSent++;
    
    this.metrics.messageHistory.push({
      type: 'sent',
      timestamp,
      size: JSON.stringify(data).length
    });
    
    this.limitHistorySize(this.metrics.messageHistory);
  }

  /**
   * 记录消息接收
   */
  private recordMessageReceived(timestamp: number, data: EventData): void {
    this.metrics.messagesReceived++;
    
    this.metrics.messageHistory.push({
      type: 'received',
      timestamp,
      size: JSON.stringify(data).length
    });
    
    this.limitHistorySize(this.metrics.messageHistory);
  }

  /**
   * 记录断开连接
   */
  private recordDisconnection(timestamp: number): void {
    if (this.connectionStartTime) {
      const uptime = timestamp - this.connectionStartTime;
      this.updateConnectionUptime(uptime);
    }
    
    this.metrics.connectionHistory.push({
      type: 'disconnect',
      timestamp
    });
    
    this.limitHistorySize(this.metrics.connectionHistory);
    this.connectionStartTime = null;
  }

  /**
   * 记录延迟
   */
  private recordLatency(timestamp: number, latency: number): void {
    this.metrics.latencyHistory.push({
      latency,
      timestamp
    });
    
    this.limitHistorySize(this.metrics.latencyHistory);
    this.updateAverageLatency();
  }

  /**
   * 更新连接正常运行时间
   */
  private updateConnectionUptime(uptime: number): void {
    // 计算加权平均正常运行时间
    if (this.metrics.connectionUptime === 0) {
      this.metrics.connectionUptime = uptime;
    } else {
      this.metrics.connectionUptime = (this.metrics.connectionUptime + uptime) / 2;
    }
  }

  /**
   * 更新平均延迟
   */
  private updateAverageLatency(): void {
    if (this.metrics.latencyHistory.length === 0) return;
    
    const recentLatencies = this.metrics.latencyHistory.slice(-50); // 最近50个延迟记录
    const sum = recentLatencies.reduce((total, item) => total + item.latency, 0);
    this.metrics.averageLatency = sum / recentLatencies.length;
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
   * 获取当前连接正常运行时间
   */
  public getCurrentUptime(): number {
    if (!this.connectionStartTime) return 0;
    return Date.now() - this.connectionStartTime;
  }

  /**
   * 获取连接稳定性指标
   */
  public getConnectionStability(): number {
    const totalConnections = this.metrics.connections + this.metrics.reconnections;
    if (totalConnections === 0) return 1;
    
    return this.metrics.connections / totalConnections;
  }

  /**
   * 获取消息吞吐量
   */
  public getMessageThroughput(timeWindow: number = 60000): MessageThroughput { // 默认1分钟窗口
    const cutoff = Date.now() - timeWindow;
    
    const recentMessages = this.metrics.messageHistory.filter(
      msg => msg.timestamp > cutoff
    );
    
    const sent = recentMessages.filter(msg => msg.type === 'sent').length;
    const received = recentMessages.filter(msg => msg.type === 'received').length;
    
    return {
      sent: sent / (timeWindow / 1000), // 每秒发送数
      received: received / (timeWindow / 1000), // 每秒接收数
      total: (sent + received) / (timeWindow / 1000)
    };
  }

  /**
   * 获取WebSocket性能指标
   */
  public getMetrics(): WebSocketMetricsReport {
    return {
      ...this.metrics,
      currentUptime: this.getCurrentUptime(),
      connectionStability: this.getConnectionStability(),
      messageThroughput: this.getMessageThroughput(),
      recentLatency: this.getRecentLatency()
    };
  }

  /**
   * 获取最近延迟统计
   */
  public getRecentLatency(count: number = 10): RecentLatencyStats | null {
    const recent = this.metrics.latencyHistory.slice(-count);
    if (recent.length === 0) return null;
    
    const latencies = recent.map(item => item.latency);
    return {
      min: Math.min(...latencies),
      max: Math.max(...latencies),
      average: latencies.reduce((sum, lat) => sum + lat, 0) / latencies.length
    };
  }

  /**
   * 重置统计数据
   */
  public reset(): void {
    this.metrics = {
      connections: 0,
      reconnections: 0,
      messagesReceived: 0,
      messagesSent: 0,
      averageLatency: 0,
      connectionUptime: 0,
      lastConnectionTime: null,
      connectionHistory: [],
      latencyHistory: [],
      messageHistory: []
    };
    this.connectionStartTime = null;
  }

  /**
   * 清理过期数据
   */
  public cleanup(maxAge: number = 24 * 60 * 60 * 1000): void { // 默认24小时
    const cutoff = Date.now() - maxAge;
    
    this.metrics.connectionHistory = this.metrics.connectionHistory.filter(
      item => item.timestamp > cutoff
    );
    
    this.metrics.latencyHistory = this.metrics.latencyHistory.filter(
      item => item.timestamp > cutoff
    );
    
    this.metrics.messageHistory = this.metrics.messageHistory.filter(
      item => item.timestamp > cutoff
    );
  }
}

// 导出类型
export type {
  ConnectionHistoryEntry,
  LatencyHistoryEntry,
  MessageHistoryEntry,
  WebSocketMetrics,
  MessageThroughput,
  RecentLatencyStats,
  WebSocketMetricsReport,
  EventData
};

// 导出实例
export const websocketMonitor = new WebSocketMonitor();