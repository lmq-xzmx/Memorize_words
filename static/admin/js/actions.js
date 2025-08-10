// Django Admin Actions JavaScript
// 修复 Cannot read properties of null (reading 'addEventListener') 错误

(function() {
    'use strict';
    
    // 确保DOM加载完成后再执行
    function initializeActions() {
        // 检查必要的元素是否存在
        const actionSelect = document.querySelector('select[name="action"]');
        const actionButton = document.querySelector('button[name="index"]');
        const checkboxes = document.querySelectorAll('input[name="_selected_action"]');
        
        if (!actionSelect) {
            if (typeof console !== 'undefined' && console.debug) {
                console.debug('Action select element not found');
            }
            return;
        }
        
        // 安全地添加事件监听器
        if (actionSelect && typeof actionSelect.addEventListener === 'function') {
            actionSelect.addEventListener('change', function() {
                const selectedAction = this.value;
                if (selectedAction) {
                    if (typeof console !== 'undefined' && console.debug) {
                        console.debug('Action selected:', selectedAction);
                    }
                }
            });
        }
        
        // 处理全选功能
        const selectAllCheckbox = document.querySelector('#action-toggle');
        if (selectAllCheckbox && typeof selectAllCheckbox.addEventListener === 'function') {
            selectAllCheckbox.addEventListener('change', function() {
                const isChecked = this.checked;
                checkboxes.forEach(function(checkbox) {
                    if (checkbox && typeof checkbox === 'object') {
                        checkbox.checked = isChecked;
                    }
                });
            });
        }
        
        // 处理单个复选框
        checkboxes.forEach(function(checkbox) {
            if (checkbox && typeof checkbox.addEventListener === 'function') {
                checkbox.addEventListener('change', function() {
                    updateSelectAllState();
                });
            }
        });
        
        function updateSelectAllState() {
            if (!selectAllCheckbox) return;
            
            const checkedBoxes = document.querySelectorAll('input[name="_selected_action"]:checked');
            const totalBoxes = document.querySelectorAll('input[name="_selected_action"]');
            
            if (checkedBoxes.length === 0) {
                selectAllCheckbox.checked = false;
                selectAllCheckbox.indeterminate = false;
            } else if (checkedBoxes.length === totalBoxes.length) {
                selectAllCheckbox.checked = true;
                selectAllCheckbox.indeterminate = false;
            } else {
                selectAllCheckbox.checked = false;
                selectAllCheckbox.indeterminate = true;
            }
        }
        
        // 初始化状态
        updateSelectAllState();
    }
    
    // 等待DOM加载完成
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeActions);
    } else {
        // DOM已经加载完成
        initializeActions();
    }
    
    // 导出到全局作用域（如果需要）
    window.Actions = {
        init: initializeActions
    };
    
})();

// 兼容旧版本的调用方式
if (typeof window !== 'undefined') {
    window.addEventListener('load', function() {
        if (window.Actions && typeof window.Actions.init === 'function') {
            window.Actions.init();
        }
    });
}