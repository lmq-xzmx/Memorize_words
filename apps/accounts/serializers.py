from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, UserRole, LearningProfile, UserLoginLog, RoleExtension, UserExtensionData


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'real_name', 'phone', 'role',
            'grade_level', 'is_active',
            'date_joined', 'last_login', 'password', 'confirm_password'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        """验证数据"""
        if 'password' in attrs and 'confirm_password' in attrs:
            if attrs['password'] != attrs['confirm_password']:
                raise serializers.ValidationError({
                    'confirm_password': '两次输入的密码不一致'
                })
        return attrs
    
    def create(self, validated_data):
        """创建用户"""
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class RoleExtensionSerializer(serializers.ModelSerializer):
    """角色增项序列化器"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    field_type_display = serializers.CharField(source='get_field_type_display', read_only=True)
    
    class Meta:
        model = RoleExtension
        fields = [
            'id', 'role', 'role_display', 'field_name', 'field_label',
            'field_type', 'field_type_display', 'field_choices', 'is_required',
            'help_text', 'sort_order', 'is_active', 'show_in_frontend_register',
            'show_in_backend_admin', 'show_in_profile', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserExtensionDataSerializer(serializers.ModelSerializer):
    """用户扩展数据序列化器"""
    extension_field_label = serializers.CharField(source='extension.field_label', read_only=True)
    extension_field_type = serializers.CharField(source='extension.field_type', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserExtensionData
        fields = [
            'id', 'user', 'user_username', 'extension', 'extension_field_label',
            'extension_field_type', 'value', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RoleExtensionListSerializer(serializers.ModelSerializer):
    """角色增项列表序列化器（简化版）"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    field_type_display = serializers.CharField(source='get_field_type_display', read_only=True)
    
    class Meta:
        model = RoleExtension
        fields = [
            'id', 'role', 'role_display', 'field_name', 'field_label',
            'field_type', 'field_type_display', 'is_required', 'is_active',
            'show_in_frontend_register', 'show_in_backend_admin', 'show_in_profile'
        ]


class DynamicRegisterSerializer(serializers.ModelSerializer):
    """动态注册序列化器 - 根据角色动态生成字段"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    extension_data = serializers.DictField(required=False, allow_empty=True, help_text='角色增项数据')
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'real_name', 'phone', 'nickname', 'role',
            'grade_level', 'password', 'confirm_password', 'extension_data'
        ]
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True},
            'phone': {'required': True},
            'nickname': {'required': False, 'allow_blank': True}
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 如果提供了角色信息，动态添加角色增项字段
        role = None
        if 'data' in kwargs and kwargs.get('data'):
            data = kwargs['data']
            if isinstance(data, dict):
                role = data.get('role')
        elif hasattr(self, 'initial_data') and self.initial_data:
            if isinstance(self.initial_data, dict):
                role = self.initial_data.get('role')
        
        if role:
            self._add_role_extension_fields(role)
    
    def _add_role_extension_fields(self, role):
        """根据角色动态添加增项字段"""
        extensions = RoleExtension.objects.filter(
            role=role,
            is_active=True,
            show_in_frontend_register=True
        ).order_by('sort_order', 'field_name')
        
        for extension in extensions:
            field_kwargs = {
                'required': extension.is_required,
                'help_text': extension.help_text,
                'allow_blank': not extension.is_required,
                'label': extension.field_label
            }
            
            # 根据字段类型创建对应的序列化器字段
            if extension.field_type == 'text':
                field = serializers.CharField(**field_kwargs)
            elif extension.field_type == 'textarea':
                field = serializers.CharField(style={'base_template': 'textarea.html'}, **field_kwargs)
            elif extension.field_type == 'number':
                field = serializers.IntegerField(**field_kwargs)
            elif extension.field_type == 'email':
                field = serializers.EmailField(**field_kwargs)
            elif extension.field_type == 'date':
                field = serializers.DateField(**field_kwargs)
            elif extension.field_type == 'choice':
                choices = extension.get_choices_list()
                field = serializers.ChoiceField(choices=choices, **field_kwargs)
            elif extension.field_type == 'boolean':
                field = serializers.BooleanField(**field_kwargs)
            elif extension.field_type == 'url':
                field = serializers.URLField(**field_kwargs)
            elif extension.field_type == 'phone':
                field = serializers.CharField(max_length=20, **field_kwargs)
            else:
                field = serializers.CharField(**field_kwargs)
            
            # 添加字段到序列化器
            self.fields[f'ext_{extension.field_name}'] = field
    
    def validate_username(self, value):
        """验证用户名"""
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError('该用户名已存在')
        return value
    
    def validate_nickname(self, value):
        """验证网名"""
        if value and value.strip():
            if CustomUser.objects.filter(nickname=value).exists():
                raise serializers.ValidationError('该网名已被使用')
            return value.strip()
        return None
    
    def validate_phone(self, value):
        """验证手机号"""
        if not value or not value.strip():
            raise serializers.ValidationError('手机号为必填项')
        return value
    
    def validate_email(self, value):
        """验证邮箱唯一性"""
        # 如果邮箱为空，直接返回None
        if not value or value.strip() == '':
            return None
            
        # 检查邮箱是否已存在
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱已被注册')
        return value
    
    def validate(self, attrs):
        """验证数据"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': '两次输入的密码不一致'
            })
        return attrs
    
    def create(self, validated_data):
        """创建用户并保存扩展数据"""
        # 移除确认密码字段
        validated_data.pop('confirm_password', None)
        
        # 移除扩展数据字段
        extension_data = validated_data.pop('extension_data', {})
        
        # 处理动态增项字段
        dynamic_extension_data = {}
        fields_to_remove = []
        
        # 创建validated_data的副本来遍历，避免在遍历时修改字典
        for field_name in list(validated_data.keys()):
            if field_name.startswith('ext_'):
                # 提取真实的字段名
                real_field_name = field_name[4:]  # 移除 'ext_' 前缀
                dynamic_extension_data[real_field_name] = validated_data[field_name]
                fields_to_remove.append(field_name)
        
        # 移除动态字段，避免传递给用户创建
        for field_name in fields_to_remove:
            validated_data.pop(field_name, None)
        
        # 合并扩展数据
        if dynamic_extension_data:
            extension_data.update(dynamic_extension_data)
        
        # 提取密码
        password = validated_data.pop('password')
        role = validated_data.get('role', 'student')
        
        # 处理空邮箱
        if 'email' in validated_data and not validated_data['email']:
            validated_data['email'] = None
        
        # 处理空网名
        if 'nickname' in validated_data and not validated_data['nickname']:
            validated_data['nickname'] = None
            
        # 如果申请管理员角色，设置为待审批状态
        if role == 'admin':
            validated_data['admin_approval_status'] = 'pending'
            validated_data['is_active'] = False  # 待审批期间账号不可用
        
        # 创建用户，只传递CustomUser模型支持的字段
        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )
        
        # 保存扩展数据
        if extension_data:
            extensions = RoleExtension.objects.filter(
                role=user.role,
                is_active=True,
                show_in_frontend_register=True
            )
            
            for extension in extensions:
                if isinstance(extension_data, dict) and extension.field_name in extension_data:
                    UserExtensionData.objects.create(
                        user=user,
                        role_extension=extension,
                        field_value=str(extension_data[extension.field_name])
                    )
        
        # 为申请管理员角色的用户创建审批记录
        if role == 'admin':
            from .models import RoleApproval
            RoleApproval.objects.create(
                user=user,
                requested_role='admin',
                current_role='student',  # 默认当前角色为学生
                reason='申请管理员角色'
            )
            
        return user


class RegisterWithExtensionSerializer(DynamicRegisterSerializer):
    """带扩展字段的注册序列化器（保持向后兼容）"""
    pass
    
    def validate_username(self, value):
        """验证用户名"""
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError('该用户名已存在')
        return value
    
    def validate_nickname(self, value):
        """验证网名"""
        if value and value.strip():
            if CustomUser.objects.filter(nickname=value).exists():
                raise serializers.ValidationError('该网名已被使用')
            return value.strip()
        return None
    
    def validate_phone(self, value):
        """验证手机号"""
        if not value or not value.strip():
            raise serializers.ValidationError('手机号为必填项')
        return value
    
    def validate_email(self, value):
        """验证邮箱唯一性"""
        # 如果邮箱为空，直接返回None
        if not value or value.strip() == '':
            return None
            
        # 检查邮箱是否已存在
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱已被注册')
        return value
    
    def validate_extension_data(self, value):
        """验证扩展数据"""
        if not value:
            return {}
        
        role = 'student'  # 默认角色
        if hasattr(self, 'initial_data') and self.initial_data and isinstance(self.initial_data, dict):
            role = self.initial_data.get('role', 'student')
        
        # 获取该角色的所有扩展字段
        extensions = RoleExtension.objects.filter(
            role=role,
            is_active=True,
            show_in_frontend_register=True
        )
        
        # 验证必填字段
        for extension in extensions:
            if extension.is_required and extension.field_name not in value:
                raise serializers.ValidationError({
                    extension.field_name: f'{extension.field_label}为必填项'
                })
        
        return value
    
    def validate(self, attrs):
        """验证数据"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': '两次输入的密码不一致'
            })
        return attrs
    
    def update(self, instance, validated_data):
        """更新用户"""
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    """用户个人资料序列化器"""
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'real_name', 'phone',
            'grade_level', 'role',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'username', 'role', 'date_joined', 'last_login']


class UserListSerializer(serializers.ModelSerializer):
    """用户列表序列化器（简化版）"""
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'real_name', 'email', 'role',
            'is_active', 'date_joined', 'last_login'
        ]


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """验证登录信息"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('用户名或密码错误')
            
            if not user.is_active:
                raise serializers.ValidationError('账号已被禁用')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('必须提供用户名和密码')


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        """验证旧密码"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value
    
    def validate(self, attrs):
        """验证新密码"""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': '两次输入的新密码不一致'
            })
        return attrs
    
    def save(self, **kwargs):
        """保存新密码"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class LearningProfileSerializer(serializers.ModelSerializer):
    """学习档案序列化器"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = LearningProfile
        fields = [
            'id', 'user', 'user_username', 'learning_goals',
            'preferred_difficulty', 'daily_target', 'study_time_preference',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class UserLoginLogSerializer(serializers.ModelSerializer):
    """用户登录日志序列化器"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserLoginLog
        fields = [
            'id', 'user', 'user_username', 'login_time',
            'ip_address', 'user_agent', 'is_successful'
        ]
        read_only_fields = ['user', 'login_time']


class RegisterSerializer(serializers.ModelSerializer):
    """注册序列化器"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'real_name', 'phone', 'nickname', 'role',
            'grade_level', 'password', 'confirm_password'
        ]
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True},
            'phone': {'required': True},
            'nickname': {'required': False, 'allow_blank': True}
        }
    
    def validate_username(self, value):
        """验证用户名"""
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError('该用户名已存在')
        return value
    
    def validate_nickname(self, value):
        """验证网名"""
        if value and value.strip():
            if CustomUser.objects.filter(nickname=value).exists():
                raise serializers.ValidationError('该网名已被使用')
            return value.strip()
        return None
    
    def validate_phone(self, value):
        """验证手机号"""
        if not value or not value.strip():
            raise serializers.ValidationError('手机号为必填项')
        return value
    
    def validate_email(self, value):
        """验证邮箱唯一性"""
        # 如果邮箱为空，直接返回None
        if not value or value.strip() == '':
            return None
            
        # 检查邮箱是否已存在
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱已被注册')
        return value
    
    def validate(self, attrs):
        """验证数据"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': '两次输入的密码不一致'
            })
        return attrs
    
    def create(self, validated_data):
        """创建用户"""
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        role = validated_data.get('role', 'student')
        
        # 处理空邮箱
        if 'email' in validated_data and not validated_data['email']:
            validated_data['email'] = None
        
        # 处理空网名
        if 'nickname' in validated_data and not validated_data['nickname']:
            validated_data['nickname'] = None
            
        # 如果申请管理员角色，设置为待审批状态
        if role == 'admin':
            validated_data['admin_approval_status'] = 'pending'
            validated_data['is_active'] = False  # 待审批期间账号不可用
            
        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )
        
        # 为申请管理员角色的用户创建审批记录
        if validated_data.get('role') == UserRole.ADMIN:
            from .models import RoleApproval
            RoleApproval.objects.create(
                user=user,
                requested_role=UserRole.ADMIN,
                current_role=UserRole.STUDENT,  # 默认当前角色为学生
                reason=validated_data.get('reason', '申请管理员角色')
            )
            
        return user