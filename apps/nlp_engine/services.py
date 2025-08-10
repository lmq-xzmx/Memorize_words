"""
NLP Engine Services - 自然语言处理服务

提供分词、词性标注、文本分析等功能
"""

import re
import os
from typing import List, Tuple, Dict, Any, Optional
from django.conf import settings


class NLTKService:
    """NLTK服务类 - 封装NLTK功能"""
    
    def __init__(self):
        self._nltk_available = False
        self._setup_nltk()
    
    def _setup_nltk(self):
        """设置NLTK环境"""
        try:
            import nltk
            from nltk.tokenize import word_tokenize
            from nltk.tag import pos_tag as nltk_pos_tag
            
            # 设置项目内的NLTK数据路径
            project_nltk_data = os.path.join(
                settings.BASE_DIR, 
                'apps', 
                'nlp_engine', 
                'nltk_data'
            )
            
            if project_nltk_data not in nltk.data.path:
                nltk.data.path.insert(0, project_nltk_data)
            
            # 检查必要的数据是否存在
            self._check_and_download_data()
            
            # 设置NLTK函数
            self.word_tokenize = word_tokenize
            self.nltk_pos_tag = nltk_pos_tag
            self._nltk_available = True
            
        except ImportError:
            self._nltk_available = False
            self._setup_fallback()
        except Exception as e:
            print(f"NLTK设置失败: {e}")
            self._nltk_available = False
            self._setup_fallback()
    
    def _check_and_download_data(self):
        """检查并下载必要的NLTK数据"""
        import nltk
        
        required_data = [
            ('tokenizers/punkt_tab', 'punkt_tab'),
            ('tokenizers/punkt', 'punkt'),
            ('taggers/averaged_perceptron_tagger_eng', 'averaged_perceptron_tagger_eng'),
            ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'),
            ('corpora/stopwords', 'stopwords'),
        ]
        
        for data_path, download_name in required_data:
            try:
                nltk.data.find(data_path)
            except LookupError:
                try:
                    print(f"下载NLTK数据: {download_name}")
                    nltk.download(download_name, download_dir=os.path.join(
                        settings.BASE_DIR, 'apps', 'nlp_engine', 'nltk_data'
                    ))
                except Exception as e:
                    print(f"下载 {download_name} 失败: {e}")
    
    def _setup_fallback(self):
        """设置备用实现"""
        def fallback_word_tokenize(text: str) -> List[str]:
            return re.findall(r'\b\w+\b', text.lower())
        
        def fallback_pos_tag(words: List[str]) -> List[Tuple[str, str]]:
            return [(word, 'NN') for word in words]  # 默认为名词
        
        self.word_tokenize = fallback_word_tokenize
        self.nltk_pos_tag = fallback_pos_tag
    
    @property
    def is_available(self) -> bool:
        """检查NLTK是否可用"""
        return self._nltk_available
    
    def tokenize(self, text: str) -> List[str]:
        """分词"""
        return self.word_tokenize(text)
    
    def pos_tag(self, words: List[str]) -> List[Tuple[str, str]]:
        """词性标注"""
        return self.nltk_pos_tag(words)
    
    def standardize_pos(self, pos: str) -> str:
        """标准化词性标签"""
        # NLTK词性标签映射
        nltk_pos_mapping = {
            'NN': 'noun', 'NNS': 'noun', 'NNP': 'noun', 'NNPS': 'noun',
            'VB': 'verb', 'VBD': 'verb', 'VBG': 'verb', 'VBN': 'verb', 
            'VBP': 'verb', 'VBZ': 'verb',
            'JJ': 'adjective', 'JJR': 'adjective', 'JJS': 'adjective',
            'RB': 'adverb', 'RBR': 'adverb', 'RBS': 'adverb',
            'IN': 'preposition', 'TO': 'preposition',
            'CC': 'conjunction',
            'PRP': 'pronoun', 'PRP$': 'pronoun', 'WP': 'pronoun', 'WP$': 'pronoun',
            'DT': 'article', 'WDT': 'article',
            'CD': 'numeral',
            'UH': 'interjection'
        }
        
        # 通用词性映射
        general_pos_mapping = {
            'n': 'noun', 'noun': 'noun', '名词': 'noun',
            'v': 'verb', 'verb': 'verb', '动词': 'verb',
            'adj': 'adjective', 'adjective': 'adjective', '形容词': 'adjective',
            'adv': 'adverb', 'adverb': 'adverb', '副词': 'adverb',
            'prep': 'preposition', 'preposition': 'preposition', '介词': 'preposition',
            'conj': 'conjunction', 'conjunction': 'conjunction', '连词': 'conjunction',
            'pron': 'pronoun', 'pronoun': 'pronoun', '代词': 'pronoun',
            'art': 'article', 'article': 'article', '冠词': 'article',
            'num': 'numeral', 'numeral': 'numeral', '数词': 'numeral',
            'int': 'interjection', 'interjection': 'interjection', '感叹词': 'interjection'
        }
        
        # 首先尝试NLTK标签映射
        if pos in nltk_pos_mapping:
            return nltk_pos_mapping[pos]
        
        # 然后尝试通用映射
        return general_pos_mapping.get(pos.lower(), 'unknown')


class TextAnalysisService:
    """文本分析服务"""
    
    def __init__(self):
        self.nltk_service = NLTKService()
    
    def analyze_text(self, text: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """分析文本"""
        if options is None:
            options = {}
        
        # 分割段落
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        analyzed_paragraphs = []
        total_words = 0
        
        for i, paragraph in enumerate(paragraphs):
            paragraph_analysis = self.analyze_paragraph(paragraph, i + 1, options)
            analyzed_paragraphs.append(paragraph_analysis)
            total_words += paragraph_analysis['word_count']
        
        return {
            'paragraphs': analyzed_paragraphs,
            'total_paragraphs': len(paragraphs),
            'total_words': total_words,
            'nltk_available': self.nltk_service.is_available,
            'analysis_options': options
        }
    
    def analyze_paragraph(self, paragraph: str, paragraph_id: int, options: Dict[str, Any]) -> Dict[str, Any]:
        """分析段落"""
        # 检测段落类型
        paragraph_type = self.detect_paragraph_type(paragraph)
        
        # 分词
        words = self.nltk_service.tokenize(paragraph.lower())
        
        # 词性标注
        pos_tags = self.nltk_service.pos_tag(words)
        
        # 分析单词
        word_data = []
        for word, pos in pos_tags:
            if word.isalpha():  # 只处理字母单词
                standardized_pos = self.nltk_service.standardize_pos(pos)
                word_info = {
                    'word': word,
                    'pos': standardized_pos,
                    'original_pos': pos,
                }
                word_data.append(word_info)
        
        return {
            'id': paragraph_id,
            'text': paragraph,
            'type': paragraph_type,
            'word_data': word_data,
            'word_count': len(word_data),
            'pos_distribution': self._get_pos_distribution(word_data)
        }
    
    def detect_paragraph_type(self, paragraph: str) -> str:
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
    
    def _get_pos_distribution(self, word_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """获取词性分布"""
        distribution = {}
        for word_info in word_data:
            pos = word_info['pos']
            distribution[pos] = distribution.get(pos, 0) + 1
        return distribution


# 全局服务实例
nltk_service = NLTKService()
text_analysis_service = TextAnalysisService()