(function() {
    'use strict';
    
    // 检查是否有新的组件系统可用
    const hasNewComponents = window.FrontendMenuSelectorFactory && 
                            window.FrontendMenuSelectorConfig;
    
    // 当DOM加载完成后执行
    document.addEventListener('DOMContentLoaded', function() {
        if (hasNewComponents) {
            // 使用新的组件系统
            initWithNewComponents();
        } else {
            // 使用原有逻辑作为降级方案
            initLegacyMenuValidityFilter();
        }
    });
    
    // 使用新组件系统初始化
    function initWithNewComponents() {
        console.log('Using new component system for menu validity filter');
        
        // 让组件系统处理菜单有效性筛选
        const config = window.FrontendMenuSelectorConfig.getMenuValidityConfig();
        window.frontendMenuSelectorFactory.create('menuValidity', config);
    }
    
    // 原有逻辑作为降级方案
    function initLegacyMenuValidityFilter() {
        console.log('Using legacy menu validity filter logic');
        
        var $ = django.jQuery;
        var roleField = $('#id_role');
        var menuField = $('#id_menu_module');
        var originalOptions = [];
        
        // 保存原始菜单选项
        if (menuField.length) {
            menuField.find('option').each(function() {
                originalOptions.push({
                    value: $(this).val(),
                    text: $(this).text(),
                    selected: $(this).prop('selected')
                });
            });
        }
        
        // 角色选择改变时的处理函数
        function onRoleChange() {
            var selectedRole = roleField.val();
            
            if (!selectedRole || selectedRole === '') {
                // 如果没有选择角色，显示所有菜单选项
                resetMenuOptions();
                return;
            }
            
            // 发送AJAX请求获取该角色的有效菜单
            $.ajax({
                url: '/admin/permissions/menuvalidity/get-valid-menus/' + encodeURIComponent(selectedRole) + '/',
                type: 'GET',
                dataType: 'json',
                success: function(response) {
                    if (response.success) {
                        updateMenuOptions(response.menus, selectedRole);
                    } else {
                        console.error('获取菜单数据失败:', response.error);
                        resetMenuOptions();
                    }
                },
                error: function(xhr, status, error) {
                    console.error('AJAX请求失败:', error);
                    resetMenuOptions();
                }
            });
        }
        
        // 更新菜单选项
        function updateMenuOptions(menus, selectedRole) {
            // 清空现有选项
            menuField.empty();
            
            // 添加空选项
            menuField.append('<option value="">---------</option>');
            
            // 根据角色筛选菜单
            var validMenus = [];
            var invalidMenus = [];
            
            menus.forEach(function(menu) {
                if (menu.is_valid_for_role) {
                    validMenus.push(menu);
                } else {
                    invalidMenus.push(menu);
                }
            });
            
            // 首先添加该角色有效的菜单（推荐选项）
            if (validMenus.length > 0) {
                var validGroup = $('<optgroup label="推荐菜单（该角色已设为有效）"></optgroup>');
                validMenus.forEach(function(menu) {
                    var option = $('<option></option>')
                        .attr('value', menu.id)
                        .text(menu.name + ' (' + menu.key + ')');
                    validGroup.append(option);
                });
                menuField.append(validGroup);
            }
            
            // 然后添加其他菜单
            if (invalidMenus.length > 0) {
                var invalidGroup = $('<optgroup label="其他菜单"></optgroup>');
                invalidMenus.forEach(function(menu) {
                    var option = $('<option></option>')
                        .attr('value', menu.id)
                        .text(menu.name + ' (' + menu.key + ')');
                    invalidGroup.append(option);
                });
                menuField.append(invalidGroup);
            }
            
            // 触发change事件以更新其他可能的依赖
            menuField.trigger('change');
        }
        
        // 重置菜单选项为原始状态
        function resetMenuOptions() {
            menuField.empty();
            originalOptions.forEach(function(option) {
                var optionElement = $('<option></option>')
                    .attr('value', option.value)
                    .text(option.text);
                if (option.selected) {
                    optionElement.prop('selected', true);
                }
                menuField.append(optionElement);
            });
            menuField.trigger('change');
        }
        
        // 绑定角色字段的change事件
        if (roleField.length && menuField.length) {
            roleField.on('change', onRoleChange);
            
            // 页面加载时如果已有角色选择，立即触发筛选
            if (roleField.val()) {
                onRoleChange();
            }
        }
        
        // 为表单添加提示信息
        if (roleField.length && menuField.length) {
            var helpText = $('<p class="help">提示：选择角色后，菜单选项将按照该角色的有效性进行分组显示。推荐选择"推荐菜单"组中的选项。</p>');
            menuField.closest('.form-row').append(helpText);
        }
    }
    
    // 导出函数供其他脚本使用
    window.menuValidityFilter = {
        initWithNewComponents: initWithNewComponents,
        initLegacyMenuValidityFilter: initLegacyMenuValidityFilter,
        hasNewComponents: hasNewComponents
    };
    
})();