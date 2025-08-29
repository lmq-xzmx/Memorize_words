/**
 * 角色槽位菜单分配管理页面的JavaScript功能
 * 实现根据角色和槽位数值进行菜单配置的功能
 */

(function() {
    'use strict';
    
    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        // 检查jQuery是否可用
        if (typeof django !== 'undefined' && django.jQuery) {
            var $ = django.jQuery;
            initRoleSlotMenuAssignment($);
            initMenuConfigPanel($);
        } else if (typeof jQuery !== 'undefined') {
            var $ = jQuery;
            initRoleSlotMenuAssignment($);
            initMenuConfigPanel($);
        } else {
            console.warn('jQuery not available, role slot menu assignment features disabled');
        }
    });
    
    function initRoleSlotMenuAssignment($) {
        const roleField = $('#id_role');
        const slotPositionField = $('#id_slot_position');
        const rootMenuField = $('#id_root_menu');
        
        if (!roleField.length || !slotPositionField.length || !rootMenuField.length) {
            // 只在表单页面（add/change）显示警告，changelist页面不需要这些元素
            if (window.location.pathname.includes('/add/') || window.location.pathname.includes('/change/')) {
                console.log('Role slot menu assignment form elements not found, skipping initialization');
            }
            return;
        }
        
        if (roleField.length) {
            // 监听角色选择变化
            roleField.on('change', function() {
                const selectedRole = $(this).val();
                updateMaxSlotPosition(selectedRole, slotPositionField, $);
                updateAvailableMenus(selectedRole, rootMenuField, $);
            });
            
            // 页面加载时如果已有角色选择，则更新相关字段
            const initialRole = roleField.val();
            if (initialRole) {
                updateMaxSlotPosition(initialRole, slotPositionField, $);
                updateAvailableMenus(initialRole, rootMenuField, $);
            }
        }
        
        // 监听槽位位置变化，进行实时验证
        if (slotPositionField.length) {
            slotPositionField.on('change blur', function() {
                validateSlotPosition($(this), roleField.val(), $);
            });
        }
    }
    
    function initMenuConfigPanel($) {
        // 初始化菜单配置面板的事件监听
        const configPanel = $('#menu-config-panel');
        if (configPanel.length) {
            // 快速配置表单提交
            $('#quick-config-form').on('submit', function(e) {
                e.preventDefault();
                submitQuickConfig($);
            });
            
            // 功能按钮事件
            $('#validate-capacity-btn').on('click', function() { validateSlotCapacity($); });
            $('#optimize-slots-btn').on('click', function() { optimizeSlots($); });
            $('#batch-assign-btn').on('click', showBatchAssignModal);
            $('#refresh-data-btn').on('click', function() { refreshConfigData($); });
            
            // 加载初始配置数据
            loadConfigData($);
        }
    }
    
    /**
     * 根据角色更新最大槽位数
     */
    function updateMaxSlotPosition(role, slotPositionField, $) {
        if (!role || !slotPositionField.length) {
            return;
        }
        
        $.ajax({
            url: '../get-max-slot-position/',
            type: 'GET',
            data: { role: role },
            success: function(response) {
                const maxSlot = response.max_slot || 5;
                
                // 更新槽位位置字段的最大值属性
                slotPositionField.attr('max', maxSlot);
                
                // 更新字段的帮助文本
                updateSlotPositionHelpText(slotPositionField, maxSlot, $);
                
                // 如果当前值超过最大值，显示警告
                const currentValue = parseInt(slotPositionField.val());
                if (currentValue && currentValue > maxSlot) {
                    showSlotPositionWarning(slotPositionField, currentValue, maxSlot, $);
                } else {
                    clearSlotPositionWarning(slotPositionField, $);
                }
            },
            error: function(xhr, status, error) {
                console.error('获取最大槽位数失败:', error);
            }
        });
    }
    
    /**
     * 根据角色更新可用菜单
     */
    function updateAvailableMenus(role, rootMenuField, $) {
        if (!role || !rootMenuField.length) {
            return;
        }
        
        // 显示加载状态
        rootMenuField.prop('disabled', true);
        const loadingOption = '<option value="">正在加载...</option>';
        rootMenuField.html(loadingOption);
        
        $.ajax({
            url: '../get-menus-for-role/',
            type: 'GET',
            data: { role: role },
            success: function(response) {
                rootMenuField.empty();
                rootMenuField.append('<option value="">---------</option>');
                
                if (response.menus && response.menus.length > 0) {
                    $.each(response.menus, function(index, menu) {
                        const optionText = `${menu.name} (${menu.menu_level})`;
                        rootMenuField.append(
                            `<option value="${menu.id}">${optionText}</option>`
                        );
                    });
                } else {
                    rootMenuField.append('<option value="">该角色暂无可用菜单</option>');
                }
                
                rootMenuField.prop('disabled', false);
            },
            error: function(xhr, status, error) {
                console.error('获取菜单失败:', error);
                rootMenuField.empty();
                rootMenuField.append('<option value="">加载失败，请重试</option>');
                rootMenuField.prop('disabled', false);
                
                showMessage('获取菜单失败，请检查网络连接后重试', 'error', $);
            }
        });
    }
    
    /**
     * 验证槽位位置
     */
    function validateSlotPosition(slotPositionField, role, $) {
        if (!role) {
            return;
        }
        
        const currentValue = parseInt(slotPositionField.val());
        const maxValue = parseInt(slotPositionField.attr('max')) || 5;
        
        if (currentValue && currentValue > maxValue) {
            showSlotPositionWarning(slotPositionField, currentValue, maxValue, $);
        } else {
            clearSlotPositionWarning(slotPositionField, $);
        }
    }
    
    /**
     * 更新槽位位置帮助文本
     */
    function updateSlotPositionHelpText(slotPositionField, maxSlot, $) {
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
    function showSlotPositionWarning(slotPositionField, currentValue, maxValue, $) {
        clearSlotPositionWarning(slotPositionField, $);
        
        const warningMsg = `警告: 槽位位置 ${currentValue} 超过最大值 ${maxValue}`;
        const warningDiv = $(`<div class="slot-position-warning" style="color: #d63384; font-size: 12px; margin-top: 5px;">${warningMsg}</div>`);
        
        slotPositionField.after(warningDiv);
        slotPositionField.addClass('is-invalid');
    }
    
    /**
     * 清除槽位位置警告
     */
    function clearSlotPositionWarning(slotPositionField, $) {
        slotPositionField.siblings('.slot-position-warning').remove();
        slotPositionField.removeClass('is-invalid');
    }
    
    /**
     * 加载配置数据
     */
    function loadConfigData($) {
        $.ajax({
            url: 'configure-menu-by-role-slot/',
            type: 'GET',
            success: function(response) {
                if (response.status === 'success') {
                    updateConfigDisplay(response.data, $);
                } else {
                    showMessage('加载配置数据失败: ' + response.message, 'error', $);
                }
            },
            error: function(xhr, status, error) {
                console.error('加载配置数据失败:', error);
                showMessage('加载配置数据失败，请刷新页面重试', 'error', $);
            }
        });
    }
    
    /**
     * 更新配置显示
     */
    function updateConfigDisplay(data, $) {
        const statusDiv = $('#config-status');
        if (statusDiv.length && data) {
            let html = '<h4>当前配置状态</h4>';
            html += `<p>总角色数: ${data.total_roles || 0}</p>`;
            html += `<p>已配置槽位: ${data.configured_slots || 0}</p>`;
            html += `<p>活跃菜单: ${data.active_menus || 0}</p>`;
            statusDiv.html(html);
        }
    }
    
    /**
     * 提交快速配置
     */
    function submitQuickConfig($) {
        const formData = $('#quick-config-form').serialize();
        
        $.ajax({
            url: 'configure-menu-by-role-slot/',
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.status === 'success') {
                    showMessage('配置保存成功', 'success', $);
                    loadConfigData($); // 重新加载数据
                } else {
                    showMessage('配置保存失败: ' + response.message, 'error', $);
                }
            },
            error: function(xhr, status, error) {
                console.error('配置保存失败:', error);
                showMessage('配置保存失败，请重试', 'error', $);
            }
        });
    }
    
    /**
     * 验证槽位容量
     */
    function validateSlotCapacity($) {
        $.ajax({
            url: 'validate-slot-capacity/',
            type: 'POST',
            success: function(response) {
                if (response.status === 'success') {
                    showMessage('槽位容量验证通过', 'success', $);
                } else {
                    showMessage('槽位容量验证失败: ' + response.message, 'warning', $);
                }
            },
            error: function(xhr, status, error) {
                console.error('槽位容量验证失败:', error);
                showMessage('槽位容量验证失败，请重试', 'error', $);
            }
        });
    }
    
    /**
     * 优化槽位
     */
    function optimizeSlots($) {
        if (!confirm('确定要自动优化槽位分配吗？这可能会调整现有配置。')) {
            return;
        }
        
        $.ajax({
            url: 'auto-optimize-slots/',
            type: 'POST',
            success: function(response) {
                if (response.status === 'success') {
                    showMessage('槽位优化完成', 'success', $);
                    loadConfigData($); // 重新加载数据
                    location.reload(); // 刷新页面以显示更新
                } else {
                    showMessage('槽位优化失败: ' + response.message, 'error', $);
                }
            },
            error: function(xhr, status, error) {
                console.error('槽位优化失败:', error);
                showMessage('槽位优化失败，请重试', 'error', $);
            }
        });
    }
    
    /**
     * 显示批量分配模态框
     */
    function showBatchAssignModal() {
        // 这里可以实现批量分配的模态框逻辑
        alert('批量分配功能开发中...');
    }
    
    /**
     * 刷新配置数据
     */
    function refreshConfigData($) {
        loadConfigData($);
        showMessage('数据已刷新', 'info', $);
    }
    
    /**
     * 显示消息
     */
    function showMessage(message, type, $) {
        type = type || 'info';
        const messageClass = type === 'error' ? 'error' : (type === 'warning' ? 'warning' : (type === 'success' ? 'success' : 'info'));
        
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
    
})();