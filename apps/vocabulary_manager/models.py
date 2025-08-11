# vocabulary_manager应用的models.py
# 学习目标、学习计划、学习记录等模型已迁移到teaching应用
# 此文件保留用于兼容性和数据迁移

import datetime
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# 注意：以下模型已迁移到apps.teaching.models，此处保留用于数据迁移
# 在完成数据迁移后，这些模型定义将被移除

# 已迁移的模型：
# - LearningGoal -> apps.teaching.models.LearningGoal
# - LearningPlan -> apps.teaching.models.LearningPlan  
# - DailyStudyRecord -> apps.teaching.models.DailyStudyRecord


# 原有的学习计划相关模型已迁移到teaching应用
# 如需使用这些模型，请从apps.teaching.models导入：
# from apps.teaching.models import LearningGoal, LearningPlan, DailyStudyRecord

# 为了兼容性，创建一些别名
VocabularySource = None
VocabularyList = None
VocabularyWord = None