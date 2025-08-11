from django.urls import path
from . import views

app_name = 'teaching'

urlpatterns = [
    # 页面路由
    path('', views.index, name='index'),
    path('dashboard/', views.learning_dashboard, name='dashboard'),
    path('goals/', views.goals_list, name='goals_list'),
    path('search-words/', views.search_words, name='search_words'),
]
