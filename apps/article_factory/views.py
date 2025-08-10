import re
from typing import Dict, List, Any, Optional, Union
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import QuerySet, Q
from .models import Article, ParsedParagraph
from .serializers import ArticleSerializer

# 使用新的NLP引擎
from apps.nlp_engine.services import nltk_service, text_analysis_service

# 为了保持向后兼容，提供相同的接口
def word_tokenize(text: str) -> List[str]:
    return nltk_service.tokenize(text)

def pos_tag(words: List[str]) -> List[tuple]:
    return nltk_service.pos_tag(words)

NLTK_AVAILABLE = nltk_service.is_available


class ArticleViewSet(viewsets.ModelViewSet):
    """文章视图集"""
    serializer_class = ArticleSerializer
    
    def get_queryset(self) -> QuerySet:
        """获取查询集"""
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            return Article.objects.filter(user=self.request.user)
        return Article.objects.none()
    
    @action(detail=True, methods=['post'])
    def parse_article(self, request, pk=None):
        """解析文章"""
        article = self.get_object()
        
        # 获取解析选项
        options = request.data if request.data else {}
        vocabulary_source = options.get('vocabulary_source', 'default')
        variant_preference = options.get('variant_preference', 'us')
        enable_paragraph_analysis = options.get('enable_paragraph_analysis', True)
        enable_tooltips = options.get('enable_tooltips', True)
        
        # 检查是否需要生成图片
        if options and 'image' in options:
            generate_image = options.get('image', False)
        else:
            generate_image = False
        
        # 更新文章字段
        article.vocabulary_source = vocabulary_source
        article.variant_preference = variant_preference
        
        # 解析选项
        parse_options = {
            'enable_paragraph_analysis': enable_paragraph_analysis,
            'enable_tooltips': enable_tooltips,
            'generate_image': generate_image
        }
        
        # 执行解析
        try:
            parsed_content = self._parse_article(article, parse_options)
            return Response({
                'message': '文章解析成功',
                'article_id': article.pk,
                'parsed_content': parsed_content
            })
        except Exception as e:
            return Response({
                'error': f'解析失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def parse_existing_article(self, request, pk=None):
        """重新解析已存在的文章"""
        article = self.get_object()
        
        # 获取解析选项
        options = request.data if request.data else {}
        
        # 清除旧的解析数据
        article.paragraphs.all().delete()
        
        # 重新解析
        try:
            parsed_content = self._parse_article(article, options)
            return Response({
                'message': '文章重新解析成功',
                'article_id': article.pk,
                'parsed_content': parsed_content
            })
        except Exception as e:
            return Response({
                'error': f'重新解析失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _parse_article(self, article: Article, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """解析文章内容"""
        if options is None:
            options = {}
        
        # 获取用户熟词和词库
        known_words = article.get_user_known_words()
        vocab_words = article.get_vocabulary_words()
        new_words = article.get_user_new_words()
        
        # 分割段落
        paragraphs = [p.strip() for p in article.content.split('\n') if p.strip()]
        
        parsed_paragraphs = []
        total_words = 0
        vocab_words_count = 0
        known_words_count = 0
        
        # 处理每个段落
        for i, paragraph in enumerate(paragraphs):
            paragraph_type = self._detect_paragraph_type(paragraph)
            
            # 分词和词性标注
            words = word_tokenize(paragraph.lower())
            pos_tags = pos_tag(words)
            
            word_data = []
            for word, pos in pos_tags:
                if word.isalpha():  # 只处理字母单词
                    standardized_pos = self._standardize_pos(pos)
                    is_vocab = word in vocab_words
                    is_known = word in known_words
                    is_new_word = word in new_words
                    
                    word_info = {
                        'word': word,
                        'pos': standardized_pos,
                        'is_vocab': is_vocab,
                        'is_known': is_known,
                        'is_new_word': is_new_word,
                        'definition': vocab_words.get(word, {}).get('definition', '') if vocab_words else '',
                        'pronunciation': vocab_words.get(word, {}).get('pronunciation', '') if vocab_words else '',
                        'tooltip_enabled': options.get('enable_tooltips', True)
                    }
                    word_data.append(word_info)
                    
                    # 统计
                    total_words += 1
                    if is_vocab:
                        vocab_words_count += 1
                    if is_known:
                        known_words_count += 1
            
            # 生成HTML内容
            html_content = self._generate_paragraph_html(paragraph, word_data, paragraph_type, i + 1)
            
            # 创建解析段落记录
            parsed_paragraph = ParsedParagraph.objects.create(
                article=article,
                order=i + 1,
                paragraph_type=paragraph_type,
                original_text=paragraph,
                processed_text=paragraph,  # 可以在这里添加预处理逻辑
                word_data=word_data,
                html_content=html_content
            )
            
            parsed_paragraphs.append({
                'id': parsed_paragraph.pk,
                'type': paragraph_type,
                'text': paragraph,
                'word_data': word_data,
                'html': html_content
            })
        
        # 统计数据
        statistics = {
            'total_words': total_words,
            'vocab_words': vocab_words_count,
            'known_words': known_words_count,
            'vocab_coverage': round((vocab_words_count / total_words * 100), 2) if total_words > 0 else 0,
            'known_coverage': round((known_words_count / total_words * 100), 2) if total_words > 0 else 0
        }
        
        # 保存解析结果
        parsed_content = {
            'paragraphs': parsed_paragraphs,
            'statistics': statistics,
            'options': options
        }
        
        # 生成完整HTML
        html_content = self._generate_complete_html(parsed_paragraphs, statistics, options)
        
        # 段落分析结果
        paragraph_analysis = self._analyze_paragraph_structure(parsed_paragraphs) if options.get('enable_paragraph_analysis') else None
        
        # 更新文章
        article.is_parsed = True
        article.parsed_content = parsed_content
        article.html_content = html_content
        if paragraph_analysis:
            article.paragraph_analysis = paragraph_analysis
        article.save()
        
        return parsed_content
    
    def _detect_paragraph_type(self, paragraph: str) -> str:
        """检测段落类型"""
        text = paragraph.strip()
        
        # 标题检测（以#开头或全大写短句）
        if text.startswith('#') or (len(text) < 50 and text.isupper()):
            return 'title'
        
        # 列表项检测
        if re.match(r'^\s*[\-\*\+]\s+', text) or re.match(r'^\s*\d+\.\s+', text):
            return 'list_item'
        
        # 引用检测
        if text.startswith('>'):
            return 'quote'
        
        # 代码块检测
        if text.startswith('```') or text.startswith('    '):
            return 'code'
        
        # 缩进文本检测
        if text.startswith('  ') or text.startswith('\t'):
            return 'indented'
        
        return 'normal'
    
    def _standardize_pos(self, pos: str) -> str:
        """标准化词性 - 使用NLP引擎"""
        return nltk_service.standardize_pos(pos)
    
    def _generate_paragraph_html(self, paragraph: str, word_data: List[Dict[str, Any]], paragraph_type: str, paragraph_index: Optional[int] = None) -> str:
        """生成段落HTML"""
        # 根据段落类型选择标签
        tag_mapping = {
            'title': 'h3',
            'list_item': 'li',
            'quote': 'blockquote',
            'code': 'pre',
            'indented': 'div',
            'normal': 'p'
        }
        
        tag = tag_mapping.get(paragraph_type, 'p')
        css_class = f'paragraph-{paragraph_type}'
        
        # 添加段落ID属性
        paragraph_id_attr = ''
        if paragraph_index is not None:
            paragraph_id_attr = f' data-paragraph-id="{paragraph_index}"'
        
        # 构建单词映射
        word_map = {item['word']: item for item in word_data}
        
        # 替换单词为HTML
        def replace_word(match):
            word = match.group().lower()
            if word in word_map:
                word_info = word_map[word]
                classes = ['word']
                
                # 词库单词标记
                if word_info['is_vocab']:
                    classes.append('vocab-word')
                
                # 熟词标记
                if word_info['is_known']:
                    classes.append('known-word')
                
                # 词性标记
                if word_info['pos'] != 'unknown':
                    classes.append(f'pos-{word_info["pos"]}')
                
                # 生词标记（优先级：明确的生词 > 词库中的未学习单词）
                if word_info.get('is_new_word', False):
                    classes.append('new-word')
                    classes.append('highlight-new')
                elif word_info['is_vocab'] and not word_info['is_known']:
                    classes.append('new-word')
                    classes.append('highlight-vocab-unknown')
                
                # 构建工具提示内容
                tooltip = ''
                if word_info.get('tooltip_enabled') and word_info['is_vocab']:
                    tooltip_parts = []
                    tooltip_parts.append(f"单词: {word_info['word']}")
                    
                    if word_info['pos'] != 'unknown':
                        pos_chinese = {
                            'noun': '名词', 'verb': '动词', 'adjective': '形容词', 
                            'adverb': '副词', 'preposition': '介词', 'conjunction': '连词',
                            'pronoun': '代词', 'article': '冠词', 'numeral': '数词', 
                            'interjection': '感叹词'
                        }.get(word_info['pos'], word_info['pos'])
                        tooltip_parts.append(f"词性: {pos_chinese}")
                    
                    if word_info['definition']:
                        tooltip_parts.append(f"释义: {word_info['definition']}")
                    if word_info['pronunciation']:
                        tooltip_parts.append(f"音标: {word_info['pronunciation']}")
                    
                    # 学习状态提示
                    if word_info['is_known']:
                        tooltip_parts.append("状态: 已掌握")
                    elif word_info.get('is_new_word', False) or (word_info['is_vocab'] and not word_info['is_known']):
                        tooltip_parts.append("状态: 生词")
                    
                    tooltip_content = '\n'.join(tooltip_parts)
                    tooltip = f' title="{tooltip_content}"'
                
                # 添加数据属性
                data_attrs = [
                    f'data-word="{word_info["word"]}"',
                    f'data-pos="{word_info["pos"]}"',
                    f'data-definition="{word_info["definition"]}"',
                    f'data-pronunciation="{word_info["pronunciation"]}"',
                    f'data-known="{str(word_info["is_known"]).lower()}"',
                    f'data-new="{str(word_info.get("is_new_word", False)).lower()}"'
                ]
                
                return f'<span class="{" ".join(classes)}" {"".join(data_attrs)}{tooltip}>{match.group()}</span>'
            return match.group()
        
        # 应用单词替换
        html_text = re.sub(r'\b\w+\b', replace_word, paragraph)
        
        return f'<{tag} class="{css_class}"{paragraph_id_attr}>{html_text}</{tag}>'
    
    def _generate_complete_html(self, paragraphs: List[Dict[str, Any]], statistics: Dict[str, Union[int, float]], options: Dict[str, Any]) -> str:
        """生成完整的HTML文档"""
        html_parts = []
        
        # 添加样式
        html_parts.append('''
        <style>
        .article-container { font-family: Arial, sans-serif; line-height: 1.6; }
        .word { cursor: pointer; transition: all 0.2s ease; }
        .vocab-word { background-color: #e3f2fd; }
        .known-word { background-color: #e8f5e8; }
        .new-word { background: linear-gradient(45deg, #ffebee, #ffcdd2); border: 1px solid #f44336; border-radius: 3px; padding: 1px 3px; font-weight: bold; }
        .highlight-new { box-shadow: 0 0 5px rgba(244, 67, 54, 0.5); animation: pulse 2s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 5px rgba(244, 67, 54, 0.5); } 50% { box-shadow: 0 0 10px rgba(244, 67, 54, 0.8); } 100% { box-shadow: 0 0 5px rgba(244, 67, 54, 0.5); } }
        .word:hover { transform: scale(1.05); z-index: 10; position: relative; }
        .pos-noun { border-bottom: 2px solid #2196f3; }
        .pos-verb { border-bottom: 2px solid #4caf50; }
        .pos-adjective { border-bottom: 2px solid #ff9800; }
        .pos-adverb { border-bottom: 2px solid #9c27b0; }
        .pos-preposition { border-bottom: 2px solid #795548; }
        .pos-conjunction { border-bottom: 2px solid #607d8b; }
        .pos-pronoun { border-bottom: 2px solid #e91e63; }
        .pos-article { border-bottom: 2px solid #009688; }
        .paragraph-title { font-size: 1.2em; font-weight: bold; margin: 1em 0; }
        .paragraph-list_item { margin-left: 1em; }
        .paragraph-quote { border-left: 4px solid #ccc; padding-left: 1em; font-style: italic; }
        .paragraph-code { background-color: #f5f5f5; padding: 1em; font-family: monospace; }
        .paragraph-indented { margin-left: 2em; }
        .statistics { margin-top: 2em; padding: 1em; background-color: #f9f9f9; }
        </style>
        ''')
        
        # 添加文章内容
        html_parts.append('<div class="article-container">')
        
        for index, paragraph in enumerate(paragraphs, 1):
            # 确保HTML包含段落ID
            html_content = paragraph['html']
            if 'data-paragraph-id' not in html_content:
                # 如果HTML中没有段落ID，添加一个
                html_content = html_content.replace('>', f' data-paragraph-id="{index}">', 1)
            html_parts.append(html_content)
        
        # 添加统计信息
        if options.get('show_statistics', True):
            html_parts.append(f'''
            <div class="statistics">
                <h4>文章统计</h4>
                <p>总词数: {statistics['total_words']}</p>
                <p>词库词数: {statistics['vocab_words']} ({statistics['vocab_coverage']}%)</p>
                <p>熟词数: {statistics['known_words']} ({statistics['known_coverage']}%)</p>
            </div>
            ''')
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def _analyze_paragraph_structure(self, paragraphs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析段落结构"""
        structure = {
            'total_paragraphs': len(paragraphs),
            'type_distribution': {},
            'structure_pattern': []
        }
        
        for paragraph in paragraphs:
            p_type = paragraph['type']
            structure['type_distribution'][p_type] = structure['type_distribution'].get(p_type, 0) + 1
            structure['structure_pattern'].append(p_type)
        
        return structure
    
    @action(detail=True, methods=['get'])
    def generate_image(self, request, pk=None):
        """生成图片格式的解析结果"""
        article = self.get_object()
        
        if not article.is_parsed:
            return Response({'error': '文章尚未解析'}, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: 实现图片生成功能
        return Response({
            'message': '图片生成功能开发中',
            'article_id': article.pk
        })