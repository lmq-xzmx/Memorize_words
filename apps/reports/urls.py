from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # 报告仪表板
    path('', views.report_dashboard, name='dashboard'),
    path('dashboard/', views.report_dashboard, name='dashboard'),
    
    # API接口
    path('api/upload/', views.upload_data, name='upload_data'),
    path('api/generate/', views.generate_report, name='generate_report'),
    path('api/export/', views.export_report, name='export_report'),
]