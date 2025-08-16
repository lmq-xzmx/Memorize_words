# Natural English 账号注册API文档

## 概述

本文档提供了Natural English平台完整的账号注册、登录和用户管理API接口说明，支持前后端分离架构。

## 基础信息

- **基础URL**: `http://localhost:8000/accounts/api/`
- **认证方式**: Token认证
- **数据格式**: JSON
- **字符编码**: UTF-8

## 1. 用户注册

### 接口地址
```
POST /accounts/api/auth/register/
```

### 请求参数
```json
{
    "username": "string",          // 用户名（必填，唯一）
    "email": "string",             // 邮箱（必填，唯一）
    "real_name": "string",         // 真实姓名（必填）
    "phone": "string",             // 手机号（可选）
    "role": "string",              // 角色：student/teacher/admin（必填）
    "grade_level": "string",       // 年级（可选）
    "school": "string",            // 学校（可选）
    "class_name": "string",        // 班级（可选）
    "password": "string",          // 密码（必填，至少8位）
    "confirm_password": "string"   // 确认密码（必填，需与密码一致）
}
```

### 响应示例
**成功响应 (201 Created)**
```json
{
    "user": {
        "id": 1,
        "username": "student001",
        "email": "student@example.com",
        "real_name": "张三",
        "phone": "13800138000",
        "role": "student",
        "grade_level": "高一",
        "school": "北京中学",
        "class_name": "1班",
        "is_active": true,
        "date_joined": "2024-01-01T10:00:00Z"
    },
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "message": "注册成功"
}
```

**错误响应 (400 Bad Request)**
```json
{
    "username": ["该用户名已存在"],
    "email": ["该邮箱已被注册"],
    "confirm_password": ["两次输入的密码不一致"]
}
```

## 2. 用户登录

### 接口地址
```
POST /accounts/api/auth/login/
```

### 请求参数
```json
{
    "username": "string",    // 用户名（必填）
    "password": "string"     // 密码（必填）
}
```

### 响应示例
**成功响应 (200 OK)**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user": {
        "id": 1,
        "username": "student001",
        "email": "student@example.com",
        "real_name": "张三",
        "role": "student",
        "is_active": true
    },
    "message": "登录成功"
}
```

**错误响应 (400 Bad Request)**
```json
{
    "non_field_errors": ["用户名或密码错误"]
}
```

## 3. 获取用户信息

### 接口地址
```
GET /accounts/api/users/profile/
```

### 请求头
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### 响应示例
```json
{
    "id": 1,
    "username": "student001",
    "email": "student@example.com",
    "real_name": "张三",
    "phone": "13800138000",
    "grade_level": "高一",
    "school": "北京中学",
    "class_name": "1班",
    "role": "student",
    "date_joined": "2024-01-01T10:00:00Z",
    "last_login": "2024-01-02T09:00:00Z"
}
```

## 4. 更新用户信息

### 接口地址
```
PUT /accounts/api/users/profile/
PATCH /accounts/api/users/profile/
```

### 请求头
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

### 请求参数
```json
{
    "email": "newemail@example.com",
    "real_name": "李四",
    "phone": "13900139000",
    "grade_level": "高二",
    "school": "上海中学",
    "class_name": "2班"
}
```

### 响应示例
```json
{
    "id": 1,
    "username": "student001",
    "email": "newemail@example.com",
    "real_name": "李四",
    "phone": "13900139000",
    "grade_level": "高二",
    "school": "上海中学",
    "class_name": "2班",
    "role": "student",
    "date_joined": "2024-01-01T10:00:00Z",
    "last_login": "2024-01-02T09:00:00Z"
}
```

## 5. 修改密码

### 接口地址
```
POST /accounts/api/users/change_password/
```

### 请求头
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

### 请求参数
```json
{
    "old_password": "string",      // 原密码（必填）
    "new_password": "string",      // 新密码（必填，至少8位）
    "confirm_password": "string"   // 确认新密码（必填）
}
```

### 响应示例
**成功响应 (200 OK)**
```json
{
    "message": "密码修改成功"
}
```

**错误响应 (400 Bad Request)**
```json
{
    "old_password": ["原密码错误"],
    "confirm_password": ["两次输入的新密码不一致"]
}
```

## 6. 用户登出

### 接口地址
```
POST /accounts/api/users/logout/
```

### 请求头
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### 响应示例
```json
{
    "message": "登出成功"
}
```

## 7. 学习档案管理

### 获取学习档案
```
GET /accounts/api/learning-profiles/
```

### 创建学习档案
```
POST /accounts/api/learning-profiles/
```

### 请求参数
```json
{
    "learning_goals": "string",           // 学习目标
    "preferred_difficulty": "string",     // 偏好难度：beginner/intermediate/advanced
    "daily_target": 30,                   // 每日学习目标（分钟）
    "study_time_preference": "string"     // 学习时间偏好：morning/afternoon/evening
}
```

## 8. 角色增项管理

### 8.1 获取角色扩展字段

#### 根据角色获取扩展字段
```
GET /accounts/api/role-extensions/by_role/?role=student
```

**请求参数**
- `role`: 角色类型（student/teacher/admin）

**响应示例**
```json
[
    {
        "id": 1,
        "role": "student",
        "role_display": "学生",
        "field_name": "school",
        "field_label": "学校",
        "field_type": "text",
        "field_type_display": "文本",
        "is_required": true,
        "is_active": true,
        "show_in_frontend_register": true,
        "show_in_backend_admin": true,
        "show_in_profile": true
    },
    {
        "id": 2,
        "role": "student",
        "role_display": "学生",
        "field_name": "class_name",
        "field_label": "班级",
        "field_type": "text",
        "field_type_display": "文本",
        "is_required": false,
        "is_active": true,
        "show_in_frontend_register": true,
        "show_in_backend_admin": true,
        "show_in_profile": true
    }
]
```

#### 获取用于注册的扩展字段
```
GET /accounts/api/role-extensions/for_register/?role=student
```

**说明**: 只返回设置为在前台注册中显示的扩展字段

#### 获取用于后台管理的扩展字段（管理员权限）
```
GET /accounts/api/role-extensions/for_admin/?role=student
```

**请求头**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**说明**: 只返回设置为在后台管理中显示的扩展字段，需要管理员权限

### 8.2 管理角色扩展字段（管理员权限）

#### 获取所有扩展字段
```
GET /accounts/api/role-extensions/
```

#### 创建扩展字段
```
POST /accounts/api/role-extensions/
```

**请求参数**
```json
{
    "role": "student",
    "field_name": "hobby",
    "field_label": "兴趣爱好",
    "field_type": "text",
    "field_choices": "",
    "is_required": false,
    "help_text": "请填写您的兴趣爱好",
    "sort_order": 10,
    "is_active": true,
    "show_in_frontend_register": true,
    "show_in_backend_admin": true,
    "show_in_profile": true
}
```

**字段类型说明**
- `text`: 文本
- `textarea`: 多行文本
- `number`: 数字
- `email`: 邮箱
- `url`: 网址
- `phone`: 电话
- `select`: 下拉选择
- `radio`: 单选
- `checkbox`: 多选
- `date`: 日期
- `datetime`: 日期时间

#### 更新扩展字段
```
PUT /accounts/api/role-extensions/{id}/
PATCH /accounts/api/role-extensions/{id}/
```

#### 删除扩展字段
```
DELETE /accounts/api/role-extensions/{id}/
```

### 8.3 用户扩展数据管理

#### 获取我的扩展数据
```
GET /accounts/api/user-extension-data/my_data/
```

**请求头**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**响应示例**
```json
[
    {
        "id": 1,
        "user": 1,
        "user_username": "student001",
        "extension": 1,
        "extension_field_label": "学校",
        "extension_field_type": "text",
        "value": "北京中学",
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
    }
]
```

#### 批量更新扩展数据
```
POST /accounts/api/user-extension-data/batch_update/
```

**请求参数**
```json
{
    "extension_data": {
        "school": "北京大学附中",
        "class_name": "高三1班",
        "hobby": "篮球、阅读"
    }
}
```

**管理员批量更新其他用户数据**
```json
{
    "user_id": 2,
    "extension_data": {
        "school": "清华大学附中",
        "class_name": "高二3班"
    }
}
```

### 8.4 带扩展字段的注册

#### 接口地址
```
POST /accounts/api/auth/register/
```

**请求参数（包含扩展字段）**
```json
{
    "username": "student002",
    "email": "student002@example.com",
    "real_name": "王五",
    "phone": "13800138001",
    "role": "student",
    "grade_level": "高一",
    "password": "password123",
    "confirm_password": "password123",
    "extension_data": {
        "school": "北京中学",
        "class_name": "1班",
        "hobby": "足球"
    }
}
```

**说明**: 
- `extension_data` 字段包含角色相关的扩展数据
- 系统会自动验证必填的扩展字段
- 只有设置为在前台注册中显示的字段才会被处理

## 9. 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或Token无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 9. 前端集成示例

### JavaScript/Axios示例

```javascript
// 用户注册
const register = async (userData) => {
    try {
        const response = await axios.post('/accounts/api/auth/register/', userData);
        // 保存Token
        localStorage.setItem('token', response.data.token);
        return response.data;
    } catch (error) {
        console.error('注册失败:', error.response.data);
        throw error;
    }
};

// 用户登录
const login = async (username, password) => {
    try {
        const response = await axios.post('/accounts/api/auth/login/', {
            username,
            password
        });
        // 保存Token
        localStorage.setItem('token', response.data.token);
        return response.data;
    } catch (error) {
        console.error('登录失败:', error.response.data);
        throw error;
    }
};

// 设置请求拦截器，自动添加Token
axios.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }
    return config;
});

// 获取用户信息
const getUserProfile = async () => {
    try {
        const response = await axios.get('/accounts/api/users/profile/');
        return response.data;
    } catch (error) {
        console.error('获取用户信息失败:', error.response.data);
        throw error;
    }
};
```

## 10. 注意事项

1. **Token认证**: 除注册和登录接口外，其他接口都需要在请求头中携带Token
2. **密码安全**: 密码需要至少8位，包含字母和数字
3. **用户名唯一性**: 注册前建议先检查用户名是否已存在
4. **邮箱验证**: 邮箱格式需要符合标准格式
5. **角色权限**: 不同角色用户具有不同的API访问权限
6. **CORS配置**: 前端开发时需要确保后端已正确配置CORS

## 11. 开发环境配置

### 启动后端服务
```bash
cd /Users/xzmx/Downloads/my-project/Natural_English
python manage.py runserver
```

### API测试
可以使用Postman、curl或浏览器开发者工具测试API接口。

---

**文档版本**: v1.0  
**更新时间**: 2024年1月  
**维护人员**: Natural English开发团队