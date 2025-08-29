from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from .managers import CustomUserManager
import json


class UserRole(models.TextChoices):
    """用户角色 - 统一角色管理中心"""
    STUDENT = 'student', '学生'
    PARENT = 'parent', '家长'
    TEACHER = 'teacher', '自由老师'
    ADMIN = 'admin', '管理员'
    DEAN = 'dean', '教导主任'
    ACADEMIC_DIRECTOR = 'academic_director', '教务主任'
    RESEARCH_LEADER = 'research_leader', '教研组长'
    PROJECT_ASSISTANT = 'project_assistant', '项目助理'
    PROJECT_MANAGER_ASSISTANT = 'project_manager_assistant', '项目管理助理'
    
    @classmethod
    def get_role_hierarchy(cls):
        """获取角色层级关系"""
        return {
            cls.ADMIN: {'level': 0, 'parent': None, 'children': [cls.DEAN, cls.ACADEMIC_DIRECTOR, cls.RESEARCH_LEADER, cls.TEACHER, cls.PARENT]},
            cls.DEAN: {'level': 1, 'parent': cls.ADMIN, 'children': [cls.ACADEMIC_DIRECTOR, cls.RESEARCH_LEADER, cls.TEACHER]},
            cls.ACADEMIC_DIRECTOR: {'level': 2, 'parent': cls.DEAN, 'children': [cls.TEACHER]},
            cls.RESEARCH_LEADER: {'level': 2, 'parent': cls.DEAN, 'children': [cls.TEACHER]},
            cls.TEACHER: {'level': 3, 'parent': [cls.ADMIN, cls.DEAN, cls.ACADEMIC_DIRECTOR, cls.RESEARCH_LEADER], 'children': [cls.STUDENT]},
            cls.PARENT: {'level': 3, 'parent': cls.ADMIN, 'children': [cls.STUDENT]},
            cls.STUDENT: {'level': 4, 'parent': [cls.TEACHER, cls.PARENT], 'children': []}
        }
    
    @classmethod
    def get_role_permissions(cls, role):
        """获取角色默认权限"""
        permissions_map = {
            cls.ADMIN: ['add_user', 'change_user', 'delete_user', 'view_user', 'manage_roles', 'manage_permissions'],
            cls.DEAN: ['view_user', 'change_user', 'manage_academic', 'manage_teaching', 'view_reports'],
            cls.ACADEMIC_DIRECTOR: ['view_user', 'manage_curriculum', 'manage_teaching', 'view_academic_reports'],
            cls.RESEARCH_LEADER: ['view_user', 'manage_research', 'manage_teaching_methods', 'view_research_reports'],
            cls.TEACHER: ['view_user', 'change_student', 'view_student', 'manage_teaching'],
            cls.PARENT: ['view_student', 'view_own_children'],
            cls.STUDENT: ['view_own_profile', 'change_own_profile']
        }
        return permissions_map.get(role, [])
    
    @classmethod
    def can_manage_role(cls, manager_role, target_role):
        """判断是否可以管理指定角色"""
        hierarchy = cls.get_role_hierarchy()
        manager_level = hierarchy.get(manager_role, {}).get('level', 999)
        target_level = hierarchy.get(target_role, {}).get('level', 999)
        return manager_level < target_level


class CustomUser(AbstractUser):
    """英语学习平台用户模型"""
    
    # 基础信息
    role = models.CharField('用户角色', max_length=30, choices=UserRole.choices, default=UserRole.STUDENT)
    phone = models.CharField('手机号码', max_length=20, validators=[RegexValidator(r'^[\d\-\+\(\)\s]+$')], blank=False)
    real_name = models.CharField('真实姓名', max_length=100, blank=True)
    nickname = models.CharField('网名', max_length=50, blank=True, unique=True, null=True, help_text='选填，不可与他人相同')
    notes = models.TextField('备注', max_length=500, blank=True, help_text='最多500字符')
    is_active = models.BooleanField('账号状态', default=True, help_text='取消勾选表示禁用账号')
    
    # 管理员角色审批状态
    admin_approval_status = models.CharField(
        '管理员审批状态', 
        max_length=20, 
        choices=[
            ('pending', '待审批'),
            ('approved', '已通过'),
            ('rejected', '已拒绝')
        ],
        default='approved',
        help_text='仅管理员角色需要审批'
    )
    
    # 学习相关字段
    grade_level = models.CharField('年级', max_length=20, blank=True, help_text='如：小学三年级、初中一年级等')
    english_level = models.CharField('英语水平', max_length=20, blank=True, 
                                   choices=[
                                       ('beginner', '初级'),
                                       ('elementary', '基础'),
                                       ('intermediate', '中级'),
                                       ('advanced', '高级'),
                                   ])
    
    # 移除了家长关联字段，改用角色增项系统管理用户关系

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'

    def __str__(self):
        role_display = dict(UserRole.choices).get(self.role, self.role)
        return f"{self.real_name or self.username} ({role_display})"
    
    # 移除了 @property is_active，直接使用数据库字段
    
    def auto_assign_group(self):
        """根据角色自动分配用户组"""
        # 角色与组的映射关系
        role_group_mapping = {
            UserRole.ADMIN: '管理员组',
            UserRole.DEAN: '教导主任组',
            UserRole.ACADEMIC_DIRECTOR: '教务主任组',
            UserRole.RESEARCH_LEADER: '教研组长组',
            UserRole.TEACHER: '教师组',
            UserRole.STUDENT: '学生组',
            UserRole.PARENT: '家长组',
        }
        
        group_name = role_group_mapping.get(self.role)
        if group_name:
            # 获取或创建对应的组
            group, created = Group.objects.get_or_create(name=group_name)
            
            # 清除用户现有的所有组
            self.groups.clear()
            
            # 添加用户到对应组
            self.groups.add(group)
            
            if created:
                print(f"创建新用户组: {group_name}")
            print(f"用户 {self.username} 已分配到 {group_name}")


@receiver(post_save, sender=CustomUser)
def auto_assign_user_group(sender, instance, created, **kwargs):
    """用户保存后自动分配组"""
    if created or kwargs.get('update_fields'):
        # 使用基础的组分配方法
        instance.auto_assign_group()


class UserLoginLog(models.Model):
    """用户登录日志"""
    username = models.CharField('用户名', max_length=150)
    login_time = models.DateTimeField('登录时间', auto_now_add=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('用户代理', blank=True)
    login_success = models.BooleanField('登录成功')

    class Meta:
        verbose_name = '登录日志'
        verbose_name_plural = '登录日志管理'
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.username} - {self.login_time}"


class RoleApproval(models.Model):
    """角色审批模型"""
    APPROVAL_STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已通过'),
        ('rejected', '已拒绝')
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='申请用户')
    requested_role = models.CharField('申请角色', max_length=30, choices=UserRole.choices)
    current_role = models.CharField('当前角色', max_length=30, choices=UserRole.choices)
    status = models.CharField('审批状态', max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    reason = models.TextField('申请理由', max_length=500, blank=True)
    admin_comment = models.TextField('管理员备注', max_length=500, blank=True)
    approved_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_roles',
        verbose_name='审批人'
    )
    created_at = models.DateTimeField('申请时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '注册管理员审批'
        verbose_name_plural = '注册管理员审批'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} 申请管理员角色 - {self.status}"


class LearningProfile(models.Model):
    """学习档案"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name='用户')
    total_study_time = models.PositiveIntegerField('总学习时长(分钟)')
    completed_lessons = models.PositiveIntegerField('完成课程数')
    current_streak = models.PositiveIntegerField('连续学习天数')
    max_streak = models.PositiveIntegerField('最长连续学习天数')
    last_study_date = models.DateField('最后学习日期', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '学习档案'
        verbose_name_plural = '学习档案管理'

    def __str__(self):
        return f"{self.user.username} 的学习档案"


class RoleTemplate(models.Model):
    """角色模板模型 - 统一管理角色增项配置"""
    role = models.CharField('角色', max_length=30, choices=UserRole.choices, unique=True, help_text='绑定的用户角色')
    template_name = models.CharField('模板名称', max_length=100, help_text='角色模板的显示名称')
    description = models.TextField('模板描述', blank=True, help_text='模板的详细描述')
    version = models.CharField('模板版本', max_length=20, default='1.0.0', help_text='模板版本号')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_role_templates',
        verbose_name='创建者'
    )
    
    class Meta:
        verbose_name = '角色模板'
        verbose_name_plural = '角色模板管理'
        ordering = ['role']
    
    def __str__(self):
        return f"{self.template_name} ({self.role})"
    
    def get_field_count(self):
        """获取模板字段数量"""
        return RoleExtension.objects.filter(role_template=self, is_active=True).count()
    
    def get_user_count(self):
        """获取使用此模板的用户数量"""
        return CustomUser.objects.filter(role=self.role, is_active=True).count()


class RoleExtension(models.Model):
    """角色增项配置模型 - 重构为基于模板的字段配置"""
    FIELD_TYPE_CHOICES = [
        ('text', '文本字段'),
        ('textarea', '多行文本'),
        ('number', '数字字段'),
        ('email', '邮箱字段'),
        ('date', '日期字段'),
        ('choice', '选择字段'),
        ('boolean', '布尔字段'),
        ('url', 'URL字段'),
        ('phone', '电话字段'),
        ('file', '文件字段'),
        ('image', '图片字段'),
    ]
    
    # 关联到角色模板
    role_template = models.ForeignKey(
        RoleTemplate,
        on_delete=models.CASCADE,
        related_name='template_fields',
        verbose_name='所属模板',
        null=True,
        blank=True
    )
    # 保持向后兼容
    role = models.CharField('角色', max_length=30, choices=UserRole.choices, help_text='绑定的用户角色')
    field_name = models.CharField('字段名称', max_length=50, help_text='字段的内部名称，用于API和数据库存储')
    field_label = models.CharField('字段标签', max_length=100, help_text='显示给用户的字段名称')
    field_type = models.CharField('字段类型', max_length=20, choices=FIELD_TYPE_CHOICES, default='text')
    field_choices = models.TextField('选择项', blank=True, help_text='JSON格式的选择项，仅当字段类型为choice时使用，格式：[["value1", "显示名1"], ["value2", "显示名2"]]')
    is_required = models.BooleanField('是否必填', default=False)
    help_text = models.CharField('帮助文本', max_length=200, blank=True)
    default_value = models.TextField('默认值', blank=True, help_text='字段的默认值')
    
    # 显示控制字段
    show_in_frontend_register = models.BooleanField('前台注册显示', default=True, help_text='是否在前台注册页面显示此字段')
    show_in_backend_admin = models.BooleanField('后台管理显示', default=True, help_text='是否在后台管理界面显示此字段')
    show_in_profile = models.BooleanField('个人资料显示', default=True, help_text='是否在个人资料页面显示此字段')
    
    # 验证规则
    validation_rules = models.TextField('验证规则', blank=True, help_text='JSON格式的验证规则')
    
    sort_order = models.IntegerField('排序', default=0, help_text='字段显示顺序，数字越小越靠前')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '角色增项配置'
        verbose_name_plural = '角色增项配置管理'
        unique_together = [['role_template', 'field_name'], ['role', 'field_name']]
        ordering = ['role', 'sort_order', 'field_name']
    
    def __str__(self):
        return f"{self.role} - {self.field_label}"
    
    def get_choices_list(self):
        """获取选择项列表"""
        if self.field_choices:
            try:
                return json.loads(self.field_choices)
            except json.JSONDecodeError:
                return []
        return []
    
    def get_validation_rules(self):
        """获取验证规则"""
        if self.validation_rules:
            try:
                return json.loads(self.validation_rules)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def save(self, *args, **kwargs):
        """保存时自动设置角色模板"""
        if not hasattr(self, 'role_template') or not self.role_template and self.role:
            template, created = RoleTemplate.objects.get_or_create(
                role=self.role,
                defaults={
                    'template_name': f'{dict(UserRole.choices).get(self.role, self.role)}模板',
                    'description': f'{dict(UserRole.choices).get(self.role, self.role)}角色的增项模板',
                    'version': '1.0.0'
                }
            )
            self.role_template = template
        super().save(*args, **kwargs)


class RoleUserGroup(models.Model):
    """角色用户组配置模型"""
    name = models.CharField('组名称', max_length=100, help_text='用户组的显示名称')
    role = models.CharField('绑定角色', max_length=30, choices=UserRole.choices, help_text='绑定的用户角色')
    description = models.TextField('组描述', blank=True, help_text='用户组的详细描述')
    users = models.ManyToManyField(
        CustomUser, 
        verbose_name='组成员', 
        blank=True,
        help_text='选择该角色下的用户加入此组',
        limit_choices_to={'is_active': True}
    )
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_role_groups',
        verbose_name='创建者'
    )
    
    class Meta:
        verbose_name = '角色所辖用户'
        verbose_name_plural = '角色所辖用户'
        ordering = ['role', 'name']
    
    def __str__(self):
        role_display = dict(UserRole.choices).get(self.role, self.role)
        return f"{role_display} - {self.name}"
    
    def get_user_count(self):
        """获取组内用户数量"""
        return self.users.count()
    
    def get_role_display_name(self):
        """获取角色显示名称"""
        return dict(UserRole.choices).get(self.role, self.role)


class UserExtensionData(models.Model):
    """用户角色增项数据"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='用户')
    role_extension = models.ForeignKey(RoleExtension, on_delete=models.CASCADE, verbose_name='角色增项')
    field_value = models.TextField('字段值', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '角色所辖用户增项'
        verbose_name_plural = '角色所辖用户增项'
        unique_together = ['user', 'role_extension']
    
    def __str__(self):
        return f"{self.user.username} - {self.role_extension.field_label}: {self.field_value}"


# ==================== 简化的角色增项系统 ====================
# 移除了过度设计的RoleLevel、RoleUser、UserExtension模型
# 保留核心的RoleExtension和UserExtensionData模型，简化系统架构


# 简化的信号处理器已移除，减少系统复杂度