from django.db import models, transaction
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import timedelta
import json
import os

# 定义年级选择
GRADE_CHOICES = (
    ('1', '一年级'),
    ('2', '二年级'),
    ('3', '三年级'),
    ('4', '四年级'),
    ('5', '五年级'),
    ('6', '六年级'),
    ('7', '初一'),
    ('8', '初二'),
    ('9', '初三'),
    ('10', '高一'),
    ('11', '高二'),
    ('12', '高三'),
)

# 定义词性选择
PART_OF_SPEECH_CHOICES = (
    ('名词', '名词'),
    ('动词', '动词'),
    ('形容词', '形容词'),
    ('副词', '副词'),
    ('代词', '代词'),
    ('数词', '数词'),
    ('冠词', '冠词'),
    ('介词', '介词'),
    ('连词', '连词'),
    ('感叹词', '感叹词'),
    ('缩写词', '缩写词'),
    ('短语', '短语'),
    ('句子', '句子'),
    ('其他', '其他'),
)

# 资源类型选择
RESOURCE_TYPE_CHOICES = (
    ('audio', '音频'),
    ('video', '视频'),
    ('image', '图片'),
    ('pdf', 'PDF文档'),
    ('markdown', 'Markdown文档'),
    ('text', '文本文档'),
    ('url', '网络链接'),
)


class WordResource(models.Model):
    """单词资源模型"""
    name = models.CharField(_('资源名称'), max_length=200)
    resource_type = models.CharField(_('资源类型'), max_length=20, choices=RESOURCE_TYPE_CHOICES)
    file = models.FileField(
        _('文件'), 
        upload_to='word_resources/%Y/%m/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['mp3', 'wav', 'mp4', 'avi', 'jpg', 'jpeg', 'png', 'gif', 'pdf', 'md', 'txt']
            )
        ]
    )
    url = models.URLField(_('网络链接'), blank=True, null=True)
    description = models.TextField(_('资源描述'), blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('单词配套资源')
        verbose_name_plural = _('单词配套资源')
        ordering = ['-created_at']
    
    def __str__(self):
        return str(self.name)
    
    def clean(self):
        """验证资源数据"""
        from django.core.exceptions import ValidationError
        
        if self.resource_type == 'url':
            if not self.url:
                raise ValidationError({'url': '网络链接类型必须提供URL'})
        else:
            if not self.file:
                raise ValidationError({'file': '非网络链接类型必须上传文件'})
    
    @property
    def file_size(self):
        """获取文件大小"""
        if self.file and self.file.name:
            return self.file.size
        return 0
    
    @property
    def file_extension(self):
        """获取文件扩展名"""
        if self.file and self.file.name:
            return os.path.splitext(str(self.file.name))[1].lower()
        return ''


class Word(models.Model):
    """单词模型 - 临时保留旧字段以便安全迁移"""
    # 基本信息
    word = models.CharField(_('单词'), max_length=100)
    
    # 学习状态相关字段
    learned_at = models.DateTimeField(_('学习时间'), null=True, blank=True)
    
    # 资源绑定
    resources = models.ManyToManyField(
        WordResource, 
        blank=True, 
        related_name='words',
        verbose_name=_('绑定资源')
    )
    
    # 分类和标签
    tags = models.CharField(_('标签'), max_length=200, blank=True, help_text='用逗号分隔多个标签')
    
    # 时间戳
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('单词')
        verbose_name_plural = _('单词')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['word']),
        ]
    
    def __str__(self):
        return str(self.word)
    
    @property
    def tag_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in str(self.tags).split(',') if tag.strip()]
        return []
    
    def add_tag(self, tag):
        """添加标签"""
        tags = self.tag_list
        if tag not in tags:
            tags.append(tag)
            self.tags = ', '.join(tags)
            self.save()
    
    def remove_tag(self, tag):
        """移除标签"""
        tags = self.tag_list
        if tag in tags:
            tags.remove(tag)
            self.tags = ', '.join(tags)
            self.save()
    



class WordEntry(models.Model):
    """词条模型 - 存储单词的具体信息和上下文"""
    # 关联单词
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name='entries',
        verbose_name='单词'
    )
    
    # 词条信息
    phonetic = models.CharField(_('音标'), max_length=100, blank=True)
    definition = models.TextField(_('释义'), blank=True)
    part_of_speech = models.CharField(_('词性'), max_length=50, choices=PART_OF_SPEECH_CHOICES, blank=True)
    example = models.TextField(_('例句'), blank=True)
    note = models.TextField(_('笔记'), blank=True)
    
    # 教材信息
    textbook_version = models.CharField('教材版本', max_length=50, blank=True)
    grade = models.CharField('年级', max_length=20, choices=GRADE_CHOICES, blank=True)
    book_volume = models.CharField('册别', max_length=20, blank=True, help_text='如：三上、三下、四上等')
    unit = models.CharField('单元', max_length=20, blank=True, help_text='如：Unit 1、Unit 2等')
    
    # 关联信息
    vocabulary_list = models.ForeignKey(
        'VocabularyList', 
        on_delete=models.CASCADE, 
        related_name='word_entries', 
        verbose_name='词库列表',
        null=True,
        blank=True
    )
    
    # 时间戳
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('词条')
        verbose_name_plural = _('词条')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['word']),
            models.Index(fields=['vocabulary_list']),
            models.Index(fields=['textbook_version', 'grade', 'book_volume', 'unit']),
        ]
        # 唯一约束：同一个单词在同一教材版本、年级、册别、单元下的相同音标、释义、词性、备注组合不能重复
        unique_together = [
            ['word', 'textbook_version', 'grade', 'book_volume', 'unit', 'phonetic', 'definition', 'part_of_speech', 'note']
        ]
    
    def __str__(self):
        return f"{str(self.word.word)} - {self.textbook_version} {self.grade} {self.book_volume} {self.unit}"
    
    def is_identical_to(self, other):
        """检查是否与另一个词条完全相同（重复数据）"""
        if not isinstance(other, WordEntry):
            return False
        
        return (
            self.word_id == other.word_id and
            self.textbook_version == other.textbook_version and
            self.grade == other.grade and
            self.book_volume == other.book_volume and
            self.unit == other.unit and
            self.phonetic == other.phonetic and
            self.definition == other.definition and
            self.part_of_speech == other.part_of_speech and
            self.note == other.note
        )
    
    def is_same_word_different_version(self, other):
        """检查是否为同一单词的不同版本（仅单词相同，其他信息不同）"""
        if not isinstance(other, WordEntry):
            return False
        
        return (
            self.word_id == other.word_id and
            not self.is_identical_to(other)
        )


class ImportRecord(models.Model):
    """导入记录模型 - 记录词条的导入来源信息"""
    # 关联词条
    word_entry = models.ForeignKey(
        WordEntry,
        on_delete=models.CASCADE,
        related_name='import_records',
        verbose_name='词条'
    )
    
    # 导入来源信息
    import_source = models.ForeignKey(
        'VocabularySource',
        on_delete=models.SET_NULL,
        related_name='import_records',
        verbose_name='导入来源',
        null=True,
        blank=True
    )
    import_batch_id = models.CharField('导入批次ID', max_length=100, blank=True)
    import_metadata = models.JSONField('导入元数据', default=dict, blank=True)
    
    # 导入类型
    IMPORT_TYPE_CHOICES = (
        ('new', '新增'),
        ('duplicate', '重复'),
        ('version', '新版本'),
    )
    import_type = models.CharField('导入类型', max_length=20, choices=IMPORT_TYPE_CHOICES, default='new')
    
    # 时间戳
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('导入记录')
        verbose_name_plural = _('导入记录')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['word_entry']),
            models.Index(fields=['import_source']),
            models.Index(fields=['import_batch_id']),
            models.Index(fields=['import_type']),
        ]
    
    def __str__(self):
        return f"{self.word_entry} - {self.import_type} - {self.created_at}"


class VocabularySource(models.Model):
    """词库导入来源"""
    name = models.CharField('来源名称', max_length=100)
    description = models.TextField('来源描述', blank=True)
    
    # 导入统计信息
    total_imports = models.IntegerField('总导入次数', default=0, help_text='该来源的总导入次数')
    total_words_imported = models.IntegerField('总导入单词数', default=0, help_text='该来源导入的总单词数')
    total_new_words = models.IntegerField('新增单词数', default=0, help_text='该来源新增的单词数')
    total_duplicate_words = models.IntegerField('重复单词数', default=0, help_text='该来源重复的单词数')
    total_version_words = models.IntegerField('版本单词数', default=0, help_text='该来源创建的版本单词数')
    
    # 最后导入信息
    last_import_at = models.DateTimeField('最后导入时间', null=True, blank=True)
    last_import_batch_id = models.CharField('最后导入批次ID', max_length=100, blank=True)
    last_import_file_name = models.CharField('最后导入文件名', max_length=200, blank=True)
    last_import_word_count = models.IntegerField('最后导入单词数', default=0)
    
    # 来源配置
    is_active = models.BooleanField('是否启用', default=True, help_text='是否允许从该来源导入')
    auto_create_lists = models.BooleanField('自动创建词库列表', default=True, help_text='是否自动创建词库列表')
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '词库导入来源设置'
        verbose_name_plural = '词库导入来源设置'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['last_import_at']),
        ]
    
    def __str__(self):
        return f"{self.name} (导入{self.total_imports}次)"
    
    def update_import_stats(self, batch_id, file_name, new_words=0, duplicate_words=0, version_words=0):
        """更新导入统计信息"""
        # 使用F表达式进行原子更新
        from django.db.models import F
        VocabularySource.objects.filter(id=self.id).update(
            total_imports=F('total_imports') + 1,
            total_words_imported=F('total_words_imported') + (new_words + duplicate_words + version_words),
            total_new_words=F('total_new_words') + new_words,
            total_duplicate_words=F('total_duplicate_words') + duplicate_words,
            total_version_words=F('total_version_words') + version_words,
            last_import_at=timezone.now(),
            last_import_batch_id=batch_id,
            last_import_file_name=file_name,
            last_import_word_count=new_words + duplicate_words + version_words
        )
        # 刷新实例
        self.refresh_from_db()
    
    def get_import_history(self):
        """获取导入历史记录"""
        # 通过导入记录获取所有批次信息
        batches = self.import_records.values('import_batch_id', 'import_metadata').distinct()
        history = []
        for batch in batches:
            batch_id = batch['import_batch_id']
            if batch_id:
                batch_records = self.import_records.filter(import_batch_id=batch_id)
                history.append({
                    'batch_id': batch_id,
                    'word_count': batch_records.count(),
                    'import_time': batch_records.first().created_at if batch_records.exists() else None,
                    'metadata': batch['import_metadata']
                })
        return sorted(history, key=lambda x: x['import_time'] or timezone.now(), reverse=True)
    
    def get_records_by_batch(self, batch_id):
        """根据批次ID获取导入记录"""
        return self.import_records.filter(import_batch_id=batch_id)
    
    def get_recent_imports(self, days=30):
        """获取最近导入记录"""
        since_date = timezone.now() - timedelta(days=days)
        return self.import_records.filter(created_at__gte=since_date)


class VocabularyList(models.Model):
    """词库列表"""
    source = models.ForeignKey(
        VocabularySource, 
        on_delete=models.CASCADE, 
        related_name='vocabulary_lists', 
        verbose_name='词库来源',
        null=True,
        blank=True
    )
    name = models.CharField('列表名称', max_length=100)
    description = models.TextField('描述', blank=True)
    is_active = models.BooleanField('是否活跃', default=True)
    word_count = models.IntegerField('单词数量', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '词库列表'
        verbose_name_plural = '词库列表'
        ordering = ['-created_at']
    
    def __str__(self):
        return str(self.name)
    
    def update_word_count(self):
        """更新单词数量"""
        new_count = self.word_entries.count()
        if self.word_count != new_count:
            self.word_count = new_count
            self.save(update_fields=['word_count'])
        return self.word_count
    
    def get_word_count(self):
        """获取词库中的单词数量"""
        return self.word_entries.count()


# ImportedVocabulary模型已合并到Word模型中


# UserStreak 模型已移动到 vocabulary_manager 应用





class WordSet(models.Model):
    """单词集模型"""
    name = models.CharField(_('单词集名称'), max_length=100, help_text='单词集的名称，必填且不能重复')
    description = models.TextField(_('描述'), blank=True)
    words = models.ManyToManyField(
        Word,
        related_name='word_sets',
        verbose_name=_('单词'),
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_word_sets',
        verbose_name=_('创建者'),
        null=True,
        blank=True
    )
    is_public = models.BooleanField(_('是否公开'), default=False)
    word_count = models.IntegerField(_('单词数量'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('单词集')
        verbose_name_plural = _('单词集')
        ordering = ['-created_at']
        unique_together = [['name', 'created_by']]  # 同一用户的单词集名称不能重复
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created_by']),
            models.Index(fields=['is_public']),
            models.Index(fields=['name', 'created_by']),  # 复合索引优化查询
        ]
    
    def __str__(self):
        return str(self.name)
    
    def clean(self):
        """模型验证"""
        super().clean()
        
        # 验证名称不能为空
        if not self.name or not self.name.strip():
            raise ValidationError({'name': _('单词集名称不能为空')})
        
        # 验证名称长度
        if len(self.name) > 100:
            raise ValidationError({'name': _('单词集名称不能超过100个字符')})
        
        # 验证名称唯一性（同一用户）
        if self.created_by:
            existing = WordSet.objects.filter(
                name=self.name,
                created_by=self.created_by
            )
            if self.pk:  # 如果是更新操作，排除自己
                existing = existing.exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError({'name': _('您已创建过同名的单词集')})
    
    def save(self, *args, **kwargs):
        """保存前进行验证"""
        self.full_clean()  # 触发clean方法
        super().save(*args, **kwargs)
    
    def update_word_count(self):
        """更新单词数量"""
        new_count = self.words.count()
        if self.word_count != new_count:
            self.word_count = new_count
            self.save(update_fields=['word_count'])
        return self.word_count
    
    def add_words(self, word_ids):
        """批量添加单词"""
        self.words.add(*word_ids)
        self.update_word_count()
    
    def remove_words(self, word_ids):
        """批量移除单词"""
        self.words.remove(*word_ids)
        self.update_word_count()


class WordGrader(models.Model):
    """单词分级器模型"""
    name = models.CharField(_('分级方案名称'), max_length=100)
    description = models.TextField(_('分级方案描述'), blank=True)
    grade_count = models.IntegerField(_('分级数量'), default=5, help_text='设置分级的数量')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_graders',
        verbose_name=_('创建者'),
        null=True,
        blank=True
    )
    is_active = models.BooleanField(_('是否启用'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('单词分级器')
        verbose_name_plural = _('单词分级器')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return str(self.name)
    
    def get_all_levels(self):
        """获取所有分级等级"""
        return self.grade_levels.all().order_by('level')
    
    def get_total_levels(self):
        """获取总分级数量"""
        return self.grade_levels.count()


class WordGradeLevel(models.Model):
    """单词分级等级模型"""
    grader = models.ForeignKey(
        WordGrader,
        on_delete=models.CASCADE,
        related_name='grade_levels',
        verbose_name=_('分级器')
    )
    level = models.IntegerField(_('等级'), help_text='分级等级，从1开始')
    name = models.CharField(_('等级名称'), max_length=50)
    description = models.TextField(_('等级描述'), blank=True)
    word_set = models.ForeignKey(
        WordSet,
        on_delete=models.SET_NULL,
        related_name='grade_levels',
        verbose_name=_('绑定单词集'),
        null=True,
        blank=True
    )
    min_difficulty = models.IntegerField(_('最低难度'), default=1)
    max_difficulty = models.IntegerField(_('最高难度'), default=5)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('单词分级等级设置')
        verbose_name_plural = _('单词分级等级设置')
        ordering = ['grader', 'level']
        unique_together = [['grader', 'level']]
        indexes = [
            models.Index(fields=['grader', 'level']),
            models.Index(fields=['word_set']),
        ]
    
    def __str__(self):
        return f"{str(self.grader.name)} - 等级{self.level}: {str(self.name)}"
    
    def get_words(self):
        """获取该等级的所有单词"""
        if self.word_set:
            return self.word_set.words.all()
        return Word.objects.none()


# StudySession 模型已移动到 vocabulary_manager 应用