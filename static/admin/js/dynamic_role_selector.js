/**
 * 动态角色选择器 - 统一角色数据源管理
 * 确保所有角色选择器使用RoleService提供的统一数据
 */

(function($) {
    'use strict';
    
    // 角色选择器配置
    const RoleSelectorConfig = {
        // API端点
        endpoints: {
            roleChoices: '/admin/permissions/rolegroupmapping/get-role-list/',
            roleInfo: '/admin/accounts/customuser/get-role-info/',
            roleMenuPermissionRoleList: '/admin/permissions/rolemenupermission/get-role-list/'
        },
        
        // 缓存配置
        cache: {
            roles: null,
            timestamp: null,
            ttl: 300000 // 5分钟缓存
        },
        
        // 选择器类名
        selectors: {
            roleField: 'select[name="role"], input[name="role"], select[id*="role"], input[id*="role"], .role-selector',
            roleMenuPermissionForm: '#rolemenupermission_form',
            roleGroupMappingForm: '#rolegroupmapping_form'
        },
        
        // 表单特定配置
        forms: {
            roleMenuPermission: {
                formId: 'rolemenupermission_form',
                roleFieldSelector: '#id_role',
                endpoint: '/admin/permissions/rolemenupermission/get-role-list/'
            }
        }
    };
    
    /**
     * 角色数据管理器
     */
    const RoleDataManager = {
        /**
         * 获取角色选择项
         */
        async getRoleChoices() {
            // 检查缓存
            if (this.isCacheValid()) {
                return RoleSelectorConfig.cache.roles;
            }
            
            try {
                const response = await $.ajax({
                    url: RoleSelectorConfig.endpoints.roleChoices,
                    method: 'GET',
                    dataType: 'json'
                });
                
                if (response.success && response.roles) {
                    // 更新缓存
                    RoleSelectorConfig.cache.roles = response.roles;
                    RoleSelectorConfig.cache.timestamp = Date.now();
                    return response.roles;
                }
            } catch (error) {
                console.error('获取角色数据失败:', error);
            }
            
            // 返回默认角色
            return this.getDefaultRoles();
        },
        
        /**
         * 检查缓存是否有效
         */
        isCacheValid() {
            return RoleSelectorConfig.cache.roles && 
                   RoleSelectorConfig.cache.timestamp && 
                   (Date.now() - RoleSelectorConfig.cache.timestamp) < RoleSelectorConfig.cache.ttl;
        },
        
        /**
         * 获取默认角色（备用）
         */
        getDefaultRoles() {
            return [
                { value: 'student', display_name: '学生' },
                { value: 'parent', display_name: '家长' },
                { value: 'teacher', display_name: '自由老师' },
                { value: 'admin', display_name: '管理员' },
                { value: 'dean', display_name: '教导主任' },
                { value: 'academic_director', display_name: '教务主任' },
                { value: 'research_leader', display_name: '教研组长' }
            ];
        },
        
        /**
         * 清除缓存
         */
        clearCache() {
            RoleSelectorConfig.cache.roles = null;
            RoleSelectorConfig.cache.timestamp = null;
        }
    };
    
    /**
     * 角色选择器增强器
     */
    const RoleSelectorEnhancer = {
        /**
         * 初始化角色选择器
         */
        async init() {
            console.log('Dynamic Role Selector: 初始化中...');
            
            // 等待DOM加载完成
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.enhance());
            } else {
                await this.enhance();
            }
        },
        
        /**
         * 增强所有角色选择器
         */
        async enhance() {
            // 检查是否是RoleMenuPermission表单，优先处理
            const roleMenuPermissionForm = $(RoleSelectorConfig.selectors.roleMenuPermissionForm);
            if (roleMenuPermissionForm.length > 0) {
                await this.enhanceRoleMenuPermissionForm();
                return;
            }
            
            const roleFields = $(RoleSelectorConfig.selectors.roleField);
            
            if (roleFields.length === 0) {
                console.log('Dynamic Role Selector: 未找到角色选择器字段');
                return;
            }
            
            console.log(`Dynamic Role Selector: 找到 ${roleFields.length} 个角色选择器`);
            
            // 获取角色数据
            const roles = await RoleDataManager.getRoleChoices();
            
            // 增强每个角色选择器
            roleFields.each((index, field) => {
                this.enhanceField($(field), roles);
            });
        },
        
        /**
         * 增强单个角色字段
         */
        enhanceField($field, roles) {
            const currentValue = $field.val();
            const fieldName = $field.attr('name');
            const fieldId = $field.attr('id');
            
            // 如果是input字段，需要转换为select
            if ($field.is('input')) {
                const $select = $('<select></select>')
                    .attr('name', fieldName)
                    .attr('id', fieldId)
                    .addClass($field.attr('class'))
                    .attr('required', $field.attr('required'));
                
                // 复制其他属性
                if ($field.attr('data-placeholder')) {
                    $select.attr('data-placeholder', $field.attr('data-placeholder'));
                }
                
                // 替换input为select
                $field.replaceWith($select);
                $field = $select;
            }
            
            // 清空现有选项（保留空选项）
            const emptyOption = $field.find('option[value=""]');
            $field.empty();
            
            // 添加空选项
            if (emptyOption.length > 0) {
                $field.append(emptyOption);
            } else {
                $field.append('<option value="">---------</option>');
            }
            
            // 添加角色选项
            roles.forEach(role => {
                const option = $('<option></option>')
                    .attr('value', role.value)
                    .text(role.display_name);
                
                if (role.value === currentValue) {
                    option.prop('selected', true);
                }
                
                $field.append(option);
            });
            
            // 添加变更事件监听
            $field.off('change.roleSelector').on('change.roleSelector', function() {
                console.log('角色选择变更:', $(this).val());
            });
            
            console.log(`Dynamic Role Selector: 已增强字段 ${fieldName || fieldId}`);
        },
        
        /**
         * 特殊处理RoleMenuPermission表单
         */
        async enhanceRoleMenuPermissionForm() {
            const $form = $(RoleSelectorConfig.selectors.roleMenuPermissionForm);
            if ($form.length === 0) {
                return;
            }
            
            try {
                // 查找角色字段（包括input和select）
                const $roleField = $form.find('select[name="role"], input[name="role"], #id_role');
                if ($roleField.length === 0) {
                    console.warn('RoleMenuPermission表单中未找到角色字段');
                    return;
                }
                
                // 使用专用端点获取角色数据
                const response = await $.ajax({
                    url: RoleSelectorConfig.forms.roleMenuPermission.endpoint,
                    method: 'GET',
                    dataType: 'json'
                });
                
                if (response.success && response.roles) {
                    this.enhanceField($roleField, response.roles);
                    console.log('Dynamic Role Selector: 已增强RoleMenuPermission表单角色选择器');
                } else {
                    throw new Error(response.error || '获取角色数据失败');
                }
                
            } catch (error) {
                console.error('增强RoleMenuPermission表单失败:', error);
                // 降级到默认角色数据
                const roles = await RoleDataManager.getRoleChoices();
                const $roleField = $form.find('select[name="role"], input[name="role"], #id_role');
                if ($roleField.length > 0) {
                    this.enhanceField($roleField, roles);
                }
            }
        },
        
        /**
         * 刷新所有角色选择器
         */
        async refresh() {
            RoleDataManager.clearCache();
            await this.enhance();
        }
    };
    
    /**
     * 全局API
     */
    window.DynamicRoleSelector = {
        init: () => RoleSelectorEnhancer.init(),
        refresh: () => RoleSelectorEnhancer.refresh(),
        getRoles: () => RoleDataManager.getRoleChoices(),
        clearCache: () => RoleDataManager.clearCache()
    };
    
    // 自动初始化
    $(document).ready(function() {
        RoleSelectorEnhancer.init();
    });
    
    // 使用MutationObserver替代废弃的DOMNodeInserted
    if (typeof MutationObserver !== 'undefined') {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Element node
                            const $node = $(node);
                            if ($node.find && $node.find(RoleSelectorConfig.selectors.roleField).length > 0) {
                                setTimeout(() => RoleSelectorEnhancer.enhance(), 100);
                            }
                        }
                    });
                }
            });
        });
        
        // 确保document.body存在后再开始观察
        if (document.body) {
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        } else {
            // 如果body还未加载，等待DOM加载完成
            document.addEventListener('DOMContentLoaded', function() {
                if (document.body) {
                    observer.observe(document.body, {
                        childList: true,
                        subtree: true
                    });
                }
            });
        }
    }
    
})(django.jQuery || jQuery);