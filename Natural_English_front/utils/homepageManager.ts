/**
 * 首页重定向管理器
 * 处理"设为首页"功能的逻辑
 */

import { UserSettingsManager } from './userSettings';

// 类型定义
interface ModeRouteMap {
  [key: string]: string;
}

interface ModeNames {
  [key: string]: string;
}

interface RedirectInfo {
  mode: string;
  route: string;
  name: string;
}

interface ModeInfo {
  key: string;
  name: string;
  route: string;
}

interface RouteObject {
  path: string;
  query?: {
    force?: string;
    [key: string]: any;
  };
}

interface Router {
  push(route: string): void;
}

export class HomepageManager {
  private userSettings: UserSettingsManager;
  private modeRouteMap: ModeRouteMap;
  private modeNames: ModeNames;

  constructor() {
    this.userSettings = new UserSettingsManager();
    this.modeRouteMap = {
      'learning-modes': '/learning-modes',
      'word-reading': '/word-reading',
      'word-learning': '/word-learning',
      'word-detail': '/word-detail/institution',
      'word-root-analysis': '/word-root-analysis',
      'story-reading': '/story-reading',
      'spelling': '/word-learning/spelling',
      'flashcard': '/word-learning/flashcard',
      'pattern-memory': '/pattern-memory',
      'word-challenge': '/word-challenge',
      'word-review': '/word-review',
      'word-selection': '/word-selection',
      'teacher-student-interaction': '/word-selection-practice2',
      'competition': '/competition',
      'quick-brush': '/quick-brush'
    };
    
    this.modeNames = {
      'learning-modes': '词汇阅读中心',
      'word-reading': '单词阅读',
      'word-learning': '单词学习',
      'word-detail': '单词详情',
      'word-root-analysis': '词根分解',
      'story-reading': '故事阅读',
      'spelling': '拼写练习',
      'flashcard': '闪卡学习',
      'pattern-memory': '模式匹配记忆',
      'word-challenge': '单词挑战',
      'word-review': '单词复习',
      'word-selection': '单词选择',
      'teacher-student-interaction': '师生互动',
      'competition': '竞技模式',
      'quick-brush': '快刷模式'
    };
  }
  
  /**
   * 设置首页模式
   * @param mode - 模式标识
   * @returns 设置是否成功
   */
  setHomepage(mode: string): boolean {
    try {
      if (!this.modeRouteMap[mode]) {
        console.error(`未知的模式: ${mode}`);
        return false;
      }
      
      this.userSettings.save('homepage_mode', mode);
      console.log(`已设置首页为: ${this.modeNames[mode]} (${mode})`);
      return true;
    } catch (error) {
      console.error('设置首页失败:', error);
      return false;
    }
  }
  
  /**
   * 获取当前首页模式
   * @returns 当前首页模式
   */
  getHomepage(): string | null {
    try {
      return this.userSettings.get('homepage_mode');
    } catch (error) {
      console.error('获取首页设置失败:', error);
      return null;
    }
  }
  
  /**
   * 清除首页设置
   * @returns 清除是否成功
   */
  clearHomepage(): boolean {
    try {
      this.userSettings.remove('homepage_mode');
      console.log('已清除首页设置');
      return true;
    } catch (error) {
      console.error('清除首页设置失败:', error);
      return false;
    }
  }
  
  /**
   * 获取模式对应的路由
   * @param mode - 模式标识
   * @returns 路由路径
   */
  getModeRoute(mode: string): string | null {
    return this.modeRouteMap[mode] || null;
  }
  
  /**
   * 获取模式的显示名称
   * @param mode - 模式标识
   * @returns 显示名称
   */
  getModeName(mode: string): string {
    return this.modeNames[mode] || mode;
  }
  
  /**
   * 检查是否应该重定向到首页
   * @param route - 当前路由对象
   * @param hasPermission - 权限检查函数
   * @returns 重定向信息或null
   */
  checkHomepageRedirect(route: RouteObject, hasPermission: ((permission: string) => boolean) | null = null): RedirectInfo | null {
    try {
      const homepageMode = this.getHomepage();
      
      // 如果没有设置首页，不重定向
      if (!homepageMode) {
        return null;
      }
      
      // 如果当前就在首页路径，不重定向
      const homepageRoute = this.getModeRoute(homepageMode);
      if (route.path === homepageRoute) {
        return null;
      }
      
      // 如果是强制显示选择页面，不重定向
      if (route.query && route.query.force === 'true') {
        return null;
      }
      
      // 只在特定路径下进行重定向，排除learning-modes等重要页面
      const redirectPaths = ['/', '/index', '/dashboard'];
      const excludePaths = ['/learning-modes', '/learning-mode', '/login', '/register', '/error'];
      
      if (!redirectPaths.includes(route.path) || excludePaths.includes(route.path)) {
        return null;
      }
      
      // 权限检查：如果提供了权限检查函数，验证用户是否有权限访问设置的首页
      if (hasPermission && typeof hasPermission === 'function') {
        const modePermissions: { [key: string]: string } = {
          'word-reading': 'practice_reading',
          'word-learning': 'view_word_learning',
          'word-detail': 'view_word_detail',
          'word-root-analysis': 'analyze_word_roots',
          'story-reading': 'practice_story_reading',
          'spelling': 'practice_spelling',
          'flashcard': 'use_flashcard',
          'pattern-memory': 'use_pattern_memory',
          'word-challenge': 'participate_challenge',
          'word-review': 'review_words',
          'word-selection': 'practice_word_selection',
          'teacher-student-interaction': 'practice_word_selection',
          'competition': 'participate_challenge',
          'quick-brush': 'review_words'
        };
        
        const requiredPermission = modePermissions[homepageMode];
        if (requiredPermission && !hasPermission(requiredPermission)) {
          console.warn(`用户无权限访问设置的首页: ${this.getModeName(homepageMode)}，将清除首页设置`);
          this.clearHomepage();
          return null;
        }
      }
      
      return {
        mode: homepageMode,
        route: homepageRoute!,
        name: this.getModeName(homepageMode)
      };
    } catch (error) {
      console.error('检查首页重定向失败:', error);
      return null;
    }
  }
  
  /**
   * 执行首页重定向
   * @param router - Vue Router实例
   * @param route - 当前路由对象
   * @returns 是否执行了重定向
   */
  performHomepageRedirect(router: Router, route: RouteObject): boolean {
    try {
      const redirectInfo = this.checkHomepageRedirect(route);
      
      if (!redirectInfo) {
        return false;
      }
      
      console.log(`重定向到首页: ${redirectInfo.name} (${redirectInfo.route})`);
      router.push(redirectInfo.route);
      return true;
    } catch (error) {
      console.error('执行首页重定向失败:', error);
      return false;
    }
  }
  
  /**
   * 获取所有可用的模式
   * @returns 模式列表
   */
  getAllModes(): ModeInfo[] {
    return Object.keys(this.modeRouteMap).map(mode => ({
      key: mode,
      name: this.getModeName(mode),
      route: this.getModeRoute(mode)!
    }));
  }
  
  /**
   * 验证模式是否有效
   * @param mode - 模式标识
   * @returns 是否有效
   */
  isValidMode(mode: string): boolean {
    return !!this.modeRouteMap[mode];
  }
}

// 创建单例实例
export const homepageManager = new HomepageManager();

// 全局方法，方便在控制台调试
if (typeof window !== 'undefined') {
  (window as any).homepageManager = homepageManager;
}

export default HomepageManager;

// 导出类型
export type {
  ModeRouteMap,
  ModeNames,
  RedirectInfo,
  ModeInfo,
  RouteObject,
  Router
};