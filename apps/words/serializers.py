from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Word, WordResource, VocabularySource, VocabularyList
)
from apps.teaching.models import LearningSession as StudySession

User = get_user_model()


class WordResourceSerializer(serializers.ModelSerializer):
    """单词资源序列化器"""
    file_size = serializers.ReadOnlyField()
    file_extension = serializers.ReadOnlyField()
    
    class Meta:
        model = WordResource
        fields = [
            'id', 'name', 'resource_type', 'file', 'url', 
            'description', 'file_size', 'file_extension',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, attrs):
        """验证资源数据"""
        resource_type = attrs.get('resource_type')
        file_data = attrs.get('file')
        url_data = attrs.get('url')
        
        if resource_type == 'url':
            if not url_data:
                raise serializers.ValidationError({
                    'url': '网络链接类型必须提供URL'
                })
        else:
            if not file_data:
                raise serializers.ValidationError({
                    'file': '非网络链接类型必须上传文件'
                })
        
        return attrs


class WordSerializer(serializers.ModelSerializer):
    """单词序列化器"""
    resources = WordResourceSerializer(many=True, read_only=True)
    resource_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text='资源ID列表'
    )
    tag_list = serializers.ReadOnlyField()
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Word
        fields = [
            'id', 'user', 'user_username', 'word', 'phonetic', 
            'definition', 'part_of_speech', 'example', 'note',
            'is_learned', 'learned_at', 'mastery_level',
            'resources', 'resource_ids', 'tags', 'tag_list',
            'difficulty_level', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'learned_at', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """创建单词"""
        resource_ids = validated_data.pop('resource_ids', [])
        word = super().create(validated_data)
        
        if resource_ids:
            resources = WordResource.objects.filter(id__in=resource_ids)
            word.resources.set(resources)
        
        return word
    
    def update(self, instance, validated_data):
        """更新单词"""
        resource_ids = validated_data.pop('resource_ids', None)
        word = super().update(instance, validated_data)
        
        if resource_ids is not None:
            resources = WordResource.objects.filter(id__in=resource_ids)
            word.resources.set(resources)
        
        return word


class WordListSerializer(serializers.ModelSerializer):
    """单词列表序列化器（简化版）"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    resource_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Word
        fields = [
            'id', 'user_username', 'word', 'phonetic', 
            'part_of_speech', 'is_learned', 'mastery_level',
            'difficulty_level', 'resource_count', 'created_at'
        ]
    
    def get_resource_count(self, obj):
        """获取资源数量"""
        return obj.resources.count()


class VocabularySourceSerializer(serializers.ModelSerializer):
    """词库来源序列化器"""
    list_count = serializers.SerializerMethodField()
    
    class Meta:
        model = VocabularySource
        fields = ['id', 'name', 'description', 'list_count', 'created_at']
        read_only_fields = ['created_at']
    
    def get_list_count(self, obj):
        """获取词库列表数量"""
        return obj.vocabulary_lists.count()


class VocabularyListSerializer(serializers.ModelSerializer):
    """词库列表序列化器"""
    source_name = serializers.CharField(source='source.name', read_only=True)
    imported_count = serializers.SerializerMethodField()
    conflict_count = serializers.SerializerMethodField()
    
    class Meta:
        model = VocabularyList
        fields = [
            'id', 'source', 'source_name', 'name', 'description',
            'is_active', 'word_count', 'imported_count', 'conflict_count',
            'created_at'
        ]
        read_only_fields = ['word_count', 'created_at']
    
    def get_imported_count(self, obj):
        """获取导入单词数量"""
        return obj.words.count()
    
    def get_conflict_count(self, obj):
        """获取冲突单词数量"""
        return obj.words.filter(has_conflict=True).count()


# ImportedVocabularySerializer已合并到WordSerializer中


# UserStreakSerializer已移除，因为UserStreak模型不存在


class StudySessionSerializer(serializers.ModelSerializer):
    """学习会话序列化器"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    words_studied_details = WordListSerializer(source='words_studied', many=True, read_only=True)
    word_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text='学习的单词ID列表'
    )
    session_duration_display = serializers.SerializerMethodField()
    accuracy_rate_display = serializers.SerializerMethodField()
    
    class Meta:
        model = StudySession
        fields = [
            'id', 'user', 'user_username', 'words_studied_details',
            'word_ids', 'session_duration', 'session_duration_display',
            'words_count', 'accuracy_rate', 'accuracy_rate_display',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['user', 'words_count', 'created_at']
    
    def get_session_duration_display(self, obj):
        """学习时长显示"""
        if obj.session_duration:
            total_seconds = int(obj.session_duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            if hours > 0:
                return f'{hours}小时{minutes}分钟{seconds}秒'
            elif minutes > 0:
                return f'{minutes}分钟{seconds}秒'
            else:
                return f'{seconds}秒'
        return None
    
    def get_accuracy_rate_display(self, obj):
        """正确率显示"""
        if obj.accuracy_rate is not None:
            return f'{obj.accuracy_rate * 100:.1f}%'
        return None
    
    def create(self, validated_data):
        """创建学习会话"""
        word_ids = validated_data.pop('word_ids', [])
        session = super().create(validated_data)
        
        if word_ids:
            words = Word.objects.filter(id__in=word_ids, user=session.user)
            session.words_studied.set(words)
        
        return session
    
    def update(self, instance, validated_data):
        """更新学习会话"""
        word_ids = validated_data.pop('word_ids', None)
        session = super().update(instance, validated_data)
        
        if word_ids is not None:
            words = Word.objects.filter(id__in=word_ids, user=session.user)
            session.words_studied.set(words)
        
        return session


class WordStatisticsSerializer(serializers.Serializer):
    """单词统计序列化器"""
    total_words = serializers.IntegerField()
    learned_words = serializers.IntegerField()
    unlearned_words = serializers.IntegerField()
    learning_rate = serializers.FloatField()
    average_mastery = serializers.FloatField()
    words_by_difficulty = serializers.DictField()
    words_by_part_of_speech = serializers.DictField()
    recent_activity = serializers.ListField()


class BulkWordOperationSerializer(serializers.Serializer):
    """批量单词操作序列化器"""
    word_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text='单词ID列表'
    )
    operation = serializers.ChoiceField(
        choices=[
            ('mark_learned', '标记为已学习'),
            ('mark_unlearned', '标记为未学习'),
            ('reset_mastery', '重置掌握程度'),
            ('delete', '删除单词'),
            ('add_tag', '添加标签'),
            ('remove_tag', '移除标签'),
        ],
        help_text='操作类型'
    )
    tag = serializers.CharField(
        required=False,
        help_text='标签名称（用于添加/移除标签操作）'
    )
    
    def validate(self, attrs):
        """验证批量操作数据"""
        operation = attrs.get('operation')
        tag = attrs.get('tag')
        
        if operation in ['add_tag', 'remove_tag'] and not tag:
            raise serializers.ValidationError({
                'tag': '添加或移除标签操作必须提供标签名称'
            })
        
        return attrs