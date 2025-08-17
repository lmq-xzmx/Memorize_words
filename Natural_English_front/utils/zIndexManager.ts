/**
 * Z-Index 层级管理器
 * 统一管理应用中所有弹出层的z-index值，避免层级冲突
 */

// 类型定义
type ZIndexLevel = 'BASE' | 'NAVIGATION' | 'POPUP_MENU' | 'SUBMENU' | 'MODAL' | 'TOOLTIP' | 'URGENT';
type CounterType = 'popup' | 'submenu' | 'modal' | 'all';
type MenuType = 'popup' | 'submenu';

interface ZIndexLevels {
  BASE: number;
  NAVIGATION: number;
  POPUP_MENU: number;
  SUBMENU: number;
  MODAL: number;
  TOOLTIP: number;
  URGENT: number;
}

interface DynamicCounter {
  popup: number;
  submenu: number;
  modal: number;
}

interface MenuInfo {
  type: MenuType;
  element: HTMLElement | null;
  zIndex: number;
  parentId: string | null;
  children: Set<string>;
}

// 基础层级定义
const Z_INDEX_LEVELS: ZIndexLevels = {
  // 基础层级
  BASE: 1000,
  
  // 导航层级
  NAVIGATION: 1100,
  
  // 弹出菜单层级
  POPUP_MENU: 1200,
  
  // 子菜单层级
  SUBMENU: 1300,
  
  // 模态框层级
  MODAL: 1400,
  
  // 提示层级
  TOOLTIP: 1500,
  
  // 最高层级（紧急通知等）
  URGENT: 1600
};

// 动态层级计数器
let dynamicCounter: DynamicCounter = {
  popup: 0,
  submenu: 0,
  modal: 0
};

/**
 * 获取基础z-index值
 * @param level - 层级名称
 * @returns z-index值
 */
export function getZIndex(level: string): number {
  const upperLevel = level.toUpperCase() as ZIndexLevel;
  return Z_INDEX_LEVELS[upperLevel] || Z_INDEX_LEVELS.BASE;
}

/**
 * 获取弹出菜单的z-index
 * @param isSubmenu - 是否为子菜单
 * @returns z-index值
 */
export function getMenuZIndex(isSubmenu: boolean = false): number {
  if (isSubmenu) {
    dynamicCounter.submenu++;
    return Z_INDEX_LEVELS.SUBMENU + dynamicCounter.submenu;
  } else {
    dynamicCounter.popup++;
    return Z_INDEX_LEVELS.POPUP_MENU + dynamicCounter.popup;
  }
}

/**
 * 获取模态框的z-index
 * @returns z-index值
 */
export function getModalZIndex(): number {
  dynamicCounter.modal++;
  return Z_INDEX_LEVELS.MODAL + dynamicCounter.modal;
}

/**
 * 重置动态计数器
 * @param type - 要重置的类型
 */
export function resetZIndexCounter(type: CounterType = 'all'): void {
  if (type === 'all') {
    dynamicCounter = {
      popup: 0,
      submenu: 0,
      modal: 0
    };
  } else if (type in dynamicCounter) {
    dynamicCounter[type as keyof DynamicCounter] = 0;
  }
}

/**
 * 获取当前最高的z-index值
 * @returns 当前最高z-index值
 */
export function getCurrentMaxZIndex(): number {
  const maxStatic = Math.max(...Object.values(Z_INDEX_LEVELS));
  const maxDynamic = Math.max(
    Z_INDEX_LEVELS.POPUP_MENU + dynamicCounter.popup,
    Z_INDEX_LEVELS.SUBMENU + dynamicCounter.submenu,
    Z_INDEX_LEVELS.MODAL + dynamicCounter.modal
  );
  return Math.max(maxStatic, maxDynamic);
}

/**
 * 确保元素在最顶层
 * @param element - 要置顶的元素
 * @returns 设置的z-index值
 */
export function bringToFront(element: HTMLElement | null): number {
  if (!element) return 0;
  
  const maxZIndex = getCurrentMaxZIndex() + 1;
  element.style.zIndex = maxZIndex.toString();
  return maxZIndex;
}

/**
 * 菜单层级管理类
 */
export class MenuZIndexManager {
  private activeMenus: Map<string, MenuInfo>;
  private menuStack: string[];

  constructor() {
    this.activeMenus = new Map(); // 存储活跃菜单及其z-index
    this.menuStack = []; // 菜单栈，用于管理菜单层级关系
  }
  
  /**
   * 注册菜单
   * @param menuId - 菜单ID
   * @param menuType - 菜单类型
   * @param element - 菜单元素
   * @param parentId - 父菜单ID（可选）
   * @returns z-index值
   */
  registerMenu(menuId: string, menuType: MenuType, element: HTMLElement | null, parentId: string | null = null): number {
    const zIndex = getMenuZIndex(menuType === 'submenu');
    
    this.activeMenus.set(menuId, {
      type: menuType,
      element,
      zIndex,
      parentId,
      children: new Set()
    });
    
    // 建立父子关系
    if (parentId && this.activeMenus.has(parentId)) {
      this.activeMenus.get(parentId)!.children.add(menuId);
    }
    
    // 添加到菜单栈
    this.menuStack.push(menuId);
    
    // 设置z-index
    if (element) {
      element.style.zIndex = zIndex.toString();
    }
    
    return zIndex;
  }
  
  /**
   * 注销菜单
   * @param menuId - 菜单ID
   */
  unregisterMenu(menuId: string): void {
    const menuInfo = this.activeMenus.get(menuId);
    if (!menuInfo) return;
    
    // 递归关闭所有子菜单
    for (const childId of menuInfo.children) {
      this.unregisterMenu(childId);
    }
    
    // 从父菜单的子菜单列表中移除
    if (menuInfo.parentId && this.activeMenus.has(menuInfo.parentId)) {
      this.activeMenus.get(menuInfo.parentId)!.children.delete(menuId);
    }
    
    // 从菜单栈中移除
    const stackIndex = this.menuStack.indexOf(menuId);
    if (stackIndex > -1) {
      this.menuStack.splice(stackIndex, 1);
    }
    
    // 从活跃菜单中移除
    this.activeMenus.delete(menuId);
  }
  
  /**
   * 获取菜单的z-index
   * @param menuId - 菜单ID
   * @returns z-index值
   */
  getMenuZIndex(menuId: string): number {
    const menuInfo = this.activeMenus.get(menuId);
    return menuInfo ? menuInfo.zIndex : 0;
  }
  
  /**
   * 清理所有菜单
   */
  clearAll(): void {
    this.activeMenus.clear();
    this.menuStack = [];
    resetZIndexCounter('all');
  }
  
  /**
   * 获取当前活跃菜单数量
   * @returns 活跃菜单数量
   */
  getActiveMenuCount(): number {
    return this.activeMenus.size;
  }
}

// 创建全局菜单层级管理器实例
export const globalMenuZIndexManager = new MenuZIndexManager();

// 导出常量和类型
export { Z_INDEX_LEVELS };
export type {
  ZIndexLevel,
  CounterType,
  MenuType,
  ZIndexLevels,
  DynamicCounter,
  MenuInfo
};