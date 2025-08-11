from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    """课程首页"""
    return HttpResponse("Courses app is working!")