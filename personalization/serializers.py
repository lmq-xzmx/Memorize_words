from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    UserPreference, LearningBehavior, RecommendationModel,
    PersonalizedRecommendation, LearningPath, LearningStep,
    AdaptiveDifficulty
)
from apps.words.models import Word

User = get_user_model()


class UserPreferenceSerializer(serializers.ModelSerializer):
    """用户偏好序列化器"""
    
    class Meta:
        model = UserPreference
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class LearningBehaviorSerializer(serializers.ModelSerializer):
    """学习行为序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    content_title = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningBehavior
        fields = '__all__'
        read_only_fields = ('user', 'timestamp')
    
    def get_content_title(self, obj):
        """获取内容标题"""
        if obj.content_type and obj.object_id:
            try:
                content_object = obj.content_type.get_object_for_this_type(pk=obj.object_id)
                if hasattr(content_object, 'title'):
                    return content_object.title
                elif hasattr(content_object, 'word'):
                    return content_object.word
                elif hasattr(content_object, 'name'):
                    return content_object.name
            except:
                pass
        return None


class RecommendationModelSerializer(serializers.ModelSerializer):
    """推荐模型序列化器"""
    
    class Meta:
        model = RecommendationModel
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class PersonalizedRecommendationSerializer(serializers.ModelSerializer):
    """个性化推荐序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True)
    content_title = serializers.SerializerMethodField()
    
    class Meta:
        model = PersonalizedRecommendation
        fields = '__all__'
        read_only_fields = ('user', 'created_at')
    
    def get_content_title(self, obj):
        """获取推荐内容标题"""
        if obj.content_type and obj.object_id:
            try:
                content_object = obj.content_type.get_object_for_this_type(pk=obj.object_id)
                if hasattr(content_object, 'title'):
                    return content_object.title
                elif hasattr(content_object, 'word'):
                    return content_object.word
                elif hasattr(content_object, 'name'):
                    return content_object.name
            except:
                pass
        return None


class LearningStepSerializer(serializers.ModelSerializer):
    """学习步骤序列化器"""
    content_title = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningStep
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_content_title(self, obj):
        """获取步骤内容标题"""
        if obj.content_type and obj.object_id:
            try:
                content_object = obj.content_type.get_object_for_this_type(pk=obj.object_id)
                if hasattr(content_object, 'title'):
                    return content_object.title
                elif hasattr(content_object, 'word'):
                    return content_object.word
                elif hasattr(content_object, 'name'):
                    return content_object.name
            except:
                pass
        return None


class LearningPathSerializer(serializers.ModelSerializer):
    """学习路径序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    steps = LearningStepSerializer(many=True, read_only=True)
    total_steps = serializers.SerializerMethodField()
    completed_steps = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPath
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
    
    def get_total_steps(self, obj):
        """获取总步骤数"""
        return obj.steps.count()
    
    def get_completed_steps(self, obj):
        """获取已完成步骤数"""
        return obj.steps.filter(is_completed=True).count()
    
    def get_progress_percentage(self, obj):
        """获取进度百分比"""
        total = self.get_total_steps(obj)
        completed = self.get_completed_steps(obj)
        if total > 0:
            return round((completed / total) * 100, 2)
        return 0


class AdaptiveDifficultySerializer(serializers.ModelSerializer):
    """自适应难度调整序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    content_title = serializers.SerializerMethodField()
    
    class Meta:
        model = AdaptiveDifficulty
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
    
    def get_content_title(self, obj):
        """获取内容标题"""
        if obj.content_type and obj.object_id:
            try:
                content_object = obj.content_type.get_object_for_this_type(pk=obj.object_id)
                if hasattr(content_object, 'title'):
                    return content_object.title
                elif hasattr(content_object, 'word'):
                    return content_object.word
                elif hasattr(content_object, 'name'):
                    return content_object.name
            except:
                pass
        return None


class PersonalizationStatsSerializer(serializers.Serializer):
    """个性化统计序列化器"""
    total_recommendations = serializers.IntegerField()
    accepted_recommendations = serializers.IntegerField()
    acceptance_rate = serializers.FloatField()
    learning_paths_count = serializers.IntegerField()
    active_learning_paths = serializers.IntegerField()
    avg_difficulty_level = serializers.FloatField()
    preferred_content_types = serializers.ListField()
    learning_time_distribution = serializers.DictField()
    recent_behaviors = LearningBehaviorSerializer(many=True)
    
    class Meta:
        fields = [
            'total_recommendations', 'accepted_recommendations', 'acceptance_rate',
            'learning_paths_count', 'active_learning_paths', 'avg_difficulty_level',
            'preferred_content_types', 'learning_time_distribution', 'recent_behaviors'
        ]