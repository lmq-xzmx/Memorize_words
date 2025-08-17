# Natural English Front-end 开发规范

## 技术栈规范

### 核心技术栈
- **框架**: Vue 3 + Composition API
- **构建工具**: Vite
- **语言**: TypeScript (不再使用 JavaScript)
- **状态管理**: Vuex 4
- **路由**: Vue Router 4
- **样式**: SCSS + CSS3 + CSS Variables + BEM

### TypeScript 配置要求
1. 所有新文件必须使用 `.ts` 或 `.vue` 扩展名
2. 严格模式开启，确保类型安全
3. 必须为所有函数参数和返回值添加类型注解
4. 使用 `vue-tsc` 进行类型检查
5. 构建前必须通过类型检查

### 文件结构规范
```
src/
├── components/     # Vue组件
├── composables/    # Vue 3 组合式函数
├── pages/         # 页面组件
├── router/        # 路由配置
├── store/         # Vuex状态管理
├── services/      # API服务
├── utils/         # 工具函数
├── styles/        # 样式文件
├── assets/        # 静态资源
└── config/        # 配置文件
```

### 开发规范
1. **模块化开发**: 单个文件代码行数控制在400行以内
2. **类型安全**: 所有模块必须有完整的TypeScript类型定义
3. **组件规范**: 使用Vue 3 Composition API + TypeScript
4. **样式规范**: 使用SCSS + BEM命名规范
5. **权限控制**: 基于RBAC模型的前端权限管理

### 构建和部署
- 开发服务器: `npm run dev`
- 类型检查: `npm run type-check`
- 构建: `npm run build` (包含类型检查)
- 预览: `npm run preview`

### 迁移说明
本项目已从 Vue+Vite+JS 技术栈迁移至 Vue+Vite+TS，所有新开发必须遵循TypeScript规范。