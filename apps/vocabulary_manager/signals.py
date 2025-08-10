from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LearningGoal, LearningPlan, DailyStudyRecord


@receiver(post_save, sender=LearningGoal)
def update_goal_progress(sender, instance, **kwargs):
    """更新学习目标进度"""
    # 这里可以添加自动更新学习目标进度的逻辑
    pass


@receiver(post_save, sender=DailyStudyRecord)
def update_plan_progress(sender, instance, **kwargs):
    """更新学习计划进度"""
    # 这里可以添加自动更新学习计划进度的逻辑
    pass