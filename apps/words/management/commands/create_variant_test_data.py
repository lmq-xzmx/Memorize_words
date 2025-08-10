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
            has_conflict=False,
            is_variant=False
        )
        self.stdout.write(f"创建主单词: {word1.word} (ID: {word1.pk})")
        
        # 创建第二个同名单词（有冲突）
        word2 = Word.objects.create(
            word='test',
            phonetic='/tɛst/',
            definition='第二个定义：考试',
            part_of_speech='verb',
            example='I will test your knowledge.',
            vocabulary_list=vocab_list,
            grade='初中',
            difficulty_level=3,
            has_conflict=True,  # 标记为有冲突
            is_variant=False,
            conflict_data={
                'conflicts': [
                    {'type': 'phonetic', 'existing': '/test/', 'new': '/tɛst/'},
                    {'type': 'definition', 'existing': '第一个定义：测试', 'new': '第二个定义：考试'},
                    {'type': 'part_of_speech', 'existing': 'noun', 'new': 'verb'}
                ],
                'total_conflicts': 3
            }
        )
        self.stdout.write(f"创建冲突单词: {word2.word} (ID: {word2.pk}) - 有冲突")
        
        # 创建第三个同名单词（有冲突）
        word3 = Word.objects.create(
            word='test',
            phonetic='/test/',
            definition='第三个定义：试验',
            part_of_speech='noun',
            example='The test was successful.',
            vocabulary_list=vocab_list,
            grade='大学',
            difficulty_level=4,
            has_conflict=True,  # 标记为有冲突
            is_variant=False,
            conflict_data={
                'conflicts': [
                    {'type': 'definition', 'existing': '第一个定义：测试', 'new': '第三个定义：试验'},
                    {'type': 'grade', 'existing': '高中', 'new': '大学'}
                ],
                'total_conflicts': 2
            }
        )
        self.stdout.write(f"创建冲突单词: {word3.word} (ID: {word3.pk}) - 有冲突")
        
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
            has_conflict=False,
            is_variant=False
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
            has_conflict=True,
            is_variant=False,
            conflict_data={
                'conflicts': [
                    {'type': 'definition', 'existing': '例子，实例', 'new': '举例说明'},
                    {'type': 'part_of_speech', 'existing': 'noun', 'new': 'verb'}
                ],
                'total_conflicts': 2
            }
        )
        self.stdout.write(f"创建冲突单词: {example2.word} (ID: {example2.pk}) - 有冲突")
        
        self.stdout.write("\n测试数据创建完成！")
        self.stdout.write("\n现在可以在管理界面中测试以下功能：")
        self.stdout.write("1. 访问 http://localhost:8002/admin/words/word/")
        self.stdout.write("2. 查看'变体状态'列中的下拉框（对于有冲突的单词）")
        self.stdout.write("3. 查看'冲突状态'列显示'有冲突'")
        self.stdout.write("4. 选择处理方案：①删除本记录 或 ②保留为新版本")
        self.stdout.write("5. 保存后查看版本号显示")
        
        self.stdout.write("\n当前数据状态：")
        all_words = Word.objects.filter(word__in=['test', 'example']).order_by('word', 'created_at')
        for word in all_words:
            status = "有冲突" if word.has_conflict else ("变体" if word.is_variant else "主单词")
            self.stdout.write(f"- {word.word} (ID: {word.pk}) - {status} - {word.definition[:20]}...")
        
        self.stdout.write(self.style.SUCCESS('\n测试数据创建成功！'))