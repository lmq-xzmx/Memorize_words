# 智能单词推荐服务 API 文档

## 概述

智能单词推荐服务为用户提供个性化的单词学习推荐，基于用户的学习历史、能力水平、学习偏好等多维度数据，运用机器学习算法生成最适合的学习内容。

## 基础配置

### 服务初始化

```python
from apps.teaching.services.recommendation_service import SmartWordRecommendationService

# 初始化推荐服务
service = SmartWordRecommendationService(user)
```

### 配置参数

推荐服务支持通过 Django settings 进行配置：

```python
# settings.py
WORD_RECOMMENDATION_CONFIG = {
    'DEFAULT_RECOMMENDATION_COUNT': 10,
    'MAX_RECOMMENDATION_COUNT': 50,
    'CACHE_TIMEOUT': 300,
    'PERSONALIZED_WEIGHTS': {
        'frequency_score': 0.25,
        'similarity_score': 0.20,
        'progress_score': 0.30,
        'random_exploration': 0.25
    }
}
```

## API 接口

### 1. 个性化推荐

根据用户的学习历史和偏好提供个性化单词推荐。

**方法签名：**
```python
get_personalized_recommendations(
    count: Optional[int] = None,
    goal_id: Optional[int] = None,
    difficulty_preference: str = 'adaptive'
) -> Dict[str, Any]
```

**参数说明：**
- `count`: 推荐单词数量，默认为配置中的 `DEFAULT_RECOMMENDATION_COUNT`
- `goal_id`: 指定学习目标ID，如果不指定则使用用户当前活跃目标
- `difficulty_preference`: 难度偏好，可选值：'easy', 'medium', 'hard', 'adaptive'

**返回值：**
```python
{
    'words': [Word对象列表],
    'recommendation_reasons': [推荐理由列表],
    'confidence_score': 0.85,  # 推荐置信度 (0-1)
    'strategy_used': 'mixed',   # 使用的推荐策略
    'user_profile': {           # 用户学习档案摘要
        'ability_level': 6.5,
        'learning_style': 'visual',
        'preferred_difficulty': 'medium'
    }
}
```

**使用示例：**
```python
# 获取10个个性化推荐单词
result = service.get_personalized_recommendations(count=10)
words = result['words']
confidence = result['confidence_score']

# 为特定学习目标推荐
result = service.get_personalized_recommendations(
    count=15, 
    goal_id=123,
    difficulty_preference='hard'
)
```

### 2. 复习推荐

基于遗忘曲线和学习记录推荐需要复习的单词。

**方法签名：**
```python
get_review_recommendations(
    count: Optional[int] = None,
    urgency_level: str = 'all'
) -> Dict[str, Any]
```

**参数说明：**
- `count`: 推荐复习单词数量
- `urgency_level`: 紧急程度，可选值：'urgent', 'important', 'normal', 'all'

**返回值：**
```python
{
    'words': [Word对象列表],
    'priorities': [0.9, 0.7, 0.5],  # 每个单词的复习优先级
    'review_reasons': [             # 复习原因
        'forgetting_risk_high',
        'long_time_no_review',
        'error_rate_increasing'
    ],
    'urgency_distribution': {       # 紧急程度分布
        'urgent': 3,
        'important': 2,
        'normal': 5
    },
    'estimated_review_time': 15     # 预估复习时间（分钟）
}
```

**使用示例：**
```python
# 获取紧急复习单词
result = service.get_review_recommendations(
    count=5, 
    urgency_level='urgent'
)

# 获取所有需要复习的单词
result = service.get_review_recommendations(count=20)
```

### 3. 自适应难度推荐

根据用户当前能力水平动态调整推荐单词的难度。

**方法签名：**
```python
get_adaptive_difficulty_recommendations(
    count: Optional[int] = None,
    target_success_rate: float = 0.75
) -> Dict[str, Any]
```

**参数说明：**
- `count`: 推荐单词数量
- `target_success_rate`: 目标成功率，用于调整难度

**返回值：**
```python
{
    'words': [Word对象列表],
    'difficulty_analysis': {
        'user_current_level': 6.2,
        'recommended_range': [5.5, 7.0],
        'difficulty_progression': 'gradual'
    },
    'user_ability': {
        'level': 6.2,
        'confidence': 0.78,
        'grade_range': [5, 8],
        'strengths': ['vocabulary', 'reading'],
        'weaknesses': ['listening', 'speaking']
    },
    'adaptation_strategy': 'zone_of_proximal_development'
}
```

**使用示例：**
```python
# 获取适应性难度推荐
result = service.get_adaptive_difficulty_recommendations(
    count=12,
    target_success_rate=0.8
)
```

### 4. 弱项针对性推荐

分析用户学习弱点，推荐针对性的单词进行强化练习。

**方法签名：**
```python
get_weakness_focused_recommendations(
    count: Optional[int] = None,
    focus_areas: Optional[List[str]] = None
) -> Dict[str, Any]
```

**参数说明：**
- `count`: 推荐单词数量
- `focus_areas`: 指定关注的弱项领域，如 ['spelling', 'pronunciation']

**返回值：**
```python
{
    'words': [Word对象列表],
    'weakness_analysis': {
        'identified_weaknesses': [
            {
                'area': 'spelling',
                'severity': 0.7,
                'affected_words': 15
            },
            {
                'area': 'pronunciation',
                'severity': 0.5,
                'affected_words': 8
            }
        ],
        'improvement_potential': 0.6
    },
    'improvement_suggestions': [
        '增加拼写练习频率',
        '使用音标学习工具',
        '进行发音对比练习'
    ],
    'focus_distribution': {         # 推荐单词的弱项分布
        'spelling': 6,
        'pronunciation': 4
    }
}
```

**使用示例：**
```python
# 获取弱项针对性推荐
result = service.get_weakness_focused_recommendations(
    count=8,
    focus_areas=['spelling', 'grammar']
)
```

### 5. 用户学习档案查询

获取用户的详细学习档案和能力分析。

**方法签名：**
```python
get_user_learning_profile() -> Dict[str, Any]
```

**返回值：**
```python
{
    'basic_stats': {
        'total_attempts': 1250,
        'accuracy_rate': 0.78,
        'avg_response_time': 2500,
        'learning_days': 45,
        'words_learned': 320
    },
    'ability_assessment': {
        'overall_level': 6.5,
        'confidence': 0.82,
        'grade_equivalent': '初二',
        'percentile': 75
    },
    'learning_patterns': {
        'preferred_time': '19:00-21:00',
        'session_duration': 25,
        'consistency_score': 0.85,
        'learning_style': 'visual'
    },
    'strengths_weaknesses': {
        'strengths': ['vocabulary', 'reading'],
        'weaknesses': ['listening', 'pronunciation'],
        'improvement_areas': ['grammar', 'writing']
    },
    'recommendations': {
        'daily_target': 15,
        'session_length': 20,
        'difficulty_level': 'medium-hard',
        'focus_areas': ['grammar', 'listening']
    }
}
```

**使用示例：**
```python
# 获取用户学习档案
profile = service.get_user_learning_profile()
ability_level = profile['ability_assessment']['overall_level']
weaknesses = profile['strengths_weaknesses']['weaknesses']
```

## REST API 端点

### 基础URL
```
/api/teaching/recommendations/
```

### 端点列表

| 端点 | 方法 | 描述 |
|------|------|------|
| `/personalized/` | GET | 获取个性化推荐 |
| `/review/` | GET | 获取复习推荐 |
| `/adaptive-difficulty/` | GET | 获取自适应难度推荐 |
| `/weakness-focused/` | GET | 获取弱项针对性推荐 |
| `/user-profile/` | GET | 获取用户学习档案 |
| `/clear-cache/` | POST | 清除推荐缓存 |

### 请求参数

所有GET请求支持以下通用参数：
- `count`: 推荐数量（整数，1-50）
- `goal_id`: 学习目标ID（可选）
- `format`: 响应格式（json/xml，默认json）

### 响应格式

**成功响应：**
```json
{
    "status": "success",
    "data": {
        "words": [...],
        "confidence_score": 0.85,
        "...": "..."
    },
    "meta": {
        "count": 10,
        "cache_hit": true,
        "processing_time": 0.15
    }
}
```

**错误响应：**
```json
{
    "status": "error",
    "error": {
        "code": "INVALID_PARAMETER",
        "message": "推荐数量必须在1-50之间",
        "details": {
            "parameter": "count",
            "value": 100,
            "allowed_range": [1, 50]
        }
    }
}
```

### 使用示例

**JavaScript/Ajax：**
```javascript
// 获取个性化推荐
fetch('/api/teaching/recommendations/personalized/?count=10&goal_id=123')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const words = data.data.words;
            const confidence = data.data.confidence_score;
            // 处理推荐结果
        }
    });

// 获取复习推荐
fetch('/api/teaching/recommendations/review/?count=5&urgency_level=urgent')
    .then(response => response.json())
    .then(data => {
        const reviewWords = data.data.words;
        const priorities = data.data.priorities;
        // 处理复习推荐
    });
```

**Python/requests：**
```python
import requests

# 获取个性化推荐
response = requests.get(
    'http://localhost:8000/api/teaching/recommendations/personalized/',
    params={'count': 10, 'goal_id': 123},
    headers={'Authorization': 'Bearer your-token'}
)

if response.status_code == 200:
    data = response.json()
    words = data['data']['words']
    confidence = data['data']['confidence_score']
```

## 缓存机制

### 缓存策略

推荐服务使用多层缓存策略提高性能：

1. **结果缓存**：推荐结果缓存5分钟
2. **用户档案缓存**：用户学习档案缓存15分钟
3. **候选词缓存**：候选单词列表缓存30分钟

### 缓存键格式

```
word_recommendation:{user_id}:{recommendation_type}:{param1}_{value1}:{param2}_{value2}
```

### 缓存清除

```python
# 清除特定用户的所有推荐缓存
service.clear_user_cache()

# 清除特定类型的缓存
service.clear_cache('personalized')

# 通过API清除缓存
POST /api/teaching/recommendations/clear-cache/
```

## 性能优化

### 批处理

对于大量推荐请求，支持批处理模式：

```python
# 批量获取多个用户的推荐
users = [user1, user2, user3]
results = SmartWordRecommendationService.batch_recommendations(
    users, 
    recommendation_type='personalized',
    count=10
)
```

### 异步处理

支持异步推荐计算：

```python
from apps.teaching.tasks import generate_recommendations_async

# 异步生成推荐
task = generate_recommendations_async.delay(
    user_id=user.id,
    recommendation_type='personalized',
    count=20
)

# 获取结果
result = task.get(timeout=30)
```

## 错误处理

### 常见错误码

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| `INVALID_PARAMETER` | 参数无效 | 检查参数类型和范围 |
| `USER_NOT_FOUND` | 用户不存在 | 验证用户ID |
| `INSUFFICIENT_DATA` | 数据不足 | 用户需要更多学习记录 |
| `GOAL_NOT_FOUND` | 学习目标不存在 | 检查目标ID或使用默认目标 |
| `CACHE_ERROR` | 缓存错误 | 重试或清除缓存 |
| `ALGORITHM_ERROR` | 算法计算错误 | 联系技术支持 |

### 降级策略

当推荐算法出现问题时，系统会自动降级：

1. **算法降级**：从复杂算法降级到简单随机推荐
2. **数据降级**：使用历史缓存数据
3. **功能降级**：返回基础推荐而非个性化推荐

## 监控和分析

### 性能指标

- 推荐响应时间
- 缓存命中率
- 推荐准确率
- 用户接受率

### 日志记录

```python
import logging

logger = logging.getLogger('recommendation_service')

# 记录推荐请求
logger.info(f'Recommendation request: user={user.id}, type=personalized, count=10')

# 记录性能数据
logger.info(f'Recommendation generated: time={processing_time}ms, confidence={confidence}')
```

### A/B测试支持

```python
# 启用A/B测试
service = SmartWordRecommendationService(
    user, 
    experiment_group='algorithm_v2'
)

result = service.get_personalized_recommendations(count=10)
```

## 最佳实践

### 1. 推荐数量选择

- **个性化推荐**：10-20个单词
- **复习推荐**：5-15个单词
- **弱项推荐**：5-10个单词

### 2. 缓存使用

- 频繁请求的用户启用缓存
- 定期清除过期缓存
- 用户数据更新后清除相关缓存

### 3. 错误处理

- 始终检查返回状态
- 实现降级策略
- 记录错误日志

### 4. 性能优化

- 使用批处理处理大量请求
- 异步处理耗时操作
- 监控性能指标

## 版本更新

### v1.0.0 (当前版本)
- 基础推荐功能
- 四种推荐策略
- 缓存机制
- REST API

### 计划功能
- 深度学习推荐算法
- 实时推荐更新
- 多语言支持
- 推荐解释功能