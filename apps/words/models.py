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
        return self.name
    
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
        if self.file and hasattr(self.file, 'size'):
            return self.file.size
        return 0
    
    @property
    def file_extension(self):
        """获取文件扩展名"""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ''


class Word(models.Model):
    """统一单词模型 - 支持版本管理"""
    # 基本信息
    word = models.CharField(_('单词'), max_length=100)
    phonetic = models.CharField(_('音标'), max_length=100, blank=True)
    definition = models.TextField(_('释义'), blank=True)
    part_of_speech = models.CharField(_('词性'), max_length=50, choices=PART_OF_SPEECH_CHOICES, blank=True)
    example = models.TextField(_('例句'), blank=True)
    note = models.TextField(_('笔记'), blank=True)
    
    # 来源信息
    vocabulary_list = models.ForeignKey(
        'VocabularyList', 
        on_delete=models.CASCADE, 
        related_name='words', 
        verbose_name='词库列表',
        null=True,
        blank=True
    )
    textbook_version = models.CharField('教材版本', max_length=50, blank=True)
    grade = models.CharField('年级', max_length=20, choices=GRADE_CHOICES, blank=True)
    book_volume = models.CharField('册别', max_length=20, blank=True, help_text='如：三上、三下、四上等')
    unit = models.CharField('单元', max_length=20, blank=True, help_text='如：Unit 1、Unit 2等')
    
    # 学习状态相关字段
    learned_at = models.DateTimeField(_('学习时间'), null=True, blank=True)
    mastery_level = models.IntegerField(_('掌握程度'), default=0, help_text='0-100的掌握程度评分')
    
    # 资源绑定
    resources = models.ManyToManyField(
        WordResource, 
        blank=True, 
        related_name='words',
        verbose_name=_('绑定资源')
    )
    
    # 分类和标签
    tags = models.CharField(_('标签'), max_length=200, blank=True, help_text='用逗号分隔多个标签')
    difficulty_level = models.IntegerField(_('难度等级'), default=1, choices=[(i, f'等级{i}') for i in range(1, 6)])
    
    # 版本管理 - 替换原有的冲突管理
    version_number = models.IntegerField('版本号', default=1, help_text='单词的版本号，从1开始')
    has_multiple_versions = models.BooleanField('是否含有多版本', default=False, help_text='该单词是否有多个版本')
    parent_word = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name='主单词',
        null=True,
        blank=True,
        help_text='指向主单词，如果为空则表示这是主单词'
    )
    version_data = models.JSONField('版本数据', default=dict, blank=True, help_text='存储版本相关的元数据')
    
    # 时间戳
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('单词')
        verbose_name_plural = _('单词')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['word']),
            models.Index(fields=['vocabulary_list', 'word']),
            models.Index(fields=['has_multiple_versions']),
            models.Index(fields=['version_number']),
            models.Index(fields=['parent_word']),
            models.Index(fields=['difficulty_level']),
        ]
    
    def __str__(self):
        if self.parent_word:
            return f"{self.word} (版本{self.version_number})"
        elif self.vocabulary_list:
            return f"{self.word} ({self.vocabulary_list.name})"
        return self.word
    
    def save(self, *args, **kwargs):
        """保存时自动处理版本管理"""
        
        # 处理单词版本管理
        if not self.pk:  # 新创建的记录
            try:
                self.handle_word_versioning()
            except Exception as e:
                # 如果处理失败，记录错误但不阻止保存
                print(f"单词版本管理处理失败: {e}")
        
        super().save(*args, **kwargs)
    
    def handle_word_versioning(self):
        """处理单词版本管理"""
        try:
            # 查找已存在的同名单词
            existing_words = Word.objects.filter(word=self.word).order_by('created_at')
            
            if existing_words.exists():
                # 获取最早创建的单词作为主单词
                parent_word = existing_words.first()
                
                # 检查是否完全相同
                if self.is_identical_to(parent_word):
                    # 完全相同，删除当前记录
                    raise ValidationError("单词完全相同，无需重复导入")
                
                # 检查是否有差异，视为不同版本
                if self.has_differences_from(parent_word):
                    # 有差异，设置为新版本
                    self.parent_word = parent_word
                    if parent_word:
                        self.version_number = parent_word.get_next_version_number()
                        self.has_multiple_versions = False  # 版本本身不标记为多版本
                        
                        # 更新主单词的多版本标记
                        parent_word.has_multiple_versions = True
                        parent_word.save(update_fields=['has_multiple_versions'])
                        
                        # 记录版本信息
                        self.version_data = {
                            'parent_word_id': parent_word.pk,
                            'differences': self.get_differences_from(parent_word),
                            'created_as_version': True,
                            'import_timestamp': timezone.now().isoformat()
                        }
                else:
                    # 无显著差异，但仍保存为版本
                    self.parent_word = parent_word
                    if parent_word:
                        self.version_number = parent_word.get_next_version_number()
                        self.has_multiple_versions = False
                        
                        # 更新主单词的多版本标记
                        parent_word.has_multiple_versions = True
                        parent_word.save(update_fields=['has_multiple_versions'])
                        
                        self.version_data = {
                            'parent_word_id': parent_word.pk,
                            'duplicate_import': True,
                            'import_timestamp': timezone.now().isoformat()
                        }
            else:
                # 第一个单词，设置为主单词
                self.parent_word = None
                self.version_number = 1
                self.has_multiple_versions = False
                
        except Exception as e:
            # 如果处理失败，记录错误但不阻止保存
            print(f"单词版本管理处理失败: {e}")
    
    def is_identical_to(self, other):
        """检查是否与另一个单词完全相同"""
        try:
            fields_to_compare = ['phonetic', 'definition', 'part_of_speech', 'example', 'note', 'textbook_version', 'grade']
            for field in fields_to_compare:
                if getattr(self, field) != getattr(other, field):
                    return False
            return True
        except Exception as e:
            print(f"相同性检测失败: {e}")
            return False
    
    def has_differences_from(self, other):
        """检查是否有差异"""
        try:
            fields_to_compare = ['phonetic', 'definition', 'part_of_speech', 'example', 'note']
            for field in fields_to_compare:
                if getattr(self, field) and getattr(other, field):
                    if getattr(self, field) != getattr(other, field):
                        return True
            return False
        except Exception as e:
            print(f"差异检测失败: {e}")
            return False
    
    def get_differences_from(self, other):
        """获取与另一个单词的差异详情"""
        try:
            differences = {}
            fields_to_compare = ['phonetic', 'definition', 'part_of_speech', 'example', 'note']
            for field in fields_to_compare:
                self_value = getattr(self, field)
                other_value = getattr(other, field)
                if self_value != other_value:
                    differences[field] = {
                        'current': self_value,
                        'existing': other_value
                    }
            return differences
        except Exception as e:
            print(f"差异详情获取失败: {e}")
            return {}
    
    def get_next_version_number(self):
        """获取下一个版本号"""
        if self.parent_word:
            # 如果是版本，返回主单词的下一个版本号
            return self.parent_word.get_next_version_number()
        else:
            # 如果是主单词，返回当前最大版本号+1
            max_version = Word.objects.filter(
                models.Q(pk=self.pk) | models.Q(parent_word=self)
            ).aggregate(models.Max('version_number'))['version_number__max']
            return (max_version or 0) + 1
    
    def get_all_versions(self):
        """获取所有版本（包括主单词）"""
        if self.parent_word:
            # 如果是版本，返回主单词的所有版本
            return self.parent_word.get_all_versions()
        else:
            # 如果是主单词，返回自己和所有版本
            return Word.objects.filter(
                models.Q(pk=self.pk) | models.Q(parent_word=self)
            ).order_by('version_number')
    
    def get_version_count(self):
        """获取版本数量"""
        return self.get_all_versions().count()
    
    def is_main_word(self):
        """判断是否为主单词"""
        return self.parent_word is None
    
    def is_version(self):
        """判断是否为版本"""
        return self.parent_word is not None
    
    @property
    def tag_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
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
    
    def create_version(self, **version_data):
        """创建新版本"""
        version_data.update({
            'word': self.word,
            'parent_word': self,
            'version_number': self.get_next_version_number(),
            'has_multiple_versions': False
        })
        new_version = Word.objects.create(**version_data)
        
        # 更新主单词的多版本标记
        self.has_multiple_versions = True
        self.save(update_fields=['has_multiple_versions'])
        
        return new_version
    
    def delete_version(self, version_number):
        """删除指定版本"""
        if self.is_version():
            raise ValidationError("只有主单词可以删除版本")
        
        version_to_delete = Word.objects.filter(
            parent_word=self,
            version_number=version_number
        ).first()
        
        if version_to_delete:
            version_to_delete.delete()
            
            # 重新编号版本
            self.renumber_versions()
            
            # 检查是否还有多版本
            if self.get_version_count() == 1:
                self.has_multiple_versions = False
                self.save(update_fields=['has_multiple_versions'])
            
            return True
        return False
    
    def renumber_versions(self):
        """重新编号版本"""
        if self.is_version():
            return
        
        versions = Word.objects.filter(parent_word=self).order_by('created_at')
        for index, version in enumerate(versions, start=2):
            if version.version_number != index:
                version.version_number = index
                version.save(update_fields=['version_number'])


class VocabularySource(models.Model):
    """词库导入来源"""
    name = models.CharField('来源名称', max_length=100)
    description = models.TextField('来源描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '词库导入来源设置'
        verbose_name_plural = '词库导入来源设置'
        ordering = ['name']
    
    def __str__(self):
        return self.name


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
        return self.name
    
    def update_word_count(self):
        """更新单词数量"""
        self.word_count = getattr(self, 'words', self.__class__.objects.none()).count()
        self.save(update_fields=['word_count'])
        return self.word_count
    
    def get_word_count(self):
        """获取词库中的单词数量"""
        return getattr(self, 'words', self.__class__.objects.none()).count()


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
        return self.name
    
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
        self.word_count = self.words.count()
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
        return self.name
    
    def get_all_levels(self):
        """获取所有分级等级"""
        return getattr(self, 'grade_levels', self.__class__.objects.none()).all().order_by('level')
    
    def get_total_levels(self):
        """获取总分级数量"""
        return getattr(self, 'grade_levels', self.__class__.objects.none()).count()


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
        return f"{self.grader.name} - 等级{self.level}: {self.name}"
    
    def get_words(self):
        """获取该等级的所有单词"""
        if self.word_set:
            return self.word_set.words.all()
        return Word.objects.none()


# StudySession 模型已移动到 vocabulary_manager 应用