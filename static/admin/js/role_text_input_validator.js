/**
 * 角色文本输入验证器
 * 为角色文本输入字段提供实时验证功能
 */

(function() {
    'use strict';
    
    // 页面加载完成后初始化
    document.addEventListener('DOMContentLoaded', function() {
        initRoleTextInputValidator();
    });
    
    function initRoleTextInputValidator() {
        const roleInputs = document.querySelectorAll('.role-text-input');
        
        roleInputs.forEach(function(roleInput) {
            if (!roleInput.hasAttribute('data-validated')) {
                roleInput.setAttribute('data-validated', 'true');
                
                // 添加输入验证事件监听器
                roleInput.addEventListener('input', function(e) {
                    validateRoleInput(e.target);
                });
                
                // 添加失焦验证事件监听器
                roleInput.addEventListener('blur', function(e) {
                    validateRoleInput(e.target);
                });
                
                // 初始验证（如果有值）
                if (roleInput.value) {
                    validateRoleInput(roleInput);
                }
            }
        });
    }
    
    function validateRoleInput(input) {
        const value = input.value.trim();
        const isValid = /^[a-z_][a-z0-9_]*$/.test(value);
        
        // 移除之前的验证状态
        input.classList.remove('role-input-valid', 'role-input-invalid');
        
        if (value) {
            if (isValid) {
                // 有效输入
                input.style.borderColor = '#28a745';
                input.style.backgroundColor = '#f8fff9';
                input.classList.add('role-input-valid');
                removeValidationMessage(input);
            } else {
                // 无效输入
                input.style.borderColor = '#dc3545';
                input.style.backgroundColor = '#fff5f5';
                input.classList.add('role-input-invalid');
                showValidationMessage(input, '角色代码只能包含小写字母、数字和下划线，且必须以字母或下划线开头');
            }
        } else {
            // 空值
            input.style.borderColor = '';
            input.style.backgroundColor = '';
            removeValidationMessage(input);
        }
    }
    
    function showValidationMessage(input, message) {
        removeValidationMessage(input);
        
        const messageElement = document.createElement('div');
        messageElement.className = 'role-validation-message';
        messageElement.style.cssText = `
            color: #dc3545;
            font-size: 12px;
            margin-top: 5px;
            padding: 5px 8px;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            display: block;
        `;
        messageElement.textContent = message;
        
        input.parentNode.insertBefore(messageElement, input.nextSibling);
    }
    
    function removeValidationMessage(input) {
        const existingMessage = input.parentNode.querySelector('.role-validation-message');
        if (existingMessage) {
            existingMessage.remove();
        }
    }
    
})();