from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, F
from django.contrib.auth.models import User
from django.core.cache import cache
import numpy as np
from collections import defaultdict, Counter
import random
import math

from ..models import (
    LearningGoal, WordLearningRecord, LearningSession,
    WordLearningProgress, DailyStudyRecord
)
from apps.words.models import Word, WordSet, VocabularyList
from apps.analytics.utils import EngagementAnalyzer, PredictiveAnalyzer
from .recommendation_config import recommendation_config, recommendation_strategies


class SmartWordRecommendationService:
    """智能单词推荐服务"""
    
    def __init__(self, user: User):
        self.user = user
        self.current_time = timezone.now()
        self.config = recommendation_config
        self.strategies = recommendation_strategies
        self.cache_timeout = 300  # 5分钟缓存
    
    def get_personalized_recommendations(
        self, 
        goal_id: Optional[int] = None,
        count: Optional[int] = None,
        difficulty_preference: str = 'adaptive'
    ) -> Dict[str, Any]:
        """获取个性化单词推荐
        
        Args:
            goal_id: 学习目标ID，如果为None则使用当前激活目标
            count: 推荐单词数量
            difficulty_preference: 难度偏好 ('easy', 'medium', 'hard', 'adaptive')
        
        Returns:
            包含推荐单词列表和推荐理由的字典
        """
        if count is None:
            count = self.config.DEFAULT_RECOMMENDATION_COUNT
        count = self.config.validate_count(count)
        
        cache_key = self.config.get_cache_key(
            self.user.pk, 'personalized', count=count, goal_id=goal_id
        )
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # 获取学习目标
        goal = self._get_learning_goal(goal_id)
        if not goal:
            return {'words': [], 'reasons': [], 'strategy': 'no_goal'}
        
        # 分析用户学习模式
        user_profile = self._analyze_user_learning_profile()
        
        # 获取候选单词池
        candidate_words = self._get_candidate_words(goal)
        
        # 应用多种推荐策略
        recommendations = self._apply_recommendation_strategies(
            candidate_words, user_profile, count, difficulty_preference
        )
        
        return {
            'words': recommendations['words'],
            'reasons': recommendations['reasons'],
            'strategy': recommendations['strategy'],
            'user_profile': user_profile,
            'confidence_score': recommendations['confidence']
        }
    
    def get_review_recommendations(self, count: int = 10) -> Dict[str, Any]:
        """获取复习推荐
        
        基于遗忘曲线和学习记录推荐需要复习的单词
        """
        # 获取需要复习的单词
        review_candidates = self._get_review_candidates()
        
        # 按优先级排序
        prioritized_words = self._prioritize_review_words(review_candidates)
        
        # 选择推荐单词
        recommended_words = prioritized_words[:count]
        
        return {
            'words': [word['word'] for word in recommended_words],
            'priorities': [word['priority'] for word in recommended_words],
            'reasons': [word['reason'] for word in recommended_words],
            'strategy': 'spaced_repetition'
        }
    
    def get_adaptive_difficulty_recommendations(
        self, 
        goal_id: Optional[int] = None,
        count: int = 15
    ) -> Dict[str, Any]:
        """获取自适应难度推荐
        
        根据用户当前能力水平动态调整推荐难度
        """
        user_ability = self._calculate_user_ability_level()
        goal = self._get_learning_goal(goal_id)
        
        if not goal:
            return {'words': [], 'ability_level': user_ability, 'strategy': 'no_goal'}
        
        # 获取适合用户能力的单词
        suitable_words = self._get_words_by_difficulty(
            goal, user_ability['level'], count * 2
        )
        
        # 应用自适应算法
        adaptive_recommendations = self._apply_adaptive_algorithm(
            suitable_words, user_ability, count
        )
        
        return {
            'words': adaptive_recommendations,
            'ability_level': user_ability,
            'strategy': 'adaptive_difficulty',
            'next_level_progress': self._calculate_level_progress(user_ability)
        }
    
    def get_weakness_focused_recommendations(
        self, 
        count: int = 12
    ) -> Dict[str, Any]:
        """获取弱项针对性推荐
        
        分析用户学习弱点，推荐相关单词加强练习
        """
        # 分析学习弱点
        weaknesses = self._analyze_learning_weaknesses()
        
        # 获取针对性单词
        targeted_words = self._get_weakness_targeted_words(weaknesses, count)
        
        return {
            'words': targeted_words['words'],
            'weaknesses': weaknesses,
            'improvement_areas': targeted_words['areas'],
            'strategy': 'weakness_focused'
        }
    
    def _get_learning_goal(self, goal_id: Optional[int]) -> Optional[LearningGoal]:
        """获取学习目标"""
        if goal_id:
            return LearningGoal.objects.filter(
                id=goal_id, user=self.user
            ).first()
        else:
            return LearningGoal.objects.filter(
                user=self.user, is_current=True
            ).first()
    
    def _analyze_user_learning_profile(self) -> Dict[str, Any]:
        """分析用户学习档案"""
        # 获取最近30天的学习数据
        recent_records = WordLearningRecord.objects.filter(
            session__user=self.user,
            created_at__gte=self.current_time - timedelta(days=30)
        )
        
        # 计算学习统计
        total_attempts = recent_records.count()
        correct_attempts = recent_records.filter(is_correct=True).count()
        avg_response_time = recent_records.aggregate(
            avg_time=Avg('response_time')
        )['avg_time'] or 0
        
        # 分析学习时间偏好
        time_preferences = self._analyze_time_preferences()
        
        # 分析难度偏好
        difficulty_preferences = self._analyze_difficulty_preferences()
        
        # 分析学习模式
        learning_patterns = self._analyze_learning_patterns()
        
        return {
            'accuracy_rate': (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0,
            'avg_response_time': float(avg_response_time),
            'total_attempts': total_attempts,
            'time_preferences': time_preferences,
            'difficulty_preferences': difficulty_preferences,
            'learning_patterns': learning_patterns,
            'engagement_level': self._calculate_engagement_level()
        }
    
    def _get_candidate_words(self, goal: LearningGoal) -> List[Word]:
        """获取候选单词池"""
        # 获取目标相关的所有单词
        goal_words = goal.get_words()
        
        # 排除已掌握的单词
        mastered_words = WordLearningProgress.objects.filter(
            user=self.user,
            mastery_level='mastered'
        ).values_list('word_id', flat=True)
        
        candidate_words = goal_words.exclude(id__in=mastered_words)
        
        return list(candidate_words)
    
    def _apply_recommendation_strategies(
        self, 
        candidates: List[Word], 
        profile: Dict[str, Any],
        count: int,
        difficulty_preference: str
    ) -> Dict[str, Any]:
        """应用推荐策略"""
        strategies = {
            'frequency_based': 0.3,  # 基于词频
            'similarity_based': 0.25,  # 基于相似性
            'progress_based': 0.25,   # 基于学习进度
            'random_exploration': 0.2  # 随机探索
        }
        
        recommendations = []
        reasons = []
        
        # 应用各种策略
        for strategy, weight in strategies.items():
            strategy_count = int(count * weight)
            if strategy_count > 0:
                strategy_words, strategy_reasons = self._apply_single_strategy(
                    strategy, candidates, profile, strategy_count, difficulty_preference
                )
                recommendations.extend(strategy_words)
                reasons.extend(strategy_reasons)
        
        # 去重并限制数量
        unique_recommendations = []
        unique_reasons = []
        seen_words = set()
        
        for word, reason in zip(recommendations, reasons):
            if word.id not in seen_words:
                unique_recommendations.append(word)
                unique_reasons.append(reason)
                seen_words.add(word.id)
                
                if len(unique_recommendations) >= count:
                    break
        
        return {
            'words': unique_recommendations,
            'reasons': unique_reasons,
            'strategy': 'multi_strategy',
            'confidence': self._calculate_recommendation_confidence(profile)
        }
    
    def _apply_single_strategy(
        self, 
        strategy: str, 
        candidates: List[Word],
        profile: Dict[str, Any],
        count: int,
        difficulty_preference: str
    ) -> Tuple[List[Word], List[str]]:
        """应用单一推荐策略"""
        if strategy == 'frequency_based':
            return self._frequency_based_recommendation(candidates, count)
        elif strategy == 'similarity_based':
            return self._similarity_based_recommendation(candidates, profile, count)
        elif strategy == 'progress_based':
            return self._progress_based_recommendation(candidates, profile, count)
        elif strategy == 'random_exploration':
            return self._random_exploration_recommendation(candidates, count)
        else:
            return [], []
    
    def _frequency_based_recommendation(
        self, 
        candidates: List[Word], 
        count: int
    ) -> Tuple[List[Word], List[str]]:
        """基于词频的推荐"""
        # 按词频排序（假设有frequency字段）
        sorted_words = sorted(
            candidates, 
            key=lambda w: getattr(w, 'frequency', 0), 
            reverse=True
        )
        
        selected_words = sorted_words[:count]
        reasons = ['高频词汇，实用性强'] * len(selected_words)
        
        return selected_words, reasons
    
    def _similarity_based_recommendation(
        self, 
        candidates: List[Word],
        profile: Dict[str, Any],
        count: int
    ) -> Tuple[List[Word], List[str]]:
        """基于相似性的推荐"""
        # 获取用户最近学习的单词
        recent_words = list(WordLearningRecord.objects.filter(
            session__user=self.user,
            created_at__gte=self.current_time - timedelta(days=7)
        ).values_list('word_id', flat=True).distinct())
        
        if not recent_words:
            return self._random_exploration_recommendation(candidates, count)
        
        # 简化的相似性计算（基于词性和难度等级）
        similar_words = []
        for candidate in candidates:
            similarity_score = self._calculate_word_similarity(
                candidate, recent_words
            )
            similar_words.append((candidate, similarity_score))
        
        # 按相似性排序
        similar_words.sort(key=lambda x: x[1], reverse=True)
        
        selected_words = [word for word, _ in similar_words[:count]]
        reasons = ['与已学单词相关，便于联想记忆'] * len(selected_words)
        
        return selected_words, reasons
    
    def _progress_based_recommendation(
        self, 
        candidates: List[Word],
        profile: Dict[str, Any],
        count: int
    ) -> Tuple[List[Word], List[str]]:
        """基于学习进度的推荐"""
        # 获取用户的学习进度数据
        progress_data = WordLearningProgress.objects.filter(
            user=self.user,
            word__in=candidates
        ).select_related('word')
        
        # 按学习进度排序（优先推荐部分掌握的单词）
        progress_words = []
        for progress in progress_data:
            if progress.mastery_level in ['learning', 'reviewing']:
                priority_score = self._calculate_progress_priority(progress)
                progress_words.append((progress.word, priority_score))
        
        # 补充新单词
        existing_word_ids = {word.pk for word, _ in progress_words}
        new_words = [
            word for word in candidates 
            if word.pk not in existing_word_ids
        ][:count - len(progress_words)]
        
        progress_words.extend([(word, 0.5) for word in new_words])
        
        # 排序并选择
        progress_words.sort(key=lambda x: x[1], reverse=True)
        selected_words = [word for word, _ in progress_words[:count]]
        
        reasons = []
        for word, score in progress_words[:count]:
            if score > 0.7:
                reasons.append('即将掌握，加强练习')
            elif score > 0.3:
                reasons.append('正在学习中，需要巩固')
            else:
                reasons.append('新单词，扩展词汇量')
        
        return selected_words, reasons
    
    def _random_exploration_recommendation(
        self, 
        candidates: List[Word], 
        count: int
    ) -> Tuple[List[Word], List[str]]:
        """随机探索推荐"""
        selected_words = random.sample(
            candidates, 
            min(count, len(candidates))
        )
        reasons = ['探索新词汇，拓展学习范围'] * len(selected_words)
        
        return selected_words, reasons
    
    def _get_review_candidates(self) -> List[Dict[str, Any]]:
        """获取复习候选单词"""
        # 获取需要复习的单词进度记录
        review_progress = WordLearningProgress.objects.filter(
            user=self.user,
            mastery_level__in=['learning', 'reviewing', 'forgotten'],
            next_review_at__lte=self.current_time
        ).select_related('word')
        
        candidates = []
        for progress in review_progress:
            urgency = self._calculate_review_urgency(progress)
            candidates.append({
                'word': progress.word,
                'progress': progress,
                'urgency': urgency,
                'last_review': progress.last_reviewed_at
            })
        
        return candidates
    
    def _prioritize_review_words(
        self, 
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """优先级排序复习单词"""
        prioritized = []
        
        for candidate in candidates:
            priority_score = self._calculate_review_priority(candidate)
            reason = self._generate_review_reason(candidate)
            
            prioritized.append({
                'word': candidate['word'],
                'priority': priority_score,
                'reason': reason,
                'urgency': candidate['urgency']
            })
        
        # 按优先级排序
        prioritized.sort(key=lambda x: x['priority'], reverse=True)
        
        return prioritized
    
    def _calculate_user_ability_level(self) -> Dict[str, Any]:
        """计算用户能力水平"""
        # 获取最近的学习记录
        recent_records = WordLearningRecord.objects.filter(
            session__user=self.user,
            created_at__gte=self.current_time - timedelta(days=14)
        )
        
        if not recent_records.exists():
            return {'level': 'beginner', 'score': 0, 'confidence': 0}
        
        # 计算各项指标
        accuracy = recent_records.filter(is_correct=True).count() / recent_records.count()
        avg_response_time = recent_records.aggregate(
            avg_time=Avg('response_time')
        )['avg_time'] or 10
        
        # 计算能力分数
        ability_score = (
            accuracy * 0.6 +  # 准确率权重60%
            (1 / max(avg_response_time, 1)) * 0.4  # 响应速度权重40%
        ) * 100
        
        # 确定能力等级
        if ability_score >= 80:
            level = 'advanced'
        elif ability_score >= 60:
            level = 'intermediate'
        else:
            level = 'beginner'
        
        return {
            'level': level,
            'score': ability_score,
            'accuracy': accuracy * 100,
            'avg_response_time': float(avg_response_time),
            'confidence': min(recent_records.count() / 50, 1.0)  # 基于数据量的置信度
        }
    
    def _get_words_by_difficulty(
        self, 
        goal: LearningGoal, 
        ability_level: str, 
        count: int
    ) -> List[Word]:
        """根据难度获取单词"""
        # 难度映射
        difficulty_mapping = {
            'beginner': [1, 2, 3],
            'intermediate': [3, 4, 5],
            'advanced': [5, 6, 7]
        }
        
        target_grades = difficulty_mapping.get(ability_level, [1, 2, 3])
        
        # 获取目标单词
        goal_words = goal.get_words()
        suitable_words = goal_words.filter(
            grade__in=target_grades
        )[:count]
        
        return list(suitable_words)
    
    def _apply_adaptive_algorithm(
        self, 
        words: List[Word], 
        ability: Dict[str, Any], 
        count: int
    ) -> List[Word]:
        """应用自适应算法"""
        if not words:
            return []
        
        # 根据用户能力调整选择策略
        if ability['confidence'] < 0.3:
            # 数据不足，保守选择
            return words[:count]
        
        # 基于能力水平的自适应选择
        adaptive_words = []
        
        # 70%选择适合当前水平的单词
        current_level_count = int(count * 0.7)
        adaptive_words.extend(words[:current_level_count])
        
        # 30%选择挑战性单词
        challenge_count = count - current_level_count
        if challenge_count > 0 and len(words) > current_level_count:
            challenge_words = words[current_level_count:current_level_count + challenge_count]
            adaptive_words.extend(challenge_words)
        
        return adaptive_words[:count]
    
    def _analyze_learning_weaknesses(self) -> Dict[str, Any]:
        """分析学习弱点"""
        # 获取错误记录
        error_records = WordLearningRecord.objects.filter(
            session__user=self.user,
            is_correct=False,
            created_at__gte=self.current_time - timedelta(days=30)
        ).select_related('word')
        
        # 分析错误模式
        error_patterns = {
            'difficult_words': [],
            'word_types': defaultdict(int),
            'time_patterns': defaultdict(int),
            'common_mistakes': []
        }
        
        for record in error_records:
            word = record.word
            
            # 统计困难单词
            error_patterns['difficult_words'].append(word)
            
            # 统计词性错误
            if hasattr(word, 'part_of_speech'):
                error_patterns['word_types'][word.part_of_speech] += 1
            
            # 统计时间模式
            hour = record.created_at.hour
            error_patterns['time_patterns'][hour] = error_patterns['time_patterns'].get(hour, 0) + 1
        
        return {
            'error_count': error_records.count(),
            'difficult_words': error_patterns['difficult_words'][:10],
            'problematic_word_types': dict(error_patterns['word_types']),
            'error_time_patterns': dict(error_patterns['time_patterns'])
        }
    
    def _get_weakness_targeted_words(
        self, 
        weaknesses: Dict[str, Any], 
        count: int
    ) -> Dict[str, Any]:
        """获取针对弱点的单词"""
        targeted_words = []
        improvement_areas = []
        
        # 针对困难单词类型
        if weaknesses['problematic_word_types']:
            most_problematic = max(
                weaknesses['problematic_word_types'].items(),
                key=lambda x: x[1]
            )[0]
            
            similar_words = Word.objects.filter(
                part_of_speech=most_problematic
            ).exclude(
                id__in=[w.id for w in weaknesses['difficult_words']]
            )[:count//2]
            
            targeted_words.extend(similar_words)
            improvement_areas.append(f'{most_problematic}词性练习')
        
        # 补充其他推荐
        remaining_count = count - len(targeted_words)
        if remaining_count > 0:
            additional_words = Word.objects.exclude(
                id__in=[w.id for w in targeted_words + weaknesses['difficult_words']]
            )[:remaining_count]
            
            targeted_words.extend(additional_words)
            improvement_areas.append('综合能力提升')
        
        return {
            'words': targeted_words,
            'areas': improvement_areas
        }
    
    # 辅助方法
    def _analyze_time_preferences(self) -> Dict[str, Any]:
        """分析时间偏好"""
        sessions = LearningSession.objects.filter(
            user=self.user,
            start_time__gte=self.current_time - timedelta(days=30)
        )
        
        hour_distribution = defaultdict(int)
        for session in sessions:
            hour_distribution[session.start_time.hour] += 1
        
        if hour_distribution:
            preferred_hour = max(hour_distribution.items(), key=lambda x: x[1])[0]
            return {
                'preferred_hour': preferred_hour,
                'distribution': dict(hour_distribution)
            }
        
        return {'preferred_hour': 9, 'distribution': {}}
    
    def _analyze_difficulty_preferences(self) -> Dict[str, Any]:
        """分析难度偏好"""
        records = WordLearningRecord.objects.filter(
            session__user=self.user,
            created_at__gte=self.current_time - timedelta(days=30)
        ).select_related('word')
        
        grade_performance = defaultdict(list)
        for record in records:
            if hasattr(record.word, 'grade') and record.word.grade:
                grade_performance[record.word.grade].append(record.is_correct)
        
        preferences = {}
        for grade, results in grade_performance.items():
            accuracy = sum(results) / len(results) if results else 0
            preferences[str(grade)] = {
                'accuracy': accuracy,
                'attempts': len(results)
            }
        
        return preferences
    
    def _analyze_learning_patterns(self) -> Dict[str, Any]:
        """分析学习模式"""
        daily_records = DailyStudyRecord.objects.filter(
            user=self.user,
            date__gte=self.current_time.date() - timedelta(days=30)
        )
        
        patterns = {
            'avg_daily_words': 0,
            'avg_session_duration': 0,
            'consistency_score': 0
        }
        
        if daily_records.exists():
            patterns['avg_daily_words'] = daily_records.aggregate(
                avg=Avg('words_studied')
            )['avg'] or 0
            
            patterns['consistency_score'] = (
                daily_records.count() / 30 * 100
            )  # 学习天数占比
        
        return patterns
    
    def _calculate_engagement_level(self) -> str:
        """计算参与度等级"""
        recent_sessions = LearningSession.objects.filter(
            user=self.user,
            start_time__gte=self.current_time - timedelta(days=7)
        )
        
        session_count = recent_sessions.count()
        
        if session_count >= 10:
            return 'high'
        elif session_count >= 5:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_word_similarity(
        self, 
        word: Word, 
        reference_words: List[int]
    ) -> float:
        """计算单词相似性（简化版）"""
        # 这里可以实现更复杂的相似性算法
        # 目前基于词性和难度等级的简单相似性
        similarity_score = 0.0
        
        reference_word_objects = Word.objects.filter(id__in=reference_words)
        
        for ref_word in reference_word_objects:
            # 词性相似性
            if (hasattr(word, 'part_of_speech') and 
                hasattr(ref_word, 'part_of_speech') and
                word.part_of_speech == ref_word.part_of_speech):
                similarity_score += 0.3
            
            # 难度等级相似性
            if (hasattr(word, 'grade') and 
                hasattr(ref_word, 'grade') and
                abs((word.grade or 0) - (ref_word.grade or 0)) <= 1):
                similarity_score += 0.2
        
        return similarity_score / max(len(reference_word_objects), 1)
    
    def _calculate_progress_priority(self, progress: WordLearningProgress) -> float:
        """计算进度优先级"""
        priority = 0.0
        
        # 基于掌握程度
        mastery_weights = {
            'learning': 0.8,
            'reviewing': 0.9,
            'forgotten': 1.0
        }
        priority += mastery_weights.get(progress.mastery_level, 0.5)
        
        # 基于准确率
        if progress.accuracy_rate < 50:
            priority += 0.3
        elif progress.accuracy_rate > 80:
            priority += 0.1
        
        return priority
    
    def _calculate_review_urgency(self, progress: WordLearningProgress) -> float:
        """计算复习紧急程度"""
        if not progress.next_review_at:
            return 1.0
        
        overdue_hours = (
            self.current_time - progress.next_review_at
        ).total_seconds() / 3600
        
        if overdue_hours > 24:
            return 1.0  # 超过1天，高紧急
        elif overdue_hours > 0:
            return 0.8  # 已过期，中等紧急
        else:
            return 0.5  # 未过期，低紧急
    
    def _calculate_review_priority(self, candidate: Dict[str, Any]) -> float:
        """计算复习优先级"""
        progress = candidate['progress']
        urgency = candidate['urgency']
        
        priority = urgency * 0.4  # 紧急程度权重40%
        
        # 遗忘状态优先级最高
        if progress.mastery_level == 'forgotten':
            priority += 0.6
        elif progress.mastery_level == 'reviewing':
            priority += 0.4
        else:
            priority += 0.2
        
        # 准确率影响
        if progress.accuracy_rate < 60:
            priority += 0.2
        
        return min(priority, 1.0)
    
    def _generate_review_reason(self, candidate: Dict[str, Any]) -> str:
        """生成复习理由"""
        progress = candidate['progress']
        urgency = candidate['urgency']
        
        if progress.mastery_level == 'forgotten':
            return '已遗忘，需要重新学习'
        elif urgency > 0.8:
            return '复习时间已到，防止遗忘'
        elif progress.accuracy_rate < 60:
            return '掌握不牢固，需要加强练习'
        else:
            return '定期复习，巩固记忆'
    
    def _calculate_recommendation_confidence(self, profile: Dict[str, Any]) -> float:
        """计算推荐置信度"""
        confidence = 0.5  # 基础置信度
        
        # 基于数据量
        if profile['total_attempts'] > 100:
            confidence += 0.3
        elif profile['total_attempts'] > 50:
            confidence += 0.2
        elif profile['total_attempts'] > 20:
            confidence += 0.1
        
        # 基于学习稳定性
        if profile['learning_patterns']['consistency_score'] > 70:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _calculate_level_progress(self, ability: Dict[str, Any]) -> Dict[str, Any]:
        """计算等级进度"""
        current_score = ability['score']
        
        level_thresholds = {
            'beginner': (0, 60),
            'intermediate': (60, 80),
            'advanced': (80, 100)
        }
        
        current_level = ability['level']
        min_score, max_score = level_thresholds[current_level]
        
        progress = (current_score - min_score) / (max_score - min_score) * 100
        progress = max(0, min(100, progress))
        
        return {
            'current_progress': progress,
            'next_level_threshold': max_score,
            'points_to_next_level': max(0, max_score - current_score)
        }