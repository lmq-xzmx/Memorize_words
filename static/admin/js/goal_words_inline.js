// 目标单词内联编辑 - 分步加载功能
(function($) {
    'use strict';
    
    // 确保jQuery可用
    if (typeof $ === 'undefined' || $ === null) {
        $ = django.jQuery || window.jQuery;
    }
    
    // 再次确保jQuery可用
    if (typeof $ === 'undefined') {
        console.error('jQuery is not available');
        return;
    }
    
    // 配置参数
    const CONFIG = {
        pageSize: 20,
        maxInitialLoad: 50,
        loadDelay: 300
    };
    
    // 状态管理
    let currentPage = 1;
    let totalPages = 1;
    let isLoading = false;
    let currentGoalId = null;
    
    // DOM元素缓存
    let $container, $table, $controls, $loadingIndicator, $errorMessage, $successMessage;
    
    // 初始化函数
    function initGoalWordsInline() {
        // 等待DOM加载完成
        $(document).ready(function() {
            setupGoalWordsInterface();
            bindEvents();
            loadInitialData();
        });
    }
    
    // 设置界面
    function setupGoalWordsInterface() {
        $container = $('#goalword_set-group');
        if (!$container.length) return;
        
        $table = $container.find('.tabular table');
        
        // 创建控制面板
        createControlPanel();
        
        // 创建消息容器
        createMessageContainers();
        
        // 获取当前学习目标ID
        currentGoalId = getCurrentGoalId();
    }
    
    // 创建控制面板
    function createControlPanel() {
        const controlsHtml = `
            <div class="goal-words-controls">
                <div>
                    <label for="words-per-page">每页显示:</label>
                    <select id="words-per-page">
                        <option value="20" selected>20条</option>
                        <option value="50">50条</option>
                        <option value="100">100条</option>
                        <option value="500">500条</option>
                    </select>
                </div>
                
                <div>
                    <label for="word-filter">筛选:</label>
                    <select id="word-filter">
                        <option value="all">全部单词</option>
                        <option value="recent">最近添加</option>
                        <option value="alphabetical">按字母排序</option>
                    </select>
                </div>
                
                <div>
                    <button type="button" class="btn-load" id="load-words">加载单词</button>
                    <button type="button" class="btn-add" id="add-word">添加单词</button>
                    <button type="button" class="btn-refresh" id="refresh-words">刷新</button>
                </div>
                
                <div class="loading-indicator" id="loading-indicator">
                    <div class="loading-spinner"></div>
                    <span>加载中...</span>
                </div>
                
                <div class="pagination-controls">
                    <span class="pagination-info" id="pagination-info">第 1 页，共 1 页</span>
                    <button type="button" class="btn-load" id="prev-page" disabled>上一页</button>
                    <button type="button" class="btn-load" id="next-page" disabled>下一页</button>
                </div>
            </div>
        `;
        
        $container.prepend(controlsHtml);
        $controls = $container.find('.goal-words-controls');
        $loadingIndicator = $('#loading-indicator');
    }
    
    // 创建消息容器
    function createMessageContainers() {
        const messagesHtml = `
            <div class="error-message" id="error-message"></div>
            <div class="success-message" id="success-message"></div>
        `;
        
        $controls.after(messagesHtml);
        $errorMessage = $('#error-message');
        $successMessage = $('#success-message');
    }
    
    // 绑定事件
    function bindEvents() {
        // 加载单词按钮
        $(document).on('click', '#load-words', function() {
            const pageSize = parseInt($('#words-per-page').val());
            const filter = $('#word-filter').val();
            loadWords(1, pageSize, filter);
        });
        
        // 添加单词按钮
        $(document).on('click', '#add-word', function() {
            showAddWordDialog();
        });
        
        // 刷新按钮
        $(document).on('click', '#refresh-words', function() {
            refreshWordsList();
        });
        
        // 分页按钮
        $(document).on('click', '#prev-page', function() {
            if (currentPage > 1) {
                loadWords(currentPage - 1);
            }
        });
        
        $(document).on('click', '#next-page', function() {
            if (currentPage < totalPages) {
                loadWords(currentPage + 1);
            }
        });
        
        // 每页显示数量变化
        $(document).on('change', '#words-per-page', function() {
            const pageSize = parseInt($(this).val());
            CONFIG.pageSize = pageSize;
            loadWords(1, pageSize);
        });
        
        // 筛选条件变化
        $(document).on('change', '#word-filter', function() {
            const filter = $(this).val();
            loadWords(1, CONFIG.pageSize, filter);
        });
    }
    
    // 获取当前学习目标ID
    function getCurrentGoalId() {
        const urlParts = window.location.pathname.split('/');
        const goalIndex = urlParts.indexOf('learninggoal');
        if (goalIndex !== -1 && goalIndex + 1 < urlParts.length) {
            return urlParts[goalIndex + 1];
        }
        return null;
    }
    
    // 加载初始数据
    function loadInitialData() {
        if (currentGoalId) {
            loadWords(1, CONFIG.pageSize, 'recent');
        }
    }
    
    // 加载单词数据
    function loadWords(page = 1, pageSize = CONFIG.pageSize, filter = 'all') {
        if (isLoading || !currentGoalId) return;
        
        isLoading = true;
        showLoading(true);
        hideMessages();
        
        const params = {
            page: page,
            page_size: pageSize,
            filter: filter
        };
        
        $.ajax({
            url: `/api/teaching/learning-goals/${currentGoalId}/words/`,
            method: 'GET',
            data: params,
            timeout: 10000
        })
        .done(function(response) {
            handleWordsResponse(response, page);
            showSuccess('单词加载成功');
        })
        .fail(function(xhr, status, error) {
            handleLoadError(xhr, status, error);
        })
        .always(function() {
            isLoading = false;
            showLoading(false);
        });
    }
    
    // 处理单词响应数据
    function handleWordsResponse(response, page) {
        currentPage = page;
        totalPages = Math.ceil(response.count / CONFIG.pageSize);
        
        // 更新表格内容
        updateWordsTable(response.results);
        
        // 更新分页信息
        updatePaginationInfo();
        
        // 更新按钮状态
        updatePaginationButtons();
    }
    
    // 更新单词表格
    function updateWordsTable(words) {
        const $tbody = $table.find('tbody');
        $tbody.empty();
        
        if (words.length === 0) {
            $tbody.append(`
                <tr>
                    <td colspan="3" class="empty-state">
                        <div class="empty-state-icon">📚</div>
                        <div>暂无单词数据</div>
                    </td>
                </tr>
            `);
            return;
        }
        
        words.forEach(function(wordData, index) {
            const row = createWordRow(wordData, index);
            $tbody.append(row);
        });
    }
    
    // 创建单词行
    function createWordRow(wordData, index) {
        const addedAt = new Date(wordData.added_at).toLocaleString('zh-CN');
        return `
            <tr class="form-row dynamic-goalword_set" id="goalword_set-${index}">
                <td class="field-word">
                    <a href="/admin/words/word/${wordData.word.id}/change/" target="_blank">
                        ${wordData.word.word}
                    </a>
                    <div style="font-size: 12px; color: #666; margin-top: 2px;">
                        ${wordData.word.definition || '暂无释义'}
                    </div>
                </td>
                <td class="field-added_at">
                    ${addedAt}
                </td>
                <td class="delete">
                    <button type="button" class="btn-delete" data-word-id="${wordData.word.id}" 
                            onclick="removeGoalWord(${wordData.word.id})">
                        删除
                    </button>
                </td>
            </tr>
        `;
    }
    
    // 更新分页信息
    function updatePaginationInfo() {
        const info = `第 ${currentPage} 页，共 ${totalPages} 页`;
        $('#pagination-info').text(info);
    }
    
    // 更新分页按钮状态
    function updatePaginationButtons() {
        $('#prev-page').prop('disabled', currentPage <= 1);
        $('#next-page').prop('disabled', currentPage >= totalPages);
    }
    
    // 显示/隐藏加载状态
    function showLoading(show) {
        if (show) {
            $loadingIndicator.addClass('show');
            $('#load-words').prop('disabled', true);
        } else {
            $loadingIndicator.removeClass('show');
            $('#load-words').prop('disabled', false);
        }
    }
    
    // 处理加载错误
    function handleLoadError(xhr, status, error) {
        let message = '加载单词失败';
        
        if (xhr.status === 404) {
            message = '未找到相关单词数据';
        } else if (xhr.status === 403) {
            message = '没有权限访问单词数据';
        } else if (status === 'timeout') {
            message = '请求超时，请重试';
        } else if (xhr.responseJSON && xhr.responseJSON.detail) {
            message = xhr.responseJSON.detail;
        }
        
        showError(message);
    }
    
    // 显示错误消息
    function showError(message) {
        $errorMessage.text(message).addClass('show');
        setTimeout(() => $errorMessage.removeClass('show'), 5000);
    }
    
    // 显示成功消息
    function showSuccess(message) {
        $successMessage.text(message).addClass('show');
        setTimeout(() => $successMessage.removeClass('show'), 3000);
    }
    
    // 隐藏所有消息
    function hideMessages() {
        $errorMessage.removeClass('show');
        $successMessage.removeClass('show');
    }
    
    // 显示添加单词对话框
    function showAddWordDialog() {
        // 这里可以集成现有的添加单词功能
        alert('添加单词功能开发中...');
    }
    
    // 刷新单词列表
    function refreshWordsList() {
        loadWords(currentPage, CONFIG.pageSize, $('#word-filter').val());
    }
    
    // 全局函数：删除目标单词
    window.removeGoalWord = function(wordId) {
        if (!confirm('确定要删除这个单词吗？')) return;
        
        $.ajax({
            url: `/api/teaching/learning-goals/${currentGoalId}/remove-word/`,
            method: 'POST',
            data: {
                word_id: wordId,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            }
        })
        .done(function() {
            showSuccess('单词删除成功');
            refreshWordsList();
        })
        .fail(function(xhr) {
            const message = xhr.responseJSON?.detail || '删除失败';
            showError(message);
        });
    };
    
    // 启动初始化
    initGoalWordsInline();
    
})(django.jQuery);