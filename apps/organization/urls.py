from django.urls import path
from . import views

app_name = 'organization'

urlpatterns = [
    # 组织管理主页
    path('', views.OrganizationIndexView.as_view(), name='index'),
    
    # 学校管理
    path('schools/', views.SchoolListView.as_view(), name='school_list'),
    path('schools/create/', views.SchoolCreateView.as_view(), name='school_create'),
    path('schools/<int:pk>/', views.SchoolDetailView.as_view(), name='school_detail'),
    path('schools/<int:pk>/edit/', views.SchoolUpdateView.as_view(), name='school_update'),
    path('schools/<int:pk>/delete/', views.SchoolDeleteView.as_view(), name='school_delete'),
    
    # 班级管理
    path('classes/', views.ClassListView.as_view(), name='class_list'),
    path('classes/create/', views.ClassCreateView.as_view(), name='class_create'),
    path('classes/<int:pk>/', views.ClassDetailView.as_view(), name='class_detail'),
    path('classes/<int:pk>/edit/', views.ClassUpdateView.as_view(), name='class_update'),
    path('classes/<int:pk>/delete/', views.ClassDeleteView.as_view(), name='class_delete'),
    
    # 学生管理
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_update'),
    
    # 教师管理
    path('teachers/', views.TeacherListView.as_view(), name='teacher_list'),
    path('teachers/<int:pk>/', views.TeacherDetailView.as_view(), name='teacher_detail'),
    path('teachers/<int:pk>/edit/', views.TeacherUpdateView.as_view(), name='teacher_update'),
    
    # AJAX接口
    path('ajax/get-classes/', views.get_classes_ajax, name='get_classes_ajax'),
    path('ajax/get-students/', views.get_students_ajax, name='get_students_ajax'),
    path('ajax/assign-student/', views.assign_student_ajax, name='assign_student_ajax'),
]