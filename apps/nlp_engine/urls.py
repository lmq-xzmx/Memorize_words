"""
NLP Engine URLs
"""

from django.urls import path
from . import views

app_name = 'nlp_engine'

urlpatterns = [
    path('status/', views.nlp_status, name='status'),
    path('analyze/', views.analyze_text, name='analyze_text'),
    path('tokenize/', views.tokenize_text, name='tokenize'),
    path('pos-tag/', views.pos_tag_text, name='pos_tag'),
]