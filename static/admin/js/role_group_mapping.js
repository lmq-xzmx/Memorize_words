// 角色组映射管理JavaScript - 修复版本

// 立即定义全局函数，确保HTML onchange事件可以调用
window.handleRoleChange = function(roleValue) {
    console.log('handleRoleChange called with:', roleValue);
    
    if (!roleValue) {
        // 清空组选择
        const groupSelect = document.getElementById('id_group');
        if (groupSelect) {
            groupSelect.innerHTML = '<option value="">---------</option>';
        }
        return;
    }
    
    // 获取CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfToken) {
        console.error('CSRF token not found');
        return;
    }
    
    // 发送AJAX请求同步角色组
    fetch('/admin/permissions/rolegroupmapping/sync-role-groups/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken.value
        },
        body: JSON.stringify({role: roleValue})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            const groupSelect = document.getElementById('id_group');
            if (groupSelect) {
                // 检查选项是否已存在
                let existingOption = groupSelect.querySelector(`option[value="${data.group_id}"]`);
                if (!existingOption) {
                    const option = document.createElement('option');
                    option.value = data.group_id;
                    option.textContent = data.group_name;
                    groupSelect.appendChild(option);
                }
                groupSelect.value = data.group_id;
                
                // 显示成功消息
                showMessage(data.created ? 
                    `成功创建并关联组: ${data.group_name}` : 
                    `已关联到现有组: ${data.group_name}`, 
                    'success'
                );
            }
        } else {
            showMessage(`同步失败: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('网络错误，请重试', 'error');
    });
};

// 显示消息函数
function showMessage(message, type) {
    // 移除现有消息
    const existingMessage = document.querySelector('.role-group-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // 创建消息元素
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert role-group-message`;
    
    // 设置消息样式
    let bgColor, textColor;
    switch(type) {
        case 'success':
            bgColor = '#d4edda';
            textColor = '#155724';
            break;
        case 'error':
            bgColor = '#f8d7da';
            textColor = '#721c24';
            break;
        case 'warning':
            bgColor = '#fff3cd';
            textColor = '#856404';
            break;
        default:
            bgColor = '#d1ecf1';
            textColor = '#0c5460';
    }
    
    messageDiv.style.cssText = `
        background-color: ${bgColor};
        color: ${textColor};
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
        border: 1px solid ${textColor}33;
    `;
    messageDiv.textContent = message;
    
    // 找到合适的位置插入消息
    const roleField = document.getElementById('id_role');
    if (roleField && roleField.parentNode) {
        roleField.parentNode.appendChild(messageDiv);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 3000);
    }
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('Role group mapping JavaScript loaded');
    
    // 如果有初始选中的角色，触发一次变化事件
    const roleSelect = document.getElementById('id_role');
    if (roleSelect && roleSelect.value) {
        handleRoleChange(roleSelect.value);
    }
});

// 兼容jQuery环境
if (typeof django !== 'undefined' && django.jQuery) {
    django.jQuery(document).ready(function($) {
        console.log('Django jQuery environment detected');
        
        // 绑定角色变化事件（jQuery方式）
        $('#id_role').on('change', function() {
            handleRoleChange(this.value);
        });
        
        // 初始化时如果有选中的角色，触发一次变化事件
        const initialRole = $('#id_role').val();
        if (initialRole) {
            handleRoleChange(initialRole);
        }
    });
}