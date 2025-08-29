from django import forms
from django.core.exceptions import ValidationError
from .models import WordEntry, ImportRecord
from apps.teaching.models import LearningPlan


class LearningPlanForm(forms.ModelForm):
    """学习计划表单 - 替代learning_plan_admin.js的动态字段显示功能"""
    
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
            'total_words', 'daily_target', 'words_per_day', 'review_interval'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_plan_type',
                'onchange': 'updatePlanSettings(this.value)'
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
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 为字段添加帮助文本
        self.fields['plan_type'].help_text = '选择计划类型将自动调整可用字段'
        self.fields['words_per_day'].help_text = '每日学习的单词数量'
        self.fields['daily_target'].help_text = '每日目标单词数'
        self.fields['review_interval'].help_text = '复习间隔天数'
        
        # 如果有初始值，设置字段可见性
        if self.instance and self.instance.plan_type:
            self._update_field_visibility(self.instance.plan_type)
    
    def _update_field_visibility(self, plan_type):
        """根据计划类型更新字段可见性"""
        if plan_type not in self.PLAN_TYPE_FIELDS:
            return
        
        config = self.PLAN_TYPE_FIELDS[plan_type]
        
        # 设置必填字段
        for field_name in config['required']:
            if field_name in self.fields:
                self.fields[field_name].required = True
                self.fields[field_name].widget.attrs['class'] += ' required'
        
        # 设置隐藏字段
        for field_name in config['hidden']:
            if field_name in self.fields:
                self.fields[field_name].widget = forms.HiddenInput()
                self.fields[field_name].required = False
    
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
    
    def get_plan_type_description(self):
        """获取当前计划类型的描述"""
        plan_type = self.data.get('plan_type') or (self.instance.plan_type if self.instance else None)
        if plan_type and plan_type in self.PLAN_TYPE_FIELDS:
            return self.PLAN_TYPE_FIELDS[plan_type]['description']
        return ''


class WordEntryForm(forms.ModelForm):
    """单词条目表单"""
    
    class Meta:
        model = WordEntry
        fields = ['phonetic', 'definition', 'part_of_speech', 'example', 'note']
        widgets = {
            'phonetic': forms.TextInput(attrs={'class': 'form-control'}),
            'definition': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'part_of_speech': forms.Select(attrs={'class': 'form-control'}),
            'example': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ImportRecordForm(forms.ModelForm):
    """导入记录表单"""
    
    class Meta:
        model = ImportRecord
        fields = ['word_entry', 'import_type', 'import_source', 'import_batch_id', 'import_metadata']
        widgets = {
            'word_entry': forms.Select(attrs={'class': 'form-control'}),
            'import_type': forms.Select(attrs={'class': 'form-control'}),
            'import_source': forms.Select(attrs={'class': 'form-control'}),
            'import_batch_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '导入批次ID'
            }),
            'import_metadata': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '导入元数据（JSON格式）'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 自动生成批次ID
        if not self.instance.pk and not self.initial.get('import_batch_id'):
            import uuid
            self.fields['import_batch_id'].initial = str(uuid.uuid4())[:8]