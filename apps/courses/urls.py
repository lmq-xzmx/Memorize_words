from django.contrib import admin

# 注意：vocabulary_manager 应用中的所有模型已迁移到 teaching 应用统一管理
# 包括：LearningGoal, LearningPlan, DailyStudyRecord, StudySession(现为LearningSession), 
#       UserStreak, WordLearningProgress
# 
# 为避免重复注册和混淆，此文件保持最小化配置
# 所有相关的 Admin 配置请参考 apps/teaching/admin.py

# 如果将来需要为 vocabulary_manager 应用添加新的独有模型，
# 可以在此文件中添加相应的 Admin 配置
