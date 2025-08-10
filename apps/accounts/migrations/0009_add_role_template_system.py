# Generated manually for role template system upgrade

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0008_create_role_hierarchy_models'),
    ]

    operations = [
        # 创建角色模板模型
        migrations.CreateModel(
            name='RoleTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('admin', '管理员'), ('teacher', '教师'), ('student', '学生'), ('parent', '家长')], help_text='绑定的用户角色', max_length=20, unique=True, verbose_name='角色')),
                ('template_name', models.CharField(help_text='角色模板的显示名称', max_length=100, verbose_name='模板名称')),
                ('description', models.TextField(blank=True, help_text='模板的详细描述', verbose_name='模板描述')),
                ('version', models.CharField(default='1.0.0', help_text='模板版本号', max_length=20, verbose_name='模板版本')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_role_templates', to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
            ],
            options={
                'verbose_name': '角色模板',
                'verbose_name_plural': '角色模板管理',
                'ordering': ['role'],
            },
        ),
        
        # 为RoleExtension添加role_template字段
        migrations.AddField(
            model_name='roleextension',
            name='role_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='template_fields', to='accounts.roletemplate', verbose_name='所属模板'),
        ),
        
        # 添加新字段
        migrations.AddField(
            model_name='roleextension',
            name='default_value',
            field=models.TextField(blank=True, help_text='字段的默认值', verbose_name='默认值'),
        ),
        
        migrations.AddField(
            model_name='roleextension',
            name='validation_rules',
            field=models.TextField(blank=True, help_text='JSON格式的验证规则', verbose_name='验证规则'),
        ),
        
        # 更新字段类型选择
        migrations.AlterField(
            model_name='roleextension',
            name='field_type',
            field=models.CharField(choices=[('text', '文本字段'), ('textarea', '多行文本'), ('number', '数字字段'), ('email', '邮箱字段'), ('date', '日期字段'), ('choice', '选择字段'), ('boolean', '布尔字段'), ('url', 'URL字段'), ('phone', '电话字段'), ('file', '文件字段'), ('image', '图片字段')], default='text', max_length=20, verbose_name='字段类型'),
        ),
        
        # 更新unique_together约束
        migrations.AlterUniqueTogether(
            name='roleextension',
            unique_together={('role_template', 'field_name'), ('role', 'field_name')},
        ),
    ]