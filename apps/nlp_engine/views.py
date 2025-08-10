"""
NLP Engine Views - NLP引擎视图
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json

from .services import text_analysis_service, nltk_service


@api_view(['GET'])
def nlp_status(request):
    """获取NLP引擎状态"""
    return Response({
        'nltk_available': nltk_service.is_available,
        'nltk_data_path': nltk_service._setup_nltk.__globals__.get('project_nltk_data', 'Unknown'),
        'status': 'ready' if nltk_service.is_available else 'fallback_mode'
    })


@api_view(['POST'])
def analyze_text(request):
    """分析文本API"""
    try:
        data = request.data
        text = data.get('text', '')
        options = data.get('options', {})
        
        if not text:
            return Response({
                'error': '文本内容不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 执行文本分析
        analysis_result = text_analysis_service.analyze_text(text, options)
        
        return Response({
            'success': True,
            'data': analysis_result
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def tokenize_text(request):
    """分词API"""
    try:
        data = request.data
        text = data.get('text', '')
        
        if not text:
            return Response({
                'error': '文本内容不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tokens = nltk_service.tokenize(text)
        
        return Response({
            'success': True,
            'tokens': tokens,
            'count': len(tokens)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def pos_tag_text(request):
    """词性标注API"""
    try:
        data = request.data
        text = data.get('text', '')
        words = data.get('words', [])
        
        if not text and not words:
            return Response({
                'error': '文本内容或单词列表不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not words:
            words = nltk_service.tokenize(text)
        
        pos_tags = nltk_service.pos_tag(words)
        
        # 标准化词性
        standardized_tags = [
            {
                'word': word,
                'pos': pos,
                'standardized_pos': nltk_service.standardize_pos(pos)
            }
            for word, pos in pos_tags
        ]
        
        return Response({
            'success': True,
            'pos_tags': standardized_tags,
            'count': len(standardized_tags)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)