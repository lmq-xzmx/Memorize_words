from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    LearningGoal, GoalWord, LearningSession, WordLearningRecord,
    LearningPlan, GuidedPracticeSession, GuidedPracticeQuestion, GuidedPracticeAnswer
)
from apps.words.models import Word
from apps.words.serializers import WordListSerializer

User = get_user_model()


class LearningGoalSerializer(serializers.ModelSerializer):
    """学习目标序列化器"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    word_count = serializers.SerializerMethodField()
    progress_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningGoal
        fields = [
            'id', 'user', 'user_username', 'name', 'description',
            'target_words_count', 'start_date', 'end_date', 'is_active',
            'word_count', 'progress_stats', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_word_count(self, obj):
        """获取目标单词数量"""
        return obj.goal_words.count()
    
    def get_progress_stats(self, obj):
        """获取进度统计"""
        return obj.get_progress_stats()


class GoalWordSerializer(serializers.ModelSerializer):
    """目标单词序列化器"""
    word_details = WordListSerializer(source='word', read_only=True)
    goal_name = serializers.CharField(source='goal.name', read_only=True)
    
    class Meta:
        model = GoalWord
        fields = [
            'id', 'goal', 'goal_name', 'word', 'word_details', 'added_at'
        ]
        read_only_fields = ['added_at']


class LearningSessionSerializer(serializers.ModelSerializer):
    """学习会话序列化器"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    goal_name = serializers.CharField(source='goal.name', read_only=True)
    accuracy_rate = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = LearningSession
        fields = [
            'id', 'user', 'user_username', 'goal', 'goal_name',
            'start_time', 'end_time', 'words_studied', 'correct_answers',
            'total_answers', 'accuracy_rate', 'duration'
        ]
        read_only_fields = ['user', 'start_time']


class WordLearningRecordSerializer(serializers.ModelSerializer):
    """单词学习记录序列化器"""
    word_details = WordListSerializer(source='word', read_only=True)
    session_id = serializers.IntegerField(source='session.id', read_only=True)
    goal_name = serializers.CharField(source='goal.name', read_only=True)
    
    class Meta:
        model = WordLearningRecord
        fields = [
            'id', 'session', 'session_id', 'goal', 'goal_name',
            'word', 'word_details', 'user_answer', 'is_correct',
            'response_time', 'created_at'
        ]
        read_only_fields = ['created_at']


class LearningPlanSerializer(serializers.ModelSerializer):
    """学习计划序列化器"""
    goal_name = serializers.CharField(source='goal.name', read_only=True)
    plan_type_display = serializers.CharField(source='get_plan_type_display', read_only=True)
    
    class Meta:
        model = LearningPlan
        fields = [
            'id', 'goal', 'goal_name', 'plan_type', 'plan_type_display',
            'words_per_day', 'review_interval', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']


# VocabularyListSerializer 和 VocabularyWordSerializer 已移除


class LearningSessionCreateSerializer(serializers.ModelSerializer):
    """学习会话创建序列化器"""
    
    class Meta:
        model = LearningSession
        fields = ['goal']
    
    def create(self, validated_data):
        """创建学习会话"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class WordLearningRecordCreateSerializer(serializers.ModelSerializer):
    """单词学习记录创建序列化器"""
    
    class Meta:
        model = WordLearningRecord
        fields = ['session', 'goal', 'word', 'user_answer', 'is_correct', 'response_time']
    
    def validate(self, attrs):
        """验证数据"""
        session = attrs.get('session')
        goal = attrs.get('goal')
        
        # 验证会话和目标是否匹配
        if session and goal and session.goal != goal:
            raise serializers.ValidationError('学习会话和学习目标不匹配')
        
        # 验证会话是否属于当前用户
        if session and session.user != self.context['request'].user:
            raise serializers.ValidationError('无权限访问该学习会话')
        
        return attrs


class LearningStatisticsSerializer(serializers.Serializer):
    """学习统计序列化器"""
    total_goals = serializers.IntegerField()
    active_goals = serializers.IntegerField()
    total_sessions = serializers.IntegerField()
    total_words_studied = serializers.IntegerField()
    average_accuracy = serializers.FloatField()
    total_study_time = serializers.FloatField()
    recent_activity = serializers.ListField()
    goal_progress = serializers.ListField()


class BulkGoalWordSerializer(serializers.Serializer):
    """批量添加目标单词序列化器"""
    goal_id = serializers.IntegerField()
    word_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text='单词ID列表'
    )
    
    def validate_goal_id(self, value):
        """验证学习目标"""
        try:
            goal = LearningGoal.objects.get(id=value, user=self.context['request'].user)
            return value
        except LearningGoal.DoesNotExist:
            raise serializers.ValidationError('学习目标不存在或无权限访问')


class UserSimpleSerializer(serializers.ModelSerializer):
    """用户简单序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class WordSimpleSerializer(serializers.ModelSerializer):
    """单词简单序列化器"""
    class Meta:
        model = Word
        fields = ['id', 'word', 'definition', 'pronunciation']


class LearningGoalSimpleSerializer(serializers.ModelSerializer):
    """学习目标简单序列化器"""
    class Meta:
        model = LearningGoal
        fields = ['id', 'name', 'description', 'target_words_count']


class GuidedPracticeSessionSerializer(serializers.ModelSerializer):
    """指导练习会话序列化器"""
    teacher = UserSimpleSerializer(read_only=True)
    students = UserSimpleSerializer(many=True, read_only=True)
    learning_goal = LearningGoalSimpleSerializer(read_only=True)
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    learning_goal_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = GuidedPracticeSession
        fields = [
            'id', 'session_name', 'practice_mode', 'status',
            'current_question_index', 'total_questions',
            'start_time', 'end_time', 'created_at', 'room_name',
            'teacher', 'students', 'learning_goal',
            'student_ids', 'learning_goal_id'
        ]
        read_only_fields = ['room_name', 'created_at']
    
    def create(self, validated_data):
        student_ids = validated_data.pop('student_ids', [])
        learning_goal_id = validated_data.pop('learning_goal_id')
        
        # 设置老师为当前用户
        validated_data['teacher'] = self.context['request'].user
        validated_data['learning_goal_id'] = learning_goal_id
        
        session = GuidedPracticeSession.objects.create(**validated_data)
        
        # 添加学生
        if student_ids:
            students = User.objects.filter(id__in=student_ids)
            session.students.set(students)
        
        return session


class GuidedPracticeQuestionSerializer(serializers.ModelSerializer):
    """指导练习题目序列化器"""
    word = WordSimpleSerializer(read_only=True)
    word_id = serializers.IntegerField(write_only=True)
    student_answers_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = GuidedPracticeQuestion
        fields = [
            'id', 'question_order', 'question_type', 'options',
            'correct_answer', 'time_limit', 'is_active',
            'started_at', 'ended_at', 'word', 'word_id',
            'student_answers_stats'
        ]
    
    def get_student_answers_stats(self, obj):
        """获取学生答案统计"""
        return obj.get_student_answers()


class GuidedPracticeAnswerSerializer(serializers.ModelSerializer):
    """指导练习答案序列化器"""
    student = UserSimpleSerializer(read_only=True)
    question = GuidedPracticeQuestionSerializer(read_only=True)
    
    class Meta:
        model = GuidedPracticeAnswer
        fields = [
            'id', 'selected_answer', 'is_correct', 'response_time',
            'answered_at', 'student', 'question'
        ]
        read_only_fields = ['answered_at']


class GuidedPracticeAnswerCreateSerializer(serializers.ModelSerializer):
    """创建指导练习答案序列化器"""
    class Meta:
        model = GuidedPracticeAnswer
        fields = ['question', 'selected_answer', 'response_time']
    
    def create(self, validated_data):
        # 设置学生为当前用户
        validated_data['student'] = self.context['request'].user
        
        # 检查答案是否正确
        question = validated_data['question']
        selected_answer = validated_data['selected_answer']
        validated_data['is_correct'] = (selected_answer == question.correct_answer)
        
        return GuidedPracticeAnswer.objects.create(**validated_data)


class GuidedPracticeSessionDetailSerializer(serializers.ModelSerializer):
    """指导练习会话详情序列化器"""
    teacher = UserSimpleSerializer(read_only=True)
    students = UserSimpleSerializer(many=True, read_only=True)
    learning_goal = LearningGoalSimpleSerializer(read_only=True)
    questions = GuidedPracticeQuestionSerializer(many=True, read_only=True)
    current_question = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = GuidedPracticeSession
        fields = [
            'id', 'session_name', 'practice_mode', 'status',
            'current_question_index', 'total_questions',
            'start_time', 'end_time', 'created_at', 'room_name',
            'teacher', 'students', 'learning_goal', 'questions',
            'current_question', 'progress_percentage'
        ]
    
    def get_current_question(self, obj):
        """获取当前题目"""
        current_question = obj.get_current_question()
        if current_question:
            return GuidedPracticeQuestionSerializer(current_question).data
        return None
    
    def get_progress_percentage(self, obj):
        """获取进度百分比"""
        return obj.get_progress_percentage()
    
    def validate_word_ids(self, value):
        """验证单词ID"""
        user = self.context['request'].user
        existing_words = Word.objects.filter(
            id__in=value,
            user=user
        ).values_list('id', flat=True)
        
        invalid_ids = set(value) - set(existing_words)
        if invalid_ids:
            raise serializers.ValidationError(f'以下单词ID无效或无权限访问: {list(invalid_ids)}')
        
        return value