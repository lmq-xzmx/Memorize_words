from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from .models import Word, WordSet
from apps.teaching.models import LearningSession as StudySession, UserStreak


@receiver(post_save, sender=Word)
def update_user_streak_on_word_learned(sender, instance, created, **kwargs):
    """当单词被标记为已学习时，更新用户学习记录"""
    # 检查单词是否有学习时间（表示已学习）
    if instance.learned_at:
        # 注意：Word模型可能没有user字段，这里需要根据实际情况调整
        # 暂时注释掉用户相关的逻辑，避免错误
        pass
        # 如果需要用户学习记录功能，需要先在Word模型中添加user字段
        # 或者通过其他方式关联用户


# ImportedVocabulary模型已被删除，相关信号处理器已移除


@receiver(post_save, sender=StudySession)
def update_session_word_count(sender, instance, created, **kwargs):
    """当学习会话被保存时，自动更新单词数量"""
    if not created:  # 只在更新时执行
        # 更新单词数量
        instance.words_count = instance.words_studied.count()
        if instance.words_count != instance._state.fields_cache.get('words_count', 0):
            # 避免无限递归，只在数量真的变化时保存
            StudySession.objects.filter(id=instance.id).update(
                words_count=instance.words_count
            )


@receiver(post_save, sender=Word)
def auto_set_difficulty_level(sender, instance, created, **kwargs):
    """根据单词长度和复杂度自动设置难度等级"""
    if created and instance.difficulty_level == 1:  # 只对新创建且未设置难度的单词
        word_length = len(instance.word)
        
        # 根据单词长度设置基础难度
        if word_length <= 3:
            base_difficulty = 1
        elif word_length <= 5:
            base_difficulty = 2
        elif word_length <= 7:
            base_difficulty = 3
        elif word_length <= 10:
            base_difficulty = 4
        else:
            base_difficulty = 5
        
        # 根据是否有音标、释义等信息调整难度
        complexity_bonus = 0
        if not instance.phonetic:
            complexity_bonus += 1
        if not instance.definition:
            complexity_bonus += 1
        if instance.part_of_speech in ['动词', '形容词', '副词']:
            complexity_bonus += 1
        
        # 计算最终难度（1-5级）
        final_difficulty = min(5, max(1, base_difficulty + complexity_bonus))
        
        if final_difficulty != instance.difficulty_level:
            Word.objects.filter(id=instance.id).update(
                difficulty_level=final_difficulty
            )


@receiver(m2m_changed, sender=WordSet.words.through)
def update_wordset_word_count(sender, instance, action, **kwargs):
    """当单词集的单词发生变化时，自动更新单词数量"""
    try:
        # 只在添加或删除单词后更新计数
        if action in ['post_add', 'post_remove', 'post_clear']:
            instance.update_word_count()
    except Exception as e:
        print(f"WordSet单词数量更新失败: {e}")