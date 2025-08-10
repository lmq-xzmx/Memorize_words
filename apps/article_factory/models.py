from django.db import models
from django.conf import settings
from django.utils import timezone


class Article(models.Model):
    """文章模型"""
    EDIT_MODE_CHOICES = [
        ('source', '源文本编辑'),
        ('visual', '可视化编辑'),
    ]
    
    PARAGRAPH_TYPE_CHOICES = [
        ('title', '标题'),
        ('list_item', '列表项'),
        ('indented', '缩进文本'),
        ('normal', '普通段落'),
        ('quote', '引用'),
        ('code', '代码块'),
    ]
    
    title = models.CharField('标题', max_length=200)
    content = models.TextField('原始内容')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    image = models.ImageField('配图', upload_to='articles/', blank=True, null=True)
    
    # 解析相关字段
    is_parsed = models.BooleanField('已解析', default=False)
    parsed_content = models.JSONField('解析内容', blank=True, null=True)
    edited_content = models.TextField('编辑内容', blank=True)
    edit_mode = models.CharField('编辑模式', max_length=10, choices=EDIT_MODE_CHOICES, default='source')
    html_content = models.TextField('HTML内容', blank=True)
    
    # 增强字段
    paragraph_analysis = models.JSONField('段落分析结果', blank=True, null=True)
    vocabulary_source = models.CharField('词库来源', max_length=50, default='default')
    variant_preference = models.CharField('变体偏好', max_length=20, default='us')
    system_vocabulary_id = models.CharField('系统词库ID', max_length=50, blank=True, null=True)
    
    # 元数据
    extra_data = models.JSONField('额外数据', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_user_known_words(self):
        """获取用户熟词列表"""
        # 由于已移除用户关联字段，返回空集合
        # 可以根据需要实现其他逻辑来判断熟词
        return set()
    
    def get_vocabulary_words(self):
        """获取词库单词"""
        from apps.words.models import Word, VocabularyList
        from django.db.models import Q
        try:
            # 根据词库来源获取单词
            if self.system_vocabulary_id:
                # 从指定的系统词库获取
                try:
                    vocab_list = VocabularyList.objects.get(id=self.system_vocabulary_id)
                    vocab_words = Word.objects.filter(vocabulary_list=vocab_list)
                except VocabularyList.DoesNotExist:
                    print(f"系统词库不存在: {self.system_vocabulary_id}")
                    vocab_words = Word.objects.none()
            elif self.vocabulary_source and self.vocabulary_source != 'default':
                # 根据词库来源筛选
                vocab_words = Word.objects.filter(
                    # 可以根据需要添加更多的筛选条件
                    tags__icontains=self.vocabulary_source
                )
            else:
                # 默认获取所有词库单词
                vocab_words = Word.objects.all()
            
            result = {}
            for w in vocab_words:
                word_key = w.word.lower() if w.word else ''
                if word_key:
                    result[word_key] = {
                        'word': w.word,
                        'pos': w.part_of_speech or 'unknown',
                        'definition': w.definition or '',
                        'pronunciation': w.phonetic or ''
                    }
            return result
        except Exception as e:
            print(f"获取词库单词失败: {e}")
            return {}
    
    def get_user_new_words(self):
        """获取用户生词列表（词库中但未学习的单词）"""
        # 由于已移除用户关联字段，返回空集合
        # 可以根据需要实现其他逻辑来判断生词
        return set()


class ParsedParagraph(models.Model):
    """解析段落模型"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='paragraphs')
    order = models.PositiveIntegerField('顺序')
    paragraph_type = models.CharField('段落类型', max_length=20, choices=Article.PARAGRAPH_TYPE_CHOICES)
    original_text = models.TextField('原始文本')
    processed_text = models.TextField('处理后文本')
    word_data = models.JSONField('单词数据', blank=True, null=True)
    html_content = models.TextField('HTML内容', blank=True)
    
    class Meta:
        verbose_name = '解析段落'
        verbose_name_plural = '解析段落'
        ordering = ['article', 'order']
    
    def __str__(self):
        return f'{self.article.title} - 段落{self.order}'