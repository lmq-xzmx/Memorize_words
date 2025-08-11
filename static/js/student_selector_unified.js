/**
 * 统一学生选择器模块
 * 整合并优化所有学生选择器相关功能，消除重复代码
 */

(function() {
    'use strict';
    
    // 配置
    const CONFIG = {
        API_URL: '/api/auth/api/students/for_select/',
        RETRY_DELAY: 1000,
        MAX_RETRIES: 3,
        ELEMENTS: {
            SELECT: 'current-student-select',
            STATUS: 'student-status',
            KNOWN_DESC: 'known-words-desc',
            NEW_WORDS_DESC: 'new-words-desc'
        }
    };
    
    // 状态管理
    let state = {
        currentStudent: null,
        studentsData: [],
        retryCount: 0,
        isLoading: false
    };
    
    // 事件回调
    let callbacks = {
        onStudentChange: [],
        onDataLoad: [],
        onError: []
    };
    
    // 工具函数
    function log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const prefix = `[${timestamp}] [UnifiedStudentSelector]`;
        
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
    
    function triggerCallbacks(type, data) {
        if (callbacks[type]) {
            callbacks[type].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    log(`回调执行错误: ${error.message}`, 'error');
                }
            });
        }
    }
    
    // UI 更新函数
    function updateSelectStatus(message, className = '', disabled = false) {
        const selectElement = getElement(CONFIG.ELEMENTS.SELECT);
        const statusElement = getElement(CONFIG.ELEMENTS.STATUS);
        
        if (selectElement) {
            selectElement.disabled = disabled;
        }
        
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `student-status ${className}`.trim();
        }
    }
    
    function showLoading() {
        if (state.isLoading) return;
        
        state.isLoading = true;
        const selectElement = getElement(CONFIG.ELEMENTS.SELECT);
        if (selectElement) {
            selectElement.innerHTML = '<option value="">-- 加载中... --</option>';
        }
        updateSelectStatus('正在加载学生数据...', 'loading', true);
        log('开始加载学生数据');
    }
    
    function showError(message) {
        state.isLoading = false;
        const selectElement = getElement(CONFIG.ELEMENTS.SELECT);
        const statusElement = getElement(CONFIG.ELEMENTS.STATUS);
        
        if (selectElement) {
            selectElement.innerHTML = '<option value="">-- 加载失败 --</option>';
        }
        
        updateSelectStatus(message || '学生数据加载失败', 'error', false);
        
        // 添加重试按钮
        if (statusElement && state.retryCount < CONFIG.MAX_RETRIES) {
            const existingRetryBtn = statusElement.querySelector('.retry-btn');
            if (existingRetryBtn) {
                existingRetryBtn.remove();
            }
            
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
        triggerCallbacks('onError', { message, retryCount: state.retryCount });
    }
    
    function showSuccess(count) {
        state.isLoading = false;
        updateSelectStatus(`已加载 ${count} 名学生，请选择学生以显示个性化词汇标记`, 'success');
        log(`学生数据加载成功，共 ${count} 名学生`);
        state.retryCount = 0;
        triggerCallbacks('onDataLoad', { count, students: state.studentsData });
    }
    
    // 核心功能函数
    function populateStudents(students) {
        const selectElement = getElement(CONFIG.ELEMENTS.SELECT);
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
        state.studentsData = students;
        showSuccess(students.length);
    }
    
    async function loadStudents() {
        if (state.isLoading) {
            log('正在加载中，跳过重复请求', 'warn');
            return;
        }
        
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
            log(`API返回数据类型: ${typeof data}, 长度: ${Array.isArray(data) ? data.length : 'N/A'}`);
            
            populateStudents(data);
            
        } catch (error) {
            state.retryCount++;
            log(`加载学生数据失败 (尝试 ${state.retryCount}/${CONFIG.MAX_RETRIES}): ${error.message}`, 'error');
            
            if (state.retryCount < CONFIG.MAX_RETRIES) {
                showError(`加载失败，将在 ${CONFIG.RETRY_DELAY/1000} 秒后重试...`);
                setTimeout(loadStudents, CONFIG.RETRY_DELAY);
            } else {
                showError('多次尝试后仍然失败，请刷新页面或联系管理员');
            }
        }
    }
    
    function handleStudentChange(studentId) {
        log(`学生选择变更: ${studentId}`);
        
        state.currentStudent = studentId;
        const statusElement = getElement(CONFIG.ELEMENTS.STATUS);
        const selectElement = getElement(CONFIG.ELEMENTS.SELECT);
        const knownWordsDesc = getElement(CONFIG.ELEMENTS.KNOWN_DESC);
        const newWordsDesc = getElement(CONFIG.ELEMENTS.NEW_WORDS_DESC);
        
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
                
                // 更新描述文本
                if (knownWordsDesc) {
                    knownWordsDesc.textContent = `显示 ${studentName} 已掌握的熟词`;
                }
                if (newWordsDesc) {
                    newWordsDesc.textContent = `显示 ${studentName} 需要学习的生词（红字黄底样式）`;
                }
                
                // 启用相关的复选框
                const showKnownCheckbox = document.getElementById('show-known');
                const showNewWordsCheckbox = document.getElementById('show-new-words');
                if (showKnownCheckbox) showKnownCheckbox.disabled = false;
                if (showNewWordsCheckbox) showNewWordsCheckbox.disabled = false;
                
                log(`已切换到学生: ${studentName} (ID: ${studentId})`);
                
                // 触发自定义事件
                window.dispatchEvent(new CustomEvent('studentChanged', {
                    detail: { studentId, studentName, englishLevel, gradeLevel }
                }));
                
                triggerCallbacks('onStudentChange', {
                    studentId, studentName, englishLevel, gradeLevel
                });
            } else {
                log(`找不到学生选项: ${studentId}`, 'error');
            }
        } else {
            statusElement.textContent = '请选择学生以显示个性化词汇标记';
            statusElement.className = 'student-status';
            
            // 恢复默认描述
            if (knownWordsDesc) {
                knownWordsDesc.textContent = '显示当前学生已掌握的熟词（需选择学生）';
            }
            if (newWordsDesc) {
                newWordsDesc.textContent = '显示当前学生需要学习的生词（需选择学生）';
            }
            
            // 禁用相关的复选框
            const showKnownCheckbox = document.getElementById('show-known');
            const showNewWordsCheckbox = document.getElementById('show-new-words');
            if (showKnownCheckbox) showKnownCheckbox.disabled = true;
            if (showNewWordsCheckbox) showNewWordsCheckbox.disabled = true;
            
            log('已取消学生选择');
            
            // 触发自定义事件
            window.dispatchEvent(new CustomEvent('studentChanged', {
                detail: { studentId: null }
            }));
            
            triggerCallbacks('onStudentChange', { studentId: null });
        }
    }
    
    // 初始化函数
    function init() {
        log('初始化统一学生选择器');
        
        // 检查必要的DOM元素
        const selectElement = getElement(CONFIG.ELEMENTS.SELECT);
        const statusElement = getElement(CONFIG.ELEMENTS.STATUS);
        
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
        window.loadStudentData = loadStudents;
        
        // 加载学生数据
        loadStudents();
        
        log('统一学生选择器初始化完成');
    }
    
    // 公共API
    window.UnifiedStudentSelector = {
        // 核心功能
        init,
        loadStudents,
        handleStudentChange,
        
        // 状态获取
        getCurrentStudent: () => state.currentStudent,
        getStudentsData: () => [...state.studentsData],
        isLoading: () => state.isLoading,
        
        // 事件监听
        onStudentChange: (callback) => {
            if (typeof callback === 'function') {
                callbacks.onStudentChange.push(callback);
            }
        },
        onDataLoad: (callback) => {
            if (typeof callback === 'function') {
                callbacks.onDataLoad.push(callback);
            }
        },
        onError: (callback) => {
            if (typeof callback === 'function') {
                callbacks.onError.push(callback);
            }
        },
        
        // 配置
        getConfig: () => ({ ...CONFIG }),
        
        // 调试接口
        debug: {
            state: () => ({ ...state }),
            callbacks: () => ({ ...callbacks }),
            log
        }
    };
    
    // 页面加载完成后自动初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    log('统一学生选择器模块加载完成');
    
})();