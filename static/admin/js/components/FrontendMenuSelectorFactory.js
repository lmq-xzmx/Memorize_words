/**
 * 前端菜单选择器工厂类
 * 提供统一的组件创建和管理接口
 */

(function(global) {
    'use strict';
    
    /**
     * 前端菜单选择器工厂类
     */
    class FrontendMenuSelectorFactory {
        constructor() {
            this.instances = new Map();
            this.autoInitialized = false;
        }
        
        /**
         * 创建前端菜单选择器实例
         */
        create(id, config = {}) {
            // 如果已存在实例，先销毁
            if (this.instances.has(id)) {
                this.destroy(id);
            }
            
            // 验证配置
            if (global.FrontendMenuSelectorConfig) {
                global.FrontendMenuSelectorConfig.validateConfig(config);
            }
            
            // 创建新实例
            const instance = new global.FrontendMenuSelector(config);
            this.instances.set(id, instance);
            
            return instance;
        }
        
        /**
         * 根据页面类型自动创建实例
         */
        createByPageType(id = 'default') {
            if (!global.FrontendMenuSelectorConfig) {
                throw new Error('FrontendMenuSelectorConfig not found');
            }
            
            const config = global.FrontendMenuSelectorConfig.getConfigByPageType();
            return this.create(id, config);
        }
        
        /**
         * 为前端菜单角色分配页面创建实例
         */
        createForFrontendMenuRoleAssignment(id = 'frontendMenuRoleAssignment') {
            if (!global.FrontendMenuSelectorConfig) {
                throw new Error('FrontendMenuSelectorConfig not found');
            }
            
            const config = global.FrontendMenuSelectorConfig.getFrontendMenuRoleAssignmentConfig();
            return this.create(id, config);
        }
        
        /**
         * 为前端菜单配置页面创建实例
         */
        createForFrontendMenuConfig(id = 'frontendMenuConfig') {
            if (!global.FrontendMenuSelectorConfig) {
                throw new Error('FrontendMenuSelectorConfig not found');
            }
            
            const config = global.FrontendMenuSelectorConfig.getFrontendMenuConfigConfig();
            return this.create(id, config);
        }
        
        /**
         * 为内联编辑器创建实例
         */
        createForInlineEditor(prefix, id = null) {
            if (!global.FrontendMenuSelectorConfig) {
                throw new Error('FrontendMenuSelectorConfig not found');
            }
            
            const instanceId = id || `inline_${prefix}`;
            const config = global.FrontendMenuSelectorConfig.getInlineEditorConfig(prefix);
            return this.create(instanceId, config);
        }
        
        /**
         * 批量创建内联编辑器实例
         */
        createForAllInlineEditors(containerSelector = '.inline-group') {
            const $ = this.getJQuery();
            const instances = [];
            
            $(containerSelector).each((index, container) => {
                const $container = $(container);
                const prefix = this.extractInlinePrefix($container);
                
                if (prefix) {
                    try {
                        const instance = this.createForInlineEditor(prefix);
                        instances.push(instance);
                    } catch (error) {
                        console.warn(`Failed to create inline editor for prefix ${prefix}:`, error);
                    }
                }
            });
            
            return instances;
        }
        
        /**
         * 提取内联编辑器前缀
         */
        extractInlinePrefix($container) {
            // 尝试从容器中找到带有前缀的字段
            const menuField = $container.find('[id*="-menu"]').first();
            if (menuField.length) {
                const id = menuField.attr('id');
                const match = id.match(/^id_(.+)-menu$/);
                return match ? match[1] : null;
            }
            
            return null;
        }
        
        /**
         * 获取实例
         */
        get(id) {
            return this.instances.get(id);
        }
        
        /**
         * 检查实例是否存在
         */
        has(id) {
            return this.instances.has(id);
        }
        
        /**
         * 销毁指定实例
         */
        destroy(id) {
            const instance = this.instances.get(id);
            if (instance) {
                instance.destroy();
                this.instances.delete(id);
                return true;
            }
            return false;
        }
        
        /**
         * 销毁所有实例
         */
        destroyAll() {
            this.instances.forEach((instance, id) => {
                instance.destroy();
            });
            this.instances.clear();
        }
        
        /**
         * 刷新所有实例
         */
        refreshAll() {
            this.instances.forEach(instance => {
                instance.refresh();
            });
        }
        
        /**
         * 自动初始化页面中的前端菜单选择器
         */
        autoInit() {
            if (this.autoInitialized) {
                console.warn('FrontendMenuSelectorFactory already auto-initialized');
                return;
            }
            
            const $ = this.getJQuery();
            
            // 等待DOM加载完成
            $(document).ready(() => {
                try {
                    // 根据页面类型自动创建主实例
                    this.createByPageType('main');
                    
                    // 为内联编辑器创建实例
                    this.createForAllInlineEditors();
                    
                    this.autoInitialized = true;
                    console.log('FrontendMenuSelectorFactory auto-initialized successfully');
                } catch (error) {
                    console.error('FrontendMenuSelectorFactory auto-init failed:', error);
                }
            });
        }
        
        /**
         * 获取jQuery实例
         */
        getJQuery() {
            return global.django && global.django.jQuery || global.jQuery || global.$;
        }
        
        /**
         * 获取所有实例的状态信息
         */
        getStatus() {
            const status = {
                totalInstances: this.instances.size,
                autoInitialized: this.autoInitialized,
                instances: []
            };
            
            this.instances.forEach((instance, id) => {
                status.instances.push({
                    id: id,
                    initialized: instance.isInitialized,
                    menuField: instance.options.menuFieldSelector,
                    roleField: instance.options.roleFieldSelector,
                    enableRoleFiltering: instance.options.enableRoleFiltering
                });
            });
            
            return status;
        }
        
        /**
         * 调试信息
         */
        debug() {
            console.group('FrontendMenuSelectorFactory Debug Info');
            console.log('Status:', this.getStatus());
            console.log('Instances:', this.instances);
            console.groupEnd();
        }
    }
    
    // 创建全局单例实例
    const factory = new FrontendMenuSelectorFactory();
    
    // 导出到全局
    global.FrontendMenuSelectorFactory = FrontendMenuSelectorFactory;
    global.frontendMenuSelectorFactory = factory;
    
    // 如果是模块环境，也支持模块导出
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = { FrontendMenuSelectorFactory, factory };
    }
    
    // 自动初始化（可选）
    // factory.autoInit();
    
})(typeof window !== 'undefined' ? window : this);