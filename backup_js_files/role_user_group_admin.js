// 角色用户组 Admin 自定义JavaScript

// 确保jQuery可用的兼容性处理
(function() {
    'use strict';
    
    // 获取可用的jQuery实例
    var $ = (typeof django !== 'undefined' && django.jQuery) ? django.jQuery : 
            (typeof jQuery !== 'undefined') ? jQuery : 
            (typeof window.$ !== 'undefined') ? window.$ : null;
    
    if (!$) {
        console.error('jQuery not found for role_user_group_admin.js');
        return;
    }
    
    $(document).ready(function() {
        // 角色字段变化时动态过滤用户
        var roleField = $('#id_role');
        var usersField = $('#id_users');
        
        if (roleField.length && usersField.length) {
            // 初始化时根据当前角色过滤用户
            filterUsersByRole();
            
            // 监听角色字段变化
            roleField.on('change', function() {
                filterUsersByRole();
            });
        }
        
        function filterUsersByRole() {
            var selectedRole = roleField.val();
            
            if (!selectedRole) {
                // 如果没有选择角色，显示所有激活用户
                loadAllActiveUsers();
                return;
            }
            
            // 显示加载状态
            showLoadingState();
            
            // 使用Django Admin的changelist API获取过滤后的用户
            var apiUrl = window.location.origin + '/admin/accounts/customuser/';
            
            $.ajax({
                url: apiUrl,
                data: {
                    'role__exact': selectedRole,
                    'is_active__exact': '1',
                    'o': '3.4',  // 按real_name, username排序
                    'format': 'json'
                },
                dataType: 'json',
                success: function(data) {
                    updateUserOptions(data);
                },
                error: function(xhr, status, error) {
                    console.error('加载用户失败:', error);
                    showErrorState();
                }
            });
        }
        
        function loadAllActiveUsers() {
            showLoadingState();
            var apiUrl = window.location.origin + '/admin/accounts/customuser/';
            
            $.ajax({
                url: apiUrl,
                data: {
                    'is_active__exact': '1',
                    'o': '2.3.4',  // 按role, real_name, username排序
                    'format': 'json'
                },
                dataType: 'json',
                success: function(data) {
                    updateUserOptions(data);
                },
                error: function(xhr, status, error) {
                    console.error('加载所有用户失败:', error);
                    showErrorState();
                }
            });
        }
        
        function showLoadingState() {
            usersField.find('option').remove();
            usersField.append('<option value="">正在加载用户...</option>');
        }
        
        function showErrorState() {
            usersField.find('option').remove();
            usersField.append('<option value="">加载用户失败，请刷新页面重试</option>');
        }
        
        function updateUserOptions(data) {
            // 清空现有选项
            usersField.find('option').remove();
            
            // 添加新选项
            if (data && data.results && data.results.length > 0) {
                $.each(data.results, function(index, user) {
                    var displayName = user.real_name || user.username;
                    var roleDisplay = user.role_display || user.role || '';
                    var optionText = displayName + ' (' + user.username + ')' + 
                                   (roleDisplay ? ' [' + roleDisplay + ']' : '');
                    usersField.append(
                        $('<option></option>').attr('value', user.id).text(optionText)
                    );
                });
            } else {
                var message = roleField.val() ? '该角色下暂无可用用户' : '暂无可用用户';
                usersField.append(
                    $('<option></option>').attr('value', '').text(message)
                );
            }
        }
        
        // 添加角色说明提示
        if (roleField.length) {
            var helpText = $('<div class="help">选择角色后，用户列表将自动过滤显示该角色下的激活用户</div>');
            roleField.parent().append(helpText);
        }
        
        // 美化用户选择器
        if (usersField.length) {
            usersField.attr('size', '10'); // 设置显示行数
            usersField.css({
                'width': '100%',
                'max-height': '200px'
            });
        }
    });
    
})();