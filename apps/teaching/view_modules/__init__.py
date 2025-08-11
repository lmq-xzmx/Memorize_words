# 从上级目录的views.py导入所有视图函数
from ..views import (
    index,
    goals_list,
    learning_dashboard,
    search_words,
)

# 从recommendation_views导入推荐相关视图
from .recommendation_views import *

# 确保所有视图函数都可以通过views模块访问
__all__ = [
    'index',
    'goals_list', 
    'learning_dashboard',
    'search_words',
]