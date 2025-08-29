/**
 * 前端菜单选择器配置管理
 * 为不同页面和使用场景提供预定义配置
 */

(function(global) {
    'use strict';
    
    /**
     * 前端菜单选择器配置类
     */
    class FrontendMenuSelectorConfig {
        
        /**
         * 获取前端菜单角色分配页面的配置
         */
        static getFrontendMenuRoleAssignmentConfig() {
            return {
                menuFieldSelector: '#id_menu',
                roleFieldSelector: '#id_role',
                enableRoleFiltering: true,
                enableHierarchy: true,
                apiEndpoints: {
                    getMenusForRole: '/admin/permissions/frontendmenuroleassignment/get-menus-for-role/',
                    getAllMenus: '/admin/permissions/frontendmenuconfig/get-all-menus/'
                },
                onMenuChange: function(menuId) {
                    console.log('前端菜单角色分配 - 菜单变化:', menuId);
                    // 可以在这里添加特定的业务逻辑
                },
                onRoleChange: function(role) {
                    console.log('前端菜单角色分配 - 角色变化:', role);
                    // 可以在这里添加特定的业务逻辑
                },
                onError: function(error) {
                    console.error('前端菜单角色分配错误:', error);
                    // 可以在这里添加错误处理逻辑
                }
            };
        }
        
        /**
         * 获取前端菜单配置页面的配置
         */
        static getFrontendMenuConfigConfig() {
            return {
                menuFieldSelector: '#id_parent',
                roleFieldSelector: null, // 菜单配置页面通常不需要角色筛选
                enableRoleFiltering: false,
                enableHierarchy: true,
                apiEndpoints: {
                    getAllMenus: '/admin/permissions/frontendmenuconfig/get-all-menus/'
                },
                onMenuChange: function(menuId) {
                    console.log('前端菜单配置 - 父菜单变化:', menuId);
                    // 可以在这里添加层级验证逻辑
                },
                onError: function(error) {
                    console.error('前端菜单配置错误:', error);
                }
            };
        }
        
        /**
         * 获取内联编辑器的配置
         */
        static getInlineEditorConfig(prefix = '') {
            const menuSelector = prefix ? `#id_${prefix}-menu` : '#id_menu';
            const roleSelector = prefix ? `#id_${prefix}-role` : '#id_role';
            
            return {
                menuFieldSelector: menuSelector,
                roleFieldSelector: roleSelector,
                enableRoleFiltering: true,
                enableHierarchy: true,
                apiEndpoints: {
                    getMenusForRole: '/admin/permissions/frontendmenuroleassignment/get-menus-for-role/',
                    getAllMenus: '/admin/permissions/frontendmenuconfig/get-all-menus/'
                },
                onMenuChange: function(menuId) {
                    console.log(`内联编辑器 (${prefix}) - 菜单变化:`, menuId);
                },
                onRoleChange: function(role) {
                    console.log(`内联编辑器 (${prefix}) - 角色变化:`, role);
                },
                onError: function(error) {
                    console.error(`内联编辑器 (${prefix}) 错误:`, error);
                }
            };
        }
        
        /**
         * 获取批量操作页面的配置
         */
        static getBulkOperationConfig() {
            return {
                menuFieldSelector: '.menu-selector',
                roleFieldSelector: '.role-selector',
                enableRoleFiltering: true,
                enableHierarchy: true,
                apiEndpoints: {
                    getMenusForRole: '/admin/permissions/frontendmenuroleassignment/get-menus-for-role/',
                    getAllMenus: '/admin/permissions/frontendmenuconfig/get-all-menus/'
                },
                onMenuChange: function(menuId) {
                    console.log('批量操作 - 菜单变化:', menuId);
                },
                onRoleChange: function(role) {
                    console.log('批量操作 - 角色变化:', role);
                },
                onError: function(error) {
                    console.error('批量操作错误:', error);
                }
            };
        }
        
        /**
         * 获取自定义配置
         */
        static getCustomConfig(options = {}) {
            const defaultConfig = {
                menuFieldSelector: '#id_menu',
                roleFieldSelector: '#id_role',
                enableRoleFiltering: true,
                enableHierarchy: true,
                emptyOptionText: '---------',
                loadingText: '加载中...',
                errorText: '加载失败，请重试',
                apiEndpoints: {
                    getMenusForRole: '/admin/permissions/frontendmenuroleassignment/get-menus-for-role/',
                    getAllMenus: '/admin/permissions/frontendmenuconfig/get-all-menus/'
                },
                onMenuChange: null,
                onRoleChange: null,
                onError: null
            };
            
            return { ...defaultConfig, ...options };
        }
        
        /**
         * 根据页面类型自动获取配置
         */
        static getConfigByPageType() {
            const currentUrl = window.location.pathname;
            
            if (currentUrl.includes('/frontendmenuroleassignment/')) {
                return this.getFrontendMenuRoleAssignmentConfig();
            } else if (currentUrl.includes('/frontendmenuconfig/')) {
                return this.getFrontendMenuConfigConfig();
            } else {
                // 默认配置
                return this.getCustomConfig();
            }
        }
        
        /**
         * 验证配置的有效性
         */
        static validateConfig(config) {
            const requiredFields = ['menuFieldSelector'];
            const missingFields = requiredFields.filter(field => !config[field]);
            
            if (missingFields.length > 0) {
                throw new Error(`配置缺少必需字段: ${missingFields.join(', ')}`);
            }
            
            // 验证API端点
            if (config.enableRoleFiltering && !config.apiEndpoints?.getMenusForRole) {
                console.warn('启用角色筛选但未配置getMenusForRole API端点');
            }
            
            return true;
        }
    }
    
    // 导出到全局
    global.FrontendMenuSelectorConfig = FrontendMenuSelectorConfig;
    
    // 如果是模块环境，也支持模块导出
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = FrontendMenuSelectorConfig;
    }
    
})(typeof window !== 'undefined' ? window : this);