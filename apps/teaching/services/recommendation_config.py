from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from django.conf import settings


@dataclass
class RecommendationConfig:
    """智能推荐算法配置类"""
    
    # 基础推荐参数
    DEFAULT_RECOMMENDATION_COUNT: int = 10
    MAX_RECOMMENDATION_COUNT: int = 50
    MIN_RECOMMENDATION_COUNT: int = 1
    
    # 个性化推荐权重
    PERSONALIZED_WEIGHTS: Optional[Dict[str, float]] = None
    
    # 复习推荐参数
    REVIEW_PRIORITY_WEIGHTS: Optional[Dict[str, float]] = None
    REVIEW_TIME_THRESHOLDS: Optional[Dict[str, int]] = None  # 小时
    
    # 自适应难度参数
    DIFFICULTY_ADJUSTMENT_FACTOR: float = 0.1
    ABILITY_CONFIDENCE_THRESHOLD: float = 0.6
    DIFFICULTY_RANGE: Optional[Dict[str, int]] = None
    
    # 弱项针对性推荐参数
    WEAKNESS_DETECTION_THRESHOLD: float = 0.4
    WEAKNESS_FOCUS_RATIO: float = 0.7
    
    # 缓存配置
    CACHE_TIMEOUT: int = 300  # 5分钟
    CACHE_KEY_PREFIX: str = 'word_recommendation'
    
    # 性能优化参数
    BATCH_SIZE: int = 100
    MAX_QUERY_TIME: float = 2.0  # 秒
    
    def __post_init__(self):
        """初始化默认配置"""
        if self.PERSONALIZED_WEIGHTS is None:
            self.PERSONALIZED_WEIGHTS = {
                'frequency_score': 0.25,
                'similarity_score': 0.20,
                'progress_score': 0.30,
                'random_exploration': 0.25
            }
        
        if self.REVIEW_PRIORITY_WEIGHTS is None:
            self.REVIEW_PRIORITY_WEIGHTS = {
                'time_since_last_review': 0.4,
                'error_rate': 0.3,
                'forgetting_curve': 0.2,
                'importance_score': 0.1
            }
        
        if self.REVIEW_TIME_THRESHOLDS is None:
            self.REVIEW_TIME_THRESHOLDS = {
                'urgent': 24,      # 24小时内必须复习
                'important': 72,   # 3天内应该复习
                'normal': 168,     # 1周内可以复习
                'optional': 336    # 2周内选择性复习
            }
        
        if self.DIFFICULTY_RANGE is None:
            self.DIFFICULTY_RANGE = {
                'min_grade': 1,
                'max_grade': 12,
                'default_grade': 6
            }
    
    @classmethod
    def from_settings(cls) -> 'RecommendationConfig':
        """从Django设置中加载配置"""
        config_dict = getattr(settings, 'WORD_RECOMMENDATION_CONFIG', {})
        
        # 创建配置实例
        config = cls()
        
        # 更新配置
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def get_cache_key(self, user_id: int, recommendation_type: str, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [
            self.CACHE_KEY_PREFIX,
            str(user_id),
            recommendation_type
        ]
        
        # 添加额外参数
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}_{value}")
        
        return ':'.join(key_parts)
    
    def validate_count(self, count: int) -> int:
        """验证并调整推荐数量"""
        if count < self.MIN_RECOMMENDATION_COUNT:
            return self.MIN_RECOMMENDATION_COUNT
        elif count > self.MAX_RECOMMENDATION_COUNT:
            return self.MAX_RECOMMENDATION_COUNT
        return count
    
    def get_difficulty_adjustment(self, user_ability: float, target_difficulty: float) -> float:
        """计算难度调整值"""
        difficulty_gap = target_difficulty - user_ability
        return difficulty_gap * self.DIFFICULTY_ADJUSTMENT_FACTOR
    
    def is_review_urgent(self, hours_since_last_review: int) -> bool:
        """判断是否需要紧急复习"""
        if not self.REVIEW_TIME_THRESHOLDS:
            return False
        return hours_since_last_review >= self.REVIEW_TIME_THRESHOLDS['urgent']
    
    def get_review_priority_level(self, hours_since_last_review: int) -> str:
        """获取复习优先级等级"""
        thresholds = self.REVIEW_TIME_THRESHOLDS
        if not thresholds:
            return 'normal'
        
        if hours_since_last_review >= thresholds['optional']:
            return 'optional'
        elif hours_since_last_review >= thresholds['normal']:
            return 'normal'
        elif hours_since_last_review >= thresholds['important']:
            return 'important'
        else:
            return 'urgent'
    
    def calculate_weighted_score(self, scores: Dict[str, float], weights: Dict[str, float]) -> float:
        """计算加权分数"""
        total_score = 0.0
        total_weight = 0.0
        
        for key, weight in weights.items():
            if key in scores:
                total_score += scores[key] * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def get_exploration_ratio(self, user_experience_level: str) -> float:
        """获取探索比例（用于平衡推荐的多样性）"""
        exploration_ratios = {
            'beginner': 0.4,    # 新手需要更多探索
            'intermediate': 0.25, # 中级用户适度探索
            'advanced': 0.15,   # 高级用户较少探索
            'expert': 0.1       # 专家用户最少探索
        }
        
        return exploration_ratios.get(user_experience_level, 0.25)
    
    def get_batch_processing_config(self) -> Dict[str, Any]:
        """获取批处理配置"""
        return {
            'batch_size': self.BATCH_SIZE,
            'max_query_time': self.MAX_QUERY_TIME,
            'enable_parallel_processing': True,
            'max_workers': 4
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'DEFAULT_RECOMMENDATION_COUNT': self.DEFAULT_RECOMMENDATION_COUNT,
            'MAX_RECOMMENDATION_COUNT': self.MAX_RECOMMENDATION_COUNT,
            'MIN_RECOMMENDATION_COUNT': self.MIN_RECOMMENDATION_COUNT,
            'PERSONALIZED_WEIGHTS': self.PERSONALIZED_WEIGHTS,
            'REVIEW_PRIORITY_WEIGHTS': self.REVIEW_PRIORITY_WEIGHTS,
            'REVIEW_TIME_THRESHOLDS': self.REVIEW_TIME_THRESHOLDS,
            'DIFFICULTY_ADJUSTMENT_FACTOR': self.DIFFICULTY_ADJUSTMENT_FACTOR,
            'ABILITY_CONFIDENCE_THRESHOLD': self.ABILITY_CONFIDENCE_THRESHOLD,
            'DIFFICULTY_RANGE': self.DIFFICULTY_RANGE,
            'WEAKNESS_DETECTION_THRESHOLD': self.WEAKNESS_DETECTION_THRESHOLD,
            'WEAKNESS_FOCUS_RATIO': self.WEAKNESS_FOCUS_RATIO,
            'CACHE_TIMEOUT': self.CACHE_TIMEOUT,
            'CACHE_KEY_PREFIX': self.CACHE_KEY_PREFIX,
            'BATCH_SIZE': self.BATCH_SIZE,
            'MAX_QUERY_TIME': self.MAX_QUERY_TIME
        }


# 全局配置实例
recommendation_config = RecommendationConfig.from_settings()


# 推荐策略配置
class RecommendationStrategies:
    """推荐策略配置"""
    
    # 策略权重配置
    STRATEGY_WEIGHTS = {
        'frequency_based': {
            'high_frequency': 0.3,
            'medium_frequency': 0.5,
            'low_frequency': 0.2
        },
        'similarity_based': {
            'semantic_similarity': 0.4,
            'phonetic_similarity': 0.3,
            'contextual_similarity': 0.3
        },
        'progress_based': {
            'mastery_level': 0.4,
            'learning_speed': 0.3,
            'retention_rate': 0.3
        },
        'difficulty_based': {
            'grade_level': 0.5,
            'complexity_score': 0.3,
            'user_ability_match': 0.2
        }
    }
    
    # 学习模式配置
    LEARNING_MODES = {
        'intensive': {
            'focus_ratio': 0.8,
            'exploration_ratio': 0.2,
            'difficulty_progression': 'gradual'
        },
        'extensive': {
            'focus_ratio': 0.6,
            'exploration_ratio': 0.4,
            'difficulty_progression': 'varied'
        },
        'review': {
            'focus_ratio': 0.9,
            'exploration_ratio': 0.1,
            'difficulty_progression': 'adaptive'
        },
        'discovery': {
            'focus_ratio': 0.3,
            'exploration_ratio': 0.7,
            'difficulty_progression': 'random'
        }
    }
    
    # 时间段推荐策略
    TIME_BASED_STRATEGIES = {
        'morning': {
            'energy_level': 'high',
            'recommended_difficulty': 'challenging',
            'focus_areas': ['new_words', 'complex_grammar']
        },
        'afternoon': {
            'energy_level': 'medium',
            'recommended_difficulty': 'moderate',
            'focus_areas': ['review', 'practice']
        },
        'evening': {
            'energy_level': 'low',
            'recommended_difficulty': 'easy',
            'focus_areas': ['light_review', 'familiar_words']
        }
    }
    
    @classmethod
    def get_strategy_for_user_state(cls, user_state: Dict[str, Any]) -> Dict[str, Any]:
        """根据用户状态获取推荐策略"""
        # 基础策略
        strategy = {
            'weights': cls.STRATEGY_WEIGHTS['frequency_based'].copy(),
            'mode': 'extensive',
            'time_preference': 'afternoon'
        }
        
        # 根据用户能力调整
        ability_level = user_state.get('ability_level', 'intermediate')
        if ability_level == 'beginner':
            strategy['weights'] = cls.STRATEGY_WEIGHTS['frequency_based']
            strategy['mode'] = 'intensive'
        elif ability_level == 'advanced':
            strategy['weights'] = cls.STRATEGY_WEIGHTS['similarity_based']
            strategy['mode'] = 'discovery'
        
        # 根据学习目标调整
        learning_goal = user_state.get('learning_goal', 'general')
        if learning_goal == 'exam_prep':
            strategy['mode'] = 'intensive'
            strategy['weights'] = cls.STRATEGY_WEIGHTS['difficulty_based']
        elif learning_goal == 'vocabulary_expansion':
            strategy['mode'] = 'discovery'
            strategy['weights'] = cls.STRATEGY_WEIGHTS['similarity_based']
        
        return strategy
    
    @classmethod
    def get_time_based_strategy(cls, current_hour: int) -> Dict[str, Any]:
        """根据时间获取推荐策略"""
        if 6 <= current_hour < 12:
            return cls.TIME_BASED_STRATEGIES['morning']
        elif 12 <= current_hour < 18:
            return cls.TIME_BASED_STRATEGIES['afternoon']
        else:
            return cls.TIME_BASED_STRATEGIES['evening']


# 全局策略实例
recommendation_strategies = RecommendationStrategies()