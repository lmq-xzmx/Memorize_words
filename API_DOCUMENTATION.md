# 统一AJAX API文档

## 概述

本文档描述了项目中统一AJAX API的使用方法，这些API替代了原有分散的JavaScript AJAX调用，提供了更加统一和标准化的接口。

## 基础信息

- **基础URL**: `/api/unified/`
- **认证方式**: Django Session认证
- **数据格式**: JSON
- **错误处理**: 标准HTTP状态码 + JSON错误信息

## API端点列表

### 1. 获取角色选择项

**端点**: `GET /api/unified/role-choices/`

**描述**: 获取所有可用的角色选择项，用于下拉菜单等场景。

**请求参数**: 无

**响应示例**:
```json
{
  "success": true,
  "roles": [
    {
      "value": "admin",
      "text": "管理员",
      "description": "系统管理员角色"
    },
    {
      "value": "teacher",
      "text": "教师",
      "description": "教师角色"
    }
  ]
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "错误描述"
}
```

**替代的JavaScript**: 原有的角色选择器相关AJAX调用

### 2. 获取角色信息

**端点**: `GET /api/unified/role-info/`

**描述**: 获取指定角色的详细信息。

**请求参数**:
- `role` (string, required): 角色标识

**请求示例**:
```
GET /api/unified/role-info/?role=admin
```

**响应示例**:
```json
{
  "success": true,
  "role_info": {
    "role": "admin",
    "display_name": "管理员",
    "description": "系统管理员角色",
    "is_active": true,
    "permissions_count": 25,
    "parent": null
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "角色不存在"
}
```

**替代的JavaScript**: `role_info` 相关AJAX调用

### 3. 同步角色组

**端点**: `POST /api/unified/sync-role-groups/`

**描述**: 将指定角色的权限同步到对应的Django组。

**请求参数**:
```json
{
  "role": "admin"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "角色组同步成功",
  "sync_result": {
    "group_created": false,
    "group_name": "Role_admin",
    "permissions_synced": 25
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "未找到角色组映射"
}
```

**替代的JavaScript**: `role_group_mapping.js`

### 4. 获取菜单有效性

**端点**: `GET /api/unified/menu-validity/`

**描述**: 获取指定角色和菜单级别的菜单权限信息。

**请求参数**:
- `role` (string, optional): 角色标识
- `menu_level` (string, optional): 菜单级别

**请求示例**:
```
GET /api/unified/menu-validity/?role=admin&menu_level=1
```

**响应示例**:
```json
{
  "success": true,
  "permissions": [
    {
      "menu_module__id": 1,
      "menu_module__name": "用户管理",
      "menu_module__key": "user_management",
      "menu_module__menu_level": 1,
      "can_access": true
    }
  ]
}
```

**替代的JavaScript**: `menu_validity_filter.js`

### 5. 获取用户同步状态

**端点**: `GET /api/unified/user-sync-status/`

**描述**: 获取用户的权限同步状态信息。

**请求参数**:
- `user_id` (integer, optional): 用户ID，不提供则返回所有用户状态

**请求示例**:
```
GET /api/unified/user-sync-status/?user_id=123
```

**响应示例**:
```json
{
  "success": true,
  "sync_status": {
    "user_id": 123,
    "username": "admin",
    "role": "admin",
    "groups": ["Role_admin", "Editors"],
    "last_sync": "2025-08-24T14:30:00Z"
  }
}
```

**批量查询响应示例**:
```json
{
  "success": true,
  "sync_status": [
    {
      "user_id": 123,
      "username": "admin",
      "role": "admin",
      "groups_count": 2
    }
  ]
}
```

**替代的JavaScript**: `user_sync_status.js`

### 6. 同步角色权限

**端点**: `POST /api/unified/role-permission-sync/`

**描述**: 同步指定角色的权限配置。

**请求参数**:
```json
{
  "role": "admin",
  "permissions": [
    {
      "menu_id": 1,
      "can_access": true
    },
    {
      "menu_id": 2,
      "can_access": false
    }
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "权限同步成功",
  "sync_result": {
    "permissions_synced": 2,
    "role": "admin"
  }
}
```

**替代的JavaScript**: `role_permission_sync.js`

## 兼容性API

为了确保平滑迁移，还提供了一些兼容性API函数：

### 兼容性端点

1. `GET /api/unified/compat/role-choices/` - 兼容原有角色选择接口
2. `POST /api/unified/compat/sync-role-groups/` - 兼容原有角色组同步接口
3. `GET /api/unified/compat/menu-validity/` - 兼容原有菜单有效性接口

## 使用示例

### JavaScript调用示例

```javascript
// 获取角色选择项
fetch('/api/unified/role-choices/')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('角色列表:', data.roles);
    } else {
      console.error('获取失败:', data.error);
    }
  });

// 同步角色组
fetch('/api/unified/sync-role-groups/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken()
  },
  body: JSON.stringify({
    role: 'admin'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('同步成功:', data.sync_result);
  } else {
    console.error('同步失败:', data.error);
  }
});

// CSRF Token获取函数
function getCsrfToken() {
  const token = document.querySelector('[name=csrfmiddlewaretoken]');
  return token ? token.value : '';
}
```

### jQuery调用示例

```javascript
// 使用jQuery进行API调用
$.ajax({
  url: '/api/unified/role-info/',
  method: 'GET',
  data: { role: 'admin' },
  success: function(data) {
    if (data.success) {
      console.log('角色信息:', data.role_info);
    }
  },
  error: function(xhr, status, error) {
    console.error('请求失败:', error);
  }
});
```

## 错误处理

### 标准错误格式

所有API都使用统一的错误响应格式：

```json
{
  "success": false,
  "error": "具体错误描述"
}
```

### 常见HTTP状态码

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

### 错误处理最佳实践

```javascript
fetch('/api/unified/role-choices/')
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    if (data.success) {
      // 处理成功响应
      handleSuccess(data);
    } else {
      // 处理业务错误
      handleError(data.error);
    }
  })
  .catch(error => {
    // 处理网络错误或其他异常
    console.error('请求失败:', error);
    showErrorMessage('网络错误，请稍后重试');
  });
```

## 性能优化

### 缓存策略

- 角色选择项数据会在客户端缓存5分钟
- 用户同步状态每30秒自动刷新
- 菜单权限信息缓存到用户会话结束

### 请求优化

- 使用批量查询减少HTTP请求数量
- 实现请求去重，避免重复调用
- 支持条件查询，减少不必要的数据传输

## 安全考虑

### 认证和授权

- 所有API都需要用户登录
- 基于Django的权限系统进行授权检查
- CSRF保护防止跨站请求伪造

### 数据验证

- 服务端对所有输入参数进行验证
- 防止SQL注入和XSS攻击
- 敏感数据不在响应中暴露

## 迁移指南

### 从旧API迁移

1. **识别现有调用**: 查找项目中的AJAX调用
2. **替换端点**: 使用新的统一API端点
3. **更新参数**: 调整请求参数格式
4. **测试验证**: 确保功能正常

### 迁移检查清单

- [ ] 更新所有AJAX调用的URL
- [ ] 调整请求参数格式
- [ ] 更新响应数据处理逻辑
- [ ] 测试错误处理流程
- [ ] 验证权限控制正常

## 版本历史

### v1.0 (2025-08-24)
- 初始版本发布
- 实现6个核心API端点
- 提供兼容性接口
- 完整的错误处理机制

---

**文档维护**: 开发团队  
**最后更新**: 2025年8月24日  
**API版本**: v1.0