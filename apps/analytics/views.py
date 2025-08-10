from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

# 占位符视图类 - 待后续实现具体功能

class AnalyticsIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/index.html'

class LearningAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/learning_analytics.html'

class ProgressAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/progress_analytics.html'

class PerformanceAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/performance_analytics.html'

class UserAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/user_analytics.html'

class EngagementAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/engagement_analytics.html'

class CourseAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/course_analytics.html'

class ContentAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/content_analytics.html'

class ReportListView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/report_list.html'

class GenerateReportView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/generate_report.html'

class ReportDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/report_detail.html'

# AJAX视图函数
def get_chart_data_ajax(request):
    return JsonResponse({'data': []})

def export_data_ajax(request):
    return JsonResponse({'success': True})