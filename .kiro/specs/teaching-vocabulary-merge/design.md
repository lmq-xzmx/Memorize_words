# Design Document

## Overview

本文档概述了合并 Teaching 和 Vocabulary_Manager 应用的技术设计方案，旨在消除功能重叠，降低系统复杂度，提高可维护性。通过深入分析，我们将采用以 Teaching 应用为主体，将 Vocabulary_Manager 的功能和数据迁移过来的策略。

## Architecture

### 当前状态分析

Teaching 和 Vocabulary_Manager 应用存在显著的功能重叠：

1. **学习目标管理**: 两个应用都有 LearningGoal 模型，但设计略有不同
2. **学习会话管理**: Teaching.LearningSession vs Vocabulary_Manager.StudySession
3. **学习计划管理**: 两个应用都有 LearningPlan 模型，功能相似但实现不同
4. **学习进度跟踪**: Teaching.WordLearningRecord vs Vocabulary_Manager.WordLearningProgress
5. **看板/仪表板视图**: 两个应用都提供类似的进度可视化功能
6. **后台管理**: 两套独立的 admin 配置

### 目标架构

合并后的应用将所有学习管理功能整合到一个统一的系统中，同时保持向后兼容性。

**选择 Teaching 作为主应用的原因：**
- Teaching 应用具有更完整的指导练习功能（GuidedPracticeSession 等）
- Teaching 的模型设计更加灵活，支持多种学习模式
- Teaching 应用的 API 设计更加成熟
- Teaching 应用已经有完整的前端界面

## Components and Interfaces

### 模型整合策略

#### 主要模型（Teaching 应用 - 目标应用）
Teaching 应用将保留并增强以下模型：
- `LearningGoal` - 增强以包含两个应用的功能
- `LearningSession` - 统一会话管理
- `LearningPlan` - 合并计划功能
- `WordLearningRecord` - 综合进度跟踪
- `GoalWord` - 目标单词关联
- 指导练习相关模型（保持不变）

#### 需要迁移的模型（从 Vocabulary_Manager）
- `StudySession` → 合并到 `LearningSession`
- `WordLearningProgress` → 合并到 `WordLearningRecord`
- `UserStreak` → 迁移到 Teaching 应用
- `DailyStudyRecord` → 迁移到 Teaching 应用

### 视图整合策略

#### URL 结构调整
- 主要路由保持在 `/teaching/` 下
- Vocabulary_Manager 路由将重定向到对应的 Teaching 路由
- 管理界面合并到 Teaching 的 admin 配置中

#### 模板整合
- 仪表板视图将统一
- 看板/进度视图将合并
- 表单模板将标准化

### Admin 界面整合

#### 合并策略
- 将 Vocabulary_Manager 的 admin 配置迁移到 Teaching 的 admin.py
- 保留 Vocabulary_Manager 中更完善的管理功能
- 统一管理界面的用户体验

## Data Models

### 增强的 LearningGoal 模型
```python
class LearningGoal(models.Model):
    # 现有 Teaching 字段
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    name = models.CharField(max_length=200, verbose_name='目标名称')
    description = models.TextField(blank=True, verbose_name='目标描述')
    target_words_count = models.IntegerField(default=100, verbose_name='目标单词数量')
    start_date = models.DateField(default=timezone.now, verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    # 从 vocabulary_manager 增强的字段
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES, default='vocabulary_list', verbose_name='目标类型')
    is_current = models.BooleanField(default=False, verbose_name='是否为当前目标')
    total_words = models.IntegerField(default=0, verbose_name='总单词数')
    learned_words = models.IntegerField(default=0, verbose_name='已学单词数')
    
    # 关联关系（现有）
    word_sets = models.ManyToManyField(WordSet, blank=True, verbose_name='关联单词集')
    vocabulary_lists = models.ManyToManyField(VocabularyList, blank=True, verbose_name='关联单词库')
    
    # 新增单一关联字段（从 vocabulary_manager）
    vocabulary_list = models.ForeignKey(VocabularyList, null=True, blank=True, on_delete=models.CASCADE, related_name='single_goals')
    word_set = models.ForeignKey(WordSet, null=True, blank=True, on_delete=models.CASCADE, related_name='single_goals')
    grade_level = models.ForeignKey('words.WordGradeLevel', null=True, blank=True, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
```

### 增强的 LearningSession 模型
```python
class LearningSession(models.Model):
    # 现有 Teaching 字段
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_sessions', verbose_name='用户')
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, related_name='sessions', verbose_name='学习目标')
    start_time = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    words_studied = models.IntegerField(default=0, verbose_name='学习单词数')
    correct_answers = models.IntegerField(default=0, verbose_name='正确答案数')
    total_answers = models.IntegerField(default=0, verbose_name='总答案数')
    
    # 从 vocabulary_manager 增强的字段
    duration = models.DurationField(null=True, blank=True, verbose_name='学习时长')
    words_learned = models.IntegerField(default=0, verbose_name='掌握单词数')
    
    # 指导模式相关字段（保持现有）
    is_guided = models.BooleanField(default=False, verbose_name='是否为指导模式')
    guided_session = models.ForeignKey('GuidedPracticeSession', on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='guided_learning_sessions')
```

### 增强的 LearningPlan 模型
```python
class LearningPlan(models.Model):
    # 合并两个应用的计划类型选择
    PLAN_TYPE_CHOICES = [
        ('daily', '每日计划'),
        ('weekly', '每周计划'),
        ('custom', '自定义计划'),
    ]
    
    PLAN_MODE_CHOICES = [
        ('mechanical', '机械模式'),
        ('daily_progress', '日进模式'),
        ('workday', '工作日模式'),
        ('weekend', '周末模式'),
    ]
    
    STATUS_CHOICES = [
        ('active', '进行中'),
        ('completed', '已完成'),
        ('paused', '已暂停'),
        ('cancelled', '已取消'),
    ]
    
    # 基本字段
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, related_name='plans', verbose_name='学习目标')
    name = models.CharField(max_length=100, verbose_name='计划名称')
    
    # 从 Teaching 的字段
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default='daily', verbose_name='计划类型')
    words_per_day = models.IntegerField(default=10, verbose_name='每日单词数')
    review_interval = models.IntegerField(default=1, verbose_name='复习间隔（天）')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    # 从 Vocabulary_Manager 的字段
    plan_mode = models.CharField(max_length=20, choices=PLAN_MODE_CHOICES, default='daily_progress', verbose_name='计划模式')
    start_date = models.DateField(default=date.today, verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    total_words = models.IntegerField(default=0, verbose_name='总单词数')
    daily_target = models.IntegerField(default=0, verbose_name='每日目标单词数')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
```

### 增强的 WordLearningRecord 模型
```python
class WordLearningRecord(models.Model):
    # 现有 Teaching 字段
    session = models.ForeignKey(LearningSession, on_delete=models.CASCADE, related_name='records', verbose_name='学习会话')
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, related_name='learning_records', verbose_name='学习目标')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='learning_records', verbose_name='单词')
    user_answer = models.CharField(max_length=200, blank=True, verbose_name='用户答案')
    is_correct = models.BooleanField(default=False, verbose_name='是否正确')
    response_time = models.FloatField(default=0, verbose_name='响应时间（秒）')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    # 从 vocabulary_manager 增强的字段
    review_count = models.IntegerField(default=0, verbose_name='复习次数')
    last_review_date = models.DateTimeField(null=True, blank=True, verbose_name='最后复习时间')
    is_mastered = models.BooleanField(default=False, verbose_name='是否已掌握')
    is_forgotten = models.BooleanField(default=False, verbose_name='是否已遗忘')
    mastered_date = models.DateTimeField(null=True, blank=True, verbose_name='掌握时间')
    first_learned_date = models.DateTimeField(auto_now_add=True, verbose_name='首次学习时间')
    
    # 指导练习相关字段（保持现有）
    is_guided = models.BooleanField(default=False, verbose_name='是否为指导模式')
    guided_question = models.ForeignKey('GuidedPracticeQuestion', on_delete=models.SET_NULL, null=True, blank=True)
```

### 需要迁移的附加模型

#### UserStreak 模型（迁移到 Teaching）
```python
class UserStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learning_streak')
    current_streak = models.IntegerField(default=0, verbose_name='当前连续天数')
    longest_streak = models.IntegerField(default=0, verbose_name='最长连续天数')
    last_study_date = models.DateField(null=True, blank=True, verbose_name='最后学习日期')
    total_study_days = models.IntegerField(default=0, verbose_name='总学习天数')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### DailyStudyRecord 模型（迁移到 Teaching）
```python
class DailyStudyRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_study_records')
    learning_plan = models.ForeignKey(LearningPlan, on_delete=models.CASCADE, related_name='daily_records')
    study_date = models.DateField(default=date.today, verbose_name='学习日期')
    target_words = models.IntegerField(default=0, verbose_name='目标单词数')
    completed_words = models.IntegerField(default=0, verbose_name='完成单词数')
    study_duration = models.DurationField(null=True, blank=True, verbose_name='学习时长')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Error Handling

### 数据迁移安全性
- 实施全面的备份程序
- 为所有迁移操作使用数据库事务
- 为失败的迁移提供回滚机制
- 在每个迁移步骤验证数据完整性

### 兼容性处理
- 在过渡期间维护 API 端点兼容性
- 为已弃用的功能实施优雅的回退
- 为现有集成提供清晰的迁移路径

### 错误恢复
- 详细的错误日志记录
- 自动错误检测和报告
- 数据一致性检查
- 失败操作的自动重试机制

## Testing Strategy

### 迁移测试
- 所有数据迁移函数的单元测试
- 合并功能的集成测试
- 大数据集的性能测试
- 失败场景的回滚测试

### 功能测试
- 合并模型的全面测试覆盖
- 向后兼容性的 API 端点测试
- 合并界面的 UI 测试
- 工作流连续性的用户验收测试

### 数据完整性测试
- 外键关系验证
- 合并模型间的数据一致性检查
- 性能影响评估
- 内存使用优化验证

### 用户体验测试
- 界面一致性测试
- 功能完整性验证
- 性能基准测试
- 用户工作流测试