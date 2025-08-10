from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from .models import LearningGoal, GoalWord, LearningSession, WordLearningRecord, LearningPlan
from apps.words.models import Word
from apps.accounts.models import CustomUser
import json

@login_required
def index(request):
    """教学中心首页"""
    user = request.user
    active_goals = LearningGoal.objects.filter(user=user, is_active=True)
    
    context = {
        'active_goals': active_goals,
        'total_goals': active_goals.count(),
    }
    return render(request, 'teaching/index.html', context)

@login_required
def goals_list(request):
    """学习目标列表"""
    user = request.user
    goals = LearningGoal.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'goals': goals,
    }
    return render(request, 'teaching/goals_list.html', context)

@login_required
def learning_dashboard(request):
    """学习中看板"""
    user = request.user
    
    # 获取用户的学习目标
    goals = LearningGoal.objects.filter(user=user, is_active=True)
    has_goal = goals.exists()
    
    if has_goal:
        goal = goals.first()  # 暂时只显示第一个目标
        progress_stats = goal.get_progress_stats() if goal else {}
    else:
        goal = None
        progress_stats = {}
    
    context = {
        'goal': goal,
        'has_goal': has_goal,
        'progress_stats': progress_stats,
    }
    return render(request, 'teaching/learning_dashboard.html', context)

# vocabulary_management 功能已移除，现在通过 LearningGoal 和 GoalWord 实现

# add_word_to_list 功能已移除

# remove_word_from_list 功能已移除

# move_word_between_lists 功能已移除

@login_required
def search_words(request):
    """搜索单词"""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'words': []})
    
    words = Word.objects.filter(
        Q(word__icontains=query) | 
        Q(definition__icontains=query)
    ).values('id', 'word', 'definition', 'phonetic')[:20]
    
    return JsonResponse({'words': list(words)})