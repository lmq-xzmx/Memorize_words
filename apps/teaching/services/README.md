# 智能单词推荐服务

## 概述

智能单词推荐服务是一个基于用户学习行为和能力水平的个性化单词推荐系统，提供多种推荐策略以优化学习效果。

## 核心组件

### 1. 推荐服务 (recommendation_service.py)
- `SmartWordRecommendationService`: 核心推荐算法实现
- 支持个性化推荐、复习推荐、自适应难度推荐、弱项针对性推荐
- 集成缓存机制和性能优化

### 2. 配置管理 (recommendation_config.py)
- `RecommendationConfig`: 推荐算法参数配置
- `RecommendationStrategies`: 推荐策略权重配置
- 支持从Django设置动态加载配置

### 3. API视图 (views/recommendation_views.py)
- `WordRecommendationViewSet`: REST API视图集
- 提供完整的推荐服务API接口
- 包含错误处理和日志记录

### 4. URL路由 (urls/recommendation_urls.py)
- 推荐服务的URL路由配置
- 集成到主应用路由系统

## API端点

### 个性化推荐
```
GET /api/recommendations/personalized/
参数:
- count: 推荐数量 (默认: 10)
- learning_goal_id: 学习目标ID (可选)
- difficulty_level: 难度级别 (可选)
```

### 复习推荐
```
GET /api/recommendations/review/
参数:
- count: 推荐数量 (默认: 10)
- urgency_level: 紧急程度 (low/medium/high)
```

### 自适应难度推荐
```
GET /api/recommendations/adaptive_difficulty/
参数:
- count: 推荐数量 (默认: 10)
- target_accuracy: 目标准确率 (0.0-1.0)
```

### 弱项针对性推荐
```
GET /api/recommendations/weakness_targeted/
参数:
- count: 推荐数量 (默认: 10)
- focus_areas: 关注领域 (逗号分隔)
```

### 用户学习档案
```
GET /api/recommendations/user_profile/
```

### 清除缓存
```
POST /api/recommendations/clear_cache/
```

### 统计信息
```
GET /api/recommendations/stats/
```

## 测试

### 单元测试
- `tests/test_recommendation_service.py`: 推荐服务单元测试
- 覆盖所有核心功能和边界情况

### 管理命令
- `management/commands/test_recommendations.py`: 推荐算法性能测试命令
- 支持性能测试和准确性测试

## 使用示例

```python
from apps.teaching.services.recommendation_service import SmartWordRecommendationService
from apps.teaching.services.recommendation_config import RecommendationConfig

# 创建推荐服务实例
config = RecommendationConfig()
service = SmartWordRecommendationService(user=user, config=config)

# 获取个性化推荐
recommendations = service.get_personalized_recommendations(count=10)

# 获取复习推荐
review_words = service.get_review_recommendations(count=5, urgency_level='high')
```

## 配置说明

推荐算法支持通过Django设置进行配置：

```python
# settings.py
RECOMMENDATION_CONFIG = {
    'DEFAULT_RECOMMENDATION_COUNT': 10,
    'MAX_RECOMMENDATION_COUNT': 50,
    'CACHE_TIMEOUT': 3600,
    'PERSONALIZATION_WEIGHTS': {
        'frequency': 0.3,
        'difficulty': 0.25,
        'similarity': 0.2,
        'recency': 0.15,
        'user_preference': 0.1
    }
}
```

## 性能优化

1. **缓存机制**: 使用Redis缓存推荐结果和用户档案
2. **批量处理**: 支持批量获取和处理推荐
3. **异步处理**: 支持异步推荐计算
4. **数据库优化**: 使用select_related和prefetch_related优化查询

## 监控和分析

- 推荐准确率监控
- 用户满意度分析
- 算法性能指标
- 缓存命中率统计

## 扩展性

系统设计支持:
- 新增推荐策略
- 自定义权重配置
- 多语言支持
- 第三方算法集成

## 文档

详细的API文档请参考 `recommendation_api_docs.md`。