"""
测试NLP引擎的管理命令
"""

from django.core.management.base import BaseCommand
from apps.nlp_engine.services import nltk_service, text_analysis_service


class Command(BaseCommand):
    help = '测试NLP引擎功能'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--text',
            type=str,
            default='This is a test sentence for NLP analysis.',
            help='要分析的测试文本'
        )
    
    def handle(self, *args, **options):
        test_text = options['text']
        
        self.stdout.write(self.style.SUCCESS('=== NLP引擎测试 ==='))
        
        # 测试NLTK服务状态
        self.stdout.write(f'NLTK可用性: {nltk_service.is_available}')
        
        # 测试分词
        self.stdout.write('\n--- 分词测试 ---')
        tokens = nltk_service.tokenize(test_text)
        self.stdout.write(f'原文: {test_text}')
        self.stdout.write(f'分词结果: {tokens}')
        
        # 测试词性标注
        self.stdout.write('\n--- 词性标注测试 ---')
        pos_tags = nltk_service.pos_tag(tokens)
        for word, pos in pos_tags:
            standardized_pos = nltk_service.standardize_pos(pos)
            self.stdout.write(f'{word}: {pos} -> {standardized_pos}')
        
        # 测试文本分析
        self.stdout.write('\n--- 文本分析测试 ---')
        analysis = text_analysis_service.analyze_text(test_text)
        self.stdout.write(f'段落数: {analysis["total_paragraphs"]}')
        self.stdout.write(f'总词数: {analysis["total_words"]}')
        
        for paragraph in analysis['paragraphs']:
            self.stdout.write(f'段落类型: {paragraph["type"]}')
            self.stdout.write(f'词性分布: {paragraph["pos_distribution"]}')
        
        self.stdout.write(self.style.SUCCESS('\n=== 测试完成 ==='))