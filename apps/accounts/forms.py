from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from .models import CustomUser, UserRole


class CustomUserCreationForm(UserCreationForm):
    """自定义用户创建表单"""
    real_name = forms.CharField(
        max_length=100,
        required=True,
        label='真实姓名',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入真实姓名'})
    )
    email = forms.EmailField(
        required=True,
        label='邮箱',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱地址'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label='手机号',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入手机号'})
    )
    role = forms.ChoiceField(
        choices=UserRole.choices,
        required=True,
        label='角色',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'real_name', 'email', 'phone', 'role', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '请输入密码'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '请确认密码'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被注册')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError('该手机号已被注册')
        return phone


class CustomUserChangeForm(UserChangeForm):
    """自定义用户修改表单"""
    password = None  # 移除密码字段
    
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('username', 'real_name', 'email', 'phone', 'role', 'grade_level', 
                 'english_level', 'is_active', 'notes')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'real_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'grade_level': forms.TextInput(attrs={'class': 'form-control'}),
            'english_level': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProfileForm(forms.ModelForm):
    """个人资料编辑表单"""
    
    class Meta:
        model = CustomUser
        fields = ('real_name', 'email', 'phone', 'grade_level', 'english_level')
        widgets = {
            'real_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'grade_level': forms.TextInput(attrs={'class': 'form-control'}),
            'english_level': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'real_name': '真实姓名',
            'email': '邮箱',
            'phone': '手机号',
            'grade_level': '年级',
            'english_level': '英语水平',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('该邮箱已被其他用户使用')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and CustomUser.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('该手机号已被其他用户使用')
        return phone


class CustomLoginForm(forms.Form):
    """自定义登录表单"""
    username = forms.CharField(
        max_length=150,
        label='用户名/邮箱/手机号',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入用户名、邮箱或手机号',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label='记住我',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError('用户名或密码错误')
            elif not self.user_cache.is_active:
                raise forms.ValidationError('该账号已被禁用')
            # is_active 字段已经在上面检查过了，无需重复检查
        
        return self.cleaned_data
    
    def get_user(self):
        return getattr(self, 'user_cache', None)


class PasswordChangeForm(forms.Form):
    """密码修改表单"""
    old_password = forms.CharField(
        label='原密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入原密码'})
    )
    new_password1 = forms.CharField(
        label='新密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入新密码'})
    )
    new_password2 = forms.CharField(
        label='确认新密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入新密码'})
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('原密码错误')
        return old_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError('两次输入的新密码不一致')
            if len(new_password1) < 6:
                raise forms.ValidationError('密码长度至少6位')
        
        return cleaned_data
    
    def save(self):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user