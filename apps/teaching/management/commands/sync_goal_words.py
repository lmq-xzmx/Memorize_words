from django.core.management.base import BaseCommand
from apps.teaching.models import LearningGoal

class Command(BaseCommand):
    help = '同步学习目标中关联的单词集和单词库到目标单词'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--goal-id',
            type=int,
            help='指定要同步的学习目标ID，不指定则同步所有目标',
        )
    
    def handle(self, *args, **options):
        goal_id = options.get('goal_id')
        
        if goal_id:
            try:
                goal = LearningGoal.objects.get(id=goal_id)
                goals = [goal]
                self.stdout.write(f'正在同步学习目标: {goal.name}')
            except LearningGoal.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'学习目标 ID {goal_id} 不存在')
                )
                return
        else:
            goals = LearningGoal.objects.all()
            self.stdout.write(f'正在同步所有 {goals.count()} 个学习目标')
        
        synced_count = 0
        for goal in goals:
            if goal.word_sets.exists() or goal.vocabulary_lists.exists():
                goal.sync_words_from_sets_and_lists()
                synced_count += 1
                self.stdout.write(f'已同步: {goal.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'成功同步了 {synced_count} 个学习目标的单词')
        )