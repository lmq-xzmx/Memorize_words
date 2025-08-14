# -*- coding: utf-8 -*-
"""
优化后的权限配置
根据优化后的权限配置方案.md实施的权限配置优化
"""

from apps.accounts.models import UserRole

# 优化后的学习目标权限配置
LEARNING_GOALS_PERMISSIONS = {
    UserRole.ADMIN: {
        'view': True,
        'create': True,
        'edit': True,
        'delete': True,
        'manage_all': True,
        'assign_to_users': True,
        'export': True,
        'analyze': True
    },
    UserRole.DEAN: {
        'view': True,
        'create': True,
        'edit': True,
        'delete': True,
        'manage_all': True,
        'assign_to_teachers': True,
        'export': True,
        'analyze': True
    },
    UserRole.ACADEMIC_DIRECTOR: {
        'view': True,
        'create': True,
        'edit': True,
        'delete': False,
        'manage_department': True,
        'assign_to_classes': True,
        'export': True,
        'analyze': True
    },
    UserRole.RESEARCH_LEADER: {
        'view': True,
        'create': False,
        'edit': 'own_group_only',  # 只能编辑本教研组的目标
        'delete': False,
        'manage_group': True,
        'suggest_improvements': True,
        'export': False,
        'analyze': True
    },
    UserRole.TEACHER: {
        'view': True,
        'create': 'class_goals_only',  # 只能为班级创建目标
        'edit': 'own_created_only',   # 只能编辑自己创建的目标
        'delete': 'own_created_only', # 只能删除自己创建的目标
        'manage_class': True,
        'track_student_progress': True,
        'export': False,
        'analyze': False
    },
    UserRole.PARENT: {
        'view': 'child_only',  # 只能查看子女的目标
        'create': False,
        'edit': False,
        'delete': False,
        'track_child_progress': True,
        'export': False,
        'analyze': False
    },
    UserRole.STUDENT: {
        'view': 'own_only',  # 只能查看自己的目标
        'create': 'personal_only',  # 只能创建个人目标
        'edit': 'own_personal_only',  # 只能编辑自己的个人目标
        'delete': 'own_personal_only',  # 只能删除自己的个人目标
        'track_own_progress': True,
        'export': False,
        'analyze': False
    }
}

# 优化后的学习计划权限配置
LEARNING_PLANS_PERMISSIONS = {
    UserRole.ADMIN: {
        'view': True,
        'create': True,
        'edit': True,
        'delete': True,
        'manage_all': True,
        'approve': True,
        'export': True,
        'analyze': True
    },
    UserRole.DEAN: {
        'view': True,
        'create': True,
        'edit': True,
        'delete': True,
        'manage_all': True,
        'approve': True,
        'export': True,
        'analyze': True
    },
    UserRole.ACADEMIC_DIRECTOR: {
        'view': True,
        'create': True,
        'edit': True,
        'delete': False,
        'manage_department': True,
        'approve': 'department_only',
        'export': True,
        'analyze': True
    },
    UserRole.RESEARCH_LEADER: {
        'view': True,
        'create': False,
        'edit': 'group_plans_only',
        'delete': False,
        'manage_group': True,
        'approve': 'group_only',  # 只能审批本教研组的计划
        'export': False,
        'analyze': True
    },
    UserRole.TEACHER: {
        'view': True,
        'create': 'student_plans_only',  # 只能为学生创建计划
        'edit': 'assigned_plans_only',   # 只能编辑分配给自己的计划
        'delete': False,
        'manage_class': True,
        'approve': 'student_plans_only',  # 只能审批学生计划
        'export': False,
        'analyze': False
    },
    UserRole.PARENT: {
        'view': 'child_only',  # 只能查看子女的计划
        'create': False,
        'edit': False,
        'delete': False,
        'approve': False,
        'track_child_progress': True,
        'export': False,
        'analyze': False
    },
    UserRole.STUDENT: {
        'view': 'own_only',  # 只能查看自己的计划
        'create': 'personal_only',  # 只能创建个人计划
        'edit': 'own_personal_only',  # 只能编辑自己的个人计划
        'delete': 'own_personal_only',  # 只能删除自己的个人计划
        'approve': False,
        'submit_for_approval': True,  # 可以提交计划供审批
        'track_own_progress': True,
        'export': False,
        'analyze': False
    }
}

# 优化后的菜单访问权限配置
MENU_PERMISSIONS = {
    # 根级菜单
    'dashboard': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: True,
        UserRole.RESEARCH_LEADER: True,
        UserRole.TEACHER: True,
        UserRole.PARENT: True,
        UserRole.STUDENT: True,
    },
    'learning': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: True,
        UserRole.RESEARCH_LEADER: True,
        UserRole.TEACHER: True,
        UserRole.PARENT: True,
        UserRole.STUDENT: True,
    },
    'teaching': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: True,
        UserRole.RESEARCH_LEADER: True,
        UserRole.TEACHER: True,
        UserRole.PARENT: False,
        UserRole.STUDENT: False,
    },
    'words': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: True,
        UserRole.RESEARCH_LEADER: True,
        UserRole.TEACHER: True,
        UserRole.PARENT: False,
        UserRole.STUDENT: False,
    },
    'accounts': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: False,
        UserRole.RESEARCH_LEADER: False,
        UserRole.TEACHER: False,
        UserRole.PARENT: False,
        UserRole.STUDENT: False,
    },
    'permissions': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: False,
        UserRole.RESEARCH_LEADER: False,
        UserRole.TEACHER: False,
        UserRole.PARENT: False,
        UserRole.STUDENT: False,
    },
    'access_dev_tools': {
        UserRole.ADMIN: True,
        UserRole.DEAN: False,
        UserRole.ACADEMIC_DIRECTOR: False,
        UserRole.RESEARCH_LEADER: False,
        UserRole.TEACHER: False,
        UserRole.PARENT: False,
        UserRole.STUDENT: False,
    },
    # 一级子菜单
    'learning_practice': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: True,
        UserRole.RESEARCH_LEADER: True,
        UserRole.TEACHER: True,
        UserRole.PARENT: False,
        UserRole.STUDENT: True,
    },
    'learning_progress': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: True,
        UserRole.RESEARCH_LEADER: True,
        UserRole.TEACHER: True,
        UserRole.PARENT: True,
        UserRole.STUDENT: True,
    },
    'teaching_plans': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: True,
        UserRole.RESEARCH_LEADER: True,
        UserRole.TEACHER: True,
        UserRole.PARENT: False,
        UserRole.STUDENT: False,
    },
    'teaching_goals': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: True,
        UserRole.RESEARCH_LEADER: False,
        UserRole.TEACHER: False,
        UserRole.PARENT: False,
        UserRole.STUDENT: False,
    },
    'words_vocabulary': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: True,
        UserRole.RESEARCH_LEADER: True,
        UserRole.TEACHER: True,
        UserRole.PARENT: False,
        UserRole.STUDENT: False,
    },
    'words_management': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: False,
        UserRole.RESEARCH_LEADER: False,
        UserRole.TEACHER: False,
        UserRole.PARENT: False,
        UserRole.STUDENT: False,
    },
    'accounts_users': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: False,
        UserRole.RESEARCH_LEADER: False,
        UserRole.TEACHER: False,
        UserRole.PARENT: False,
        UserRole.STUDENT: False,
    },
    'accounts_roles': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: False,
        UserRole.RESEARCH_LEADER: False,
        UserRole.TEACHER: False,
        UserRole.PARENT: False,
        UserRole.STUDENT: False,
    },
    'permissions_menu': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: False,
        UserRole.RESEARCH_LEADER: False,
        UserRole.TEACHER: False,
        UserRole.PARENT: False,
        UserRole.STUDENT: False,
    },
    'permissions_role': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: False,
        UserRole.RESEARCH_LEADER: False,
        UserRole.TEACHER: False,
        UserRole.PARENT: False,
        UserRole.STUDENT: False,
    },
    # 二级子菜单
    'learning_practice_word': {
        UserRole.ADMIN: True,
        UserRole.DEAN: False,
        UserRole.ACADEMIC_DIRECTOR: False,
        UserRole.RESEARCH_LEADER: False,
        UserRole.TEACHER: False,
        UserRole.PARENT: False,
        UserRole.STUDENT: True,
    },
    'learning_practice_test': {
        UserRole.ADMIN: True,
        UserRole.DEAN: False,
        UserRole.ACADEMIC_DIRECTOR: False,
        UserRole.RESEARCH_LEADER: False,
        UserRole.TEACHER: False,
        UserRole.PARENT: False,
        UserRole.STUDENT: True,
    },
    # 学习目标和学习计划的详细权限配置
    'learning_goals': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: True,
        UserRole.RESEARCH_LEADER: True,
        UserRole.TEACHER: True,
        UserRole.PARENT: True,
        UserRole.STUDENT: True,
    },
    'learning_plans': {
        UserRole.ADMIN: True,
        UserRole.DEAN: True,
        UserRole.ACADEMIC_DIRECTOR: True,
        UserRole.RESEARCH_LEADER: True,
        UserRole.TEACHER: True,
        UserRole.PARENT: True,
        UserRole.STUDENT: True,
    }
}

# 权限检查辅助函数
def has_learning_goal_permission(user_role, permission_type, context=None):
    """
    检查学习目标权限
    
    Args:
        user_role: 用户角色
        permission_type: 权限类型 (view, create, edit, delete等)
        context: 上下文信息 (如目标所属者、教研组等)
    
    Returns:
        bool: 是否有权限
    """
    if user_role not in LEARNING_GOALS_PERMISSIONS:
        return False
    
    role_permissions = LEARNING_GOALS_PERMISSIONS[user_role]
    permission = role_permissions.get(permission_type, False)
    
    # 处理条件权限
    if isinstance(permission, str):
        if permission == 'own_group_only' and context:
            # 检查是否是本教研组的目标
            return context.get('is_own_group', False)
        elif permission == 'class_goals_only' and context:
            # 检查是否是班级目标
            return context.get('is_class_goal', False)
        elif permission == 'own_created_only' and context:
            # 检查是否是自己创建的目标
            return context.get('is_own_created', False)
        elif permission == 'child_only' and context:
            # 检查是否是子女的目标
            return context.get('is_child_goal', False)
        elif permission == 'own_only' and context:
            # 检查是否是自己的目标
            return context.get('is_own_goal', False)
        elif permission == 'personal_only' and context:
            # 检查是否是个人目标
            return context.get('is_personal_goal', False)
        elif permission == 'own_personal_only' and context:
            # 检查是否是自己的个人目标
            return context.get('is_own_personal_goal', False)
        return False
    
    return bool(permission)

def has_learning_plan_permission(user_role, permission_type, context=None):
    """
    检查学习计划权限
    
    Args:
        user_role: 用户角色
        permission_type: 权限类型 (view, create, edit, delete等)
        context: 上下文信息 (如计划所属者、教研组等)
    
    Returns:
        bool: 是否有权限
    """
    if user_role not in LEARNING_PLANS_PERMISSIONS:
        return False
    
    role_permissions = LEARNING_PLANS_PERMISSIONS[user_role]
    permission = role_permissions.get(permission_type, False)
    
    # 处理条件权限
    if isinstance(permission, str):
        if permission == 'department_only' and context:
            # 检查是否是本部门的计划
            return context.get('is_department_plan', False)
        elif permission == 'group_plans_only' and context:
            # 检查是否是本教研组的计划
            return context.get('is_group_plan', False)
        elif permission == 'group_only' and context:
            # 检查是否是本教研组的计划
            return context.get('is_group_plan', False)
        elif permission == 'student_plans_only' and context:
            # 检查是否是学生计划
            return context.get('is_student_plan', False)
        elif permission == 'assigned_plans_only' and context:
            # 检查是否是分配给自己的计划
            return context.get('is_assigned_plan', False)
        elif permission == 'child_only' and context:
            # 检查是否是子女的计划
            return context.get('is_child_plan', False)
        elif permission == 'own_only' and context:
            # 检查是否是自己的计划
            return context.get('is_own_plan', False)
        elif permission == 'personal_only' and context:
            # 检查是否是个人计划
            return context.get('is_personal_plan', False)
        elif permission == 'own_personal_only' and context:
            # 检查是否是自己的个人计划
            return context.get('is_own_personal_plan', False)
        return False
    
    return bool(permission)

def has_menu_permission(user_role, menu_key, action):
    """
    检查菜单权限
    
    Args:
        user_role: 用户角色
        menu_key: 菜单标识
        action: 操作类型
    
    Returns:
        bool: 是否有权限
    """
    if menu_key not in MENU_PERMISSIONS:
        return False
    
    menu_permissions = MENU_PERMISSIONS[menu_key]
    if user_role not in menu_permissions:
        return False
    
    return action in menu_permissions[user_role]

def get_menu_actions(user_role, menu_key):
    """
    获取用户在指定菜单下的可用操作列表
    
    Args:
        user_role: 用户角色
        menu_key: 菜单标识
    
    Returns:
        list: 可用操作列表
    """
    if menu_key not in MENU_PERMISSIONS:
        return []
    
    menu_permissions = MENU_PERMISSIONS[menu_key]
    if user_role not in menu_permissions:
        return []
    
    return menu_permissions[user_role]