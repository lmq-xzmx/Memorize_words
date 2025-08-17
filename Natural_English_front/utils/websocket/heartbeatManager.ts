/**
 * WebSocket心跳管理模块
 * 负责心跳发送、接收和连接质量监控
 */

import globalErrorHandler from '../globalErrorHandler';
import type { ConnectionManager } from './connectionManager';

// 接口定义
interface ConnectionQuality {
  latency: number;
  lastPongTime: number;
  missedPongs: number;
  maxMissedPongs: number;
  isStable: boolean;
  lastPingAt?: number;
  lastPongAt?: number;
}

interface PongData {
  timestamp?: number;
  [key: string]: any;
}

export class HeartbeatManager {
  private connectionManager: ConnectionManager;
  private heartbeatInterval: number = 25000; // 心跳间隔25秒
  private heartbeatTimer: number | null = null;
  
  // 连接质量监控
  private connectionQuality: ConnectionQuality;

  constructor(connectionManager: ConnectionManager) {
    this.connectionManager = connectionManager;
    
    this.connectionQuality = {
      latency: 0,
      lastPongTime: 0,
      missedPongs: 0,
      maxMissedPongs: 3,
      isStable: true,
      lastPingAt: 0,
      lastPongAt: 0
    };
    
    // 绑定方法上下文
    this.sendHeartbeat = this.sendHeartbeat.bind(this);
  }

  /**
   * 开始心跳
   */
  start(): void {
    this.heartbeatTimer = window.setInterval(this.sendHeartbeat, this.heartbeatInterval);
  }

  /**
   * 停止心跳
   */
  stop(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  /**
   * 发送心跳
   */
  private sendHeartbeat(): void {
    if (!this.connectionManager.isConnected) {
      return;
    }

    // 检查是否有太多未响应的心跳
    if (this.connectionQuality.missedPongs >= this.connectionQuality.maxMissedPongs) {
      console.warn('[WebSocket] 心跳超时过多，主动断开连接');
      this.connectionManager.disconnect();
      return;
    }

    try {
      const pingTime = Date.now();
      const success = this.connectionManager.send({
        type: 'ping',
        timestamp: pingTime
      });

      if (success) {
        this.connectionQuality.missedPongs++;
        console.log('[WebSocket] 心跳已发送');
      } else {
        console.error('[WebSocket] 心跳发送失败');
      }
    } catch (error) {
      console.error('[WebSocket] 心跳发送异常:', error);
      globalErrorHandler.handleWebSocketError(error as any);
    }
  }

  /**
   * 处理pong消息
   */
  handlePong(data: PongData): void {
    const now = Date.now();
    
    if (data.timestamp) {
      // 计算延迟
      this.connectionQuality.latency = now - data.timestamp;
    }
    
    // 更新连接质量指标
    this.connectionQuality.lastPongTime = now;
    this.connectionQuality.missedPongs = Math.max(0, this.connectionQuality.missedPongs - 1);
    
    console.log('[WebSocket] 收到pong，延迟:', this.connectionQuality.latency + 'ms');
  }

  /**
   * 获取连接质量信息
   */
  getConnectionQuality(): ConnectionQuality {
    return {
      latency: this.connectionQuality.latency,
      lastPongTime: this.connectionQuality.lastPongTime,
      missedPongs: this.connectionQuality.missedPongs,
      maxMissedPongs: this.connectionQuality.maxMissedPongs,
      isStable: this.connectionQuality.isStable,
      lastPingAt: this.connectionQuality.lastPingAt,
      lastPongAt: this.connectionQuality.lastPongAt
    };
  }

  /**
   * 重置连接质量指标
   */
  resetQuality(): void {
    this.connectionQuality.latency = 0;
    this.connectionQuality.lastPongTime = 0;
    this.connectionQuality.missedPongs = 0;
  }

  /**
   * 清理资源
   */
  destroy(): void {
    this.stop();
    this.resetQuality();
  }
}

export type { ConnectionQuality, PongData };