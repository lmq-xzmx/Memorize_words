/**
 * Django后台权限管理系统集成模块 - TypeScript版本
 * 提供与Django Admin后台的完整集成功能
 */

// 环境变量类型声明
// 使用any类型处理import.meta以避免TypeScript声明问题
const importMeta: any = {
  env: {
    VITE_DJANGO_ADMIN_URL: process.env.VITE_DJANGO_ADMIN_URL,
    VITE_DJANGO_WS_URL: process.env.VITE_DJANGO_WS_URL
  }
};

// 类型定义
interface DjangoConfig {
  baseURL: string;
  apiEndpoints: {
    permissions: string;
    roles: string;
    frontendFunctions: string;
    permissionMatrix: string;
    learningModePermissions: string;
    configSync: string;
    configExport: string;
    configImport: string;
    versionManagement: string;
  };
  headers: {
    'Content-Type': string;
    'X-Requested-With': string;
  };
}

interface Permission {
  id: string | number;
  name: string;
  codename: string;
  content_type?: string;
}

interface Role {
  id: string | number;
  name: string;
  permissions: Permission[];
}

interface FrontendFunction {
  id?: string | number;
  name: string;
  path: string;
  component: string;
  permissions: string[];
}

interface PermissionMatrix {
  roles: Role[];
  permissions: Permission[];
  matrix: Record<string, string[]>;
}

interface VersionData {
  name: string;
  description?: string;
  config: any;
}

interface WebSocketMessage {
  type: string;
  payload?: any;
  userId?: string | number;
  timestamp?: number;
}

interface RequestOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: string;
  credentials?: RequestCredentials;
}

interface UserData {
  id?: string | number;
  user_id?: string | number;
  username?: string;
  role?: string;
}

// Django后台API配置
const DJANGO_CONFIG: DjangoConfig = {
  baseURL: importMeta.env.VITE_DJANGO_ADMIN_URL || 'http://localhost:8000/admin',
  apiEndpoints: {
    permissions: '/api/permissions/',
    roles: '/api/roles/',
    frontendFunctions: '/api/frontend-functions/',
    permissionMatrix: '/api/permission-matrix/',
    learningModePermissions: '/api/learning-mode-permissions/',
    configSync: '/api/permission-config-sync/',
    configExport: '/api/permission-config-export/',
    configImport: '/api/permission-config-import/',
    versionManagement: '/api/permission-versions/'
  },
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
};

/**
 * Django权限管理API客户端
 */
class DjangoPermissionAPI {
  private baseURL: string;
  private endpoints: DjangoConfig['apiEndpoints'];

  constructor() {
    this.baseURL = DJANGO_CONFIG.baseURL;
    this.endpoints = DJANGO_CONFIG.apiEndpoints;
  }

  /**
   * 获取CSRF Token
   */
  async getCSRFToken(): Promise<string | null> {
    try {
      const response = await fetch(`${this.baseURL}/csrf-token/`);
      const data = await response.json();
      return data.csrf_token;
    } catch (error) {
      console.error('获取CSRF Token失败:', error);
      return null;
    }
  }

  /**
   * 发送API请求
   */
  async request(endpoint: string, options: RequestOptions = {}): Promise<any> {
    const csrfToken = await this.getCSRFToken();
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        ...DJANGO_CONFIG.headers,
        'X-CSRFToken': csrfToken || ''
      },
      credentials: 'include'
    };

    const finalOptions: RequestInit = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers
      }
    };

    try {
      const response = await fetch(url, finalOptions);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API请求失败 [${endpoint}]:`, error);
      throw error;
    }
  }

  /**
   * 获取所有权限
   */
  async getPermissions(): Promise<Permission[]> {
    return await this.request(this.endpoints.permissions);
  }

  /**
   * 获取所有角色
   */
  async getRoles(): Promise<Role[]> {
    return await this.request(this.endpoints.roles);
  }

  /**
   * 获取前台功能列表
   */
  async getFrontendFunctions(): Promise<FrontendFunction[]> {
    return await this.request(this.endpoints.frontendFunctions);
  }

  /**
   * 获取权限矩阵
   */
  async getPermissionMatrix(): Promise<PermissionMatrix> {
    return await this.request(this.endpoints.permissionMatrix);
  }

  /**
   * 更新角色权限
   */
  async updateRolePermissions(roleId: string | number, permissions: string[]): Promise<any> {
    return await this.request(`${this.endpoints.roles}${roleId}/permissions/`, {
      method: 'POST',
      body: JSON.stringify({ permissions })
    });
  }

  /**
   * 注册前台功能
   */
  async registerFrontendFunction(functionData: FrontendFunction): Promise<any> {
    return await this.request(this.endpoints.frontendFunctions, {
      method: 'POST',
      body: JSON.stringify(functionData)
    });
  }

  /**
   * 同步权限配置
   */
  async syncPermissionConfig(): Promise<any> {
    return await this.request(this.endpoints.configSync);
  }

  /**
   * 导出权限配置
   */
  async exportPermissionConfig(): Promise<any> {
    return await this.request(this.endpoints.configExport);
  }

  /**
   * 导入权限配置
   */
  async importPermissionConfig(configData: any): Promise<any> {
    return await this.request(this.endpoints.configImport, {
      method: 'POST',
      body: JSON.stringify(configData)
    });
  }

  /**
   * 获取权限配置版本列表
   */
  async getPermissionVersions(): Promise<any[]> {
    return await this.request(this.endpoints.versionManagement);
  }

  /**
   * 创建权限配置版本
   */
  async createPermissionVersion(versionData: VersionData): Promise<any> {
    return await this.request(this.endpoints.versionManagement, {
      method: 'POST',
      body: JSON.stringify(versionData)
    });
  }

  /**
   * 回滚到指定版本
   */
  async rollbackToVersion(versionId: string | number): Promise<any> {
    return await this.request(`${this.endpoints.versionManagement}${versionId}/rollback/`, {
      method: 'POST'
    });
  }
}

/**
 * Django后台集成管理器
 */
class DjangoBackendIntegration {
  private api: DjangoPermissionAPI;
  private syncInterval: any = null;
  private websocket: WebSocket | null = null;
  private reconnectAttempts: number = 0;

  constructor() {
    this.api = new DjangoPermissionAPI();
  }

  /**
   * 初始化后端集成
   */
  async initialize(): Promise<void> {
    try {
      // 同步权限配置
      await this.syncPermissionConfig();
      
      // 建立WebSocket连接
      this.setupWebSocket();
      
      // 设置定期同步
      this.startPeriodicSync();
      
      console.log('Django后台集成初始化成功');
    } catch (error) {
      console.error('Django后台集成初始化失败:', error);
    }
  }

  /**
   * 同步权限配置
   */
  async syncPermissionConfig(): Promise<any> {
    try {
      const config = await this.api.syncPermissionConfig();
      
      // 更新本地权限缓存
      if ((window as any).permissionCache) {
        (window as any).permissionCache.updateFromBackend(config);
      }
      
      return config;
    } catch (error) {
      console.error('权限配置同步失败:', error);
      throw error;
    }
  }

  /**
   * 设置WebSocket连接
   */
  setupWebSocket(): void {
    const wsURL = importMeta.env.VITE_DJANGO_WS_URL || 'ws://127.0.0.1:8000/ws/permissions/';
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (!token || !user) {
      console.warn('Django WebSocket连接失败：缺少认证信息');
      return;
    }
    
    try {
      let userData: UserData;
      try {
        userData = JSON.parse(user);
      } catch (e) {
        console.error('用户数据解析失败:', e);
        return;
      }
      
      const wsUrlWithAuth = `${wsURL}?token=${token}&userId=${userData.id || userData.user_id}`;
      console.log('正在连接Django WebSocket:', wsUrlWithAuth);
      
      this.websocket = new WebSocket(wsUrlWithAuth);
      
      this.websocket.onopen = () => {
        console.log('权限同步WebSocket连接已建立');
        // 发送认证确认
        if (this.websocket) {
          this.websocket.send(JSON.stringify({
            type: 'auth_confirm',
            userId: userData.id || userData.user_id,
            timestamp: Date.now()
          }));
        }
      };
      
      this.websocket.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);
          console.log('收到Django WebSocket消息:', data);
          this.handleWebSocketMessage(data);
        } catch (error: any) {
          console.error('WebSocket消息解析错误:', error);
        }
      };
      
      this.websocket.onclose = (event) => {
        console.log('权限同步WebSocket连接已关闭，代码:', event.code);
        // 增加重连延迟
        const delay = Math.min(5000 * Math.pow(2, this.reconnectAttempts), 30000);
        setTimeout(() => {
          if (this.reconnectAttempts < 5) {
            this.reconnectAttempts += 1;
            this.setupWebSocket();
          }
        }, delay);
      };
      
      this.websocket.onerror = (error) => {
        console.error('权限同步WebSocket错误:', error);
      };
    } catch (error) {
      console.error('WebSocket连接失败:', error);
    }
  }

  /**
   * 处理WebSocket消息
   */
  handleWebSocketMessage(data: WebSocketMessage): void {
    switch (data.type) {
      case 'permission_updated':
        this.handlePermissionUpdate(data.payload);
        break;
      case 'role_updated':
        this.handleRoleUpdate(data.payload);
        break;
      case 'config_changed':
        this.syncPermissionConfig();
        break;
      default:
        console.log('未知的WebSocket消息类型:', data.type);
    }
  }

  /**
   * 处理权限更新
   */
  handlePermissionUpdate(payload: any): void {
    if ((window as any).permissionCache) {
      (window as any).permissionCache.updatePermission(payload.permission);
    }
    
    // 触发权限更新事件
    window.dispatchEvent(new CustomEvent('permissionUpdated', {
      detail: payload
    }));
  }

  /**
   * 处理角色更新
   */
  handleRoleUpdate(payload: any): void {
    if ((window as any).permissionCache) {
      (window as any).permissionCache.updateRole(payload.role);
    }
    
    // 触发角色更新事件
    window.dispatchEvent(new CustomEvent('roleUpdated', {
      detail: payload
    }));
  }

  /**
   * 开始定期同步
   */
  startPeriodicSync(): void {
    // 每5分钟同步一次
    this.syncInterval = setInterval(() => {
      this.syncPermissionConfig();
    }, 5 * 60 * 1000);
  }

  /**
   * 停止定期同步
   */
  stopPeriodicSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  /**
   * 销毁集成
   */
  destroy(): void {
    this.stopPeriodicSync();
    
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }
}

// 创建全局实例
const djangoBackendIntegration = new DjangoBackendIntegration();

export {
  DjangoPermissionAPI,
  DjangoBackendIntegration,
  djangoBackendIntegration,
  DJANGO_CONFIG
};

export type {
  DjangoConfig,
  Permission,
  Role,
  FrontendFunction,
  PermissionMatrix,
  VersionData,
  WebSocketMessage,
  RequestOptions,
  UserData
};

export default djangoBackendIntegration;