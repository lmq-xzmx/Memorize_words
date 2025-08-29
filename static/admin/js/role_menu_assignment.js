/**
 * 角色菜单分配管理页面的JavaScript功能
 * 实现角色依赖的菜单模块筛选和槽位位置动态验证
 */

(function($) {
    'use strict';
    
    // 检查是否有新的组件系统可用
    const hasNewComponents = window.FrontendMenuSelectorFactory && 
                            window.FrontendMenuSelectorConfig;

    // 页面加载完成后初始化
    $(document).ready(function() {
        if (hasNewComponents) {
            // 使用新的组件系统
            initWithNewComponents();
        } else {
            // 使用原有逻辑作为降级方案
            initRoleMenuAssignment();
        }
    });

    // 使用新组件系统初始化
    function initWithNewComponents() {
        console.log('Using new component system for role menu assignment');
        
        // 让组件系统处理角色菜单分配
        // 这里主要是兼容性处理，实际逻辑由组件处理
        const config = window.FrontendMenuSelectorConfig.getRoleMenuAssignmentConfig();
        window.frontendMenuSelectorFactory.create('roleMenuAssignment', config);
    }
    
    function initRoleMenuAssignment() {
        const roleField = $('#id_role');
        const menuModuleField = $('#id_menu_module');
        const slotPositionField = $('#id_slot_position');
        
        if (roleField.length && menuModuleField.length) {
            // 监听角色选择变化
            roleField.on('change', function() {
                const selectedRole = $(this).val();
                updateMenuModulesForRole(selectedRole, menuModuleField);
                updateMaxSlotPosition(selectedRole, slotPositionField);
            });
            
            // 页面加载时如果已有角色选择，则更新菜单模块
            const initialRole = roleField.val();
            if (initialRole) {
                updateMenuModulesForRole(initialRole, menuModuleField);
                updateMaxSlotPosition(initialRole, slotPositionField);
            }
        }
        
        // 监听槽位位置变化，进行实时验证
        if (slotPositionField.length) {
            slotPositionField.on('change blur', function() {
                validateSlotPosition($(this), roleField.val());
            });
        }
    }
    
    /**
     * 根据角色更新菜单模块选项
     */
    function updateMenuModulesForRole(role, menuModuleField) {
        if (!role) {
            // 如果没有选择角色，清空菜单模块选项
            menuModuleField.empty().append('<option value="">---------</option>');
            return;
        }
        
        // 显示加载状态
        menuModuleField.prop('disabled', true);
        const loadingOption = '<option value="">正在加载...</option>';
        menuModuleField.html(loadingOption);
        
        // 发送AJAX请求获取该角色可用的菜单模块
        $.ajax({
            url: '../get-menus-for-role/',
            type: 'GET',
            data: { role: role },
            success: function(response) {
                menuModuleField.empty();
                menuModuleField.append('<option value="">---------</option>');
                
                if (response.menus && response.menus.length > 0) {
                    $.each(response.menus, function(index, menu) {
                        const optionText = `${menu.name} (${menu.menu_level})`;
                        menuModuleField.append(
                            `<option value="${menu.id}">${optionText}</option>`
                        );
                    });
                } else {
                    menuModuleField.append('<option value="">该角色暂无可用菜单</option>');
                }
                
                menuModuleField.prop('disabled', false);
            },
            error: function(xhr, status, error) {
                console.error('获取菜单模块失败:', error);
                menuModuleField.empty();
                menuModuleField.append('<option value="">加载失败，请重试</option>');
                menuModuleField.prop('disabled', false);
                
                // 显示错误提示
                showMessage('获取菜单模块失败，请检查网络连接后重试', 'error');
            }
        });
    }
    
    /**
     * 根据角色更新槽位位置的最大值
     */
    function updateMaxSlotPosition(role, slotPositionField) {
        if (!role || !slotPositionField.length) {
            return;
        }
        
        // 发送AJAX请求获取该角色的最大槽位数
        $.ajax({
            url: '../get-max-slot-position/',
            type: 'GET',
            data: { role: role },
            success: function(response) {
                const maxSlot = response.max_slot || 4;
                
                // 更新槽位位置字段的最大值属性
                slotPositionField.attr('max', maxSlot);
                
                // 更新字段的帮助文本
                updateSlotPositionHelpText(slotPositionField, maxSlot);
                
                // 如果当前值超过最大值，显示警告
                const currentValue = parseInt(slotPositionField.val());
                if (currentValue && currentValue > maxSlot) {
                    showSlotPositionWarning(slotPositionField, currentValue, maxSlot);
                } else {
                    clearSlotPositionWarning(slotPositionField);
                }
            },
            error: function(xhr, status, error) {
                console.error('获取最大槽位数失败:', error);
            }
        });
    }
    
    /**
     * 验证槽位位置
     */
    function validateSlotPosition(slotPositionField, role) {
        if (!role) {
            return;
        }
        
        const currentValue = parseInt(slotPositionField.val());
        const maxValue = parseInt(slotPositionField.attr('max')) || 4;
        
        if (currentValue && currentValue > maxValue) {
            showSlotPositionWarning(slotPositionField, currentValue, maxValue);
        } else {
            clearSlotPositionWarning(slotPositionField);
        }
    }
    
    /**
     * 更新槽位位置字段的帮助文本
     */
    function updateSlotPositionHelpText(slotPositionField, maxSlot) {
        let helpText = slotPositionField.siblings('.help');
        if (helpText.length === 0) {
            helpText = $('<div class="help"></div>');
            slotPositionField.after(helpText);
        }
        helpText.text(`当前角色最大槽位数: ${maxSlot}`);
    }
    
    /**
     * 显示槽位位置警告
     */
    function showSlotPositionWarning(slotPositionField, currentValue, maxValue) {
        clearSlotPositionWarning(slotPositionField);
        
        const warningMsg = `警告: 槽位位置 ${currentValue} 超过最大值 ${maxValue}`;
        const warningDiv = $(`<div class="slot-position-warning" style="color: #d63384; font-size: 12px; margin-top: 5px;">${warningMsg}</div>`);
        
        slotPositionField.after(warningDiv);
        slotPositionField.addClass('is-invalid');
    }
    
    /**
     * 清除槽位位置警告
     */
    function clearSlotPositionWarning(slotPositionField) {
        slotPositionField.siblings('.slot-position-warning').remove();
        slotPositionField.removeClass('is-invalid');
    }
    
    /**
     * 显示消息提示
     */
    function showMessage(message, type) {
        type = type || 'info';
        const messageClass = type === 'error' ? 'error' : 'success';
        
        // 创建消息元素
        const messageDiv = $(`
            <div class="messagelist">
                <div class="${messageClass}">${message}</div>
            </div>
        `);
        
        // 插入到页面顶部
        const contentMain = $('.content-main, #content-main, .main');
        if (contentMain.length) {
            contentMain.prepend(messageDiv);
        } else {
            $('body').prepend(messageDiv);
        }
        
        // 3秒后自动隐藏
        setTimeout(function() {
            messageDiv.fadeOut(500, function() {
                $(this).remove();
            });
        }, 3000);
    }
    
    // 导出函数供其他脚本使用
    window.roleMenuAssignment = {
        updateMenuModulesForRole: updateMenuModulesForRole,
        updateMaxSlotPosition: updateMaxSlotPosition,
        validateSlotPosition: validateSlotPosition,
        initWithNewComponents: hasNewComponents ? initWithNewComponents : null,
        initRoleMenuAssignment: initRoleMenuAssignment,
        hasNewComponents: hasNewComponents
    };
    
})(django.jQuery || jQuery);