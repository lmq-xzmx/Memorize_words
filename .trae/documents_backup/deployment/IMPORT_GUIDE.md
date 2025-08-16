# 单词导入和数据统一指南

## 问题解决状态

✅ **已解决的问题：**
1. HTTP 405 错误 - 批量操作页面现在支持GET请求
2. TemplateDoesNotExist 错误 - 已创建所有必需的模板文件
3. FieldError 错误 - 已修复admin.py中的字段引用错误
4. "导入的单词"和"单词"统一问题 - 提供了转换工具

## 新增功能

### 1. 批量操作页面
- **批量解决冲突**: `/words/batch-resolve-conflicts/`
- **批量导入到用户词库**: `/words/batch-import-to-words/`
- **批量删除单词**: `/words/batch-delete-words/`
- **冲突解决记录**: `/words/conflict-resolution/`

### 2. 管理命令

#### CSV导入命令
```bash
python manage.py import_vocabulary_from_csv /path/to/file.csv --source="教材名称" --list-name="词库名称"
```

**参数说明：**
- `--source`: 词库来源（必需）
- `--list-name`: 词库列表名称（必需）
- `--description`: 词库描述
- `--conflict-strategy`: 冲突处理策略（mark/skip/overwrite/merge）
- `--encoding`: 文件编码（默认utf-8）
- `--delimiter`: CSV分隔符（默认逗号）

#### 数据转换命令（解决"导入的单词"和"单词"统一问题）
```bash
# 试运行，查看转换效果
python manage.py convert_imported_to_words --dry-run

# 为特定用户转换
python manage.py convert_imported_to_words --user-id=1 --conflict-strategy=merge

# 转换特定词库
python manage.py convert_imported_to_words --vocabulary-list-id=1

# 自动分配用户并转换所有数据
python manage.py convert_imported_to_words --auto-assign-user --conflict-strategy=merge
```

**冲突处理策略：**
- `merge`: 智能合并数据（推荐）
- `skip`: 跳过已存在的单词
- `overwrite`: 覆盖已存在的单词

### 3. 数据迁移工具

从wordbook_backend项目迁移数据：
```bash
python migrate_wordbook_data.py --source-db=/path/to/wordbook_backend/db.sqlite3 --action=sync_all
```

## 使用流程

### 方案1：从CSV文件导入
1. 准备CSV文件（包含word, definition, phonetic等字段）
2. 使用import_vocabulary_from_csv命令导入
3. 使用convert_imported_to_words命令转换为用户单词

### 方案2：从wordbook_backend迁移
1. 使用migrate_wordbook_data.py脚本迁移数据
2. 使用convert_imported_to_words命令统一数据结构

### 方案3：通过Web界面操作
1. 访问批量操作页面
2. 使用API进行批量操作（需要POST请求发送JSON数据）

## CSV文件格式要求

```csv
word,definition,phonetic,part_of_speech,example,note,grade,textbook_version
hello,你好,/həˈloʊ/,interjection,Hello world!,常用问候语,1,人教版
world,世界,/wɜːrld/,noun,The world is beautiful,,,人教版
```

**必需字段：**
- `word`: 单词（必需）
- `definition`: 释义（推荐）

**可选字段：**
- `phonetic`: 音标
- `part_of_speech`: 词性
- `example`: 例句
- `note`: 备注
- `grade`: 年级
- `textbook_version`: 教材版本

## 注意事项

1. **权限要求**: 所有操作都需要用户登录
2. **数据备份**: 执行转换前建议备份数据库
3. **试运行**: 使用--dry-run参数先测试转换效果
4. **批量操作**: Web界面的批量操作需要通过POST请求发送JSON数据
5. **冲突处理**: 建议使用merge策略进行智能合并

## 故障排除

### 常见错误
1. **FieldError**: 检查模型字段名称是否正确
2. **TemplateDoesNotExist**: 确认模板文件已创建
3. **HTTP 405**: 确认视图支持相应的HTTP方法
4. **权限错误**: 确认用户已登录且有相应权限

### 日志查看
```bash
tail -f django.log
```

## 技术实现

- **模型统一**: ImportedVocabulary → Word 转换
- **冲突解决**: 智能合并算法
- **批量处理**: 事务保护和错误处理
- **模板系统**: 完整的前端页面支持
- **管理命令**: 灵活的命令行工具