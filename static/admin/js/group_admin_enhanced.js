/**
 * 增强的Django组管理界面JavaScript功能
 */

// 组一致性检查功能
function checkGroupConsistency(groupId) {
    if (!groupId) {
        alert('无效的组ID');
        return;
    }
    
    // 显示加载状态
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = '🔄 检查中...';
    button.disabled = true;
    
    // 发送AJAX请求进行一致性检查
    fetch(`/admin/permissions/group/${groupId}/consistency-check/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            'action': 'check_consistency',
            'group_id': groupId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showConsistencyResult(data.result);
        } else {
            alert('检查失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        console.error('一致性检查错误:', error);
        alert('检查过程中发生错误，请查看控制台日志');
    })
    .finally(() => {
        // 恢复按钮状态
        button.textContent = originalText;
        button.disabled = false;
    });
}

// 显示一致性检查结果
function showConsistencyResult(result) {
    const modal = createModal('一致性检查结果');
    
    let content = '<div class="consistency-result">';
    
    // 检查状态
    if (result.is_consistent) {
        content += '<div class="alert alert-success">✅ 组状态一致</div>';
    } else {
        content += '<div class="alert alert-warning">⚠️ 发现不一致问题</div>';
    }
    
    // 详细信息
    if (result.issues && result.issues.length > 0) {
        content += '<h4>发现的问题:</h4><ul>';
        result.issues.forEach(issue => {
            content += `<li class="issue-item">${issue}</li>`;
        });
        content += '</ul>';
        
        // 修复按钮
        content += `
            <div class="fix-actions">
                <button type="button" class="btn btn-warning" onclick="fixGroupIssues(${result.group_id})">
                    🔧 自动修复
                </button>
            </div>
        `;
    }
    
    // 组信息
    if (result.group_info) {
        content += '<h4>组信息:</h4>';
        content += '<table class="table table-sm">';
        content += `<tr><td>组名:</td><td>${result.group_info.name}</td></tr>`;
        content += `<tr><td>用户数:</td><td>${result.group_info.user_count}</td></tr>`;
        content += `<tr><td>权限数:</td><td>${result.group_info.permission_count}</td></tr>`;
        if (result.group_info.role_identifier) {
            content += `<tr><td>角色标识:</td><td>${result.group_info.role_identifier}</td></tr>`;
        }
        content += '</table>';
    }
    
    content += '</div>';
    
    modal.querySelector('.modal-body').innerHTML = content;
    modal.style.display = 'block';
}

// 修复组问题
function fixGroupIssues(groupId) {
    if (!confirm('确定要自动修复发现的问题吗？此操作可能会修改组的配置。')) {
        return;
    }
    
    fetch(`/admin/permissions/group/${groupId}/fix-issues/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            'action': 'fix_issues',
            'group_id': groupId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ 问题修复完成！页面将刷新以显示最新状态。');
            location.reload();
        } else {
            alert('修复失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        console.error('修复错误:', error);
        alert('修复过程中发生错误，请查看控制台日志');
    });
}

// 批量同步所有组
function batchSyncAllGroups() {
    if (!confirm('确定要同步所有组的角色映射吗？这可能需要一些时间。')) {
        return;
    }
    
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = '🔄 同步中...';
    button.disabled = true;
    
    fetch('/admin/permissions/group/batch-sync/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            'action': 'batch_sync_all'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`✅ 批量同步完成！\n成功: ${data.success_count}\n失败: ${data.error_count}`);
            location.reload();
        } else {
            alert('批量同步失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        console.error('批量同步错误:', error);
        alert('同步过程中发生错误，请查看控制台日志');
    })
    .finally(() => {
        button.textContent = originalText;
        button.disabled = false;
    });
}

// 创建模态框
function createModal(title) {
    // 移除已存在的模态框
    const existingModal = document.getElementById('group-admin-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modal = document.createElement('div');
    modal.id = 'group-admin-modal';
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${title}</h5>
                    <button type="button" class="close" onclick="closeModal()">
                        <span>&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <!-- 内容将在这里填充 -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal()">关闭</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    return modal;
}

// 关闭模态框
function closeModal() {
    const modal = document.getElementById('group-admin-modal');
    if (modal) {
        modal.style.display = 'none';
        modal.remove();
    }
}

// 获取CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 添加批量操作按钮
    const changelistActions = document.querySelector('.actions');
    if (changelistActions) {
        const batchSyncButton = document.createElement('button');
        batchSyncButton.type = 'button';
        batchSyncButton.className = 'btn btn-info';
        batchSyncButton.innerHTML = '🔄 批量同步所有组';
        batchSyncButton.onclick = batchSyncAllGroups;
        
        changelistActions.appendChild(batchSyncButton);
    }
    
    // 为状态列添加工具提示
    const statusCells = document.querySelectorAll('td[class*="field-get_role_status"], td[class*="field-get_sync_status"]');
    statusCells.forEach(cell => {
        cell.title = '点击查看详细信息';
        cell.style.cursor = 'help';
    });
    
    // 点击模态框外部关闭
    document.addEventListener('click', function(event) {
        const modal = document.getElementById('group-admin-modal');
        if (modal && event.target === modal) {
            closeModal();
        }
    });
    
    // ESC键关闭模态框
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeModal();
        }
    });
});