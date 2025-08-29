from django import forms
from django.core.exceptions import ValidationError
from .models import RoleSlotMenuAssignment, MenuModuleConfig, SlotConfig
from apps.accounts.models import UserRole


class RoleSlotMenuAssignmentForm(forms.ModelForm):
    """角色槽位菜单分配原生Django表单"""
    
    class Meta:
        model = RoleSlotMenuAssignment
        fields = ['role', 'slot_position', 'root_menu', 'menu_status', 'is_active', 'sort_order']
        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_role',
                'onchange': 'updateSlotOptions(this.value)'
            }),
            'slot_position': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_slot_position',
                'min': '1',
                'onchange': 'validateSlotPosition(this.value)'
            }),
            'root_menu': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_root_menu'
            }),
            'menu_status': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_menu_status'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_is_active'
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_sort_order',
                'min': '0'
            })
        }
        labels = {
            'role': '角色',
            'slot_position': '槽位位置',
            'root_menu': '根菜单',
            'menu_status': '菜单状态',
            'is_active': '是否激活',
            'sort_order': '排序'
        }
        help_texts = {
            'role': '选择要配置的角色',
            'slot_position': '选择槽位位置（1-N）',
            'root_menu': '选择要分配的根菜单',
            'menu_status': '设置菜单状态',
            'is_active': '是否激活此配置',
            'sort_order': '排序优先级（数字越小越靠前）'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 动态设置角色选择项（从SlotConfig获取）
        role_choices = [('', '请选择角色...')]
        active_slot_configs = SlotConfig.objects.filter(is_active=True)
        for slot_config in active_slot_configs:
            role_display = dict(UserRole.choices).get(slot_config.role, slot_config.role)
            role_choices.append((slot_config.role, f"{role_display} ({slot_config.name})"))
        
        self.fields['role'].choices = role_choices
        
        # 设置根菜单选择项
        menu_choices = [('', '请选择根菜单...')]
        root_menus = MenuModuleConfig.objects.filter(menu_level='root', is_active=True)
        for menu in root_menus:
            menu_choices.append((menu.id, menu.name))
        
        self.fields['root_menu'].choices = menu_choices
        
        # 设置菜单状态选择项
        self.fields['menu_status'].choices = RoleSlotMenuAssignment.MENU_STATUS_CHOICES
        
        # 设置默认值
        if not self.instance.pk:
            self.fields['is_active'].initial = True
            self.fields['menu_status'].initial = 'active'
    
    def clean_role(self):
        """验证角色"""
        role = self.cleaned_data.get('role')
        if not role:
            raise ValidationError('请选择角色')
        
        # 验证角色是否有有效的槽位配置
        slot_config = SlotConfig.objects.filter(role=role, is_active=True).first()
        if not slot_config:
            raise ValidationError(f'角色 {role} 没有有效的槽位配置')
        
        return role
    
    def clean_slot_position(self):
        """验证槽位位置"""
        slot_position = self.cleaned_data.get('slot_position')
        role = self.cleaned_data.get('role')
        
        if not slot_position:
            raise ValidationError('请输入槽位位置')
        
        if slot_position < 1:
            raise ValidationError('槽位位置必须大于0')
        
        if role:
            # 验证槽位位置是否超出最大槽位数
            slot_config = SlotConfig.objects.filter(role=role, is_active=True).first()
            if slot_config and slot_position > slot_config.slot_count:
                raise ValidationError(f'槽位位置 {slot_position} 超出最大槽位数 {slot_config.slot_count}')
        
        return slot_position
    
    def clean_root_menu(self):
        """验证根菜单"""
        root_menu = self.cleaned_data.get('root_menu')
        if not root_menu:
            raise ValidationError('请选择根菜单')
        return root_menu
    
    def clean(self):
        """表单整体验证"""
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        slot_position = cleaned_data.get('slot_position')
        
        if role and slot_position:
            # 检查槽位是否已被占用（编辑时排除当前记录）
            existing_query = RoleSlotMenuAssignment.objects.filter(
                role=role,
                slot_position=slot_position,
                is_active=True
            )
            
            if self.instance.pk:
                existing_query = existing_query.exclude(pk=self.instance.pk)
            
            if existing_query.exists():
                raise ValidationError(f'角色 {role} 的槽位 {slot_position} 已被占用')
        
        return cleaned_data
    
    def save(self, commit=True):
        """保存表单"""
        instance = super().save(commit=False)
        
        # 如果没有设置排序，使用槽位位置作为默认排序
        if not instance.sort_order:
            instance.sort_order = instance.slot_position
        
        if commit:
            instance.save()
        
        return instance