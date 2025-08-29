// 用户管理页面同步状态实时更新

// 确保在Django admin环境中正确加载
if (typeof django !== 'undefined' && django.jQuery) {
    (function($) {
        'use strict';
        
        // 等待DOM加载完成
        $(document).ready(function() {
            initUserSyncStatus();
        });
        
        // 如果页面已经加载完成，立即初始化
        if (document.readyState === 'complete' || document.readyState === 'interactive') {
            setTimeout(initUserSyncStatus, 100);
        }
    
    function initUserSyncStatus() {
        // 检查是否在用户列表页面
        if (!isUserListPage()) {
            return;
        }
        
        // 添加刷新按钮
        addSyncRefreshButton();
        
        // 定期检查同步状态
        startSyncStatusMonitoring();
        
        // 初始化时检查一次
        checkAllUserSyncStatus();
    }
    
    function isUserListPage() {
        // 检查是否在customuser的列表页面
        return window.location.pathname.includes('/admin/accounts/customuser/') && 
               !window.location.pathname.includes('/add/') && 
               !window.location.pathname.match(/\/\d+\/(change|delete)\//); 
    }
    
    function addSyncRefreshButton() {
        // 在操作栏添加同步状态刷新按钮
        var actionBar = $('.actions');
        if (actionBar.length > 0) {
            var refreshBtn = $('<button type="button" class="btn btn-info" id="refresh-sync-status" style="margin-left: 10px;"><i class="fas fa-sync-alt"></i> 刷新同步状态</button>');
            actionBar.append(refreshBtn);
            
            refreshBtn.on('click', function(e) {
                e.preventDefault();
                checkAllUserSyncStatus();
            });
        }
        
        // 在页面标题旁添加全局刷新按钮
        var pageTitle = $('h1');
        if (pageTitle.length > 0) {
            var globalRefreshBtn = $('<button type="button" class="btn btn-sm btn-outline-primary" id="global-refresh-sync" style="margin-left: 15px; vertical-align: middle;"><i class="fas fa-sync"></i> 刷新所有同步状态</button>');
            pageTitle.append(globalRefreshBtn);
            
            globalRefreshBtn.on('click', function(e) {
                e.preventDefault();
                refreshAllSyncData();
            });
        }
    }
    
    function startSyncStatusMonitoring() {
        // 每30秒自动检查一次同步状态
        setInterval(function() {
            checkAllUserSyncStatus();
        }, 30000);
    }
    
    function checkAllUserSyncStatus() {
        // 获取所有用户的角色权限信息元素
        var roleInfoElements = $('[id^="role_info_"]');
        
        if (roleInfoElements.length === 0) {
            return;
        }
        
        showSyncStatusMessage('正在检查用户同步状态...', 'info');
        
        var userRoles = [];
        roleInfoElements.each(function() {
            var $element = $(this);
            var role = $element.data('role');
            var userId = $element.data('user-id');
            
            if (role && userId) {
                userRoles.push({
                    role: role,
                    userId: userId,
                    element: $element
                });
            }
        });
        
        // 批量检查同步状态
        checkUserRolesSyncStatus(userRoles);
    }
    
    function checkUserRolesSyncStatus(userRoles) {
        var promises = [];
        
        userRoles.forEach(function(userRole) {
            var promise = $.ajax({
                url: '/admin/permissions/rolegroupmapping/check-sync-status/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val() || getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                data: JSON.stringify({
                    role: userRole.role,
                    user_id: userRole.userId
                })
            }).done(function(response) {
                if (response.success) {
                    updateUserSyncStatus(userRole.element, response.sync_data);
                }
            }).fail(function() {
                console.warn('Failed to check sync status for role:', userRole.role);
            });
            
            promises.push(promise);
        });
        
        $.when.apply($, promises).always(function() {
            showSyncStatusMessage('同步状态检查完成', 'success');
        });
    }
    
    function updateUserSyncStatus(element, syncData) {
        var syncStatusSpan = element.find('[id^="sync_status_"]');
        
        if (syncStatusSpan.length > 0) {
            var syncStatus, syncColor, syncBg, syncText;
            
            if (syncData.group_perms === syncData.role_perms && syncData.role_perms > 0) {
                syncStatus = "✅";
                syncColor = "#28a745";
                syncBg = "#d4edda";
                syncText = "已同步";
            } else if (syncData.group_perms > 0 && syncData.group_perms !== syncData.role_perms) {
                syncStatus = "⚠️";
                syncColor = "#ffc107";
                syncBg = "#fff3cd";
                syncText = "部分同步";
            } else {
                syncStatus = "❌";
                syncColor = "#dc3545";
                syncBg = "#f8d7da";
                syncText = syncData.has_mapping ? "未同步" : "无映射";
            }
            
            syncStatusSpan.css({
                'color': syncColor,
                'background': syncBg
            }).attr('title', `组权限: ${syncData.group_perms}个 / 角色权限: ${syncData.role_perms}个`)
              .html(`${syncStatus} ${syncText}`);
        }
    }
    
    function refreshAllSyncData() {
        showSyncStatusMessage('正在强制刷新所有同步数据...', 'info');
        
        $.ajax({
            url: '/admin/permissions/rolegroupmapping/refresh-all-sync/',
            method: 'POST',
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val() || getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({})
        }).done(function(response) {
            if (response.success) {
                showSyncStatusMessage('所有同步数据已刷新，正在更新显示...', 'success');
                // 延迟1秒后重新检查状态
                setTimeout(function() {
                    checkAllUserSyncStatus();
                }, 1000);
            } else {
                showSyncStatusMessage('刷新失败: ' + response.error, 'error');
            }
        }).fail(function() {
            showSyncStatusMessage('刷新失败: 网络错误', 'error');
        });
    }
    
    function showSyncStatusMessage(message, type) {
        // 创建状态提示
        var statusClass = 'alert-info';
        var iconClass = 'fas fa-info-circle';
        
        switch(type) {
            case 'success':
                statusClass = 'alert-success';
                iconClass = 'fas fa-check-circle';
                break;
            case 'error':
                statusClass = 'alert-danger';
                iconClass = 'fas fa-exclamation-circle';
                break;
            case 'warning':
                statusClass = 'alert-warning';
                iconClass = 'fas fa-exclamation-triangle';
                break;
        }
        
        var statusHtml = '<div class="alert ' + statusClass + ' alert-dismissible fade show sync-status-message" role="alert" style="margin: 10px 0; font-size: 14px; position: fixed; top: 80px; right: 20px; z-index: 9999; min-width: 300px;">' +
            '<i class="' + iconClass + '"></i> ' + message +
            '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
            '<span aria-hidden="true">&times;</span>' +
            '</button>' +
            '</div>';
        
        // 移除现有状态消息
        $('.sync-status-message').remove();
        
        // 添加新状态消息
        var statusDiv = $(statusHtml);
        $('body').append(statusDiv);
        
        // 3秒后自动隐藏（成功消息）或5秒后隐藏（错误消息）
        var hideDelay = type === 'success' ? 3000 : 5000;
        setTimeout(function() {
            statusDiv.fadeOut(function() {
                $(this).remove();
            });
        }, hideDelay);
    }
    
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
        
    })(django.jQuery);
} else {
    // 备用方案：使用标准jQuery或原生JavaScript
    console.warn('Django jQuery not found, using fallback for user sync status');
    if (typeof jQuery !== 'undefined') {
        jQuery(document).ready(function($) {
            initUserSyncStatusFallback($);
        });
    } else if (typeof $ !== 'undefined') {
        $(document).ready(function() {
            initUserSyncStatusFallback($);
        });
    } else {
        // 原生JavaScript备用方案
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Using native JavaScript fallback for user sync status');
            initUserSyncStatusNative();
        });
    }
}

function initUserSyncStatusFallback($) {
    // jQuery备用方案的实现
    console.log('Initializing user sync status with fallback jQuery');
    // 这里可以实现简化版的同步状态检查功能
}

function initUserSyncStatusNative() {
    // 原生JavaScript的实现
    console.log('Initializing user sync status with native JavaScript');
    // 这里可以实现基础的同步状态检查功能
}