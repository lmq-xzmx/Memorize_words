from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Word, VocabularyList
import json



@login_required
@permission_required('words.view_word', raise_exception=True)
def word_version_list(request):
    """单词版本列表"""
    # 获取筛选参数
    search_query = request.GET.get('search', '')
    
    # 构建查询 - 获取所有有多版本的单词
    queryset = Word.objects.filter(has_multiple_versions=True).order_by('word')
    
    if search_query:
        queryset = queryset.filter(word__icontains=search_query)
    
    # 分页
    paginator = Paginator(queryset, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'words/word_version_list.html', context)