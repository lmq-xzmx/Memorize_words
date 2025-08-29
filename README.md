# 单词记忆系统

一个基于Django的智能单词记忆和学习管理系统，支持多角色权限管理、个性化学习计划和进度跟踪。

## 🚀 最新更新 (2025-08-24)

### 架构重构完成

我们完成了一次重要的架构重构，主要改进包括：

- ✅ **JavaScript代码优化**: 删除6个冗余文件，减少代码重复
- ✅ **统一API接口**: 使用Django REST Framework提供标准化API
- ✅ **后端逻辑迁移**: 将业务逻辑从前端迁移到后端
- ✅ **模块化设计**: 采用模块化开发规范，提升代码质量

详细信息请查看 [架构重构文档](ARCHITECTURE_REFACTOR.md)

## 📋 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [API文档](#api文档)
- [部署指南](#部署指南)
- [开发指南](#开发指南)
- [更新日志](#更新日志)

## ✨ 功能特性

### 核心功能
- 🎯 **智能单词记忆**: 基于艾宾浩斯遗忘曲线的复习算法
- 📚 **多样化学习模式**: 支持拼写、选择、听力等多种练习方式
- 📊 **学习进度跟踪**: 详细的学习数据分析和可视化
- 🎮 **游戏化学习**: 积分、等级、成就系统提升学习动力

### 管理功能
- 👥 **多角色权限管理**: 管理员、教师、学生等不同角色权限
- 📖 **课程内容管理**: 灵活的课程和单词库管理
- 📈 **数据统计分析**: 学习效果分析和报告生成
- 🔄 **权限同步机制**: 自动化的角色权限同步

### 技术特性
- 🌐 **响应式设计**: 支持PC、平板、手机等多端访问
- ⚡ **高性能**: 优化的数据库查询和缓存机制
- 🔒 **安全可靠**: 完善的认证授权和数据保护
- 🔧 **易于扩展**: 模块化架构，便于功能扩展

## 🛠 技术栈

### 后端
- **框架**: Django 4.2+
- **API**: Django REST Framework
- **数据库**: PostgreSQL / MySQL / SQLite
- **缓存**: Redis
- **任务队列**: Celery

### 前端
- **基础**: HTML5, CSS3, JavaScript ES6+
- **UI框架**: Bootstrap 5
- **图表**: Chart.js
- **图标**: Font Awesome

### 开发工具
- **版本控制**: Git
- **代码质量**: ESLint, Prettier
- **测试**: Django Test Framework
- **部署**: Docker, Nginx

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 14+ (前端开发)
- PostgreSQL 12+ (推荐) 或 MySQL 8.0+
- Redis 6.0+ (可选，用于缓存)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd memorize-words
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置数据库**
   ```bash
   # 复制配置文件
   cp .env.example .env
   # 编辑 .env 文件，配置数据库连接
   
   # 执行数据库迁移
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **创建超级用户**
   ```bash
   python manage.py createsuperuser
   ```

6. **收集静态文件**
   ```bash
   python manage.py collectstatic
   ```

7. **启动开发服务器**
   ```bash
   python manage.py runserver
   ```

8. **访问应用**
   - 前端应用: http://localhost:8000
   - 管理后台: http://localhost:8000/admin
   - API文档: http://localhost:8000/api/docs

## 📁 项目结构

```
memorize-words/
├── apps/                          # Django应用目录
│   ├── accounts/                  # 用户账户管理
│   ├── permissions/               # 权限管理
│   │   ├── unified_ajax_api.py   # 统一API接口
│   │   └── api_urls.py           # API路由配置
│   ├── teaching/                  # 教学管理
│   └── words/                     # 单词管理
├── static/                        # 静态文件
│   ├── admin/js/                 # 管理后台JavaScript
│   │   ├── unified_role_selector.js  # 统一角色选择器
│   │   ├── xpath_optimizer.js        # XPath优化工具
│   │   └── role_management_auto_fill.js  # 自动填充
│   ├── css/                      # 样式文件
│   └── images/                   # 图片资源
├── templates/                     # 模板文件
├── memorize_words/               # 项目配置
├── requirements.txt              # Python依赖
├── manage.py                     # Django管理脚本
├── ARCHITECTURE_REFACTOR.md      # 架构重构文档
├── API_DOCUMENTATION.md          # API文档
└── README.md                     # 项目说明
```

## 📖 API文档

### 统一API端点

我们提供了统一的REST API接口，替代了原有分散的AJAX调用：

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/unified/role-choices/` | GET | 获取角色选择项 |
| `/api/unified/role-info/` | GET | 获取角色信息 |
| `/api/unified/sync-role-groups/` | POST | 同步角色组 |
| `/api/unified/menu-validity/` | GET | 菜单有效性检查 |
| `/api/unified/user-sync-status/` | GET | 用户同步状态 |
| `/api/unified/role-permission-sync/` | POST | 权限同步 |

详细的API使用说明请查看 [API文档](API_DOCUMENTATION.md)

### 认证方式
- **Web界面**: Django Session认证
- **API调用**: Token认证 (可选)
- **管理后台**: Django Admin认证

## 🚀 部署指南

### Docker部署 (推荐)

1. **构建镜像**
   ```bash
   docker build -t memorize-words .
   ```

2. **运行容器**
   ```bash
   docker-compose up -d
   ```

### 传统部署

1. **配置Web服务器** (Nginx)
2. **配置WSGI服务器** (Gunicorn)
3. **配置数据库**
4. **配置静态文件服务**
5. **配置SSL证书**

详细部署步骤请参考部署文档。

## 👨‍💻 开发指南

### 代码规范

- **Python**: 遵循PEP 8规范
- **JavaScript**: 使用ESLint配置
- **模块化**: 每个文件不超过400行代码
- **注释**: 关键逻辑必须添加注释

### 开发流程

1. **创建功能分支**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **开发和测试**
   ```bash
   python manage.py test
   ```

3. **代码检查**
   ```bash
   flake8 .
   ```

4. **提交代码**
   ```bash
   git commit -m "feat: add new feature"
   ```

### 测试

```bash
# 运行所有测试
python manage.py test

# 运行特定应用测试
python manage.py test apps.accounts

# 生成测试覆盖率报告
coverage run --source='.' manage.py test
coverage report
```

## 📝 更新日志

### v2.0.0 (2025-08-24)

#### 🎉 重大更新
- **架构重构**: 完成JavaScript代码重构，提升代码质量
- **统一API**: 实现Django REST Framework统一API接口
- **性能优化**: 减少前端代码量，提升页面加载速度

#### ✨ 新增功能
- 统一角色选择器组件
- 自动化权限同步机制
- 完善的错误处理和日志记录

#### 🔧 技术改进
- 删除6个冗余JavaScript文件
- 实现模块化开发规范
- 优化数据库查询性能

#### 📚 文档更新
- 新增架构重构文档
- 完善API使用文档
- 更新开发指南

### v1.x.x
- 基础功能实现
- 用户管理系统
- 单词学习功能
- 权限管理系统

## 🤝 贡献指南

我们欢迎所有形式的贡献，包括但不限于：

- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复

### 贡献流程

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- **项目维护者**: 开发团队
- **问题反馈**: 通过GitHub Issues
- **技术讨论**: 通过GitHub Discussions

---

**⭐ 如果这个项目对你有帮助，请给我们一个Star！**