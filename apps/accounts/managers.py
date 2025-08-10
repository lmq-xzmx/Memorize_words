from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """自定义用户管理器"""
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        """创建普通用户"""
        if not username:
            raise ValueError('用户名不能为空')
        
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """创建超级用户"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级用户必须设置is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须设置is_superuser=True')
        
        return self.create_user(username, email, password, **extra_fields)
    
    def get_by_role(self, role):
        """根据角色获取用户"""
        return self.filter(role=role)
    
    def get_active_users(self):
        """获取活跃用户"""
        return self.filter(is_active_account=True, is_active=True)
    
    def get_students(self):
        """获取学生用户"""
        return self.filter(role='student', is_active_account=True)
    
    def get_teachers(self):
        """获取教师用户"""
        return self.filter(role='teacher', is_active_account=True)
    
    def get_parents(self):
        """获取家长用户"""
        return self.filter(role='parent', is_active_account=True)