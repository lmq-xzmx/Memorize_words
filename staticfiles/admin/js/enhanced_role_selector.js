/**
 * 增强角色选择器 JavaScript
 * 提供统一的角色选择器交互功能和实时数据同步
 */

(function($) {
    'use strict';
    
    // 角色选择器配置
    const RoleSelectorConfig = {
        // API端点
        endpoints: {
            choices: '/api/roles/choices/',
            validate: '/api/roles/{role}/validate/',
            stats: '/api/roles/stats/',
            clearCache: '/api/roles/clear_cache/',
            refreshCache: '/api/roles/refresh_cache/'
        },
        
        // 缓存配置
        cache: {
            enabled: true,
            duration: 5 * 60 * 1000, // 5分钟
            key: 'role_selector_data'
        },
        
        // 选择器样式类
        classes: {
            selector: 'role-selector',
            enhanced: 'role-selector-enhanced',
            loading: 'role-selector-loading',
            error: 'role-selector-error',
            valid: 'role-selector-valid',
            invalid: 'role-selector-invalid'
        }
    };
    
    // 角色选择器管理器
    class RoleSelectorManager {
        constructor() {
            this.cache = new Map();
            this.selectors = new Set();
            this.init();
        }
        
        init() {
            this.bindEvents();
            this.enhanceExistingSelectors();
            this.loadRoleData();
        }
        
        // 绑定全局事件
        bindEvents() {
            // 监听DOM变化，自动增强新添加的角色选择器
            if (window.MutationObserver) {
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        mutation.addedNodes.forEach((node) => {
                            if (node.nodeType === 1) { // Element node
                                this.enhanceSelectorsInNode(node);
                            }
                        });
                    });
                });
                
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            }
            
            // 监听角色数据变更事件
            $(document).on('role:changed', (e, data) => {
                this.handleRoleChange(data);
            });
            
            // 监听缓存刷新事件
            $(document).on('role:cache:refresh', () => {
                this.refreshCache();
            });
        }
        
        // 增强现有的角色选择器
        enhanceExistingSelectors() {
            $('[data-role-selector], select[name*="role"], #id_role').each((index, element) => {
                this.enhanceSelector($(element));
            });
        }
        
        // 在指定节点中查找并增强角色选择器
        enhanceSelectorsInNode(node) {
            const $node = $(node);
            $node.find('[data-role-selector], select[name*="role"], #id_role').each((index, element) => {
                this.enhanceSelector($(element));
            });
        }
        
        // 增强单个角色选择器
        enhanceSelector($selector) {
            if ($selector.hasClass(RoleSelectorConfig.classes.enhanced)) {
                return; // 已经增强过
            }
            
            $selector.addClass(RoleSelectorConfig.classes.enhanced);
            this.selectors.add($selector[0]);
            
            // 添加加载状态
            this.setLoadingState($selector, true);
            
            // 绑定选择器事件
            this.bindSelectorEvents($selector);
            
            // 加载角色数据
            this.populateSelector($selector);
        }
        
        // 绑定选择器事件
        bindSelectorEvents($selector) {
            // 角色变更事件
            $selector.on('change', (e) => {
                const selectedRole = $(e.target).val();
                this.validateRole(selectedRole, $selector);
                
                // 触发自定义事件
                $(document).trigger('role:changed', {
                    selector: $selector,
                    role: selectedRole,
                    element: e.target
                });
            });
            
            // 焦点事件
            $selector.on('focus', () => {
                $selector.removeClass(RoleSelectorConfig.classes.error);
            });
        }
        
        // 加载角色数据
        async loadRoleData() {
            try {
                // 检查缓存
                const cachedData = this.getCachedData();
                if (cachedData) {
                    this.updateAllSelectors(cachedData);
                    return;
                }
                
                // 从API加载
                const response = await this.fetchRoleChoices();
                if (response.success) {
                    this.setCachedData(response.data);
                    this.updateAllSelectors(response.data);
                } else {
                    console.error('加载角色数据失败:', response.error);
                    this.handleLoadError();
                }
            } catch (error) {
                console.error('角色数据加载异常:', error);
                this.handleLoadError();
            }
        }
        
        // 获取角色选择项
        async fetchRoleChoices() {
            const response = await fetch(RoleSelectorConfig.endpoints.choices, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            return await response.json();
        }
        
        // 验证角色
        async validateRole(role, $selector) {
            if (!role) {
                $selector.removeClass(RoleSelectorConfig.classes.valid + ' ' + RoleSelectorConfig.classes.invalid);
                return;
            }
            
            try {
                const url = RoleSelectorConfig.endpoints.validate.replace('{role}', encodeURIComponent(role));
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });
                
                const result = await response.json();
                if (result.success && result.valid) {
                    $selector.removeClass(RoleSelectorConfig.classes.invalid)
                            .addClass(RoleSelectorConfig.classes.valid);
                } else {
                    $selector.removeClass(RoleSelectorConfig.classes.valid)
                            .addClass(RoleSelectorConfig.classes.invalid);
                }
            } catch (error) {
                console.error('角色验证失败:', error);
            }
        }
        
        // 填充选择器选项
        populateSelector($selector) {
            const cachedData = this.getCachedData();
            if (cachedData) {
                this.updateSelector($selector, cachedData);
            }
        }
        
        // 更新单个选择器
        updateSelector($selector, roleData) {
            const currentValue = $selector.val();
            
            // 清空现有选项（保留空选项）
            $selector.find('option:not([value=""])').remove();
            
            // 添加角色选项
            roleData.forEach(role => {
                const option = $('<option></option>')
                    .attr('value', role.value)
                    .text(role.display_name);
                
                if (role.value === currentValue) {
                    option.prop('selected', true);
                }
                
                $selector.append(option);
            });
            
            // 移除加载状态
            this.setLoadingState($selector, false);
        }
        
        // 更新所有选择器
        updateAllSelectors(roleData) {
            this.selectors.forEach(selector => {
                this.updateSelector($(selector), roleData);
            });
        }
        
        // 处理角色变更
        handleRoleChange(data) {
            // 可以在这里添加角色变更后的逻辑
            console.log('角色已变更:', data);
        }
        
        // 设置加载状态
        setLoadingState($selector, loading) {
            if (loading) {
                $selector.addClass(RoleSelectorConfig.classes.loading)
                        .prop('disabled', true);
            } else {
                $selector.removeClass(RoleSelectorConfig.classes.loading)
                        .prop('disabled', false);
            }
        }
        
        // 处理加载错误
        handleLoadError() {
            this.selectors.forEach(selector => {
                const $selector = $(selector);
                $selector.addClass(RoleSelectorConfig.classes.error);
                this.setLoadingState($selector, false);
            });
        }
        
        // 缓存管理
        getCachedData() {
            if (!RoleSelectorConfig.cache.enabled) return null;
            
            const cached = localStorage.getItem(RoleSelectorConfig.cache.key);
            if (!cached) return null;
            
            try {
                const data = JSON.parse(cached);
                const now = Date.now();
                
                if (now - data.timestamp > RoleSelectorConfig.cache.duration) {
                    localStorage.removeItem(RoleSelectorConfig.cache.key);
                    return null;
                }
                
                return data.roles;
            } catch (error) {
                localStorage.removeItem(RoleSelectorConfig.cache.key);
                return null;
            }
        }
        
        setCachedData(roles) {
            if (!RoleSelectorConfig.cache.enabled) return;
            
            const data = {
                roles: roles,
                timestamp: Date.now()
            };
            
            try {
                localStorage.setItem(RoleSelectorConfig.cache.key, JSON.stringify(data));
            } catch (error) {
                console.warn('无法缓存角色数据:', error);
            }
        }
        
        // 刷新缓存
        async refreshCache() {
            localStorage.removeItem(RoleSelectorConfig.cache.key);
            await this.loadRoleData();
        }
        
        // 获取CSRF令牌
        getCSRFToken() {
            return $('[name=csrfmiddlewaretoken]').val() || 
                   $('meta[name=csrf-token]').attr('content') || 
                   '';
        }
        
        // 公共API
        static getInstance() {
            if (!window.roleSelectorManager) {
                window.roleSelectorManager = new RoleSelectorManager();
            }
            return window.roleSelectorManager;
        }
    }
    
    // 工具函数
    const RoleSelectorUtils = {
        // 手动增强选择器
        enhance: function(selector) {
            const manager = RoleSelectorManager.getInstance();
            manager.enhanceSelector($(selector));
        },
        
        // 刷新角色数据
        refresh: function() {
            $(document).trigger('role:cache:refresh');
        },
        
        // 获取角色统计
        getStats: async function() {
            try {
                const response = await fetch(RoleSelectorConfig.endpoints.stats);
                return await response.json();
            } catch (error) {
                console.error('获取角色统计失败:', error);
                return null;
            }
        }
    };
    
    // 初始化
    $(document).ready(function() {
        RoleSelectorManager.getInstance();
    });
    
    // 导出到全局
    window.RoleSelectorManager = RoleSelectorManager;
    window.RoleSelectorUtils = RoleSelectorUtils;
    
})(django.jQuery || jQuery);