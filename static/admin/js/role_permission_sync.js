/**
 * 角色权限同步功能
 * 实现角色权限单向同步到Django组
 */

(function() {
    'use strict';
    
    // 检查jQuery是否可用
    const $ = window.django && window.django.jQuery ? window.django.jQuery : window.jQuery;
    
    if (!$) {
        console.warn('jQuery not available, role permission sync features disabled');
        return;
    }
    
    $(document).ready(function() {
        initRolePermissionSync();
    });
    
    function initRolePermissionSync() {
        // 在角色管理页面添加同步按钮
        if (window.location.pathname.includes('/admin/permissions/rolemanagement/')) {
            addSyncButtons();
        }
        
        // 在权限配置区域添加说明
        addPermissionSyncNotice();
    }
    
    function addSyncButtons() {
        // 在列表页面添加批量同步按钮
        if ($('.changelist-search').length > 0) {
            const batchSyncButton = $(`
                <div class="role-sync-actions" style="margin: 10px 0; padding: 10px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px;">
                    <h3 style="margin: 0 0 10px 0; color: #495057;">🔄 权限同步管理</h3>
                    <p style="margin: 0 0 10px 0; color: #6c757d; font-size: 13px;">
                        角色权限将单向同步到Django组中，组管理中可创建独立的特殊控制组。
                    </p>
                    <button type="button" class="btn btn-primary btn-sm" id="sync-all-roles" style="margin-right: 10px;">
                        🔄 同步所有角色权限到组
                    </button>
                    <button type="button" class="btn btn-info btn-sm" id="view-sync-logs">
                        📋 查看同步日志
                    </button>
                </div>
            `);
            
            $('.changelist-search').after(batchSyncButton);
            
            // 绑定事件
            $('#sync-all-roles').on('click', handleSyncAllRoles);
            $('#view-sync-logs').on('click', handleViewSyncLogs);
        }
        
        // 在详情页面添加单个同步按钮
        if ($('#rolemanagement_form').length > 0) {
            const roleId = $('#id_role').val();
            if (roleId) {
                const syncButton = $(`
                    <div class="role-sync-single" style="margin: 10px 0; padding: 10px; background: #e7f3ff; border: 1px solid #b3d7ff; border-radius: 4px;">
                        <button type="button" class="btn btn-primary btn-sm" id="sync-single-role" data-role-id="${roleId}">
                            🔄 同步此角色权限到组
                        </button>
                        <span style="margin-left: 10px; color: #0056b3; font-size: 12px;">
                            权限将自动同步到对应的Django组
                        </span>
                    </div>
                `);
                
                $('.field-permissions').before(syncButton);
                $('#sync-single-role').on('click', handleSyncSingleRole);
            }
        }
    }
    
    function addPermissionSyncNotice() {
        // 在权限选择区域添加说明
        const permissionField = $('.field-permissions');
        if (permissionField.length > 0) {
            const notice = $(`
                <div class="permission-sync-notice" style="margin: 10px 0; padding: 10px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;">
                    <h4 style="margin: 0 0 8px 0; color: #856404;">🔄 权限同步说明</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #856404; font-size: 13px;">
                        <li>此处配置的权限将<strong>单向同步</strong>到对应的Django组中</li>
                        <li>角色管理中的所有权限都会在组管理中创建对应的权限</li>
                        <li>组管理中可以创建独立于角色管理的组，用于特殊控制</li>
                        <li>权限同步是单向的（角色→组），组中的权限修改不会影响角色配置</li>
                    </ul>
                </div>
            `);
            
            permissionField.before(notice);
        }
    }
    
    function handleSyncAllRoles() {
        if (!confirm('确定要同步所有角色的权限到对应的Django组吗？\n\n这个操作将：\n1. 为每个角色创建或更新对应的Django组\n2. 同步角色的所有权限到组中\n3. 记录同步日志')) {
            return;
        }
        
        const button = $('#sync-all-roles');
        const originalText = button.text();
        
        button.prop('disabled', true).text('🔄 同步中...');
        
        $.ajax({
            url: '/admin/permissions/rolemanagement/sync-all-roles-to-groups/',
            method: 'POST',
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({}),
            success: function(response) {
                if (response.success) {
                    showMessage(response.message, 'success');
                } else {
                    showMessage('同步失败: ' + response.error, 'error');
                }
            },
            error: function() {
                showMessage('网络错误，请重试', 'error');
            },
            complete: function() {
                button.prop('disabled', false).text(originalText);
            }
        });
    }
    
    function handleSyncSingleRole() {
        const button = $(this);
        const roleId = button.data('role-id');
        
        if (!roleId) {
            showMessage('无法获取角色ID', 'error');
            return;
        }
        
        if (!confirm(`确定要同步角色 "${roleId}" 的权限到对应的Django组吗？`)) {
            return;
        }
        
        const originalText = button.text();
        button.prop('disabled', true).text('🔄 同步中...');
        
        $.ajax({
            url: '/admin/permissions/rolemanagement/sync-role-to-groups/',
            method: 'POST',
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({role_id: roleId}),
            success: function(response) {
                if (response.success) {
                    showMessage(response.message, 'success');
                } else {
                    showMessage('同步失败: ' + response.error, 'error');
                }
            },
            error: function() {
                showMessage('网络错误，请重试', 'error');
            },
            complete: function() {
                button.prop('disabled', false).text(originalText);
            }
        });
    }
    
    function handleViewSyncLogs() {
        // 打开同步日志页面
        window.open('/admin/permissions/permissionsynclog/?target_type__exact=role', '_blank');
    }
    
    function showMessage(message, type) {
        // 创建消息提示
        const messageClass = type === 'success' ? 'alert-success' : 
                           type === 'error' ? 'alert-danger' : 
                           type === 'warning' ? 'alert-warning' : 'alert-info';
        
        const messageHtml = `
            <div class="alert ${messageClass} alert-dismissible fade show role-sync-message" role="alert" style="margin: 10px 0; position: relative; z-index: 1000;">
                ${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
        `;
        
        // 移除现有消息
        $('.role-sync-message').remove();
        
        // 添加新消息
        const messageDiv = $(messageHtml);
        
        // 根据页面类型选择插入位置
        if ($('.role-sync-actions').length > 0) {
            $('.role-sync-actions').after(messageDiv);
        } else if ($('.role-sync-single').length > 0) {
            $('.role-sync-single').after(messageDiv);
        } else {
            $('body').prepend(messageDiv);
        }
        
        // 3秒后自动隐藏
        setTimeout(function() {
            messageDiv.fadeOut(function() {
                $(this).remove();
            });
        }, 3000);
    }
    
})();