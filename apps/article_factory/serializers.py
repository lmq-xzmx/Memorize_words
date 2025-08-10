from rest_framework import serializers
from .models import Article, ParsedParagraph
from apps.words.models import VocabularyList


class ArticleSerializer(serializers.ModelSerializer):
    """文章序列化器"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'user', 'image', 'is_parsed',
            'parsed_content', 'edited_content', 'edit_mode', 'html_content',
            'paragraph_analysis', 'vocabulary_source', 'variant_preference',
            'extra_data', 'created_at', 'updated_at', 'progress_percentage'
        ]
        read_only_fields = ['is_parsed', 'parsed_content', 'html_content', 'paragraph_analysis']
    
    def get_progress_percentage(self, obj):
        """计算解析进度百分比"""
        if not obj.parsed_content:
            return 0
        try:
            stats = obj.parsed_content.get('statistics', {})
            total_words = stats.get('total_words', 0)
            vocab_words = stats.get('vocab_words', 0)
            if total_words > 0:
                return round((vocab_words / total_words) * 100, 2)
        except:
            pass
        return 0


class ArticleParseSerializer(serializers.Serializer):
    """文章解析请求序列化器"""
    content = serializers.CharField(help_text='文章内容')
    title = serializers.CharField(max_length=200, required=False, help_text='文章标题')
    image = serializers.ImageField(required=False, help_text='文章配图')
    vocabulary_source = serializers.CharField(
        max_length=50, 
        default='default',
        help_text='词库来源选择'
    )
    variant_preference = serializers.ChoiceField(
        choices=[('us', '美式英语'), ('uk', '英式英语')],
        default='us',
        help_text='变体偏好'
    )
    enable_paragraph_analysis = serializers.BooleanField(
        help_text='启用段落类型分析'
    )
    enable_tooltip = serializers.BooleanField(
        help_text='启用工具提示'
    )


class ParsedParagraphSerializer(serializers.ModelSerializer):
    """解析段落序列化器"""
    
    class Meta:
        model = ParsedParagraph
        fields = [
            'id', 'order', 'paragraph_type', 'original_text',
            'processed_text', 'word_data', 'html_content'
        ]


class VocabularySourceSerializer(serializers.ModelSerializer):
    """词库来源序列化器"""
    
    class Meta:
        model = VocabularyList
        fields = ['id', 'name', 'description', 'word_count']
        read_only_fields = ['word_count']