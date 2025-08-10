# Generated manually to remove parent and children fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_create_role_hierarchy_models'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='children',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='parent',
        ),
    ]