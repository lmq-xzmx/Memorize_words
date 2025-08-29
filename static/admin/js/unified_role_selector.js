/**
 * 统一角色选择器 JavaScript
 * 合并并优化多个角色选择器文件，提供统一的角色选择器交互功能
 * 替代: dynamic_role_selector.js 和 enhanced_role_selector.js
 */

(function($) {
    'use strict';
    
    // 统一配置对象
    const UnifiedRoleSelectorConfig = {
        // API端点配置
        endpoints: {
            roleChoices: '/admin/permissions/rolegroupmapping/get-role-list/',
            roleInfo: '/admin/accounts/customuser/get-role-info/',
            // roleMenuPermissionRoleList: '/admin/permissions/rolemenupermission/get-role-list/',  // RoleMenuPermission已废弃
            validate: '/api/roles/{role}/validate/',
            stats: '/api/roles/stats/',
            clearCache: '/api/roles/clear_cache/',
            refreshCache: '/api/roles/refresh_cache/'
        },
        
        // 缓存配置
        cache: {
            enabled: true,
            duration: 5 * 60 * 1000, // 5分钟
            key: 'unified_role_selector_data',
            roles: null,
            timestamp: null
        },
        
        // 选择器配置
        selectors: {
            roleField: 'select[name="role"], input[name="role"], select[id*="role"], input[id*="role"], .role-selector, [data-role-selector]',
            // roleMenuPermissionForm: '#rolemenupermission_form',  // RoleMenuPermission已废弃
            roleGroupMappingForm: '#rolegroupmapping_form'
        },
        
        // 样式类配置
        classes: {
            selector: 'unified-role-selector',
            enhanced: 'role-selector-enhanced',
            loading: 'role-selector-loading',
            error: 'role-selector-error',
            valid: 'role-selector-valid',
            invalid: 'role-selector-invalid'
        },
        
        // 表单特定配置
        forms: {
            // roleMenuPermission: {  // RoleMenuPermission已废弃
            //     formId: 'rolemenupermission_form',
            //     roleFieldSelector: '#id_role',
            //     endpoint: '/admin/permissions/rolemenupermission/get-role-list/'
            // }
        }
    };
    
    /**
     * 统一角色数据管理器
     */
    class UnifiedRoleDataManager {
        constructor() {
            this.cache = new Map();
            this.requestQueue = new Map();
        }
        
        /**
         * 获取角色选择项
         */
        async getRoleChoices(endpoint = null) {
            const targetEndpoint = endpoint || UnifiedRoleSelectorConfig.endpoints.roleChoices;
            
            // 检查缓存
            if (this.isCacheValid()) {
                return UnifiedRoleSelectorConfig.cache.roles;
            }
            
            // 检查是否已有相同请求在进行
            if (this.requestQueue.has(targetEndpoint)) {
                return await this.requestQueue.get(targetEndpoint);
            }
            
            // 创建新请求
            const requestPromise = this.fetchRoleData(targetEndpoint);
            this.requestQueue.set(targetEndpoint, requestPromise);
            
            try {
                const result = await requestPromise;
                this.requestQueue.delete(targetEndpoint);
                return result;
            } catch (error) {
                this.requestQueue.delete(targetEndpoint);
                throw error;
            }
        }
        
        /**
         * 从服务器获取角色数据
         */
        async fetchRoleData(endpoint) {
            try {
                const response = await fetch(endpoint, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json'
                    },
                    credentials: 'same-origin'
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                
                // 更新缓存
                UnifiedRoleSelectorConfig.cache.roles = data.roles || data;
                UnifiedRoleSelectorConfig.cache.timestamp = Date.now();
                
                // 保存到本地存储
                this.saveToLocalStorage(data.roles || data);
                
                return data.roles || data;
            } catch (error) {
                console.error('获取角色数据失败:', error);
                
                // 尝试从本地存储恢复
                const cachedData = this.getFromLocalStorage();
                if (cachedData) {
                    console.warn('使用本地缓存的角色数据');
                    return cachedData;
                }
                
                throw error;
            }
        }
        
        /**
         * 验证角色
         */
        async validateRole(role) {
            if (!role) return false;
            
            try {
                const url = UnifiedRoleSelectorConfig.endpoints.validate.replace('{role}', encodeURIComponent(role));
                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin'
                });
                
                if (!response.ok) return false;
                
                const data = await response.json();
                return data.valid === true;
            } catch (error) {
                console.error('角色验证失败:', error);
                return false;
            }
        }
        
        /**
         * 检查缓存是否有效
         */
        isCacheValid() {
            return UnifiedRoleSelectorConfig.cache.roles &&
                   UnifiedRoleSelectorConfig.cache.timestamp &&
                   (Date.now() - UnifiedRoleSelectorConfig.cache.timestamp) < UnifiedRoleSelectorConfig.cache.duration;
        }
        
        /**
         * 清除缓存
         */
        clearCache() {
            UnifiedRoleSelectorConfig.cache.roles = null;
            UnifiedRoleSelectorConfig.cache.timestamp = null;
            localStorage.removeItem(UnifiedRoleSelectorConfig.cache.key);
        }
        
        /**
         * 保存到本地存储
         */
        saveToLocalStorage(data) {
            if (!UnifiedRoleSelectorConfig.cache.enabled) return;
            
            try {
                const cacheData = {
                    data: data,
                    timestamp: Date.now()
                };
                localStorage.setItem(UnifiedRoleSelectorConfig.cache.key, JSON.stringify(cacheData));
            } catch (error) {
                console.warn('保存角色数据到本地存储失败:', error);
            }
        }
        
        /**
         * 从本地存储获取
         */
        getFromLocalStorage() {
            if (!UnifiedRoleSelectorConfig.cache.enabled) return null;
            
            try {
                const cached = localStorage.getItem(UnifiedRoleSelectorConfig.cache.key);
                if (!cached) return null;
                
                const data = JSON.parse(cached);
                const now = Date.now();
                
                if (now - data.timestamp > UnifiedRoleSelectorConfig.cache.duration) {
                    localStorage.removeItem(UnifiedRoleSelectorConfig.cache.key);
                    return null;
                }
                
                return data.data;
            } catch (error) {
                localStorage.removeItem(UnifiedRoleSelectorConfig.cache.key);
                return null;
            }
        }
    }
    
    /**
     * 统一角色选择器管理器
     */
    class UnifiedRoleSelectorManager {
        constructor() {
            this.dataManager = new UnifiedRoleDataManager();
            this.selectors = new Set();
            this.init();
        }
        
        /**
         * 初始化
         */
        init() {
            console.log('Unified Role Selector: 初始化中...');
            this.bindEvents();
            this.enhanceExistingSelectors();
            this.loadInitialData();
        }
        
        /**
         * 绑定事件
         */
        bindEvents() {
            // DOM变化监听
            if (window.MutationObserver) {
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'childList') {
                            mutation.addedNodes.forEach((node) => {
                                if (node.nodeType === Node.ELEMENT_NODE) {
                                    this.enhanceNewSelectors($(node));
                                }
                            });
                        }
                    });
                });
                
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            }
            
            // 页面加载完成后再次检查
            $(document).ready(() => {
                setTimeout(() => this.enhanceExistingSelectors(), 100);
            });
        }
        
        /**
         * 增强现有选择器
         */
        enhanceExistingSelectors() {
            const $selectors = $(UnifiedRoleSelectorConfig.selectors.roleField);
            
            if ($selectors.length === 0) {
                console.log('Unified Role Selector: 未找到角色选择器字段');
                return;
            }
            
            console.log(`Unified Role Selector: 找到 ${$selectors.length} 个角色选择器`);
            
            $selectors.each((index, element) => {
                this.enhanceSelector($(element));
            });
        }
        
        /**
         * 增强新选择器
         */
        enhanceNewSelectors($container) {
            const $newSelectors = $container.find(UnifiedRoleSelectorConfig.selectors.roleField);
            
            $newSelectors.each((index, element) => {
                const $selector = $(element);
                if (!$selector.hasClass(UnifiedRoleSelectorConfig.classes.enhanced)) {
                    this.enhanceSelector($selector);
                }
            });
        }
        
        /**
         * 增强单个选择器
         */
        async enhanceSelector($selector) {
            if ($selector.hasClass(UnifiedRoleSelectorConfig.classes.enhanced)) {
                return;
            }
            
            $selector.addClass(UnifiedRoleSelectorConfig.classes.enhanced);
            this.selectors.add($selector[0]);
            
            try {
                // 添加加载状态
                $selector.addClass(UnifiedRoleSelectorConfig.classes.loading);
                
                // 获取角色数据
                const roleData = await this.dataManager.getRoleChoices();
                
                // 更新选择器选项
                this.updateSelectorOptions($selector, roleData);
                
                // 绑定事件
                this.bindSelectorEvents($selector);
                
                // 移除加载状态
                $selector.removeClass(UnifiedRoleSelectorConfig.classes.loading);
                
                console.log(`Unified Role Selector: 已增强选择器 ${$selector.attr('name') || $selector.attr('id')}`);
            } catch (error) {
                console.error('增强角色选择器失败:', error);
                $selector.removeClass(UnifiedRoleSelectorConfig.classes.loading)
                        .addClass(UnifiedRoleSelectorConfig.classes.error);
            }
        }
        
        /**
         * 更新选择器选项
         */
        updateSelectorOptions($selector, roleData) {
            if (!Array.isArray(roleData)) {
                console.warn('角色数据格式不正确:', roleData);
                return;
            }
            
            const currentValue = $selector.val();
            
            // 清空现有选项（保留空选项）
            $selector.find('option').not('[value=""]').remove();
            
            // 添加新选项
            roleData.forEach(role => {
                const value = role.value || role.id || role.name;
                const text = role.text || role.display_name || role.name || value;
                
                const $option = $('<option></option>')
                    .attr('value', value)
                    .text(text);
                
                $selector.append($option);
            });
            
            // 恢复之前的值
            if (currentValue) {
                $selector.val(currentValue);
            }
        }
        
        /**
         * 绑定选择器事件
         */
        bindSelectorEvents($selector) {
            $selector.off('change.unifiedRoleSelector').on('change.unifiedRoleSelector', async (event) => {
                const selectedRole = $(event.target).val();
                if (selectedRole) {
                    await this.validateAndMarkSelector($selector, selectedRole);
                }
            });
        }
        
        /**
         * 验证并标记选择器
         */
        async validateAndMarkSelector($selector, role) {
            try {
                $selector.removeClass(`${UnifiedRoleSelectorConfig.classes.valid} ${UnifiedRoleSelectorConfig.classes.invalid}`);
                
                const isValid = await this.dataManager.validateRole(role);
                
                if (isValid) {
                    $selector.addClass(UnifiedRoleSelectorConfig.classes.valid);
                } else {
                    $selector.addClass(UnifiedRoleSelectorConfig.classes.invalid);
                }
            } catch (error) {
                console.error('角色验证失败:', error);
                $selector.addClass(UnifiedRoleSelectorConfig.classes.error);
            }
        }
        
        /**
         * 加载初始数据
         */
        async loadInitialData() {
            try {
                await this.dataManager.getRoleChoices();
                console.log('Unified Role Selector: 初始数据加载完成');
            } catch (error) {
                console.error('Unified Role Selector: 初始数据加载失败:', error);
            }
        }
        
        /**
         * 刷新所有选择器
         */
        async refresh() {
            this.dataManager.clearCache();
            
            try {
                const roleData = await this.dataManager.getRoleChoices();
                
                this.selectors.forEach(selector => {
                    const $selector = $(selector);
                    this.updateSelectorOptions($selector, roleData);
                });
                
                console.log('Unified Role Selector: 所有选择器已刷新');
            } catch (error) {
                console.error('刷新角色选择器失败:', error);
            }
        }
        
        /**
         * 获取实例（单例模式）
         */
        static getInstance() {
            if (!window.unifiedRoleSelectorManager) {
                window.unifiedRoleSelectorManager = new UnifiedRoleSelectorManager();
            }
            return window.unifiedRoleSelectorManager;
        }
    }
    
    /**
     * 统一工具函数
     */
    const UnifiedRoleSelectorUtils = {
        /**
         * 手动刷新所有选择器
         */
        refresh() {
            const manager = UnifiedRoleSelectorManager.getInstance();
            return manager.refresh();
        },
        
        /**
         * 清除缓存
         */
        clearCache() {
            const manager = UnifiedRoleSelectorManager.getInstance();
            manager.dataManager.clearCache();
        },
        
        /**
         * 获取角色统计信息
         */
        async getStats() {
            try {
                const response = await fetch(UnifiedRoleSelectorConfig.endpoints.stats);
                return await response.json();
            } catch (error) {
                console.error('获取角色统计失败:', error);
                return null;
            }
        }
    };
    
    // 自动初始化
    $(document).ready(function() {
        UnifiedRoleSelectorManager.getInstance();
    });
    
    // 暴露全局接口
    window.UnifiedRoleSelectorManager = UnifiedRoleSelectorManager;
    window.UnifiedRoleSelectorUtils = UnifiedRoleSelectorUtils;
    window.UnifiedRoleSelector = {
        init: () => UnifiedRoleSelectorManager.getInstance(),
        refresh: () => UnifiedRoleSelectorUtils.refresh(),
        clearCache: () => UnifiedRoleSelectorUtils.clearCache(),
        getStats: () => UnifiedRoleSelectorUtils.getStats()
    };
    
})(django.jQuery || jQuery);