// 学生选择器修复脚本
// 这个脚本提供了一个更健壮的学生选择器实现

(function() {
    'use strict';
    
    // 配置
    const CONFIG = {
        API_URL: '/api/auth/api/students/for_select/',
        RETRY_DELAY: 1000,
        MAX_RETRIES: 3
    };
    
    // 状态管理
    let currentStudent = null;
    let studentsData = [];
    let retryCount = 0;
    
    // 工具函数
    function log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const prefix = `[${timestamp}] [StudentSelector]`;
        
        switch (type) {
            case 'error':
                console.error(prefix, message);
                break;
            case 'warn':
                console.warn(prefix, message);
                break;
            default:
                console.log(prefix, message);
        }
    }
    
    function getElement(id) {
        const element = document.getElementById(id);
        if (!element) {
            log(`找不到元素: ${id}`, 'error');
        }
        return element;
    }
    
    // 更新选择器状态
    function updateSelectStatus(message, className = '', disabled = false) {
        const selectElement = getElement('current-student-select');
        const statusElement = getElement('student-status');
        
        if (selectElement) {
            selectElement.disabled = disabled;
        }
        
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `student-status ${className}`.trim();
        }
    }
    
    // 显示加载状态
    function showLoading() {
        const selectElement = getElement('current-student-select');
        if (selectElement) {
            selectElement.innerHTML = '<option value="">-- 加载中... --</option>';
        }
        updateSelectStatus('正在加载学生数据...', 'loading', true);
        log('开始加载学生数据');
    }
    
    // 显示错误状态
    function showError(message) {
        const selectElement = getElement('current-student-select');
        const statusElement = getElement('student-status');
        
        if (selectElement) {
            selectElement.innerHTML = '<option value="">-- 加载失败 --</option>';
        }
        
        updateSelectStatus(message || '学生数据加载失败', 'error', false);
        
        // 添加重试按钮
        if (statusElement && retryCount < CONFIG.MAX_RETRIES) {
            const retryBtn = document.createElement('button');
            retryBtn.textContent = '重试';
            retryBtn.className = 'retry-btn';
            retryBtn.style.cssText = 'margin-left: 10px; padding: 2px 8px; font-size: 11px; background: #6c757d; color: white; border: none; border-radius: 3px; cursor: pointer;';
            retryBtn.onclick = function() {
                this.remove();
                setTimeout(loadStudents, CONFIG.RETRY_DELAY);
            };
            statusElement.appendChild(retryBtn);
        }
        
        log(message || '学生数据加载失败', 'error');
    }
    
    // 显示成功状态
    function showSuccess(count) {
        updateSelectStatus(`已加载 ${count} 名学生，请选择学生以显示个性化词汇标记`, 'success');
        log(`学生数据加载成功，共 ${count} 名学生`);
        retryCount = 0; // 重置重试计数
    }
    
    // 填充学生选择器
    function populateStudents(students) {
        const selectElement = getElement('current-student-select');
        if (!selectElement) return;
        
        // 清空现有选项
        selectElement.innerHTML = '<option value="">-- 选择学生 --</option>';
        
        // 验证数据
        if (!Array.isArray(students)) {
            log('学生数据格式错误，不是数组', 'error');
            showError('学生数据格式错误');
            return;
        }
        
        if (students.length === 0) {
            selectElement.innerHTML = '<option value="">-- 暂无学生数据 --</option>';
            updateSelectStatus('系统中暂无学生用户，请联系管理员添加学生账户', 'warning', true);
            log('学生数据为空', 'warn');
            return;
        }
        
        // 添加学生选项
        students.forEach((student, index) => {
            try {
                const option = document.createElement('option');
                option.value = student.id || '';
                
                // 构建显示名称
                let displayName = student.display_name;
                if (!displayName) {
                    const name = student.real_name || student.username || '未知用户';
                    const username = student.username || '';
                    displayName = username ? `${name} (${username})` : name;
                }
                
                option.textContent = displayName;
                option.dataset.englishLevel = student.english_level || '';
                option.dataset.gradeLevel = student.grade_level || '';
                
                selectElement.appendChild(option);
                
                log(`添加学生 ${index + 1}: ${displayName} (ID: ${student.id})`);
            } catch (error) {
                log(`添加学生选项时出错: ${error.message}`, 'error');
            }
        });
        
        // 启用选择器
        selectElement.disabled = false;
        studentsData = students;
        showSuccess(students.length);
    }
    
    // 加载学生数据
    async function loadStudents() {
        showLoading();
        
        try {
            const response = await fetch(CONFIG.API_URL, {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            log(`API响应: ${response.status} ${response.statusText}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            log(`API返回数据: ${JSON.stringify(data)}`);
            
            populateStudents(data);
            
        } catch (error) {
            retryCount++;
            log(`加载学生数据失败 (尝试 ${retryCount}/${CONFIG.MAX_RETRIES}): ${error.message}`, 'error');
            
            if (retryCount < CONFIG.MAX_RETRIES) {
                showError(`加载失败，将在 ${CONFIG.RETRY_DELAY/1000} 秒后重试...`);
                setTimeout(loadStudents, CONFIG.RETRY_DELAY);
            } else {
                showError('多次尝试后仍然失败，请刷新页面或联系管理员');
            }
        }
    }
    
    // 学生切换处理
    function handleStudentChange(studentId) {
        log(`学生选择变更: ${studentId}`);
        
        currentStudent = studentId;
        const statusElement = getElement('student-status');
        const selectElement = getElement('current-student-select');
        
        if (!statusElement || !selectElement) return;
        
        if (studentId && studentId !== '') {
            const selectedOption = selectElement.querySelector(`option[value="${studentId}"]`);
            if (selectedOption) {
                const studentName = selectedOption.textContent;
                const englishLevel = selectedOption.dataset.englishLevel;
                const gradeLevel = selectedOption.dataset.gradeLevel;
                
                // 构建状态文本
                let statusText = `当前学生: ${studentName}`;
                if (englishLevel || gradeLevel) {
                    const levelInfo = [];
                    if (gradeLevel) levelInfo.push(`${gradeLevel}年级`);
                    if (englishLevel) levelInfo.push(`英语水平: ${englishLevel}`);
                    statusText += ` (${levelInfo.join(', ')})`;
                }
                
                statusElement.textContent = statusText;
                statusElement.className = 'student-status selected';
                
                log(`已切换到学生: ${studentName} (ID: ${studentId})`);
                
                // 触发自定义事件
                window.dispatchEvent(new CustomEvent('studentChanged', {
                    detail: { studentId, studentName, englishLevel, gradeLevel }
                }));
            } else {
                log(`找不到学生选项: ${studentId}`, 'error');
            }
        } else {
            statusElement.textContent = '请选择学生以显示个性化词汇标记';
            statusElement.className = 'student-status';
            log('已取消学生选择');
            
            // 触发自定义事件
            window.dispatchEvent(new CustomEvent('studentChanged', {
                detail: { studentId: null }
            }));
        }
    }
    
    // 初始化
    function init() {
        log('初始化学生选择器');
        
        // 检查必要的DOM元素
        const selectElement = getElement('current-student-select');
        const statusElement = getElement('student-status');
        
        if (!selectElement || !statusElement) {
            log('缺少必要的DOM元素，无法初始化', 'error');
            return;
        }
        
        // 绑定事件处理器
        selectElement.addEventListener('change', function() {
            handleStudentChange(this.value);
        });
        
        // 替换全局函数
        window.switchCurrentStudent = handleStudentChange;
        
        // 加载学生数据
        loadStudents();
        
        log('学生选择器初始化完成');
    }
    
    // 导出调试接口
    window.StudentSelectorDebug = {
        loadStudents,
        populateStudents,
        handleStudentChange,
        getStudentsData: () => studentsData,
        getCurrentStudent: () => currentStudent,
        getConfig: () => CONFIG
    };
    
    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    log('学生选择器修复脚本加载完成');
    
})();