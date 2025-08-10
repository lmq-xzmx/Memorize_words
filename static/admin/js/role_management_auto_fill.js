(function() {
    'use strict';
    
    // 确保jQuery可用
    let $;
    if (typeof django !== 'undefined' && django.jQuery) {
        $ = django.jQuery;
    } else if (typeof jQuery !== 'undefined') {
        $ = jQuery;
    } else {
        console.error('jQuery not found for role management auto fill');
        return;
    }
    
    console.log('Role management auto fill script loaded');
    
    // 中文到英文的映射表
    const chineseToEnglishMap = {
        '管理员': 'admin',
        '教师': 'teacher',
        '学生': 'student',
        '家长': 'parent',
        '访客': 'guest',
        '超级管理员': 'super_admin',
        '系统管理员': 'system_admin',
        '班主任': 'class_teacher',
        '科任教师': 'subject_teacher',
        '助教': 'assistant_teacher',
        '实习教师': 'intern_teacher',
        '年级主任': 'grade_director',
        '教务主任': 'academic_director',
        '校长': 'principal',
        '副校长': 'vice_principal',
        '普通学生': 'regular_student',
        '班长': 'class_monitor',
        '学习委员': 'study_committee',
        '课代表': 'subject_representative',
        '监考员': 'invigilator',
        '阅卷员': 'grader',
        '审核员': 'reviewer',
        '编辑': 'editor',
        '内容管理员': 'content_admin',
        '技术支持': 'tech_support',
        '客服': 'customer_service'
    };
    
    // 中文转拼音的简单实现（常用字符）
    const chineseToPinyinMap = {
        '一': 'yi', '二': 'er', '三': 'san', '四': 'si', '五': 'wu',
        '六': 'liu', '七': 'qi', '八': 'ba', '九': 'jiu', '十': 'shi',
        '年': 'nian', '级': 'ji', '班': 'ban', '组': 'zu', '长': 'zhang',
        '员': 'yuan', '师': 'shi', '生': 'sheng', '主': 'zhu', '任': 'ren',
        '副': 'fu', '助': 'zhu', '理': 'li', '务': 'wu', '科': 'ke',
        '课': 'ke', '代': 'dai', '表': 'biao', '委': 'wei', '监': 'jian',
        '考': 'kao', '阅': 'yue', '卷': 'juan', '审': 'shen', '核': 'he',
        '编': 'bian', '辑': 'ji', '内': 'nei', '容': 'rong', '技': 'ji',
        '术': 'shu', '支': 'zhi', '持': 'chi', '客': 'ke', '服': 'fu',
        '超': 'chao', '系': 'xi', '统': 'tong', '实': 'shi', '习': 'xi',
        '普': 'pu', '通': 'tong', '校': 'xiao', '家': 'jia', '访': 'fang'
    };
    
    // 将中文转换为英文标识符
    function convertChineseToEnglish(chinese) {
        // 去除空格
        chinese = chinese.trim();
        
        // 如果为空，返回空字符串
        if (!chinese) {
            return '';
        }
        
        // 首先检查是否有直接映射
        if (chineseToEnglishMap[chinese]) {
            return chineseToEnglishMap[chinese];
        }
        
        // 如果没有直接映射，尝试转换为拼音
        let result = '';
        for (let i = 0; i < chinese.length; i++) {
            const char = chinese[i];
            if (chineseToPinyinMap[char]) {
                result += chineseToPinyinMap[char];
                if (i < chinese.length - 1) {
                    result += '_';
                }
            } else if (/[a-zA-Z0-9_]/.test(char)) {
                // 如果是英文字母、数字或下划线，直接添加
                result += char.toLowerCase();
            }
        }
        
        // 如果转换失败，使用默认格式
        if (!result) {
            result = 'custom_role_' + Date.now();
        }
        
        // 确保符合标识符规范
        result = result.replace(/[^a-zA-Z0-9_]/g, '_');
        result = result.replace(/_{2,}/g, '_');
        result = result.replace(/^_+|_+$/g, '');
        
        return result;
    }
    
    // 当DOM加载完成后执行
    $(document).ready(function() {
        console.log('DOM ready, checking for add page');
        console.log('Current pathname:', window.location.pathname);
        
        // 检查是否在添加页面
        if (window.location.pathname.includes('/add/')) {
            console.log('On add page, looking for fields');
            const $roleField = $('#id_role');
            const $displayNameField = $('#id_display_name');
            
            console.log('Role field found:', $roleField.length > 0);
            console.log('Display name field found:', $displayNameField.length > 0);
            
            if ($roleField.length && $displayNameField.length) {
                console.log('Both fields found, setting up auto fill');
                // 为显示名称字段添加输入事件监听
                $displayNameField.on('input', function() {
                    const displayName = $(this).val();
                    const englishRole = convertChineseToEnglish(displayName);
                    
                    // 只有当role字段为空或者用户没有手动修改过时才自动填充
                    if (!$roleField.data('manually-changed')) {
                        $roleField.val(englishRole);
                    }
                });
                
                // 监听role字段的手动修改
                $roleField.on('input', function() {
                    // 标记为手动修改
                    $(this).data('manually-changed', true);
                });
                
                // 添加重置按钮
                const $resetBtn = $('<button type="button" class="btn btn-sm btn-secondary" style="margin-left: 10px;">重新生成</button>');
                $roleField.after($resetBtn);
                
                $resetBtn.on('click', function() {
                    $roleField.removeData('manually-changed');
                    const displayName = $displayNameField.val();
                    const englishRole = convertChineseToEnglish(displayName);
                    $roleField.val(englishRole);
                });
                
                // 添加提示信息
                const $helpText = $('<div class="help" style="margin-top: 5px; color: #666; font-size: 12px;">提示：在"显示名称"中输入中文，系统会自动生成对应的英文标识符</div>');
                $roleField.parent().append($helpText);
            }
        } else {
            console.log('Fields not found or not on add page');
        }
    });
    
})();