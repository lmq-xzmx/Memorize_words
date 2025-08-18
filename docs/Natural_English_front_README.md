# Natural English 前端项目

## 项目简介

Natural English 前端项目是一个基于 Vue 3 + Vite 构建的现代化英语学习平台前端应用，提供用户注册、登录和个人信息管理功能。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vue Router 4** - 官方路由管理器
- **Vite** - 下一代前端构建工具
- **Axios** - HTTP 客户端库
- **现代 CSS** - 响应式设计和美观界面

## 项目结构

```
Natural_English_front/
├── index.html          # HTML 入口文件
├── main.js            # 应用入口文件
├── App.vue            # 根组件
├── vite.config.js     # Vite 配置文件
├── package.json       # 项目依赖配置
├── pages/             # 页面组件
│   ├── Login.vue      # 登录页面
│   ├── Register.vue   # 注册页面
│   └── Dashboard.vue  # 用户仪表板
└── utils/             # 工具模块
    └── api.js         # API 接口封装
```

## 功能特性

### 🔐 用户认证
- 用户注册（支持学生/教师角色）
- 用户登录
- 自动 Token 认证
- 安全登出

### 👤 个人信息管理
- 查看个人资料
- 编辑个人信息
- 修改密码
- 角色权限管理

### 🎨 界面设计
- 现代化 UI 设计
- 响应式布局
- 移动端适配
- 渐变色彩搭配

### 🔧 技术特性
- 模块化组件设计
- API 统一封装
- 路由守卫保护
- 错误处理机制

## 快速开始

### 环境要求
- Node.js >= 16.0.0
- npm >= 8.0.0

### 安装依赖
```bash
cd Natural_English_front
npm install
```

### 启动开发服务器
```bash
npm run dev
```

访问 http://localhost:3000 查看应用

### 构建生产版本
```bash
npm run build
```

### 预览生产版本
```bash
npm run preview
```

## API 集成

项目已完整集成后端 API 接口：

- **基础 URL**: `http://localhost:8000/accounts/api/`
- **认证方式**: Token 认证
- **代理配置**: Vite 开发服务器已配置 API 代理

### 主要接口

| 功能 | 方法 | 路径 |
|------|------|------|
| 用户注册 | POST | `/auth/register/` |
| 用户登录 | POST | `/auth/login/` |
| 获取用户信息 | GET | `/users/profile/` |
| 更新用户信息 | PUT | `/users/profile/` |
| 修改密码 | POST | `/users/change_password/` |
| 用户登出 | POST | `/users/logout/` |

## 页面说明

### 登录页面 (`/login`)
- 用户名/密码登录
- 表单验证
- 错误提示
- 自动跳转

### 注册页面 (`/register`)
- 完整用户信息收集
- 角色选择（学生/教师）
- 实时表单验证
- 响应式布局

### 用户仪表板 (`/dashboard`)
- 个人信息展示
- 信息编辑功能
- 密码修改
- 快速操作入口

## 开发规范

### 代码组织
- 组件按功能模块划分
- API 接口统一封装
- 样式采用 Scoped CSS
- 遵循 Vue 3 Composition API 规范

### 命名规范
- 组件名使用 PascalCase
- 文件名使用 kebab-case
- 变量名使用 camelCase

### 错误处理
- 统一的 API 错误拦截
- 用户友好的错误提示
- 网络异常处理

## 部署说明

### 开发环境
1. 确保后端服务运行在 `http://localhost:8000`
2. 启动前端开发服务器
3. 访问 `http://localhost:3000`

### 生产环境
1. 构建生产版本：`npm run build`
2. 部署 `dist` 目录到 Web 服务器
3. 配置反向代理到后端 API

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88
- 移动端：Android >= 4.4, iOS >= 9

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

---

**开发团队**: Natural English 项目组  
**更新时间**: 2024年1月  
**版本**: v1.0.0