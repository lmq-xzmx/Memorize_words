// 学生选择器调试脚本
// 在浏览器控制台中运行此脚本来调试学生选择器问题

console.log('=== 学生选择器调试脚本 ===');

// 1. 检查DOM元素是否存在
function checkDOMElements() {
    console.log('1. 检查DOM元素:');
    
    const selectElement = document.getElementById('current-student-select');
    const statusElement = document.getElementById('student-status');
    
    console.log('- 学生选择器元素:', selectElement);
    console.log('- 状态显示元素:', statusElement);
    
    if (selectElement) {
        console.log('- 选择器当前内容:', selectElement.innerHTML);
        console.log('- 选择器是否禁用:', selectElement.disabled);
    }
    
    if (statusElement) {
        console.log('- 状态文本:', statusElement.textContent);
        console.log('- 状态CSS类:', statusElement.className);
    }
    
    return { selectElement, statusElement };
}

// 2. 测试API端点
async function testStudentAPI() {
    console.log('2. 测试API端点:');
    
    try {
        console.log('- 发送请求到: /accounts/api/students/for_select/');
        
        const response = await fetch('/accounts/api/students/for_select/', {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        console.log('- 响应状态:', response.status, response.statusText);
        console.log('- 响应头:', Object.fromEntries(response.headers));
        
        if (response.ok) {
            const data = await response.json();
            console.log('- 响应数据:', data);
            console.log('- 数据类型:', typeof data);
            console.log('- 是否为数组:', Array.isArray(data));
            console.log('- 数据长度:', data.length);
            
            return data;
        } else {
            const errorText = await response.text();
            console.error('- API错误:', errorText);
            return null;
        }
    } catch (error) {
        console.error('- 请求异常:', error);
        return null;
    }
}

// 3. 手动填充学生选择器
function manualPopulateStudents(students) {
    console.log('3. 手动填充学生选择器:');
    
    const selectElement = document.getElementById('current-student-select');
    if (!selectElement) {
        console.error('- 找不到学生选择器元素');
        return;
    }
    
    // 清空现有选项
    selectElement.innerHTML = '<option value="">-- 选择学生 --</option>';
    
    if (!students || !Array.isArray(students)) {
        console.error('- 学生数据无效:', students);
        return;
    }
    
    // 添加学生选项
    students.forEach((student, index) => {
        console.log(`- 添加学生 ${index + 1}:`, student);
        
        const option = document.createElement('option');
        option.value = student.id;
        option.textContent = student.display_name || `${student.real_name || student.username} (${student.username})`;
        option.dataset.englishLevel = student.english_level || '';
        option.dataset.gradeLevel = student.grade_level || '';
        selectElement.appendChild(option);
    });
    
    // 启用选择器
    selectElement.disabled = false;
    
    console.log('- 学生选择器填充完成');
}

// 4. 测试学生切换功能
function testStudentSwitch(studentId) {
    console.log('4. 测试学生切换功能:');
    console.log('- 切换到学生ID:', studentId);
    
    if (typeof window.switchCurrentStudent === 'function') {
        window.switchCurrentStudent(studentId);
        console.log('- 学生切换函数调用完成');
    } else {
        console.error('- 找不到学生切换函数');
    }
}

// 5. 完整的调试流程
async function fullDebug() {
    console.log('=== 开始完整调试流程 ===');
    
    // 检查DOM元素
    const { selectElement, statusElement } = checkDOMElements();
    
    if (!selectElement || !statusElement) {
        console.error('关键DOM元素缺失，无法继续调试');
        return;
    }
    
    // 测试API
    const students = await testStudentAPI();
    
    if (students && students.length > 0) {
        // 手动填充学生数据
        manualPopulateStudents(students);
        
        // 测试切换到第一个学生
        if (students[0] && students[0].id) {
            setTimeout(() => {
                testStudentSwitch(students[0].id);
            }, 500);
        }
    } else {
        console.error('无法获取学生数据，调试结束');
    }
    
    console.log('=== 调试流程完成 ===');
}

// 导出调试函数到全局作用域
window.debugStudentSelector = {
    checkDOMElements,
    testStudentAPI,
    manualPopulateStudents,
    testStudentSwitch,
    fullDebug
};

console.log('调试脚本加载完成。使用以下命令进行调试:');
console.log('- debugStudentSelector.checkDOMElements() - 检查DOM元素');
console.log('- debugStudentSelector.testStudentAPI() - 测试API端点');
console.log('- debugStudentSelector.fullDebug() - 运行完整调试流程');

// 自动运行完整调试
fullDebug();