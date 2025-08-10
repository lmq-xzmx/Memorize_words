from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # 课程管理主页
    path('', views.CourseIndexView.as_view(), name='index'),
    
    # 课程管理
    path('list/', views.CourseListView.as_view(), name='course_list'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_update'),
    path('<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    
    # 课程内容管理
    path('<int:course_id>/lessons/', views.LessonListView.as_view(), name='lesson_list'),
    path('<int:course_id>/lessons/create/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('lessons/<int:pk>/edit/', views.LessonUpdateView.as_view(), name='lesson_update'),
    path('lessons/<int:pk>/delete/', views.LessonDeleteView.as_view(), name='lesson_delete'),
    
    # 练习管理
    path('lessons/<int:lesson_id>/exercises/', views.ExerciseListView.as_view(), name='exercise_list'),
    path('lessons/<int:lesson_id>/exercises/create/', views.ExerciseCreateView.as_view(), name='exercise_create'),
    path('exercises/<int:pk>/', views.ExerciseDetailView.as_view(), name='exercise_detail'),
    path('exercises/<int:pk>/edit/', views.ExerciseUpdateView.as_view(), name='exercise_update'),
    path('exercises/<int:pk>/delete/', views.ExerciseDeleteView.as_view(), name='exercise_delete'),
    
    # 学习记录
    path('progress/', views.LearningProgressView.as_view(), name='learning_progress'),
    path('progress/<int:user_id>/', views.UserProgressView.as_view(), name='user_progress'),
    
    # AJAX接口
    path('ajax/get-lessons/', views.get_lessons_ajax, name='get_lessons_ajax'),
    path('ajax/submit-exercise/', views.submit_exercise_ajax, name='submit_exercise_ajax'),
    path('ajax/get-progress/', views.get_progress_ajax, name='get_progress_ajax'),
]