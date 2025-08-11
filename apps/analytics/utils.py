from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from scipy import stats
from .models import (
    UserEngagementMetrics, UserRetentionData, ABTestExperiment, 
    ABTestParticipant, UserBehaviorPattern, GameElementEffectiveness
)


class EngagementAnalyzer:
    """用户粘性分析工具类"""
    
    @staticmethod
    def calculate_daily_active_users(start_date, end_date):
        """计算日活跃用户数"""
        return UserEngagementMetrics.objects.filter(
            date__range=[start_date, end_date],
            session_count__gt=0
        ).values('date').annotate(
            dau=Count('user', distinct=True)
        ).order_by('date')
    
    @staticmethod
    def calculate_retention_rates(cohort_date, periods=[1, 3, 7, 30]):
        """计算留存率"""
        # 获取队列用户
        cohort_users = UserRetentionData.objects.filter(
            registration_date=cohort_date
        ).values_list('user_id', flat=True)
        
        if not cohort_users:
            return {f'day{p}_retention': 0 for p in periods}
        
        cohort_size = len(cohort_users)
        retention_data = {}
        
        for period in periods:
            target_date = cohort_date + timedelta(days=period)
            
            # 计算在目标日期活跃的用户数
            active_users = UserEngagementMetrics.objects.filter(
                user_id__in=cohort_users,
                date=target_date,
                session_count__gt=0
            ).count()
            
            retention_rate = (active_users / cohort_size) * 100 if cohort_size > 0 else 0
            retention_data[f'day{period}_retention'] = round(retention_rate, 2)
        
        return retention_data
    
    @staticmethod
    def analyze_user_behavior_patterns(user_id, start_date, end_date):
        """分析用户行为模式"""
        metrics = UserEngagementMetrics.objects.filter(
            user_id=user_id,
            date__range=[start_date, end_date]
        )
        
        if not metrics.exists():
            return None
        
        # 计算学习时间偏好
        time_preferences = defaultdict(int)
        total_sessions = 0
        
        for metric in metrics:
            if metric.peak_activity_hour:
                if 6 <= metric.peak_activity_hour < 12:
                    time_preferences['morning'] += metric.session_count
                elif 12 <= metric.peak_activity_hour < 18:
                    time_preferences['afternoon'] += metric.session_count
                elif 18 <= metric.peak_activity_hour < 24:
                    time_preferences['evening'] += metric.session_count
                else:
                    time_preferences['night'] += metric.session_count
                total_sessions += metric.session_count
        
        # 转换为百分比
        if total_sessions > 0:
            for key in time_preferences:
                time_preferences[key] = round((time_preferences[key] / total_sessions) * 100, 2)
        
        # 计算学习一致性
        daily_sessions = [m.session_count for m in metrics]
        consistency_score = 100 - (np.std(daily_sessions) / np.mean(daily_sessions) * 100) if daily_sessions else 0
        
        # 计算平均指标
        avg_metrics = metrics.aggregate(
            avg_session_duration=Avg('avg_session_duration'),
            avg_words_per_session=Avg('words_learned_count'),
            avg_accuracy=Avg('accuracy_rate')
        )
        
        return {
            'time_preferences': dict(time_preferences),
            'consistency_score': max(0, min(100, consistency_score)),
            'avg_session_duration': avg_metrics['avg_session_duration'] or 0,
            'avg_words_per_session': avg_metrics['avg_words_per_session'] or 0,
            'avg_accuracy': avg_metrics['avg_accuracy'] or 0,
            'total_study_days': metrics.count(),
            'total_sessions': total_sessions
        }
    
    @staticmethod
    def calculate_engagement_score(user_id, date_range_days=30):
        """计算用户粘性评分"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=date_range_days)
        
        metrics = UserEngagementMetrics.objects.filter(
            user_id=user_id,
            date__range=[start_date, end_date]
        )
        
        if not metrics.exists():
            return 0
        
        # 活跃天数权重 (40%)
        active_days = metrics.filter(session_count__gt=0).count()
        activity_score = (active_days / date_range_days) * 40
        
        # 学习时长权重 (30%)
        avg_duration = metrics.aggregate(avg=Avg('avg_session_duration'))['avg'] or 0
        duration_score = min(avg_duration / 1800, 1) * 30  # 30分钟为满分
        
        # 学习效果权重 (20%)
        avg_accuracy = metrics.aggregate(avg=Avg('accuracy_rate'))['avg'] or 0
        accuracy_score = avg_accuracy * 20
        
        # 连续性权重 (10%)
        consecutive_days = EngagementAnalyzer._calculate_max_consecutive_days(metrics)
        consistency_score = min(consecutive_days / 7, 1) * 10  # 7天连续为满分
        
        total_score = activity_score + duration_score + accuracy_score + consistency_score
        return min(100, max(0, total_score))
    
    @staticmethod
    def _calculate_max_consecutive_days(metrics):
        """计算最大连续学习天数"""
        dates = sorted([m.date for m in metrics if m.session_count > 0])
        if not dates:
            return 0
        
        max_consecutive = 1
        current_consecutive = 1
        
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1
        
        return max_consecutive


class GameElementAnalyzer:
    """游戏化元素效果分析工具类"""
    
    @staticmethod
    def analyze_element_effectiveness(element_type, start_date, end_date):
        """分析游戏化元素效果"""
        effectiveness_data = GameElementEffectiveness.objects.filter(
            element_type=element_type,
            date__range=[start_date, end_date]
        )
        
        if not effectiveness_data.exists():
            return {
                'element_type': element_type,
                'avg_effectiveness': 0,
                'usage_count': 0,
                'user_feedback': 0
            }
        
        avg_data = effectiveness_data.aggregate(
            avg_effectiveness=Avg('effectiveness_score'),
            total_usage=Sum('usage_count'),
            avg_feedback=Avg('user_feedback_score')
        )
        
        return {
            'element_type': element_type,
            'avg_effectiveness': round(avg_data['avg_effectiveness'] or 0, 2),
            'usage_count': avg_data['total_usage'] or 0,
            'user_feedback': round(avg_data['avg_feedback'] or 0, 2)
        }
    
    @staticmethod
    def get_top_performing_elements(start_date, end_date, limit=10):
        """获取表现最佳的游戏化元素"""
        elements = GameElementEffectiveness.objects.filter(
            date__range=[start_date, end_date]
        ).values('element_type', 'element_name').annotate(
            avg_effectiveness=Avg('effectiveness_score'),
            total_usage=Sum('usage_count'),
            avg_feedback=Avg('user_feedback_score')
        ).order_by('-avg_effectiveness')[:limit]
        
        return list(elements)
    
    @staticmethod
    def calculate_roi_by_element(element_type, start_date, end_date):
        """计算游戏化元素的投资回报率"""
        # 获取使用该元素的用户
        element_users = GameElementEffectiveness.objects.filter(
            element_type=element_type,
            date__range=[start_date, end_date]
        ).values_list('user_id', flat=True).distinct()
        
        if not element_users:
            return 0
        
        # 计算这些用户的平均粘性提升
        user_engagement_before = UserEngagementMetrics.objects.filter(
            user_id__in=element_users,
            date__lt=start_date
        ).aggregate(avg_score=Avg('engagement_score'))['avg_score'] or 0
        
        user_engagement_after = UserEngagementMetrics.objects.filter(
            user_id__in=element_users,
            date__range=[start_date, end_date]
        ).aggregate(avg_score=Avg('engagement_score'))['avg_score'] or 0
        
        improvement = user_engagement_after - user_engagement_before
        return max(0, improvement)


class ABTestAnalyzer:
    """A/B测试分析工具类"""
    
    @staticmethod
    def calculate_test_results(experiment_id):
        """计算A/B测试结果"""
        try:
            experiment = ABTestExperiment.objects.get(id=experiment_id)
        except ABTestExperiment.DoesNotExist:
            return None
        
        # 获取参与者数据
        participants = ABTestParticipant.objects.filter(experiment=experiment)
        
        control_group = participants.filter(group='control')
        test_group = participants.filter(group='test')
        
        control_size = control_group.count()
        test_size = test_group.count()
        
        if control_size == 0 or test_size == 0:
            return {
                'experiment_id': experiment_id,
                'control_group_size': control_size,
                'test_group_size': test_size,
                'conversion_rate_control': 0,
                'conversion_rate_test': 0,
                'statistical_significance': False,
                'p_value': 1.0,
                'confidence_level': 0,
                'improvement_percentage': 0
            }
        
        # 计算转化率
        control_conversions = control_group.filter(converted=True).count()
        test_conversions = test_group.filter(converted=True).count()
        
        control_rate = control_conversions / control_size
        test_rate = test_conversions / test_size
        
        # 进行统计显著性检验
        significance_result = ABTestAnalyzer._chi_square_test(
            control_conversions, control_size - control_conversions,
            test_conversions, test_size - test_conversions
        )
        
        # 计算提升百分比
        improvement = float((test_rate - control_rate) / control_rate) if control_rate > 0 else 0.0
        
        return {
            'experiment_id': experiment_id,
            'control_group_size': control_size,
            'test_group_size': test_size,
            'conversion_rate_control': control_rate,
            'conversion_rate_test': test_rate,
            'statistical_significance': significance_result['significant'],
            'p_value': significance_result['p_value'],
            'confidence_level': significance_result['confidence'],
            'improvement_percentage': improvement
        }
    
    @staticmethod
    def _chi_square_test(control_success, control_failure, test_success, test_failure):
        """卡方检验"""
        # 构建列联表
        observed = np.array([[control_success, control_failure],
                           [test_success, test_failure]])
        
        try:
            chi2, p_value, dof, expected = stats.chi2_contingency(observed)
            
            # 判断统计显著性 (p < 0.05)
            significant = p_value < 0.05
            confidence = (1 - p_value) * 100
            
            return {
                'significant': significant,
                'p_value': p_value,
                'confidence': min(99.9, confidence),
                'chi2_statistic': chi2
            }
        except Exception:
            return {
                'significant': False,
                'p_value': 1.0,
                'confidence': 0,
                'chi2_statistic': 0
            }
    
    @staticmethod
    def get_experiment_recommendations(experiment_id):
        """获取实验建议"""
        results = ABTestAnalyzer.calculate_test_results(experiment_id)
        if not results:
            return []
        
        recommendations = []
        
        # 基于结果给出建议
        if results['statistical_significance']:
            if results['improvement_percentage'] > 0.1:  # 10%以上提升
                recommendations.append({
                    'type': 'success',
                    'message': f"实验组表现显著优于对照组，建议全量推广该功能。提升幅度：{results['improvement_percentage']:.1%}"
                })
            elif results['improvement_percentage'] < -0.05:  # 5%以上下降
                recommendations.append({
                    'type': 'warning',
                    'message': f"实验组表现显著差于对照组，建议停止该功能。下降幅度：{abs(results['improvement_percentage']):.1%}"
                })
        else:
            recommendations.append({
                'type': 'info',
                'message': "实验结果无统计显著性，建议延长实验时间或增加样本量。"
            })
        
        # 样本量建议
        total_sample = results['control_group_size'] + results['test_group_size']
        if total_sample < 1000:
            recommendations.append({
                'type': 'warning',
                'message': f"当前样本量({total_sample})较小，建议增加到至少1000个样本以提高结果可信度。"
            })
        
        return recommendations


class PredictiveAnalyzer:
    """预测分析工具类"""
    
    @staticmethod
    def predict_user_churn_risk(user_id, days_ahead=7):
        """预测用户流失风险"""
        # 获取用户最近30天的数据
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        metrics = UserEngagementMetrics.objects.filter(
            user_id=user_id,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        if metrics.count() < 7:  # 数据不足
            return {'risk_level': 'unknown', 'risk_score': 0, 'factors': []}
        
        # 计算趋势指标
        recent_metrics = list(metrics.values(
            'session_count', 'avg_session_duration', 
            'accuracy_rate', 'engagement_score'
        ))
        
        # 计算各指标的趋势
        session_trend = PredictiveAnalyzer._calculate_trend([m['session_count'] for m in recent_metrics])
        duration_trend = PredictiveAnalyzer._calculate_trend([m['avg_session_duration'] or 0 for m in recent_metrics])
        accuracy_trend = PredictiveAnalyzer._calculate_trend([m['accuracy_rate'] or 0 for m in recent_metrics])
        engagement_trend = PredictiveAnalyzer._calculate_trend([m['engagement_score'] or 0 for m in recent_metrics])
        
        # 计算风险评分
        risk_factors = []
        risk_score = 0
        
        if float(session_trend) < -0.1:  # 会话数下降
            risk_score += 30
            risk_factors.append('学习频率下降')
        
        if float(duration_trend) < -0.1:  # 学习时长下降
            risk_score += 25
            risk_factors.append('学习时长减少')
        
        if float(accuracy_trend) < -0.05:  # 准确率下降
            risk_score += 20
            risk_factors.append('学习效果下降')
        
        if float(engagement_trend) < -0.1:  # 粘性下降
            risk_score += 25
            risk_factors.append('参与度降低')
        
        # 最近活跃度检查
        recent_activity = metrics.filter(
            date__gte=end_date - timedelta(days=3)
        ).aggregate(total_sessions=Sum('session_count'))['total_sessions'] or 0
        
        if recent_activity == 0:
            risk_score += 40
            risk_factors.append('近期无学习活动')
        
        # 确定风险等级
        if risk_score >= 70:
            risk_level = 'high'
        elif risk_score >= 40:
            risk_level = 'medium'
        elif risk_score >= 20:
            risk_level = 'low'
        else:
            risk_level = 'minimal'
        
        return {
            'risk_level': risk_level,
            'risk_score': min(100, risk_score),
            'factors': risk_factors,
            'trends': {
                'session_trend': session_trend,
                'duration_trend': duration_trend,
                'accuracy_trend': accuracy_trend,
                'engagement_trend': engagement_trend
            }
        }
    
    @staticmethod
    def _calculate_trend(values):
        """计算数值序列的趋势"""
        if len(values) < 2:
            return 0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # 去除无效值
        valid_indices = ~np.isnan(y)
        if np.sum(valid_indices) < 2:
            return 0
        
        x = x[valid_indices]
        y = y[valid_indices]
        
        # 计算线性回归斜率
        try:
            slope, _, _, _, _ = stats.linregress(x, y)
            return slope
        except Exception:
            return 0
    
    @staticmethod
    def recommend_interventions(user_id):
        """推荐干预措施"""
        churn_analysis = PredictiveAnalyzer.predict_user_churn_risk(user_id)
        behavior_pattern = EngagementAnalyzer.analyze_user_behavior_patterns(
            user_id, 
            timezone.now().date() - timedelta(days=30),
            timezone.now().date()
        )
        
        recommendations = []
        
        if churn_analysis['risk_level'] in ['high', 'medium']:
            # 高风险用户的干预建议
            if '学习频率下降' in churn_analysis['factors']:
                recommendations.append({
                    'type': 'engagement',
                    'priority': 'high',
                    'action': '发送学习提醒推送',
                    'description': '用户学习频率下降，建议增加个性化学习提醒'
                })
            
            if '学习时长减少' in churn_analysis['factors']:
                recommendations.append({
                    'type': 'motivation',
                    'priority': 'medium',
                    'action': '调整学习目标',
                    'description': '降低每日学习目标，提高完成率和成就感'
                })
            
            if '学习效果下降' in churn_analysis['factors']:
                recommendations.append({
                    'type': 'content',
                    'priority': 'high',
                    'action': '调整学习内容难度',
                    'description': '根据用户能力调整学习内容，提高学习效果'
                })
        
        # 基于行为模式的建议
        if behavior_pattern:
            if behavior_pattern['consistency_score'] < 50:
                recommendations.append({
                    'type': 'habit',
                    'priority': 'medium',
                    'action': '建立学习习惯',
                    'description': '帮助用户建立固定的学习时间和习惯'
                })
        
        return recommendations