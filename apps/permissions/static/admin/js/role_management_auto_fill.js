/**
 * 角色管理自动填充功能
 * 为角色管理页面提供自动填充和权限同步功能
 */

(function() {
    'use strict';
    
    // 确保jQuery可用
    var $ = window.jQuery || window.django.jQuery || django.jQuery;
    
    if (typeof $ === 'undefined') {
        console.error('jQuery未找到，role_management_auto_fill.js无法初始化');
        return;
    }

    // 角色权限同步管理器
    const RolePermissionSync = {
        init: function() {
            this.bindEvents();
            this.initSyncButtons();
            this.checkSyncStatus();
        },

        bindEvents: function() {
            // 角色字段变化时自动填充显示名称
            $('#id_role').on('change', this.autoFillDisplayName);
            
            // 权限变化时显示同步提示
            $('#id_permissions').on('change', this.onPermissionsChange);
            
            // 绑定同步按钮事件
            $(document).on('click', '.sync-role-permissions', this.syncRolePermissions);
            $(document).on('click', '.sync-all-roles', this.syncAllRoles);
        },

        autoFillDisplayName: function() {
            const roleValue = $(this).val();
            const displayNameField = $('#id_display_name');
            
            if (roleValue && !displayNameField.val()) {
                // 将角色值转换为友好的显示名称
                const displayName = roleValue.replace(/_/g, ' ')
                    .replace(/\b\w/g, l => l.toUpperCase());
                displayNameField.val(displayName);
            }
        },

        onPermissionsChange: function() {
            const selectedPermissions = $(this).val() || [];
            const syncStatus = $('.sync-status');
            
            if (selectedPermissions.length > 0) {
                syncStatus.removeClass('success error')
                    .addClass('warning')
                    .text(`已选择 ${selectedPermissions.length} 个权限，保存后将自动同步到组`);
            } else {
                syncStatus.removeClass('warning error')
                    .addClass('success')
                    .text('无权限选择');
            }
        },

        initSyncButtons: function() {
            // 在权限字段后添加同步按钮
            const permissionsField = $('.field-permissions');
            if (permissionsField.length && !$('.role-permission-sync').length) {
                const syncHtml = `
                    <div class="role-permission-sync">
                        <h3>权限同步控制</h3>
                        <button type="button" class="sync-role-permissions sync-button">
                            同步当前角色权限到组
                        </button>
                        <button type="button" class="sync-all-roles sync-button">
                            同步所有角色权限到组
                        </button>
                        <span class="sync-status">等待同步</span>
                        
                        <div class="sync-progress">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: 0%"></div>
                            </div>
                            <div class="progress-text">同步中...</div>
                        </div>
                        
                        <div class="sync-log"></div>
                    </div>
                `;
                permissionsField.after(syncHtml);
            }
        },

        checkSyncStatus: function() {
            const roleField = $('#id_role');
            if (!roleField.val()) return;

            $.ajax({
                url: '/admin/permissions/rolemanagement/check_sync_status/',
                method: 'GET',
                data: { role: roleField.val() },
                success: function(response) {
                    if (response.success && response.sync_data) {
                        const data = response.sync_data;
                        const status = $('.sync-status');
                        
                        if (data.is_synced) {
                            status.removeClass('warning error')
                                .addClass('success')
                                .text(`权限已同步 (${data.role_perms}/${data.group_perms})`);
                        } else {
                            status.removeClass('success error')
                                .addClass('warning')
                                .text(`权限未同步 (角色:${data.role_perms}, 组:${data.group_perms})`);
                        }
                    }
                },
                error: function() {
                    $('.sync-status').removeClass('success warning')
                        .addClass('error')
                        .text('检查同步状态失败');
                }
            });
        },

        syncRolePermissions: function(e) {
            e.preventDefault();
            const roleField = $('#id_role');
            const roleId = roleField.val();
            
            if (!roleId) {
                alert('请先选择角色');
                return;
            }

            RolePermissionSync.showProgress(true);
            RolePermissionSync.addLogEntry('开始同步角色权限...', 'info');

            $.ajax({
                url: '/admin/permissions/rolemanagement/sync_role_to_groups/',
                method: 'POST',
                data: JSON.stringify({ role_id: roleId }),
                contentType: 'application/json',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
                },
                success: function(response) {
                    RolePermissionSync.showProgress(false);
                    
                    if (response.success) {
                        $('.sync-status').removeClass('warning error')
                            .addClass('success')
                            .text('权限同步成功');
                        RolePermissionSync.addLogEntry(response.message, 'success');
                    } else {
                        $('.sync-status').removeClass('success warning')
                            .addClass('error')
                            .text('权限同步失败');
                        RolePermissionSync.addLogEntry(response.error || '同步失败', 'error');
                    }
                    
                    // 重新检查同步状态
                    setTimeout(RolePermissionSync.checkSyncStatus, 1000);
                },
                error: function() {
                    RolePermissionSync.showProgress(false);
                    $('.sync-status').removeClass('success warning')
                        .addClass('error')
                        .text('同步请求失败');
                    RolePermissionSync.addLogEntry('同步请求失败', 'error');
                }
            });
        },

        syncAllRoles: function(e) {
            e.preventDefault();
            
            if (!confirm('确定要同步所有角色的权限到组吗？这可能需要一些时间。')) {
                return;
            }

            RolePermissionSync.showProgress(true);
            RolePermissionSync.addLogEntry('开始批量同步所有角色权限...', 'info');

            $.ajax({
                url: '/admin/permissions/rolemanagement/sync_all_roles_to_groups/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
                },
                success: function(response) {
                    RolePermissionSync.showProgress(false);
                    
                    if (response.success) {
                        $('.sync-status').removeClass('warning error')
                            .addClass('success')
                            .text('批量同步完成');
                        RolePermissionSync.addLogEntry(
                            `批量同步完成：成功 ${response.success_count} 个，失败 ${response.error_count} 个`, 
                            response.error_count > 0 ? 'warning' : 'success'
                        );
                    } else {
                        $('.sync-status').removeClass('success warning')
                            .addClass('error')
                            .text('批量同步失败');
                        RolePermissionSync.addLogEntry(response.error || '批量同步失败', 'error');
                    }
                    
                    // 重新检查当前角色的同步状态
                    setTimeout(RolePermissionSync.checkSyncStatus, 2000);
                },
                error: function() {
                    RolePermissionSync.showProgress(false);
                    $('.sync-status').removeClass('success warning')
                        .addClass('error')
                        .text('批量同步请求失败');
                    RolePermissionSync.addLogEntry('批量同步请求失败', 'error');
                }
            });
        },

        showProgress: function(show) {
            const progress = $('.sync-progress');
            if (show) {
                progress.addClass('active');
                this.animateProgress();
            } else {
                progress.removeClass('active');
                $('.progress-fill').css('width', '0%');
            }
        },

        animateProgress: function() {
            let width = 0;
            const interval = setInterval(function() {
                width += Math.random() * 10;
                if (width >= 90) {
                    width = 90;
                    clearInterval(interval);
                }
                $('.progress-fill').css('width', width + '%');
            }, 200);
        },

        addLogEntry: function(message, type) {
            const log = $('.sync-log');
            const timestamp = new Date().toLocaleTimeString();
            const entry = `<div class="log-entry ${type}">[${timestamp}] ${message}</div>`;
            
            log.append(entry);
            log.scrollTop(log[0].scrollHeight);
            
            // 限制日志条目数量
            const entries = log.find('.log-entry');
            if (entries.length > 50) {
                entries.first().remove();
            }
        }
    };

    // 页面加载完成后初始化
    $(document).ready(function() {
        RolePermissionSync.init();
    });

})();