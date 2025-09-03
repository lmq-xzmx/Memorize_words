/**
 * 全局组件注册
 * 统一管理和注册全局组件
 */

// 导入组件
import DynamicMenu from './DynamicMenu/DynamicMenu.vue'
import MenuManager from './MenuManager/MenuManager.vue'
import BaseLayout from './Layout/BaseLayout.vue'

/**
 * 注册全局组件
 * @param {Object} app Vue应用实例
 */
export function registerGlobalComponents(app) {
  // 动态菜单组件
  app.component('DynamicMenu', DynamicMenu)
  
  // 菜单管理器组件
  app.component('MenuManager', MenuManager)
  
  // 基础布局组件
  app.component('BaseLayout', BaseLayout)
}

/**
 * 组件列表
 */
export const globalComponents = {
  DynamicMenu,
  MenuManager,
  BaseLayout
}

/**
 * 默认导出注册函数
 */
export default registerGlobalComponents