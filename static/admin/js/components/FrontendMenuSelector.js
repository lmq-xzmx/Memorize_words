/**
 * 前端菜单选择器组件
 * 解决RelatedObjectLookups.js权限策略违规问题，提供统一的前端菜单选择功能
 * 支持角色依赖的菜单筛选和动态加载
 */

(function(global) {
    'use strict';
    
    /**
     * 前端菜单选择器类
     */
    class FrontendMenuSelector {
        constructor(options = {}) {
            this.options = {
                // 菜单字段选择器
                menuFieldSelector: '#id_menu',
                // 角色字段选择器
                roleFieldSelector: '#id_role',
                // API端点配置
                apiEndpoints: {
                    getMenusForRole: '/admin/permissions/frontendmenuroleassignment/get-menus-for-role/',
                    getAllMenus: '/admin/permissions/frontendmenuconfig/get-all-menus/'
                },
                // 是否启用角色依赖筛选
                enableRoleFiltering: true,
                // 是否启用层级显示
                enableHierarchy: true,
                // 空选项文本
                emptyOptionText: '---------',
                // 加载提示文本
                loadingText: '加载中...',
                // 错误提示文本
                errorText: '加载失败，请重试',
                // 回调函数
                onMenuChange: null,
                onRoleChange: null,
                onError: null,
                ...options
            };
            
            this.menuField = null;
            this.roleField = null;
            this.originalMenuOptions = [];
            this.isInitialized = false;
            
            this.init();
        }
        
        /**
         * 初始化组件
         */
        init() {
            if (this.isInitialized) {
                console.warn('FrontendMenuSelector already initialized');
                return;
            }
            
            this.findElements();
            this.bindEvents();
            this.saveOriginalOptions();
            this.loadInitialData();
            
            this.isInitialized = true;
        }
        
        /**
         * 查找DOM元素
         */
        findElements() {
            const $ = this.getJQuery();
            
            this.menuField = $(this.options.menuFieldSelector);
            this.roleField = $(this.options.roleFieldSelector);
            
            if (!this.menuField.length) {
                throw new Error(`Menu field not found: ${this.options.menuFieldSelector}`);
            }
        }
        
        /**
         * 绑定事件
         */
        bindEvents() {
            const self = this;
            
            // 角色变化事件
            if (this.roleField.length && this.options.enableRoleFiltering) {
                this.roleField.on('change', function() {
                    const selectedRole = $(this).val();
                    self.handleRoleChange(selectedRole);
                });
            }
            
            // 菜单变化事件
            this.menuField.on('change', function() {
                const selectedMenu = $(this).val();
                self.handleMenuChange(selectedMenu);
            });
            
            // 避免使用unload事件，使用beforeunload替代
            window.addEventListener('beforeunload', function() {
                self.cleanup();
            });
        }
        
        /**
         * 保存原始菜单选项
         */
        saveOriginalOptions() {
            const $ = this.getJQuery();
            this.originalMenuOptions = [];
            
            this.menuField.find('option').each(function() {
                const $option = $(this);
                self.originalMenuOptions.push({
                    value: $option.val(),
                    text: $option.text(),
                    selected: $option.prop('selected'),
                    data: $option.data()
                });
            });
        }
        
        /**
         * 加载初始数据
         */
        loadInitialData() {
            if (this.roleField.length && this.options.enableRoleFiltering) {
                const initialRole = this.roleField.val();
                if (initialRole) {
                    this.loadMenusForRole(initialRole);
                }
            }
        }
        
        /**
         * 处理角色变化
         */
        handleRoleChange(role) {
            if (this.options.onRoleChange) {
                this.options.onRoleChange(role);
            }
            
            if (!role) {
                this.resetMenuOptions();
                return;
            }
            
            this.loadMenusForRole(role);
        }
        
        /**
         * 处理菜单变化
         */
        handleMenuChange(menuId) {
            if (this.options.onMenuChange) {
                this.options.onMenuChange(menuId);
            }
        }
        
        /**
         * 为指定角色加载菜单
         */
        loadMenusForRole(role) {
            const $ = this.getJQuery();
            const self = this;
            
            // 显示加载状态
            this.setLoadingState(true);
            
            $.ajax({
                url: this.options.apiEndpoints.getMenusForRole,
                type: 'GET',
                data: { role: role },
                dataType: 'json',
                success: function(response) {
                    self.setLoadingState(false);
                    
                    if (response.success) {
                        self.updateMenuOptions(response.menus);
                    } else {
                        self.handleError(response.error || '获取菜单数据失败');
                    }
                },
                error: function(xhr, status, error) {
                    self.setLoadingState(false);
                    self.handleError(`AJAX请求失败: ${error}`);
                }
            });
        }
        
        /**
         * 更新菜单选项
         */
        updateMenuOptions(menus) {
            const $ = this.getJQuery();
            const currentValue = this.menuField.val();
            
            // 清空现有选项
            this.menuField.empty();
            
            // 添加空选项
            this.menuField.append(`<option value="">${this.options.emptyOptionText}</option>`);
            
            // 添加菜单选项
            menus.forEach(menu => {
                const optionText = this.options.enableHierarchy && menu.level > 0 
                    ? '　'.repeat(menu.level) + menu.name
                    : menu.name;
                    
                const $option = $(`<option value="${menu.id}">${optionText}</option>`);
                
                // 添加数据属性
                if (menu.menu_type) $option.data('menu-type', menu.menu_type);
                if (menu.position) $option.data('position', menu.position);
                if (menu.parent_id) $option.data('parent-id', menu.parent_id);
                
                this.menuField.append($option);
            });
            
            // 恢复之前的选择
            if (currentValue) {
                this.menuField.val(currentValue);
            }
            
            // 触发change事件
            this.menuField.trigger('change');
        }
        
        /**
         * 重置菜单选项到原始状态
         */
        resetMenuOptions() {
            const $ = this.getJQuery();
            
            this.menuField.empty();
            
            this.originalMenuOptions.forEach(option => {
                const $option = $(`<option value="${option.value}">${option.text}</option>`);
                
                if (option.selected) {
                    $option.prop('selected', true);
                }
                
                // 恢复数据属性
                if (option.data) {
                    Object.keys(option.data).forEach(key => {
                        $option.data(key, option.data[key]);
                    });
                }
                
                this.menuField.append($option);
            });
        }
        
        /**
         * 设置加载状态
         */
        setLoadingState(isLoading) {
            if (isLoading) {
                this.menuField.prop('disabled', true);
                this.menuField.empty().append(`<option value="">${this.options.loadingText}</option>`);
            } else {
                this.menuField.prop('disabled', false);
            }
        }
        
        /**
         * 处理错误
         */
        handleError(error) {
            console.error('FrontendMenuSelector Error:', error);
            
            if (this.options.onError) {
                this.options.onError(error);
            }
            
            // 显示错误状态
            this.menuField.empty().append(`<option value="">${this.options.errorText}</option>`);
            
            // 3秒后恢复原始选项
            setTimeout(() => {
                this.resetMenuOptions();
            }, 3000);
        }
        
        /**
         * 获取jQuery实例
         */
        getJQuery() {
            return global.django && global.django.jQuery || global.jQuery || global.$;
        }
        
        /**
         * 获取当前选中的菜单
         */
        getSelectedMenu() {
            return this.menuField.val();
        }
        
        /**
         * 设置选中的菜单
         */
        setSelectedMenu(menuId) {
            this.menuField.val(menuId).trigger('change');
        }
        
        /**
         * 获取当前选中的角色
         */
        getSelectedRole() {
            return this.roleField.length ? this.roleField.val() : null;
        }
        
        /**
         * 刷新菜单数据
         */
        refresh() {
            const currentRole = this.getSelectedRole();
            if (currentRole && this.options.enableRoleFiltering) {
                this.loadMenusForRole(currentRole);
            } else {
                this.resetMenuOptions();
            }
        }
        
        /**
         * 销毁组件
         */
        destroy() {
            if (this.menuField) {
                this.menuField.off('change');
            }
            
            if (this.roleField) {
                this.roleField.off('change');
            }
            
            this.cleanup();
            this.isInitialized = false;
        }
        
        /**
         * 清理资源
         */
        cleanup() {
            // 清理可能的定时器或其他资源
        }
    }
    
    // 导出到全局
    global.FrontendMenuSelector = FrontendMenuSelector;
    
    // 如果是模块环境，也支持模块导出
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = FrontendMenuSelector;
    }
    
})(typeof window !== 'undefined' ? window : this);