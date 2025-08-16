# FieldError 'wordset' 字段错误修复报告

## 问题描述

用户在访问 `/admin/teaching/learninggoal/32/change/` 页面时遇到 `FieldError`：

```
FieldError at /admin/teaching/learninggoal/32/change/
Cannot resolve keyword 'wordset' into field. Choices are: created_at, definition, difficulty_level, example, goal_associations, grade, guidedpracticequestion, has_multiple_versions, id, learned_at, learning_progress, learning_records, mastery_level, note, parent_word, parent_word_id, part_of_speech, phonetic, resources, tags, textbook_version, updated_at, user_progress, version_data, version_number, versions, vocabulary_list, vocabulary_list_id, word, word_sets
```

## 问题分析

通过代码搜索发现，在 Django ORM 查询中使用了错误的字段名 `wordset`，而实际的字段名应该是 `word_sets`。

### 错误位置

1. **apps/teaching/models.py 第176行**
   ```python
   # 错误的代码
   wordset_words = Word.objects.filter(wordset__in=self.word_sets.all()).distinct()
   ```

2. **apps/teaching/unified_models.py 第101行**
   ```python
   # 错误的代码
   wordset_words = Word.objects.filter(
       wordset__in=self.word_sets.all()
   ).distinct()
   ```

### 根本原因

在 Word 模型中，与 WordSet 的多对多关系字段名为 `word_sets`（在 WordSet 模型中定义）：

```python
# apps/words/models.py - WordSet 模型
words = models.ManyToManyField(
    Word,
    related_name='word_sets',  # 这是正确的反向关系名
    verbose_name=_('单词'),
    blank=True
)
```

因此，从 Word 模型查询关联的 WordSet 时，应该使用 `word_sets` 而不是 `wordset`。

## 修复方案

### 1. 修复 teaching/models.py

```python
# 修复前
wordset_words = Word.objects.filter(wordset__in=self.word_sets.all()).distinct()

# 修复后
wordset_words = Word.objects.filter(word_sets__in=self.word_sets.all()).distinct()
```

### 2. 修复 teaching/unified_models.py

```python
# 修复前
wordset_words = Word.objects.filter(
    wordset__in=self.word_sets.all()
).distinct()

# 修复后
wordset_words = Word.objects.filter(
    word_sets__in=self.word_sets.all()
).distinct()
```

## 验证结果

修复完成后，运行 Django 系统检查：

```bash
python manage.py check
```

结果显示：
```
System check identified no issues (0 silenced).
```

## 技术要点

### Django ORM 关系查询规则

1. **正向查询**：从定义外键的模型查询关联模型
   ```python
   # WordSet 查询关联的 Word
   word_set.words.all()
   ```

2. **反向查询**：从被关联的模型查询定义外键的模型
   ```python
   # Word 查询关联的 WordSet，使用 related_name
   word.word_sets.all()
   ```

3. **跨关系查询**：使用双下划线语法
   ```python
   # 查询属于特定 WordSet 的所有 Word
   Word.objects.filter(word_sets__in=wordset_list)
   ```

### 字段命名约定

- **外键字段**：通常使用单数形式（如 `word_set`）
- **多对多字段**：通常使用复数形式（如 `word_sets`）
- **反向关系名**：通过 `related_name` 参数指定

## 预防措施

1. **代码审查**：在代码提交前仔细检查 ORM 查询语句
2. **单元测试**：为模型关系查询编写测试用例
3. **IDE 支持**：使用支持 Django 的 IDE，可以提供字段名自动补全
4. **文档维护**：保持模型关系文档的更新

## 总结

此次修复解决了因字段名错误导致的 `FieldError`，确保了后台管理界面的正常运行。修复涉及两个文件中的字段名纠正，从 `wordset` 改为正确的 `word_sets`。

**修复文件：**
- `apps/teaching/models.py`
- `apps/teaching/unified_models.py`

**修复效果：**
- 消除了 FieldError 错误
- 恢复了学习目标管理页面的正常功能
- 确保了 Django ORM 查询的正确性