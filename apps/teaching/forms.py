from django import forms
from django.core.exceptions import ValidationError
from .models import LearningPlan, LearningGoal, DailyStudyRecord


class LearningPlanAdminForm(forms.ModelForm):
    """学习计划管理表单 - 替代learning_plan_admin.js的动态字段显示功能"""
    
    # 定义不同计划类型需要的字段配置
    PLAN_TYPE_FIELDS = {
        'mechanical': {
            'required': ['words_per_day', 'review_interval'],
            'optional': ['total_words'],
            'hidden': ['start_date', 'end_date', 'daily_target'],
            'description': '机械模式：固定每日单词数量，按设定间隔复习'
        },
        'daily_progress': {
            'required': ['daily_target', 'start_date', 'end_date'],
            'optional': ['review_interval'],
            'hidden': ['words_per_day'],
            'description': '日进模式：设定每日目标，在指定时间内完成'
        },
        'weekday': {
            'required': ['words_per_day', 'start_date', 'end_date'],
            'optional': ['daily_target', 'review_interval'],
            'hidden': [],
            'description': '工作日模式：仅在工作日学习，周末休息'
        },
        'weekend': {
            'required': ['words_per_day', 'start_date', 'end_date'],
            'optional': ['daily_target', 'review_interval'],
            'hidden': [],
            'description': '周末模式：仅在周末学习，工作日休息'
        },
        'daily': {
            'required': ['words_per_day', 'start_date'],
            'optional': ['end_date', 'daily_target', 'review_interval'],
            'hidden': [],
            'description': '每日计划：每天固定学习量'
        },
        'weekly': {
            'required': ['total_words', 'start_date', 'end_date'],
            'optional': ['words_per_day', 'daily_target'],
            'hidden': ['review_interval'],
            'description': '每周计划：按周安排学习进度'
        },
        'custom': {
            'required': ['start_date'],
            'optional': ['end_date', 'words_per_day', 'daily_target', 'total_words', 'review_interval'],
            'hidden': [],
            'description': '自定义计划：灵活设置各项参数'
        }
    }
    
    class Meta:
        model = LearningPlan
        fields = [
            'name', 'plan_type', 'start_date', 'end_date',
            'total_words', 'daily_target', 'words_per_day', 'review_interval',
            'status', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_plan_type'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'total_words': forms.NumberInput(attrs={'class': 'form-control'}),
            'daily_target': forms.NumberInput(attrs={'class': 'form-control'}),
            'words_per_day': forms.NumberInput(attrs={'class': 'form-control'}),
            'review_interval': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 为字段添加帮助文本
        self.fields['plan_type'].help_text = '选择计划类型将自动调整可用字段'
        self.fields['words_per_day'].help_text = '每日学习的单词数量'
        self.fields['daily_target'].help_text = '每日目标单词数'
        self.fields['review_interval'].help_text = '复习间隔天数'
        
        # 添加CSS类用于JavaScript控制
        for field_name, field in self.fields.items():
            if field_name != 'plan_type':
                field.widget.attrs['data-field'] = field_name
    
    def clean(self):
        cleaned_data = super().clean()
        plan_type = cleaned_data.get('plan_type')
        
        if plan_type and plan_type in self.PLAN_TYPE_FIELDS:
            config = self.PLAN_TYPE_FIELDS[plan_type]
            
            # 验证必填字段
            for field_name in config['required']:
                if field_name in self.fields and not cleaned_data.get(field_name):
                    self.add_error(field_name, f'此字段在{plan_type}模式下为必填项')
            
            # 特殊验证逻辑
            if plan_type in ['daily_progress', 'weekday', 'weekend', 'weekly']:
                start_date = cleaned_data.get('start_date')
                end_date = cleaned_data.get('end_date')
                if start_date and end_date and start_date >= end_date:
                    self.add_error('end_date', '结束日期必须晚于开始日期')
        
        return cleaned_data
    
    def get_plan_type_config(self):
        """获取计划类型配置，用于前端JavaScript"""
        return self.PLAN_TYPE_FIELDS
    
    def get_plan_type_description(self):
        """获取当前计划类型的描述"""
        plan_type = self.data.get('plan_type') or (self.instance.plan_type if self.instance else None)
        if plan_type and plan_type in self.PLAN_TYPE_FIELDS:
            return self.PLAN_TYPE_FIELDS[plan_type]['description']
        return ''


class LearningGoalForm(forms.ModelForm):
    """学习目标表单"""
    
    class Meta:
        model = LearningGoal
        fields = [
            'name', 'description', 'goal_type', 'target_words_count',
            'start_date', 'end_date', 'is_active', 'vocabulary_list',
            'word_set', 'grade_level'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'goal_type': forms.Select(attrs={'class': 'form-control'}),
            'target_words_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'vocabulary_list': forms.Select(attrs={'class': 'form-control'}),
            'word_set': forms.Select(attrs={'class': 'form-control'}),
            'grade_level': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            self.add_error('end_date', '结束日期必须晚于开始日期')
        
        return cleaned_data


class DailyStudyRecordForm(forms.ModelForm):
    """每日学习记录表单"""
    
    class Meta:
        model = DailyStudyRecord
        fields = [
            'study_date', 'target_words', 'completed_words', 'study_duration'
        ]
        widgets = {
            'study_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'target_words': forms.NumberInput(attrs={'class': 'form-control'}),
            'completed_words': forms.NumberInput(attrs={'class': 'form-control'}),
            'study_duration': forms.TimeInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        target_words = cleaned_data.get('target_words', 0)
        completed_words = cleaned_data.get('completed_words', 0)
        
        if completed_words > target_words:
            self.add_error('completed_words', '完成单词数不能超过目标单词数')
        
        return cleaned_data