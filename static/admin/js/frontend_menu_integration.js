/**
 * 前端菜单集成脚本
 * 替换原有的前端菜单选择器实现，使用组件化方案
 * 解决权限策略违规问题，提供统一的前端菜单管理功能
 */

(function($) {
    'use strict';
    
    // 确保依赖已加载
    function ensureDependencies() {
        const dependencies = [
            'FrontendMenuSelector',
            'FrontendMenuSelectorConfig', 
            'FrontendMenuSelectorFactory'
        ];
        
        const missing = dependencies.filter(dep => !window[dep]);
        if (missing.length > 0) {
            console.error('Missing dependencies:', missing);
            return false;
        }
        
        return true;
    }
    
    // 初始化前端菜单选择器
    function initFrontendMenuSelectors() {
        if (!ensureDependencies()) {
            console.warn('Dependencies not loaded, falling back to basic functionality');
            return;
        }
        
        try {
            // 使用工厂自动初始化
            window.frontendMenuSelectorFactory.autoInit();
            
            // 为特定页面添加额外的初始化逻辑
            initPageSpecificFeatures();
            
        } catch (error) {
            console.error('Failed to initialize frontend menu selectors:', error);
            // 降级到基本功能
            fallbackInit();
        }
    }
    
    // 页面特定功能初始化
    function initPageSpecificFeatures() {
        const currentUrl = window.location.pathname;
        
        if (currentUrl.includes('/frontendmenuroleassignment/')) {
            initFrontendMenuRoleAssignmentPage();
        } else if (currentUrl.includes('/frontendmenuconfig/')) {
            initFrontendMenuConfigPage();
        }
    }
    
    // 前端菜单角色分配页面初始化
    function initFrontendMenuRoleAssignmentPage() {
        console.log('Initializing frontend menu role assignment page');
        
        // 添加批量分配功能
        addBulkAssignmentFeature();
        
        // 添加菜单预览功能
        addMenuPreviewFeature();
    }
    
    // 前端菜单配置页面初始化
    function initFrontendMenuConfigPage() {
        console.log('Initializing frontend menu config page');
        
        // 添加层级验证
        addHierarchyValidation();
        
        // 添加菜单排序功能
        addMenuSortingFeature();
    }
    
    // 批量分配功能
    function addBulkAssignmentFeature() {
        // 检查是否在列表页面
        if (!$('.changelist').length) return;
        
        // 添加批量分配按钮
        const bulkButton = $('<button type="button" class="btn btn-primary">批量分配菜单</button>');
        $('.changelist-search').after(bulkButton);
        
        bulkButton.on('click', function() {
            showBulkAssignmentModal();
        });
    }
    
    // 显示批量分配模态框
    function showBulkAssignmentModal() {
        const modalHtml = `
            <div id="bulk-assignment-modal" class="modal fade" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">批量分配菜单</h5>
                            <button type="button" class="close" data-dismiss="modal">&times;</button>
                        </div>
                        <div class="modal-body">
                            <form id="bulk-assignment-form">
                                <div class="form-group">
                                    <label for="bulk-role">选择角色:</label>
                                    <select id="bulk-role" class="form-control role-selector"></select>
                                </div>
                                <div class="form-group">
                                    <label for="bulk-menus">选择菜单:</label>
                                    <select id="bulk-menus" class="form-control menu-selector" multiple></select>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" id="confirm-bulk-assignment">确认分配</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('body').append(modalHtml);
        $('#bulk-assignment-modal').modal('show');
        
        // 为模态框中的选择器创建组件实例
        const config = window.FrontendMenuSelectorConfig.getBulkOperationConfig();
        window.frontendMenuSelectorFactory.create('bulkOperation', config);
    }
    
    // 菜单预览功能
    function addMenuPreviewFeature() {
        // 在菜单字段旁边添加预览按钮
        $('#id_menu').after('<button type="button" id="preview-menu" class="btn btn-sm btn-info">预览</button>');
        
        $('#preview-menu').on('click', function() {
            const menuId = $('#id_menu').val();
            if (menuId) {
                showMenuPreview(menuId);
            } else {
                alert('请先选择一个菜单');
            }
        });
    }
    
    // 显示菜单预览
    function showMenuPreview(menuId) {
        // 发送AJAX请求获取菜单详情
        $.ajax({
            url: `/admin/permissions/frontendmenuconfig/${menuId}/preview/`,
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    showMenuPreviewModal(response.menu);
                } else {
                    alert('获取菜单预览失败: ' + response.error);
                }
            },
            error: function() {
                alert('获取菜单预览失败');
            }
        });
    }
    
    // 显示菜单预览模态框
    function showMenuPreviewModal(menu) {
        const modalHtml = `
            <div id="menu-preview-modal" class="modal fade" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">菜单预览: ${menu.name}</h5>
                            <button type="button" class="close" data-dismiss="modal">&times;</button>
                        </div>
                        <div class="modal-body">
                            <div class="menu-preview">
                                <p><strong>名称:</strong> ${menu.name}</p>
                                <p><strong>标识:</strong> ${menu.key}</p>
                                <p><strong>类型:</strong> ${menu.menu_type_display}</p>
                                <p><strong>位置:</strong> ${menu.position_display}</p>
                                <p><strong>链接:</strong> <a href="${menu.url}" target="_blank">${menu.url}</a></p>
                                <p><strong>图标:</strong> <i class="${menu.icon}"></i> ${menu.icon}</p>
                                <p><strong>排序:</strong> ${menu.sort_order}</p>
                                <p><strong>状态:</strong> ${menu.is_active ? '启用' : '禁用'}</p>
                                ${menu.description ? `<p><strong>描述:</strong> ${menu.description}</p>` : ''}
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('body').append(modalHtml);
        $('#menu-preview-modal').modal('show');
        
        // 模态框关闭后移除
        $('#menu-preview-modal').on('hidden.bs.modal', function() {
            $(this).remove();
        });
    }
    
    // 层级验证
    function addHierarchyValidation() {
        $('#id_parent').on('change', function() {
            const parentId = $(this).val();
            const currentId = getObjectId(); // 从URL获取当前对象ID
            
            if (parentId && currentId && parentId === currentId) {
                alert('不能将菜单设置为自己的父菜单');
                $(this).val('');
                return;
            }
            
            // 检查循环引用
            if (parentId) {
                checkCircularReference(currentId, parentId);
            }
        });
    }
    
    // 检查循环引用
    function checkCircularReference(currentId, parentId) {
        if (!currentId) return;
        
        $.ajax({
            url: `/admin/permissions/frontendmenuconfig/check-circular-reference/`,
            type: 'POST',
            data: {
                'current_id': currentId,
                'parent_id': parentId,
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (!response.success) {
                    alert('检测到循环引用: ' + response.error);
                    $('#id_parent').val('');
                }
            },
            error: function() {
                console.warn('循环引用检查失败');
            }
        });
    }
    
    // 菜单排序功能
    function addMenuSortingFeature() {
        // 在排序字段旁边添加自动排序按钮
        $('#id_sort_order').after('<button type="button" id="auto-sort" class="btn btn-sm btn-secondary">自动排序</button>');
        
        $('#auto-sort').on('click', function() {
            const position = $('#id_position').val();
            const parentId = $('#id_parent').val();
            
            $.ajax({
                url: `/admin/permissions/frontendmenuconfig/get-next-sort-order/`,
                type: 'GET',
                data: {
                    'position': position,
                    'parent_id': parentId
                },
                success: function(response) {
                    if (response.success) {
                        $('#id_sort_order').val(response.next_sort_order);
                    }
                },
                error: function() {
                    console.warn('获取自动排序值失败');
                }
            });
        });
    }
    
    // 降级初始化（当组件不可用时）
    function fallbackInit() {
        console.log('Using fallback initialization for frontend menu selectors');
        
        // 基本的角色依赖菜单筛选
        const roleField = $('#id_role');
        const menuField = $('#id_menu');
        
        if (roleField.length && menuField.length) {
            roleField.on('change', function() {
                const role = $(this).val();
                if (role) {
                    // 简单的AJAX请求
                    $.get('/admin/permissions/frontendmenuroleassignment/get-menus-for-role/', 
                          { role: role }, 
                          function(data) {
                              if (data.success) {
                                  updateMenuOptions(menuField, data.menus);
                              }
                          });
                }
            });
        }
    }
    
    // 更新菜单选项（降级版本）
    function updateMenuOptions(menuField, menus) {
        const currentValue = menuField.val();
        menuField.empty().append('<option value="">---------</option>');
        
        menus.forEach(function(menu) {
            menuField.append(`<option value="${menu.id}">${menu.name}</option>`);
        });
        
        if (currentValue) {
            menuField.val(currentValue);
        }
    }
    
    // 获取当前对象ID（从URL）
    function getObjectId() {
        const match = window.location.pathname.match(/\/(\d+)\/change\/$/);
        return match ? match[1] : null;
    }
    
    // 页面卸载时清理
    $(window).on('beforeunload', function() {
        if (window.frontendMenuSelectorFactory) {
            window.frontendMenuSelectorFactory.destroyAll();
        }
    });
    
    // DOM加载完成后初始化
    $(document).ready(function() {
        initFrontendMenuSelectors();
    });
    
    // 导出到全局（用于调试）
    window.frontendMenuIntegration = {
        init: initFrontendMenuSelectors,
        fallback: fallbackInit,
        addBulkAssignment: addBulkAssignmentFeature,
        addMenuPreview: addMenuPreviewFeature
    };
    
})(django.jQuery || jQuery);