/**
 * 学习计划管理页面的动态字段显示逻辑
 * 根据选择的计划类型显示相应的设置字段
 */

// 不同计划类型需要的字段配置
const PLAN_TYPE_FIELDS = {
    'mechanical': {
        required: ['words_per_day', 'review_interval'],
        optional: ['total_words'],
        hidden: ['daily_target', 'start_date', 'end_date'],
        description: '机械模式：固定每日学习量，不考虑学习进展更新。'
    },
    'daily_progress': {
        required: ['start_date', 'end_date', 'total_words', 'review_interval'],
        optional: ['daily_target'],
        hidden: ['words_per_day'],
        description: '日进模式：根据学习进展每日更新，按剩余时间均分。'
    },
    'weekday': {
        required: ['start_date', 'end_date', 'total_words', 'review_interval'],
        optional: ['daily_target'],
        hidden: ['words_per_day'],
        description: '工作日模式：只在工作日学习，按剩余工作日均分。'
    },
    'weekend': {
        required: ['start_date', 'end_date', 'total_words', 'review_interval'],
        optional: ['daily_target'],
        hidden: ['words_per_day'],
        description: '周末模式：只在周末学习，按剩余周末天数均分。'
    },
    'daily': {
        required: ['words_per_day', 'review_interval'],
        optional: ['start_date', 'end_date'],
        hidden: ['daily_target', 'total_words'],
        description: '每日计划：标准每日学习计划，平均分配学习任务。'
    },
    'weekly': {
        required: ['words_per_day', 'review_interval'],
        optional: ['start_date', 'end_date'],
        hidden: ['daily_target', 'total_words'],
        description: '每周计划：按周制定学习计划，灵活安排每周学习进度。'
    },
    'custom': {
        required: ['words_per_day', 'review_interval'],
        optional: ['start_date', 'end_date', 'total_words', 'daily_target'],
        hidden: [],
        description: '自定义计划：用户自定义学习节奏，完全个性化的学习安排。'
    }
};

/**
 * 更新计划设置字段的显示状态
 * @param {string} planType - 选择的计划类型
 */
function updatePlanSettings(planType) {
    const config = PLAN_TYPE_FIELDS[planType];
    if (!config) {
        console.warn('未知的计划类型:', planType);
        return;
    }

    // 获取所有字段
    const allFields = ['name', 'start_date', 'end_date', 'total_words', 'daily_target', 'words_per_day', 'review_interval', 'status'];
    
    allFields.forEach(fieldName => {
        const fieldRow = document.querySelector(`.field-${fieldName}`);
        if (!fieldRow) return;

        // 重置样式
        fieldRow.classList.remove('required-field', 'optional-field', 'hidden-field');
        fieldRow.style.display = '';
        
        // 获取字段标签
        const label = fieldRow.querySelector('label');
        if (label) {
            // 移除之前的必填标记
            const existingAsterisk = label.querySelector('.required-asterisk');
            if (existingAsterisk) {
                existingAsterisk.remove();
            }
        }

        // 根据配置设置字段状态
        if (config.hidden.includes(fieldName)) {
            fieldRow.style.display = 'none';
            fieldRow.classList.add('hidden-field');
        } else if (config.required.includes(fieldName)) {
            fieldRow.classList.add('required-field');
            // 添加必填标记
            if (label && !label.querySelector('.required-asterisk')) {
                const asterisk = document.createElement('span');
                asterisk.className = 'required-asterisk';
                asterisk.textContent = ' *';
                asterisk.style.color = 'red';
                label.appendChild(asterisk);
            }
        } else if (config.optional.includes(fieldName)) {
            fieldRow.classList.add('optional-field');
        }
    });

    // 更新描述信息
    updatePlanDescription(config.description);
}

/**
 * 更新计划类型描述信息
 * @param {string} description - 描述文本
 */
function updatePlanDescription(description) {
    // 查找计划设置fieldset的描述区域
    const fieldset = document.querySelector('.dynamic-fieldset');
    if (!fieldset) return;

    let descriptionDiv = fieldset.querySelector('.plan-type-description');
    if (!descriptionDiv) {
        descriptionDiv = document.createElement('div');
        descriptionDiv.className = 'plan-type-description';
        descriptionDiv.style.cssText = `
            background: #e3f2fd;
            border: 1px solid #2196f3;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
            font-size: 14px;
            color: #1565c0;
        `;
        
        // 插入到fieldset的开头
        const firstField = fieldset.querySelector('.form-row');
        if (firstField) {
            fieldset.insertBefore(descriptionDiv, firstField);
        } else {
            fieldset.appendChild(descriptionDiv);
        }
    }
    
    descriptionDiv.innerHTML = `<strong>📋 当前模式说明：</strong> ${description}`;
}

/**
 * 页面加载完成后初始化
 */
document.addEventListener('DOMContentLoaded', function() {
    // 获取当前选择的计划类型
    const planTypeSelect = document.querySelector('#id_plan_type');
    if (planTypeSelect) {
        // 初始化显示
        updatePlanSettings(planTypeSelect.value);
        
        // 绑定change事件
        planTypeSelect.addEventListener('change', function() {
            updatePlanSettings(this.value);
        });
    }
});

// 全局函数，供HTML onchange调用
window.updatePlanSettings = updatePlanSettings;