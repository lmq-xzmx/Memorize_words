from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from words.models import Word
from django.db.models import Q
import json


class Command(BaseCommand):
    help = '管理单词版本 - 列出、创建、删除、修改单词版本'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['list', 'create', 'delete', 'update', 'show'],
            help='操作类型: list(列表), create(创建), delete(删除), update(更新), show(显示)'
        )
        parser.add_argument(
            '--word',
            type=str,
            help='单词名称'
        )
        parser.add_argument(
            '--version',
            type=int,
            help='版本号'
        )
        parser.add_argument(
            '--data',
            type=str,
            help='JSON格式的数据 (用于create和update操作)'
        )
        parser.add_argument(
            '--all-versions',
            action='store_true',
            help='显示所有版本 (用于list操作)'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'list':
            self.list_versions(options)
        elif action == 'create':
            self.create_version(options)
        elif action == 'delete':
            self.delete_version(options)
        elif action == 'update':
            self.update_version(options)
        elif action == 'show':
            self.show_version(options)

    def list_versions(self, options):
        """列出单词版本"""
        word_name = options.get('word')
        show_all = options.get('all_versions', False)
        
        if word_name:
            # 显示特定单词的所有版本
            words = Word.objects.filter(word=word_name).order_by('version_number')
            if not words.exists():
                self.stdout.write(
                    self.style.ERROR(f'未找到单词 "{word_name}"')
                )
                return
            
            self.stdout.write(f'\n单词 "{word_name}" 的版本列表:')
            self.stdout.write('=' * 50)
            
            for word in words:
                status = '主单词' if word.is_main_word() else f'版本 {word.version_number}'
                created = word.created_at.strftime('%Y-%m-%d %H:%M:%S')
                self.stdout.write(
                    f'{word.pk:4d} | {status:8s} | {word.phonetic:15s} | {word.definition[:30]:30s} | {created}'
                )
        else:
            # 显示所有有多版本的单词
            if show_all:
                # 显示所有单词
                words = Word.objects.filter(parent_word__isnull=True).order_by('word')
                self.stdout.write('\n所有单词列表:')
            else:
                # 只显示有多版本的单词
                words = Word.objects.filter(has_multiple_versions=True).order_by('word')
                self.stdout.write('\n有多版本的单词列表:')
            
            self.stdout.write('=' * 80)
            
            for word in words:
                version_count = word.get_version_count()
                created = word.created_at.strftime('%Y-%m-%d %H:%M:%S')
                self.stdout.write(
                    f'{word.pk:4d} | {word.word:15s} | {version_count:2d} 个版本 | {word.definition[:40]:40s} | {created}'
                )

    def create_version(self, options):
        """创建新版本"""
        word_name = options.get('word')
        data_str = options.get('data')
        
        if not word_name:
            raise CommandError('创建版本需要指定 --word 参数')
        
        if not data_str:
            raise CommandError('创建版本需要指定 --data 参数')
        
        try:
            data = json.loads(data_str)
        except json.JSONDecodeError:
            raise CommandError('--data 参数必须是有效的JSON格式')
        
        # 查找主单词
        main_word = Word.objects.filter(
            word=word_name,
            parent_word__isnull=True
        ).first()
        
        if not main_word:
            self.stdout.write(
                self.style.ERROR(f'未找到单词 "{word_name}" 的主单词')
            )
            return
        
        try:
            with transaction.atomic():
                # 创建新版本
                new_version = main_word.create_version(**data)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'成功创建单词 "{word_name}" 的版本 {new_version.version_number}'
                    )
                )
                self.stdout.write(f'版本ID: {new_version.pk}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'创建版本失败: {str(e)}')
            )

    def delete_version(self, options):
        """删除版本"""
        word_name = options.get('word')
        version_number = options.get('version')
        
        if not word_name:
            raise CommandError('删除版本需要指定 --word 参数')
        
        if not version_number:
            raise CommandError('删除版本需要指定 --version 参数')
        
        # 查找主单词
        main_word = Word.objects.filter(
            word=word_name,
            parent_word__isnull=True
        ).first()
        
        if not main_word:
            self.stdout.write(
                self.style.ERROR(f'未找到单词 "{word_name}" 的主单词')
            )
            return
        
        try:
            with transaction.atomic():
                # 删除指定版本
                success = main_word.delete_version(version_number)
                
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'成功删除单词 "{word_name}" 的版本 {version_number}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'未找到单词 "{word_name}" 的版本 {version_number}')
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'删除版本失败: {str(e)}')
            )

    def update_version(self, options):
        """更新版本"""
        word_name = options.get('word')
        version_number = options.get('version')
        data_str = options.get('data')
        
        if not word_name:
            raise CommandError('更新版本需要指定 --word 参数')
        
        if not version_number:
            raise CommandError('更新版本需要指定 --version 参数')
        
        if not data_str:
            raise CommandError('更新版本需要指定 --data 参数')
        
        try:
            data = json.loads(data_str)
        except json.JSONDecodeError:
            raise CommandError('--data 参数必须是有效的JSON格式')
        
        # 查找要更新的版本
        if version_number == 1:
            # 更新主单词
            word = Word.objects.filter(
                word=word_name,
                parent_word__isnull=True
            ).first()
        else:
            # 更新指定版本
            word = Word.objects.filter(
                word=word_name,
                version_number=version_number
            ).first()
        
        if not word:
            self.stdout.write(
                self.style.ERROR(f'未找到单词 "{word_name}" 的版本 {version_number}')
            )
            return
        
        try:
            with transaction.atomic():
                # 更新字段
                for field, value in data.items():
                    if hasattr(word, field):
                        setattr(word, field, value)
                
                word.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'成功更新单词 "{word_name}" 的版本 {version_number}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'更新版本失败: {str(e)}')
            )

    def show_version(self, options):
        """显示版本详情"""
        word_name = options.get('word')
        version_number = options.get('version')
        
        if not word_name:
            raise CommandError('显示版本需要指定 --word 参数')
        
        if not version_number:
            raise CommandError('显示版本需要指定 --version 参数')
        
        # 查找指定版本
        if version_number == 1:
            # 显示主单词
            word = Word.objects.filter(
                word=word_name,
                parent_word__isnull=True
            ).first()
        else:
            # 显示指定版本
            word = Word.objects.filter(
                word=word_name,
                version_number=version_number
            ).first()
        
        if not word:
            self.stdout.write(
                self.style.ERROR(f'未找到单词 "{word_name}" 的版本 {version_number}')
            )
            return
        
        # 显示版本详情
        self.stdout.write(f'\n单词 "{word_name}" 版本 {version_number} 详情:')
        self.stdout.write('=' * 50)
        self.stdout.write(f'ID: {word.pk}')
        self.stdout.write(f'单词: {word.word}')
        self.stdout.write(f'音标: {word.phonetic or "无"}')
        self.stdout.write(f'词性: {word.part_of_speech or "无"}')
        self.stdout.write(f'释义: {word.definition or "无"}')
        self.stdout.write(f'例句: {word.example or "无"}')
        self.stdout.write(f'笔记: {word.note or "无"}')
        self.stdout.write(f'教材版本: {word.textbook_version or "无"}')
        self.stdout.write(f'年级: {word.grade or "无"}')
        self.stdout.write(f'词库列表: {word.vocabulary_list.name if word.vocabulary_list else "无"}')
        self.stdout.write(f'创建时间: {word.created_at}')
        self.stdout.write(f'更新时间: {word.updated_at}')
        
        if word.version_data:
            self.stdout.write(f'版本数据: {json.dumps(word.version_data, indent=2, ensure_ascii=False)}') 