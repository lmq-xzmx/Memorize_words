# 文章解析工厂 (Article Factory)

## 概述

文章解析工厂是Natural English平台的核心模块，专门用于智能解析英语文章，提供词汇分析、段落类型识别和交互式学习功能。

## 核心功能

### 1. 智能文章解析
- **词汇识别**: 自动识别文章中的词汇，支持多种词库来源
- **熟词检测**: 结合用户学习记录，标识已掌握词汇
- **词性标注**: 自动标注词性，支持标准化处理
- **频率分析**: 统计词汇出现频率

### 2. 段落类型识别
- **标题识别**: 自动识别文章标题
- **列表项**: 识别有序和无序列表
- **引用块**: 识别引用内容
- **代码块**: 识别代码片段
- **缩进文本**: 识别特殊格式文本
- **普通段落**: 标准段落内容

### 3. 交互式工具提示
- **悬停显示**: 鼠标悬停显示词汇详细信息
- **多词库支持**: 可选择不同词库作为信息来源
- **变体偏好**: 支持英式/美式等语言变体
- **自定义配置**: 可配置显示内容和样式

### 4. 可视化编辑器
- **实时预览**: 支持文章内容的实时预览
- **词汇高亮**: 可切换词汇高亮显示
- **段落导航**: 侧边栏段落结构导航
- **快捷操作**: 支持键盘快捷键操作

## 技术特性

### 数据模型
- **Article模型**: 存储文章基本信息和解析配置
- **ParsedParagraph模型**: 存储段落解析结果
- **用户关联**: 支持多用户文章管理

### API接口
- **RESTful API**: 提供完整的REST API接口
- **解析接口**: 支持文章首次解析和重新解析
- **配置接口**: 支持解析参数配置

### 管理后台
- **文章管理**: 完整的文章CRUD操作
- **批量操作**: 支持批量重新解析
- **预览功能**: 多种预览模式
- **编辑功能**: 源码编辑和可视化编辑

## 安装配置

### 1. 添加到INSTALLED_APPS
```python
LOCAL_APPS = [
    # ... 其他应用
    'apps.article_factory',
]
```

### 2. 配置URL路由
```python
urlpatterns = [
    # ... 其他路由
    path('article-factory/', include('apps.article_factory.urls')),
]
```

### 3. 运行数据库迁移
```bash
python manage.py makemigrations article_factory
python manage.py migrate
```

## 使用方法

### 管理后台使用
1. 访问 `/admin/article_factory/article/`
2. 点击"添加文章"创建新文章
3. 配置解析参数（词库来源、变体偏好等）
4. 点击"解析文章"进行智能解析
5. 使用预览、编辑功能查看和修改结果

### API使用
```python
# 解析文章
POST /article-factory/articles/{id}/parse_article/
{
    "vocabulary_source": "oxford",
    "variant_preference": "british",
    "enable_paragraph_analysis": true,
    "enable_tooltip": true
}

# 重新解析
POST /article-factory/articles/{id}/parse_existing_article/
```

## 配置选项

### 词库来源
- `oxford`: 牛津词典
- `cambridge`: 剑桥词典
- `collins`: 柯林斯词典
- `custom`: 自定义词库

### 语言变体
- `british`: 英式英语
- `american`: 美式英语
- `australian`: 澳式英语

### 解析选项
- `enable_paragraph_analysis`: 启用段落类型分析
- `enable_tooltip`: 启用工具提示功能

## 快捷键

- `Ctrl/Cmd + S`: 保存内容
- `Ctrl/Cmd + P`: 触发解析
- `Ctrl/Cmd + H`: 切换词汇高亮
- `Ctrl/Cmd + T`: 切换工具提示
- `ESC`: 关闭弹窗和提示

## 扩展开发

### 自定义词库
可以通过继承基础词库类来实现自定义词库：

```python
class CustomVocabulary:
    def get_word_info(self, word):
        # 实现自定义词汇信息获取逻辑
        pass
```

### 自定义段落类型
可以扩展段落类型识别逻辑：

```python
def custom_paragraph_detector(text):
    # 实现自定义段落类型识别
    return paragraph_type
```

## 依赖要求

- Django >= 4.2
- Django REST Framework
- Python >= 3.8
- 相关词库模块 (apps.words)
- 用户管理模块 (apps.accounts)

## 注意事项

1. 确保已正确配置用户认证系统
2. 词库数据需要预先导入
3. 大文章解析可能需要较长时间
4. 建议在生产环境中使用缓存优化性能

## 更新日志

### v1.0.0
- 初始版本发布
- 基础文章解析功能
- 段落类型识别
- 工具提示功能
- 管理后台界面
- 可视化编辑器