#!/usr/bin/env python
"""
测试NLTK数据迁移
"""

import os
import sys

# 添加项目路径
sys.path.append('.')

# 设置NLTK数据路径
import nltk
project_nltk_data = os.path.join(os.getcwd(), 'apps', 'nlp_engine', 'nltk_data')
nltk.data.path.insert(0, project_nltk_data)

print(f"项目NLTK数据路径: {project_nltk_data}")
print(f"NLTK搜索路径: {nltk.data.path[:3]}...")  # 只显示前3个路径

# 测试NLTK功能
try:
    from nltk.tokenize import word_tokenize
    from nltk.tag import pos_tag
    
    test_text = "This is a test sentence."
    print(f"\n测试文本: {test_text}")
    
    # 分词测试
    tokens = word_tokenize(test_text)
    print(f"分词结果: {tokens}")
    
    # 词性标注测试
    pos_tags = pos_tag(tokens)
    print(f"词性标注: {pos_tags}")
    
    print("\n✅ NLTK功能测试成功！")
    
except Exception as e:
    print(f"\n❌ NLTK功能测试失败: {e}")

# 检查数据文件是否存在
print(f"\n检查NLTK数据文件:")
data_files = [
    'tokenizers/punkt',
    'taggers/averaged_perceptron_tagger_eng',
    'corpora/stopwords'
]

for data_file in data_files:
    try:
        nltk.data.find(data_file)
        print(f"✅ {data_file} - 找到")
    except LookupError:
        print(f"❌ {data_file} - 未找到")

print(f"\n项目NLTK数据目录大小:")
if os.path.exists(project_nltk_data):
    import subprocess
    result = subprocess.run(['du', '-sh', project_nltk_data], capture_output=True, text=True)
    print(f"大小: {result.stdout.strip()}")
else:
    print("❌ 项目NLTK数据目录不存在")