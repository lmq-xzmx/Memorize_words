# Generated manually for guided practice models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('words', '0009_remove_conflict_resolution'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teaching', '0006_merge_20250810_0628'),
    ]

    operations = [
        # Add guided practice fields to existing models
        migrations.AddField(
            model_name='learningsession',
            name='is_guided',
            field=models.BooleanField(default=False, verbose_name='是否为指导模式'),
        ),
        migrations.AddField(
            model_name='learningsession',
            name='teacher',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='guided_learning_sessions',
                to=settings.AUTH_USER_MODEL,
                verbose_name='指导老师'
            ),
        ),
        migrations.AddField(
            model_name='wordlearningrecord',
            name='is_guided',
            field=models.BooleanField(default=False, verbose_name='是否为指导模式'),
        ),
        
        # Create new guided practice models
        migrations.CreateModel(
            name='GuidedPracticeSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_name', models.CharField(max_length=200, verbose_name='会话名称')),
                ('practice_mode', models.CharField(
                    choices=[
                        ('multiple_choice', '选择题'),
                        ('fill_blank', '填空题'),
                        ('translation', '翻译题'),
                        ('mixed', '混合模式'),
                    ],
                    default='multiple_choice',
                    max_length=20,
                    verbose_name='练习模式'
                )),
                ('status', models.CharField(
                    choices=[
                        ('waiting', '等待中'),
                        ('active', '进行中'),
                        ('paused', '暂停'),
                        ('completed', '已完成'),
                        ('cancelled', '已取消'),
                    ],
                    default='waiting',
                    max_length=20,
                    verbose_name='会话状态'
                )),
                ('current_question_index', models.IntegerField(default=0, verbose_name='当前题目索引')),
                ('total_questions', models.IntegerField(default=0, verbose_name='总题目数')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='开始时间')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='结束时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('room_name', models.CharField(max_length=100, unique=True, verbose_name='房间名称')),
                ('learning_goal', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='teaching.learninggoal',
                    verbose_name='学习目标'
                )),
                ('students', models.ManyToManyField(
                    related_name='participated_sessions',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='参与学生'
                )),
                ('teacher', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='guided_sessions',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='指导老师'
                )),
            ],
            options={
                'verbose_name': '指导练习会话',
                'verbose_name_plural': '指导练习会话',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='GuidedPracticeQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_order', models.IntegerField(verbose_name='题目顺序')),
                ('question_type', models.CharField(
                    choices=[
                        ('multiple_choice', '选择题'),
                        ('fill_blank', '填空题'),
                        ('translation', '翻译题'),
                    ],
                    default='multiple_choice',
                    max_length=20,
                    verbose_name='题目类型'
                )),
                ('options', models.JSONField(default=list, verbose_name='选项列表')),
                ('correct_answer', models.IntegerField(verbose_name='正确答案索引')),
                ('time_limit', models.IntegerField(default=30, verbose_name='答题时限(秒)')),
                ('is_active', models.BooleanField(default=False, verbose_name='是否激活')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='开始时间')),
                ('ended_at', models.DateTimeField(blank=True, null=True, verbose_name='结束时间')),
                ('session', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='questions',
                    to='teaching.guidedpracticesession',
                    verbose_name='练习会话'
                )),
                ('word', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='words.word',
                    verbose_name='单词'
                )),
            ],
            options={
                'verbose_name': '指导练习题目',
                'verbose_name_plural': '指导练习题目',
                'ordering': ['question_order'],
            },
        ),
        migrations.CreateModel(
            name='GuidedPracticeAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected_answer', models.IntegerField(verbose_name='选择的答案')),
                ('is_correct', models.BooleanField(verbose_name='是否正确')),
                ('response_time', models.FloatField(verbose_name='响应时间(秒)')),
                ('answered_at', models.DateTimeField(auto_now_add=True, verbose_name='答题时间')),
                ('question', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='answers',
                    to='teaching.guidedpracticequestion',
                    verbose_name='题目'
                )),
                ('student', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='学生'
                )),
            ],
            options={
                'verbose_name': '指导练习答案',
                'verbose_name_plural': '指导练习答案',
                'ordering': ['-answered_at'],
            },
        ),
        
        # Add foreign key relationships
        migrations.AddField(
            model_name='learningsession',
            name='guided_session',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='teaching.guidedpracticesession',
                verbose_name='指导练习会话'
            ),
        ),
        migrations.AddField(
            model_name='wordlearningrecord',
            name='guided_question',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='teaching.guidedpracticequestion',
                verbose_name='指导练习题目'
            ),
        ),
        
        # Add unique constraints
        migrations.AlterUniqueTogether(
            name='guidedpracticequestion',
            unique_together={('session', 'question_order')},
        ),
        migrations.AlterUniqueTogether(
            name='guidedpracticeanswer',
            unique_together={('question', 'student')},
        ),
    ]