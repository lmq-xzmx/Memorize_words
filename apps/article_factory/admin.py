from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Article, ParsedParagraph
from .views import ArticleViewSet
from apps.words.models import VocabularyList
import json


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'is_parsed', 'vocabulary_source', 'created_at', 'edit_actions']
    list_filter = ['is_parsed', 'vocabulary_source', 'variant_preference', 'created_at']
    search_fields = ['title', 'content', 'user__username']
    readonly_fields = ['is_parsed', 'parsed_content', 'html_content', 'paragraph_analysis', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'user', 'content', 'image')
        }),
        ('解析配置', {
            'fields': ('vocabulary_source', 'variant_preference'),
            'classes': ('collapse',)
        }),
        ('解析结果', {
            'fields': ('is_parsed', 'parsed_content', 'html_content', 'paragraph_analysis'),
            'classes': ('collapse',)
        }),
        ('编辑内容', {
            'fields': ('edit_mode', 'edited_content'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:article_id>/parse/', self.admin_site.admin_view(self.parse_article_view), name='article_factory_article_parse'),
            path('<int:article_id>/preview/', self.admin_site.admin_view(self.preview_article_view), name='article_factory_article_preview'),
            path('<int:article_id>/switch_vocabulary/', self.admin_site.admin_view(self.switch_vocabulary_view), name='article_factory_article_switch_vocabulary'),
            path('<int:article_id>/get_vocabulary_lists/', self.admin_site.admin_view(self.get_vocabulary_lists_view), name='article_factory_article_get_vocabulary_lists'),
            path('<int:article_id>/edit_source/', self.admin_site.admin_view(self.edit_source_view), name='article_factory_article_edit_source'),
            path('reparse_articles/', self.admin_site.admin_view(self.reparse_articles), name='article_factory_article_reparse')
        ]
        return custom_urls + urls
    
    @admin.display(description='操作')
    def edit_actions(self, obj):
        """编辑操作按钮"""
        if obj.pk:
            parse_url = reverse('admin:article_factory_article_parse', args=[obj.pk])
            preview_url = reverse('admin:article_factory_article_preview', args=[obj.pk])
            edit_source_url = reverse('admin:article_factory_article_edit_source', args=[obj.pk])
            
            buttons = [
                f'<a class="button" href="{parse_url}">解析</a>',
                f'<a class="button" href="{preview_url}" target="_blank">预览</a>',
                f'<a class="button" href="{edit_source_url}">源码编辑</a>',
            ]
            return format_html(' '.join(buttons))
        return '-'
    
    def parse_article_view(self, request, article_id):
        """解析文章视图"""
        article = get_object_or_404(Article, pk=article_id)
        
        if request.method == 'POST':
            # 获取解析选项
            vocabulary_source = request.POST.get('vocabulary_source', article.vocabulary_source)
            variant_preference = request.POST.get('variant_preference', article.variant_preference)
            enable_paragraph_analysis = request.POST.get('enable_paragraph_analysis') == 'on'
            enable_tooltip = request.POST.get('enable_tooltip') == 'on'
            
            # 更新文章配置
            article.vocabulary_source = vocabulary_source
            article.variant_preference = variant_preference
            article.save()
            
            # 执行解析
            viewset = ArticleViewSet()
            parse_options = {
                'enable_paragraph_analysis': enable_paragraph_analysis,
                'enable_tooltip': enable_tooltip,
            }
            
            try:
                # 清除旧的解析数据
                ParsedParagraph.objects.filter(article=article).delete()
                
                result = viewset._parse_article(article, parse_options)
                messages.success(request, f'文章 "{article.title}" 解析完成！')
                
                # 根据用户选择跳转
                next_action = request.POST.get('next_action', 'preview')
                if next_action == 'preview':
                    return redirect('admin:article_factory_article_preview', article_id=article.pk)
                elif next_action == 'edit_source':
                    return redirect('admin:article_factory_article_edit_source', article_id=article.pk)
                else:
                    return redirect('admin:article_factory_article_changelist')
                    
            except Exception as e:
                messages.error(request, f'解析失败: {str(e)}')
        
        # 获取可用的词库列表
        vocabulary_lists = VocabularyList.objects.all()
        
        context = {
            'article': article,
            'vocabulary_lists': vocabulary_lists,
            'title': f'解析文章: {article.title}',
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/article_factory/article/parse_form.html', context)
    
    def preview_article_view(self, request, article_id):
        """预览文章视图"""
        article = get_object_or_404(Article, pk=article_id)
        
        if not article.is_parsed:
            messages.warning(request, '文章尚未解析，请先解析文章。')
            return redirect('admin:article_factory_article_parse', article_id=article.pk)
        
        context = {
            'article': article,
            'title': f'预览文章: {article.title}',
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/article_factory/article/preview.html', context)
    
    def switch_vocabulary_view(self, request, article_id):
        """切换词库来源"""
        article = get_object_or_404(Article, pk=article_id)
        
        if request.method == 'POST':
            import json
            try:
                data = json.loads(request.body)
                new_source = data.get('vocabulary_source', 'default')
                
                # 检查是否是系统词库
                if new_source.startswith('vocab_'):
                    vocab_id = new_source.replace('vocab_', '')
                    try:
                        vocab_list = VocabularyList.objects.get(pk=vocab_id)
                        article.vocabulary_source = f'system_{vocab_list.name}'
                        article.system_vocabulary_id = vocab_id
                        
                        # 保存用户选择到session
                        request.session['last_vocabulary_selection'] = vocab_id
                        
                    except VocabularyList.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'error': f'词库不存在: {vocab_id}'
                        }, status=404)
                else:
                    # 标准词库来源
                    article.vocabulary_source = new_source
                    article.system_vocabulary_id = None
                    
                    # 对于标准词库，清除session中的选择
                    if 'last_vocabulary_selection' in request.session:
                        del request.session['last_vocabulary_selection']
                
                article.save()
                
                # 重新解析文章以应用新词库
                viewset = ArticleViewSet()
                parse_options = {
                    'enable_paragraph_analysis': True,
                    'enable_tooltips': True,
                }
                
                # 清除旧的解析数据
                ParsedParagraph.objects.filter(article=article).delete()
                
                # 重新解析
                viewset._parse_article(article, parse_options)
                
                return JsonResponse({
                    'success': True,
                    'message': f'词库已切换为: {new_source}'
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
        
        return JsonResponse({'success': False, 'error': '仅支持POST请求'}, status=405)
    
    def get_vocabulary_lists_view(self, request, article_id):
        """获取词库列表"""
        if request.method == 'GET':
            try:
                from apps.words.models import VocabularyList
                
                # 获取所有活跃的词库列表，按创建时间排序
                vocab_lists = VocabularyList.objects.filter(is_active=True).order_by('created_at').values(
                    'id', 'name', 'description', 'word_count', 'created_at'
                )
                
                # 获取最早创建的词库作为默认值
                earliest_vocab = None
                if vocab_lists.exists():
                    earliest_vocab = vocab_lists.first()
                
                # 获取用户上次选择的词库（从session或cookie）
                user_last_selection = request.session.get('last_vocabulary_selection')
                
                # 确定默认选择的词库
                default_vocab = None
                if user_last_selection:
                    # 检查用户上次选择的词库是否仍然存在
                    try:
                        last_vocab = VocabularyList.objects.get(pk=user_last_selection, is_active=True)
                        default_vocab = {
                            'id': last_vocab.pk,
                            'name': last_vocab.name,
                            'description': last_vocab.description,
                            'word_count': last_vocab.word_count,
                            'created_at': last_vocab.created_at.isoformat()
                        }
                    except VocabularyList.DoesNotExist:
                        pass
                
                # 如果用户没有上次选择或上次选择的词库不存在，使用最早创建的词库
                if not default_vocab and earliest_vocab:
                    default_vocab = {
                        'id': earliest_vocab['id'],
                        'name': earliest_vocab['name'],
                        'description': earliest_vocab['description'],
                        'word_count': earliest_vocab['word_count'],
                        'created_at': earliest_vocab['created_at'].isoformat()
                    }
                
                return JsonResponse({
                    'success': True,
                    'vocabulary_lists': list(vocab_lists),
                    'default_selection': default_vocab,
                    'earliest_vocab': {
                        'id': earliest_vocab['id'],
                        'name': earliest_vocab['name'],
                        'description': earliest_vocab['description'],
                        'word_count': earliest_vocab['word_count'],
                        'created_at': earliest_vocab['created_at'].isoformat()
                    } if earliest_vocab else None
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
        
        return JsonResponse({'success': False, 'error': '仅支持GET请求'}, status=405)
    
    def edit_source_view(self, request, article_id):
        """源码编辑视图"""
        article = get_object_or_404(Article, pk=article_id)
        
        if request.method == 'POST':
            # 保存编辑内容
            edited_content = request.POST.get('edited_content', '')
            article.edited_content = edited_content
            article.edit_mode = 'source'
            
            # 是否触发重新解析
            if request.POST.get('trigger_reparse') == 'on':
                article.content = edited_content
                article.is_parsed = False
                article.save()
                
                # 执行解析
                viewset = ArticleViewSet()
                try:
                    result = viewset._parse_article(article)
                    messages.success(request, '内容已保存并重新解析完成！')
                except Exception as e:
                    messages.error(request, f'重新解析失败: {str(e)}')
            else:
                article.save()
                messages.success(request, '编辑内容已保存！')
            
            # 根据用户选择跳转
            next_action = request.POST.get('next_action', 'stay')
            if next_action == 'preview':
                return redirect('admin:article_factory_article_preview', article_id=article.pk)
            elif next_action == 'list':
                return redirect('admin:article_factory_article_changelist')
        
        context = {
            'article': article,
            'title': f'源码编辑: {article.title}',
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/article_factory/article/edit_source.html', context)
    

    
    def html_preview(self, obj):
        """HTML预览"""
        if obj.html_content:
            return format_html(
                '<div style="max-height: 200px; overflow-y: auto; border: 1px solid #ddd; padding: 10px;">{}</div>',
                mark_safe(obj.html_content)
            )
        return '-'
    
    setattr(html_preview, 'short_description', 'HTML预览')
    
    def reparse_articles(self, request):
        """批量重新解析文章"""
        if request.method == 'POST':
            article_ids = request.POST.getlist('article_ids')
            if article_ids:
                viewset = ArticleViewSet()
                success_count = 0
                error_count = 0
                
                for article_id in article_ids:
                    try:
                        article = Article.objects.get(pk=article_id)
                        viewset._parse_article(article)
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                
                if success_count > 0:
                    messages.success(request, f'成功重新解析 {success_count} 篇文章')
                if error_count > 0:
                    messages.error(request, f'{error_count} 篇文章解析失败')
            else:
                messages.warning(request, '请选择要重新解析的文章')
        
        return redirect('admin:article_factory_article_changelist')
    
    actions = ['reparse_selected_articles']
    
    def reparse_selected_articles(self, request, queryset):
        """批量重新解析选中的文章"""
        viewset = ArticleViewSet()
        success_count = 0
        error_count = 0
        
        for article in queryset:
            try:
                viewset._parse_article(article)
                success_count += 1
            except Exception as e:
                error_count += 1
        
        if success_count > 0:
            self.message_user(request, f'成功重新解析 {success_count} 篇文章')
        if error_count > 0:
            self.message_user(request, f'{error_count} 篇文章解析失败', level=messages.ERROR)
    
    setattr(reparse_selected_articles, 'short_description', '重新解析选中的文章')
    



@admin.register(ParsedParagraph)
class ParsedParagraphAdmin(admin.ModelAdmin):
    list_display = ['article', 'order', 'paragraph_type', 'word_count', 'vocab_word_count']
    list_filter = ['paragraph_type', 'article__user']
    search_fields = ['article__title', 'original_text']
    readonly_fields = ['word_data', 'html_content']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('article', 'order', 'paragraph_type')
        }),
        ('文本内容', {
            'fields': ('original_text', 'processed_text')
        }),
        ('解析数据', {
            'fields': ('word_data', 'html_content'),
            'classes': ('collapse',)
        })
    )
    
    def word_count(self, obj):
        """单词数量"""
        if obj.word_data:
            return len(obj.word_data)
        return 0
    
    setattr(word_count, 'short_description', '单词数')
    
    def vocab_word_count(self, obj):
        """词库单词数量"""
        if obj.word_data:
            return len([w for w in obj.word_data if w.get('is_vocab', False)])
        return 0
    
    setattr(vocab_word_count, 'short_description', '词库词数')