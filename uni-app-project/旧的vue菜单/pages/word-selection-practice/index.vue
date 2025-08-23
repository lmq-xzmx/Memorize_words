from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # 课程相关的URL配置
    path('', views.index, name='index'),
    # path('<int:course_id>/', views.course_detail, name='course_detail'),
]