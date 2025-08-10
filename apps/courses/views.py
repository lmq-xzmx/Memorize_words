from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet

# 占位符视图类 - 待后续实现具体功能

class CourseIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'courses/index.html'

class CourseListView(LoginRequiredMixin, ListView):
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    
    def get_queryset(self) -> QuerySet:
        from django.contrib.auth.models import User
        return User.objects.none()

class CourseCreateView(LoginRequiredMixin, CreateView):
    template_name = 'courses/course_form.html'

class CourseDetailView(LoginRequiredMixin, DetailView):
    template_name = 'courses/course_detail.html'

class CourseUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'courses/course_form.html'

class CourseDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'courses/course_confirm_delete.html'

class LessonListView(LoginRequiredMixin, ListView):
    template_name = 'courses/lesson_list.html'
    context_object_name = 'lessons'
    
    def get_queryset(self) -> QuerySet:
        from django.contrib.auth.models import User
        return User.objects.none()

class LessonCreateView(LoginRequiredMixin, CreateView):
    template_name = 'courses/lesson_form.html'

class LessonDetailView(LoginRequiredMixin, DetailView):
    template_name = 'courses/lesson_detail.html'

class LessonUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'courses/lesson_form.html'

class LessonDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'courses/lesson_confirm_delete.html'

class ExerciseListView(LoginRequiredMixin, ListView):
    template_name = 'courses/exercise_list.html'
    context_object_name = 'exercises'
    
    def get_queryset(self) -> QuerySet:
        from django.contrib.auth.models import User
        return User.objects.none()

class ExerciseCreateView(LoginRequiredMixin, CreateView):
    template_name = 'courses/exercise_form.html'

class ExerciseDetailView(LoginRequiredMixin, DetailView):
    template_name = 'courses/exercise_detail.html'

class ExerciseUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'courses/exercise_form.html'

class ExerciseDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'courses/exercise_confirm_delete.html'

class LearningProgressView(LoginRequiredMixin, TemplateView):
    template_name = 'courses/learning_progress.html'

class UserProgressView(LoginRequiredMixin, TemplateView):
    template_name = 'courses/user_progress.html'

# AJAX视图函数
def get_lessons_ajax(request):
    return JsonResponse({'lessons': []})

def submit_exercise_ajax(request):
    return JsonResponse({'success': True})

def get_progress_ajax(request):
    return JsonResponse({'progress': 0})