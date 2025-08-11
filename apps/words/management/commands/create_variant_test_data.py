from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.words.models import Word, VocabularyList, VocabularySource

class Command(BaseCommand):
    help = '创建变体UI功能测试数据'
    
    def handle(self, *args, **options):
        self.stdout.write("开始创建测试数据...")
        
        # 创建词库来源和列表
        source, _ = VocabularySource.objects.get_or_create(
            name='测试来源',
            defaults={'description': '用于测试变体功能的词库来源'}
        )
        
        vocab_list, _ = VocabularyList.objects.get_or_create(
            name='变体测试词库',
            defaults={
                'source': source,
                'description': '用于测试变体功能的词库列表',
                'is_active': True
            }
        )
        
        # 清理现有的测试数据
        Word.objects.filter(word__in=['test', 'example', 'sample']).delete()
        
        # 创建第一个单词（主单词）
        word1 = Word.objects.create(
            word='test',
            phonetic='/test/',
            definition='第一个定义：测试',
            part_of_speech='noun',
            example='This is a test.',
            vocabulary_list=vocab_list,
            grade='高中',
            difficulty_level=2,
            has_multiple_versions=True,
            parent_word=None
        )
        self.stdout.write(f"创建主单词: {word1.word} (ID: {word1.pk})")
        
        # 创建第二个同名单词（版本）
        word2 = Word.objects.create(
            word='test',
            phonetic='/tɛst/',
            definition='第二个定义：考试',
            part_of_speech='verb',
            example='I will test your knowledge.',
            vocabulary_list=vocab_list,
            grade='初中',
            difficulty_level=3,
            has_multiple_versions=False,
            parent_word=word1,
            version_number=2
        )
        self.stdout.write(f"创建版本单词: {word2.word} (ID: {word2.pk}) - 版本2")
        
        # 创建第三个同名单词（版本）
        word3 = Word.objects.create(
            word='test',
            phonetic='/test/',
            definition='第三个定义：试验',
            part_of_speech='noun',
            example='The test was successful.',
            vocabulary_list=vocab_list,
            grade='大学',
            difficulty_level=4,
            has_multiple_versions=False,
            parent_word=word1,
            version_number=3
        )
        self.stdout.write(f"创建版本单词: {word3.word} (ID: {word3.pk}) - 版本3")
        
        # 创建另一组测试数据
        example1 = Word.objects.create(
            word='example',
            phonetic='/ɪɡˈzæmpəl/',
            definition='例子，实例',
            part_of_speech='noun',
            example='This is an example.',
            vocabulary_list=vocab_list,
            grade='初中',
            difficulty_level=2,
            has_multiple_versions=True,
            parent_word=None
        )
        self.stdout.write(f"创建主单词: {example1.word} (ID: {example1.pk})")
        
        example2 = Word.objects.create(
            word='example',
            phonetic='/ɪɡˈzæmpəl/',
            definition='举例说明',
            part_of_speech='verb',
            example='Let me example this concept.',
            vocabulary_list=vocab_list,
            grade='高中',
            difficulty_level=3,
            has_multiple_versions=False,
            parent_word=example1,
            version_number=2
        )
        self.stdout.write(f"创建版本单词: {example2.word} (ID: {example2.pk}) - 版本2")
        
        self.stdout.write("\n测试数据创建完成！")
        self.stdout.write("\n现在可以在管理界面中测试以下功能：")
        self.stdout.write("1. 访问 http://localhost:8001/admin/words/word/")
        self.stdout.write("2. 查看'版本状态'列显示版本信息")
        self.stdout.write("3. 查看'多版本状态'列显示是否有多个版本")
        self.stdout.write("4. 查看父子关系和版本号")
        self.stdout.write("5. 测试版本管理功能")
        
        self.stdout.write("\n当前数据状态：")
        all_words = Word.objects.filter(word__in=['test', 'example']).order_by('word', 'created_at')
        for word in all_words:
            if word.parent_word is None:
                status = "主单词" if word.has_multiple_versions else "单一版本"
            else:
                status = f"版本{word.version_number}"
            self.stdout.write(f"- {word.word} (ID: {word.pk}) - {status} - {word.definition[:20]}...")
        
        self.stdout.write(self.style.SUCCESS('\n测试数据创建成功！'))