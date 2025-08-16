/**
 * 前后端菜单同步工具
 * 用于将前端菜单配置同步到后端数据库
 */

import { menuConfig } from '../config/menuConfig.js';
import { apiRequest } from './api.js';

/**
 * 菜单同步管理器
 */
class MenuSyncManager {
    constructor() {
        this.syncEndpoint = '/permissions/api/sync-frontend-menus/';
        this.getConfigEndpoint = '/permissions/api/frontend-menu-config/';
    }

    /**
     * 将前端菜单配置转换为后端格式
     * @param {Object} frontendConfig 前端菜单配置
     * @returns {Array} 后端菜单格式数组
     */
    convertToBackendFormat(frontendConfig) {
        const menus = [];
        let sortOrder = 0;

        // 处理底部导航菜单
        if (frontendConfig.bottomNavMenus) {
            frontendConfig.bottomNavMenus.forEach((menu, index) => {
                menus.push({
                    key: menu.id || menu.key,
                    name: menu.name || menu.title,
                    icon: menu.icon || '',
                    url: menu.path || menu.url || '',
                    description: menu.description || '',
                    sort_order: index,
                    menu_level: 'bottom_nav',
                    parent_key: '',
                    enabled: menu.enabled !== false,
                    permission: menu.permission || ''
                });
            });
        }

        // 处理工具菜单
        if (frontendConfig.toolsMenuConfig && frontendConfig.toolsMenuConfig.items) {
            frontendConfig.toolsMenuConfig.items.forEach((menu, index) => {
                menus.push({
                    key: menu.id || menu.key,
                    name: menu.name || menu.title,
                    icon: menu.icon || '',
                    url: menu.path || menu.url || '',
                    description: menu.description || '',
                    sort_order: index + 100,
                    menu_level: 'tools',
                    parent_key: 'tools',
                    enabled: menu.enabled !== false,
                    permission: menu.permission || ''
                });
            });
        }

        // 处理时尚菜单
        if (frontendConfig.fashionMenuConfig && frontendConfig.fashionMenuConfig.items) {
            frontendConfig.fashionMenuConfig.items.forEach((menu, index) => {
                menus.push({
                    key: menu.id || menu.key,
                    name: menu.name || menu.title,
                    icon: menu.icon || '',
                    url: menu.path || menu.url || '',
                    description: menu.description || '',
                    sort_order: index + 200,
                    menu_level: 'fashion',
                    parent_key: 'fashion',
                    enabled: menu.enabled !== false,
                    permission: menu.permission || ''
                });
            });
        }

        // 处理管理菜单
        if (frontendConfig.adminMenuConfig && frontendConfig.adminMenuConfig.items) {
            frontendConfig.adminMenuConfig.items.forEach((menu, index) => {
                menus.push({
                    key: menu.id || menu.key,
                    name: menu.name || menu.title,
                    icon: menu.icon || '',
                    url: menu.path || menu.url || '',
                    description: menu.description || '',
                    sort_order: index + 300,
                    menu_level: 'admin',
                    parent_key: 'admin',
                    enabled: menu.enabled !== false,
                    permission: menu.permission || ''
                });
            });
        }

        return menus;
    }

    /**
     * 同步前端菜单配置到后端
     * @returns {Promise<Object>} 同步结果
     */
    async syncMenusToBackend() {
        try {
            // 获取前端菜单配置
            const frontendMenus = {
                bottomNavMenus: menuConfig.bottomNavMenus || [],
                toolsMenuConfig: menuConfig.toolsMenuConfig || { items: [] },
                fashionMenuConfig: menuConfig.fashionMenuConfig || { items: [] },
                adminMenuConfig: menuConfig.adminMenuConfig || { items: [] }
            };

            // 转换为后端格式
            const backendMenus = this.convertToBackendFormat(frontendMenus);

            // 发送同步请求
            const response = await apiRequest(this.syncEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    menus: backendMenus
                })
            });

            if (response.success) {
                console.log('菜单同步成功:', response.message);
                return {
                    success: true,
                    message: response.message,
                    data: response.data
                };
            } else {
                console.error('菜单同步失败:', response.message);
                return {
                    success: false,
                    message: response.message
                };
            }
        } catch (error) {
            console.error('菜单同步异常:', error);
            return {
                success: false,
                message: `同步异常: ${error.message}`
            };
        }
    }

    /**
     * 从后端获取菜单配置
     * @returns {Promise<Object>} 菜单配置
     */
    async getMenuConfigFromBackend() {
        try {
            const response = await apiRequest(this.getConfigEndpoint, {
                method: 'GET'
            });

            if (response.success) {
                return {
                    success: true,
                    data: response.data
                };
            } else {
                console.error('获取后端菜单配置失败:', response.message);
                return {
                    success: false,
                    message: response.message
                };
            }
        } catch (error) {
            console.error('获取后端菜单配置异常:', error);
            return {
                success: false,
                message: `获取配置异常: ${error.message}`
            };
        }
    }

    /**
     * 比较前后端菜单配置差异
     * @returns {Promise<Object>} 差异分析结果
     */
    async compareMenuConfigs() {
        try {
            const backendResult = await this.getMenuConfigFromBackend();
            if (!backendResult.success) {
                return backendResult;
            }

            const frontendMenus = {
                bottomNavMenus: menuConfig.bottomNavMenus || [],
                toolsMenuConfig: menuConfig.toolsMenuConfig || { items: [] },
                fashionMenuConfig: menuConfig.fashionMenuConfig || { items: [] },
                adminMenuConfig: menuConfig.adminMenuConfig || { items: [] }
            };

            const backendMenus = backendResult.data;

            // 简单的差异检测
            const frontendKeys = new Set();
            const backendKeys = new Set();

            // 收集前端菜单键
            frontendMenus.bottomNavMenus.forEach(menu => frontendKeys.add(menu.id || menu.key));
            frontendMenus.toolsMenuConfig.items.forEach(menu => frontendKeys.add(menu.id || menu.key));
            frontendMenus.fashionMenuConfig.items.forEach(menu => frontendKeys.add(menu.id || menu.key));
            frontendMenus.adminMenuConfig.items.forEach(menu => frontendKeys.add(menu.id || menu.key));

            // 收集后端菜单键
            backendMenus.bottomNavMenus.forEach(menu => backendKeys.add(menu.id || menu.key));
            backendMenus.toolsMenuConfig.items.forEach(menu => backendKeys.add(menu.id || menu.key));
            backendMenus.fashionMenuConfig.items.forEach(menu => backendKeys.add(menu.id || menu.key));
            backendMenus.adminMenuConfig.items.forEach(menu => backendKeys.add(menu.id || menu.key));

            const onlyInFrontend = [...frontendKeys].filter(key => !backendKeys.has(key));
            const onlyInBackend = [...backendKeys].filter(key => !frontendKeys.has(key));
            const common = [...frontendKeys].filter(key => backendKeys.has(key));

            return {
                success: true,
                data: {
                    onlyInFrontend,
                    onlyInBackend,
                    common,
                    needsSync: onlyInFrontend.length > 0 || onlyInBackend.length > 0
                }
            };
        } catch (error) {
            console.error('菜单配置比较异常:', error);
            return {
                success: false,
                message: `比较异常: ${error.message}`
            };
        }
    }
}

// 创建全局实例
const menuSyncManager = new MenuSyncManager();

// 导出工具函数
export {
    MenuSyncManager,
    menuSyncManager
};

// 导出便捷方法
export const syncMenus = () => menuSyncManager.syncMenusToBackend();
export const getBackendMenuConfig = () => menuSyncManager.getMenuConfigFromBackend();
export const compareMenus = () => menuSyncManager.compareMenuConfigs();

// 开发环境下的自动同步功能
if (process.env.NODE_ENV === 'development') {
    // 可以在这里添加自动同步逻辑
    console.log('菜单同步工具已加载，可使用 syncMenus() 进行同步');
}