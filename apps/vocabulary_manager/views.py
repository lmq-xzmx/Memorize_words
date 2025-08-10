from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import date, timedelta
from .models import LearningGoal, LearningPlan, DailyStudyRecord
from apps.words.models import VocabularyList, WordSet, WordGradeLevel


@login_required
def dashboard(request):
    """生词率管理器仪表板"""
    user = request.user
    
    # 获取当前学习目标
    current_goal = LearningGoal.objects.filter(
        user=user, is_current=True
    ).first()
    
    # 获取活跃的学习计划
    active_plans = LearningPlan.objects.filter(
        user=user, status='active'
    ).select_related('learning_goal')
    
    # 获取最近7天的学习记录
    recent_records = DailyStudyRecord.objects.filter(
        user=user,
        study_date__gte=date.today() - timedelta(days=7)
    ).select_related('learning_plan').order_by('-study_date')
    
    # 计算当前目标的总单词数和已学单词数
    if current_goal:
        current_goal.total_words = current_goal.get_word_count()
        # 这里需要根据实际的学习进度来计算已学单词数
        # 暂时使用模型中的learned_words字段
    
    context = {
        'current_goal': current_goal,
        'active_plans': active_plans,
        'recent_records': recent_records,
    }
    
    return render(request, 'vocabulary_manager/dashboard.html', context)


@login_required
def learning_goals(request):
    """学习目标列表"""
    goals = LearningGoal.objects.filter(
        user=request.user
    ).select_related(
        'vocabulary_list', 'word_set', 'grade_level'
    ).order_by('-is_current', '-created_at')
    
    context = {
        'goals': goals,
    }
    
    return render(request, 'vocabulary_manager/learning_goals.html', context)


@login_required
def create_learning_goal(request):
    """创建学习目标"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        goal_type = request.POST.get('goal_type')
        is_current = request.POST.get('is_current') == 'on'
        
        # 根据目标类型获取相应的对象
        vocabulary_list = None
        word_set = None
        grade_level = None
        
        if goal_type == 'vocabulary_list':
            vocabulary_list_id = request.POST.get('vocabulary_list')
            if vocabulary_list_id:
                vocabulary_list = get_object_or_404(VocabularyList, id=vocabulary_list_id)
        elif goal_type == 'word_set':
            word_set_id = request.POST.get('word_set')
            if word_set_id:
                word_set = get_object_or_404(WordSet, id=word_set_id)
        elif goal_type == 'grade_level':
            grade_level_id = request.POST.get('grade_level')
            if grade_level_id:
                grade_level = get_object_or_404(WordGradeLevel, id=grade_level_id)
        
        # 创建学习目标
        goal = LearningGoal.objects.create(
            user=request.user,
            name=name,
            description=description,
            goal_type=goal_type,
            vocabulary_list=vocabulary_list,
            word_set=word_set,
            grade_level=grade_level,
            is_current=is_current
        )
        
        messages.success(request, f'学习目标 "{goal.name}" 创建成功！')
        return redirect('vocabulary_manager:learning_goals')
    
    # GET请求，显示创建表单
    vocabulary_lists = VocabularyList.objects.filter(is_active=True)
    word_sets = WordSet.objects.filter(is_public=True)
    grade_levels = WordGradeLevel.objects.select_related('grader')
    
    context = {
        'vocabulary_lists': vocabulary_lists,
        'word_sets': word_sets,
        'grade_levels': grade_levels,
    }
    
    return render(request, 'vocabulary_manager/create_goal.html', context)


@login_required
def set_current_goal(request, goal_id):
    """设置当前学习目标"""
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)
    
    # 取消其他目标的当前状态
    LearningGoal.objects.filter(
        user=request.user, is_current=True
    ).update(is_current=False)
    
    # 设置当前目标
    goal.is_current = True
    goal.save()
    
    messages.success(request, f'已将 "{goal.name}" 设置为当前学习目标')
    return redirect('vocabulary_manager:learning_goals')


@login_required
def learning_plans(request):
    """学习计划列表"""
    plans = LearningPlan.objects.filter(
        user=request.user
    ).select_related('learning_goal').order_by('-created_at')
    
    context = {
        'plans': plans,
    }
    
    return render(request, 'vocabulary_manager/learning_plans.html', context)


@login_required
def create_learning_plan(request):
    """创建学习计划"""
    if request.method == 'POST':
        name = request.POST.get('name')
        learning_goal_id = request.POST.get('learning_goal')
        plan_mode = request.POST.get('plan_mode')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        learning_goal = get_object_or_404(
            LearningGoal, id=learning_goal_id, user=request.user
        )
        
        # 创建学习计划
        plan = LearningPlan.objects.create(
            user=request.user,
            learning_goal=learning_goal,
            name=name,
            plan_mode=plan_mode,
            start_date=start_date,
            end_date=end_date
        )
        
        messages.success(request, f'学习计划 "{plan.name}" 创建成功！')
        return redirect('vocabulary_manager:learning_plans')
    
    # GET请求，显示创建表单
    learning_goals = LearningGoal.objects.filter(user=request.user)
    
    context = {
        'learning_goals': learning_goals,
    }
    
    return render(request, 'vocabulary_manager/create_plan.html', context)


@login_required
def plan_detail(request, plan_id):
    """学习计划详情"""
    plan = get_object_or_404(
        LearningPlan, id=plan_id, user=request.user
    )
    
    # 获取最近30天的学习记录
    records = DailyStudyRecord.objects.filter(
        learning_plan=plan,
        study_date__gte=date.today() - timedelta(days=30)
    ).order_by('-study_date')
    
    context = {
        'plan': plan,
        'records': records,
    }
    
    return render(request, 'vocabulary_manager/plan_detail.html', context)


@login_required
@require_http_methods(["POST"])
def update_daily_progress(request):
    """更新每日学习进度"""
    plan_id = request.POST.get('plan_id')
    completed_words = int(request.POST.get('completed_words', 0))
    study_duration = request.POST.get('study_duration')  # 格式: HH:MM:SS
    
    plan = get_object_or_404(
        LearningPlan, id=plan_id, user=request.user
    )
    
    # 获取或创建今日学习记录
    record, created = DailyStudyRecord.objects.get_or_create(
        user=request.user,
        learning_plan=plan,
        study_date=date.today(),
        defaults={
            'target_words': plan.daily_target,
            'completed_words': completed_words,
        }
    )
    
    if not created:
        record.completed_words = completed_words
    
    # 处理学习时长
    if study_duration:
        try:
            hours, minutes, seconds = map(int, study_duration.split(':'))
            record.study_duration = timedelta(
                hours=hours, minutes=minutes, seconds=seconds
            )
        except ValueError:
            pass
    
    record.save()
    
    # 更新学习目标进度
    plan.learning_goal.update_progress()
    
    # 如果是动态模式，更新每日目标
    if plan.plan_mode in ['daily_progress', 'workday', 'weekend']:
        plan.update_daily_target()
    
    return JsonResponse({
        'success': True,
        'message': '学习进度更新成功',
        'completion_rate': record.completion_rate,
        'is_completed': record.is_completed,
        'new_daily_target': plan.daily_target,
    })


@login_required
def study_statistics(request):
    """学习统计"""
    user = request.user
    
    # 获取统计数据
    total_goals = LearningGoal.objects.filter(user=user).count()
    total_plans = LearningPlan.objects.filter(user=user).count()
    active_plans = LearningPlan.objects.filter(user=user, status='active').count()
    
    # 最近30天的学习记录
    recent_records = DailyStudyRecord.objects.filter(
        user=user,
        study_date__gte=date.today() - timedelta(days=30)
    ).order_by('study_date')
    
    # 计算统计指标
    total_study_days = recent_records.count()
    total_completed_words = sum(record.completed_words for record in recent_records)
    avg_daily_words = total_completed_words / max(1, total_study_days)
    
    # 连续学习天数
    consecutive_days = 0
    current_date = date.today()
    while True:
        if recent_records.filter(study_date=current_date).exists():
            consecutive_days += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    context = {
        'total_goals': total_goals,
        'total_plans': total_plans,
        'active_plans': active_plans,
        'total_study_days': total_study_days,
        'total_completed_words': total_completed_words,
        'avg_daily_words': round(avg_daily_words, 1),
        'consecutive_days': consecutive_days,
        'recent_records': recent_records,
    }
    
    return render(request, 'vocabulary_manager/statistics.html', context)


@login_required
def learning_kanban(request):
    """学习中（看板）视图"""
    user = request.user
    
    # 获取当前学习目标
    current_goal = LearningGoal.objects.filter(
        user=user, is_current=True
    ).first()
    
    if not current_goal:
        messages.warning(request, '请先设置当前学习目标')
        return redirect('vocabulary_manager:learning_goals')
    
    # 获取该目标下的所有单词
    words = current_goal.get_words()
    
    # 获取单词学习进度
    from .models import WordLearningProgress
    progress_records = WordLearningProgress.objects.filter(
        user=user,
        learning_goal=current_goal
    ).select_related('word')
    
    # 创建进度字典
    progress_dict = {record.word_id: record for record in progress_records}
    
    # 统计看板数据
    kanban_data = {
        'review_1': 0,  # 第1次复习
        'review_2': 0,  # 第2次复习
        'review_3': 0,  # 第3次复习
        'review_4': 0,  # 第4次复习
        'review_5': 0,  # 第5次复习
        'review_6': 0,  # 第6次复习
        'mastered': 0,  # 已掌握
        'forgotten': 0,  # 已遗忘
        'remaining': 0,  # 剩余待学习
    }
    
    # 统计各状态的单词数量
    for word in words:
        progress = progress_dict.get(word.id)
        if progress:
            if progress.is_mastered:
                kanban_data['mastered'] += 1
            elif progress.is_forgotten:
                kanban_data['forgotten'] += 1
            elif progress.review_count > 0:
                review_key = f'review_{min(progress.review_count, 6)}'
                kanban_data[review_key] += 1
            else:
                kanban_data['remaining'] += 1
        else:
            kanban_data['remaining'] += 1
    
    # 计算总单词数
    total_words = len(words)
    
    context = {
        'current_goal': current_goal,
        'kanban_data': kanban_data,
        'total_words': total_words,
        'progress_records': progress_records,
    }
    
    return render(request, 'vocabulary_manager/learning_kanban.html', context)


@login_required
@require_http_methods(["POST"])
def update_word_progress(request):
    """更新单词学习进度"""
    user = request.user
    word_id = request.POST.get('word_id')
    action = request.POST.get('action')  # 'review', 'master', 'forget', 'reset'
    
    if not word_id:
        return JsonResponse({'success': False, 'error': '缺少单词ID'})
    
    # 获取当前学习目标
    current_goal = LearningGoal.objects.filter(
        user=user, is_current=True
    ).first()
    
    if not current_goal:
        return JsonResponse({'success': False, 'error': '请先设置当前学习目标'})
    
    # 获取或创建单词学习进度
    from .models import WordLearningProgress
    from apps.words.models import Word
    
    word = get_object_or_404(Word, id=word_id)
    progress, created = WordLearningProgress.objects.get_or_create(
        user=user,
        learning_goal=current_goal,
        word=word,
        defaults={'review_count': 0}
    )
    
    # 根据操作更新进度
    if action == 'review':
        progress.add_review()
        message = f'单词 "{word.word}" 复习次数更新为 {progress.review_count} 次'
    elif action == 'master':
        progress.is_mastered = True
        progress.mastered_date = timezone.now()
        progress.save()
        message = f'单词 "{word.word}" 标记为已掌握'
    elif action == 'forget':
        progress.mark_as_forgotten()
        message = f'单词 "{word.word}" 标记为已遗忘'
    elif action == 'reset':
        progress.reset_progress()
        message = f'单词 "{word.word}" 学习进度已重置'
    else:
        return JsonResponse({'success': False, 'error': '无效的操作'})
    
    # 重新计算看板数据
    kanban_data = calculate_kanban_data(user, current_goal)
    
    return JsonResponse({
        'success': True,
        'message': message,
        'kanban_data': kanban_data,
        'progress': {
            'review_count': progress.review_count,
            'is_mastered': progress.is_mastered,
            'is_forgotten': progress.is_forgotten,
            'status': progress.status,
            'status_display': progress.status_display,
        }
    })


def calculate_kanban_data(user, learning_goal):
    """计算看板数据"""
    from .models import WordLearningProgress
    
    # 获取该目标下的所有单词
    words = learning_goal.get_words()
    
    # 获取单词学习进度
    progress_records = WordLearningProgress.objects.filter(
        user=user,
        learning_goal=learning_goal
    ).select_related('word')
    
    # 创建进度字典
    progress_dict = {record.word_id: record for record in progress_records}
    
    # 统计看板数据
    kanban_data = {
        'review_1': 0,
        'review_2': 0,
        'review_3': 0,
        'review_4': 0,
        'review_5': 0,
        'review_6': 0,
        'mastered': 0,
        'forgotten': 0,
        'remaining': 0,
    }
    
    # 统计各状态的单词数量
    for word in words:
        progress = progress_dict.get(word.id)
        if progress:
            if progress.is_mastered:
                kanban_data['mastered'] += 1
            elif progress.is_forgotten:
                kanban_data['forgotten'] += 1
            elif progress.review_count > 0:
                review_key = f'review_{min(progress.review_count, 6)}'
                kanban_data[review_key] += 1
            else:
                kanban_data['remaining'] += 1
        else:
            kanban_data['remaining'] += 1
    
    return kanban_data
