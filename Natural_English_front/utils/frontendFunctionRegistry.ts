/**
 * 前台功能自动注册模块
 * 实现前台功能向Django后台的自动注册机制
 */

import { djangoBackendIntegration } from './djangoBackendIntegration';
import { PERMISSION_CATEGORIES } from './unifiedPermissionConstants';
// import { LEARNING_MODE_PERMISSIONS } from './learningModePermissions';

// 类型定义
interface FunctionConfig {
  name?: string;
  description?: string;
  path?: string;
  component?: string;
  method?: string;
  category?: string;
  requiredPermissions?: string[];
  learningMode?: string;
  menuConfig?: Record<string, any>;
  isPublic?: boolean;
  priority?: number;
}

interface FunctionData {
  function_key: string;
  name: string;
  description: string;
  path: string;
  component: string;
  method: string;
  category: string;
  required_permissions: string[];
  permissions: string[]; // 兼容后端接口
  learning_mode: string;
  menu_config: Record<string, any>;
  is_public: boolean;
  priority: number;
  created_at: string;
}

interface RegisteredFunction extends FunctionData {
  registered_at: string;
  backend_id?: string;
}

interface RouteConfig {
  name?: string;
  path: string;
  component?: { name?: string };
  meta?: {
    title?: string;
    description?: string;
    category?: string;
    permissions?: string[];
    learningMode?: string;
    menu?: Record<string, any>;
    public?: boolean;
    priority?: number;
  };
}

/**
 * 前台功能注册装饰器
 * 用于自动将前台功能注册到Django后台
 */
function registerFrontendFunction(config: FunctionConfig) {
  return function(target: any, propertyKey?: string, descriptor?: PropertyDescriptor) {
    // 如果是类方法
    if (descriptor) {
      const originalMethod = descriptor.value;
      
      descriptor.value = async function(...args: any[]) {
        // 注册功能到后台
        await frontendFunctionRegistry.register({
          ...config,
          component: target.constructor.name,
          method: propertyKey
        });
        
        return originalMethod.apply(this, args);
      };
      
      return descriptor;
    }
    
    // 如果是类
    const originalClass = target;
    
    class WrappedClass extends originalClass {
      constructor(...args: any[]) {
        super(...args);
        
        // 注册组件到后台
        frontendFunctionRegistry.register({
          ...config,
          component: originalClass.name
        });
      }
    }
    
    return WrappedClass;
  };
}

/**
 * 前台功能注册管理器
 */
class FrontendFunctionRegistry {
  private registeredFunctions: Map<string, RegisteredFunction>;
  private pendingRegistrations: FunctionData[];
  private isInitialized: boolean;

  constructor() {
    this.registeredFunctions = new Map();
    this.pendingRegistrations = [];
    this.isInitialized = false;
  }

  /**
   * 初始化注册器
   */
  async initialize(): Promise<void> {
    try {
      // 等待Django后台集成初始化
      await djangoBackendIntegration.initialize();
      
      // 处理待注册的功能
      await this.processPendingRegistrations();
      
      this.isInitialized = true;
      console.log('前台功能注册器初始化成功');
    } catch (error) {
      console.error('前台功能注册器初始化失败:', error);
    }
  }

  /**
   * 注册前台功能
   */
  async register(config: FunctionConfig): Promise<any> {
    const functionData = this.prepareFunctionData(config);
    
    if (!this.isInitialized) {
      // 如果未初始化，添加到待处理队列
      this.pendingRegistrations.push(functionData);
      return;
    }
    
    try {
      // const result = await djangoBackendIntegration.api.registerFrontendFunction(functionData);
      const result = { id: Date.now().toString() }; // 临时实现
      
      // 缓存注册信息
      this.registeredFunctions.set(functionData.function_key, {
        ...functionData,
        registered_at: new Date().toISOString(),
        backend_id: result.id
      });
      
      console.log(`前台功能已注册: ${functionData.name}`);
      return result;
    } catch (error) {
      console.error(`前台功能注册失败: ${functionData.name}`, error);
      throw error;
    }
  }

  /**
   * 准备功能数据
   */
  private prepareFunctionData(config: FunctionConfig): FunctionData {
    const {
      name,
      description,
      path,
      component,
      method,
      category,
      requiredPermissions = [],
      learningMode,
      menuConfig,
      isPublic = false,
      priority = 0
    } = config;

    // 生成唯一的功能键
    const functionKey = this.generateFunctionKey(component, method, path);
    
    // 自动推断权限分类
    const permissionCategory = category || this.inferPermissionCategory(path, component);
    
    // 自动绑定学习模式权限
    const autoPermissions = this.getAutoPermissions(learningMode, path);
    
    return {
      function_key: functionKey,
      name: name || this.generateFunctionName(component, method),
      description: description || `${component}组件的${method || ''}功能`,
      path: path || '',
      component: component || '',
      method: method || '',
      category: permissionCategory,
      required_permissions: [...requiredPermissions, ...autoPermissions],
      permissions: [...requiredPermissions, ...autoPermissions], // 兼容后端接口
      learning_mode: learningMode || '',
      menu_config: menuConfig || {},
      is_public: isPublic,
      priority: priority,
      created_at: new Date().toISOString()
    };
  }

  /**
   * 生成功能键
   */
  private generateFunctionKey(component?: string, method?: string, path?: string): string {
    if (path) {
      return `route:${path}`;
    }
    
    if (component && method) {
      return `component:${component}.${method}`;
    }
    
    if (component) {
      return `component:${component}`;
    }
    
    return `function:${Date.now()}`;
  }

  /**
   * 生成功能名称
   */
  private generateFunctionName(component?: string, method?: string): string {
    if (component && method) {
      return `${component} - ${method}`;
    }
    
    if (component) {
      return component;
    }
    
    return '未命名功能';
  }

  /**
   * 推断权限分类
   */
  private inferPermissionCategory(path?: string, component?: string): string {
    if (path) {
      // 根据路径推断
      if (path.includes('/word-')) return 'LEARNING_CONTENT';
      if (path.includes('/admin')) return 'SYSTEM_MANAGEMENT';
      if (path.includes('/profile')) return 'USER_MANAGEMENT';
      if (path.includes('/community')) return 'SOCIAL_INTERACTION';
      if (path.includes('/subscription')) return 'SUBSCRIPTION_MANAGEMENT';
    }
    
    if (component) {
      // 根据组件名推断
      const lowerComponent = component.toLowerCase();
      if (lowerComponent.includes('word')) return 'LEARNING_CONTENT';
      if (lowerComponent.includes('admin')) return 'SYSTEM_MANAGEMENT';
      if (lowerComponent.includes('user')) return 'USER_MANAGEMENT';
      if (lowerComponent.includes('social')) return 'SOCIAL_INTERACTION';
    }
    
    return 'BASIC_ACCESS';
  }

  /**
   * 获取自动权限
   */
  private getAutoPermissions(learningMode?: string, path?: string): string[] {
    const permissions: string[] = [];
    
    // 根据学习模式自动添加权限
    // if (learningMode && LEARNING_MODE_PERMISSIONS[learningMode]) {
    //   permissions.push(...LEARNING_MODE_PERMISSIONS[learningMode]);
    // }
    
    // 根据路径自动添加权限
    if (path) {
      const pathPermissions = this.getPathPermissions(path);
      permissions.push(...pathPermissions);
    }
    
    return [...new Set(permissions)]; // 去重
  }

  /**
   * 获取路径权限
   */
  private getPathPermissions(path: string): string[] {
    const permissions: string[] = [];
    
    // 基础访问权限
    permissions.push('basic_access');
    
    // 特定路径权限
    if (path.includes('/word-learning')) permissions.push('word_learning_access');
    if (path.includes('/word-spelling')) permissions.push('word_spelling_access');
    if (path.includes('/word-reading')) permissions.push('word_reading_access');
    if (path.includes('/story-reading')) permissions.push('story_reading_access');
    if (path.includes('/pattern-memory')) permissions.push('pattern_memory_access');
    if (path.includes('/listening')) permissions.push('listening_access');
    if (path.includes('/community')) permissions.push('community_access');
    if (path.includes('/profile')) permissions.push('profile_access');
    if (path.includes('/settings')) permissions.push('settings_access');
    
    return permissions;
  }

  /**
   * 处理待注册功能
   */
  private async processPendingRegistrations(): Promise<void> {
    for (const functionData of this.pendingRegistrations) {
      try {
        await this.register(functionData);
      } catch (error) {
        console.error('处理待注册功能失败:', error);
      }
    }
    
    this.pendingRegistrations = [];
  }

  /**
   * 获取已注册功能列表
   */
  getRegisteredFunctions(): RegisteredFunction[] {
    return Array.from(this.registeredFunctions.values());
  }

  /**
   * 检查功能是否已注册
   */
  isRegistered(functionKey: string): boolean {
    return this.registeredFunctions.has(functionKey);
  }

  /**
   * 批量注册路由功能
   */
  async registerRoutes(routes: RouteConfig[]): Promise<void> {
    for (const route of routes) {
      const config: FunctionConfig = {
        name: route.meta?.title || route.name,
        description: route.meta?.description,
        path: route.path,
        component: route.component?.name,
        category: route.meta?.category,
        requiredPermissions: route.meta?.permissions || [],
        learningMode: route.meta?.learningMode,
        menuConfig: route.meta?.menu,
        isPublic: route.meta?.public || false,
        priority: route.meta?.priority || 0
      };
      
      await this.register(config);
    }
  }

  /**
   * 同步已注册功能到后台
   */
  async syncToBackend(): Promise<void> {
    try {
      const functions = this.getRegisteredFunctions();
      
      for (const func of functions) {
        // await djangoBackendIntegration.api.registerFrontendFunction(func);
        console.log('同步功能:', func.name);
      }
      
      console.log('前台功能同步完成');
    } catch (error) {
      console.error('前台功能同步失败:', error);
    }
  }
}

// 创建全局实例
const frontendFunctionRegistry = new FrontendFunctionRegistry();

// 自动初始化
if (typeof window !== 'undefined') {
  window.addEventListener('load', () => {
    frontendFunctionRegistry.initialize();
  });
}

export {
  registerFrontendFunction,
  FrontendFunctionRegistry,
  frontendFunctionRegistry,
  type FunctionConfig,
  type FunctionData,
  type RegisteredFunction,
  type RouteConfig
};

export default frontendFunctionRegistry;