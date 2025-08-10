// 文章解析工厂管理后台JavaScript

(function() {
    'use strict';
    
    // 全局变量
    let currentTooltip = null;
    let tooltipsEnabled = true;
    let highlightEnabled = true;
    
    // DOM加载完成后初始化
    document.addEventListener('DOMContentLoaded', function() {
        initializeArticleFactory();
    });
    
    function initializeArticleFactory() {
        initializeTooltips();
        initializeWordHighlight();
        initializeParagraphNavigation();
        initializeFormEnhancements();
        initializeKeyboardShortcuts();
    }
    
    // 工具提示功能
    function initializeTooltips() {
        const words = document.querySelectorAll('.word');
        
        words.forEach(word => {
            word.addEventListener('mouseenter', function(e) {
                if (tooltipsEnabled && this.hasAttribute('title')) {
                    showTooltip(this, e);
                }
            });
            
            word.addEventListener('mouseleave', function() {
                hideTooltip();
            });
        });
    }
    
    function showTooltip(element, event) {
        hideTooltip();
        
        const title = element.getAttribute('title');
        const pos = element.getAttribute('data-pos') || '';
        const definition = element.getAttribute('data-definition') || '';
        const frequency = element.getAttribute('data-frequency') || '';
        
        if (!title && !definition) return;
        
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        
        let content = '';
        if (title) {
            content += `<div class="tooltip-word">${title}</div>`;
        }
        if (pos) {
            content += `<div class="tooltip-pos">${pos}</div>`;
        }
        if (definition) {
            content += `<div class="tooltip-definition">${definition}</div>`;
        }
        if (frequency) {
            content += `<div class="tooltip-frequency">频率: ${frequency}</div>`;
        }
        
        tooltip.innerHTML = content;
        document.body.appendChild(tooltip);
        
        // 定位工具提示
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        let top = rect.top - tooltipRect.height - 10;
        
        // 边界检查
        if (left < 10) left = 10;
        if (left + tooltipRect.width > window.innerWidth - 10) {
            left = window.innerWidth - tooltipRect.width - 10;
        }
        if (top < 10) {
            top = rect.bottom + 10;
            tooltip.classList.add('tooltip-bottom');
        }
        
        tooltip.style.left = left + 'px';
        tooltip.style.top = top + 'px';
        
        currentTooltip = tooltip;
        
        // 添加淡入动画
        setTimeout(() => {
            tooltip.style.opacity = '1';
            tooltip.style.transform = 'translateY(0)';
        }, 10);
    }
    
    function hideTooltip() {
        if (currentTooltip) {
            currentTooltip.style.opacity = '0';
            currentTooltip.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                if (currentTooltip && currentTooltip.parentNode) {
                    currentTooltip.parentNode.removeChild(currentTooltip);
                }
                currentTooltip = null;
            }, 200);
        }
    }
    
    // 词汇高亮功能
    function initializeWordHighlight() {
        const words = document.querySelectorAll('.word');
        
        words.forEach(word => {
            word.addEventListener('click', function(e) {
                if (highlightEnabled) {
                    this.classList.toggle('highlighted');
                    
                    // 播放点击音效（如果需要）
                    playClickSound();
                }
            });
            
            word.addEventListener('dblclick', function(e) {
                e.preventDefault();
                if (highlightEnabled) {
                    // 双击显示详细信息
                    showWordDetails(this);
                }
            });
        });
    }
    
    function playClickSound() {
        // 简单的点击音效
        if (window.AudioContext || window.webkitAudioContext) {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.1);
        }
    }
    
    function showWordDetails(wordElement) {
        const word = wordElement.textContent;
        const pos = wordElement.getAttribute('data-pos');
        const definition = wordElement.getAttribute('data-definition');
        
        // 创建详情弹窗
        const modal = document.createElement('div');
        modal.className = 'word-details-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>词汇详情</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="word-info">
                        <h4>${word}</h4>
                        ${pos ? `<p><strong>词性:</strong> ${pos}</p>` : ''}
                        ${definition ? `<p><strong>释义:</strong> ${definition}</p>` : ''}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 关闭弹窗
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn.addEventListener('click', () => {
            modal.remove();
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
    
    // 段落导航功能
    function initializeParagraphNavigation() {
        const paragraphItems = document.querySelectorAll('.paragraph-item');
        
        paragraphItems.forEach(item => {
            item.addEventListener('click', function() {
                const paragraphId = this.getAttribute('data-paragraph-id');
                if (paragraphId) {
                    scrollToParagraph(paragraphId);
                    highlightParagraph(paragraphId);
                    
                    // 更新导航状态
                    paragraphItems.forEach(p => p.classList.remove('active'));
                    this.classList.add('active');
                }
            });
        });
    }
    
    function scrollToParagraph(paragraphId) {
        const paragraph = document.querySelector(`[data-paragraph-id="${paragraphId}"]`);
        if (paragraph) {
            paragraph.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }
    }
    
    function highlightParagraph(paragraphId) {
        // 移除所有段落高亮
        document.querySelectorAll('.paragraph-highlight').forEach(p => {
            p.classList.remove('paragraph-highlight');
        });
        
        // 高亮目标段落
        const paragraph = document.querySelector(`[data-paragraph-id="${paragraphId}"]`);
        if (paragraph) {
            paragraph.classList.add('paragraph-highlight');
            
            // 3秒后移除高亮
            setTimeout(() => {
                paragraph.classList.remove('paragraph-highlight');
            }, 3000);
        }
    }
    
    // 表单增强功能
    function initializeFormEnhancements() {
        // 解析配置表单
        const parseForm = document.getElementById('parse-form');
        if (parseForm) {
            parseForm.addEventListener('submit', function(e) {
                e.preventDefault();
                submitParseForm(this);
            });
        }
        
        // 实时预览功能
        const contentTextarea = document.querySelector('textarea[name="content"]');
        if (contentTextarea) {
            let debounceTimer;
            contentTextarea.addEventListener('input', function() {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    updatePreview(this.value);
                }, 500);
            });
        }
        
        // 配置选项联动
        const vocabularySourceSelect = document.querySelector('select[name="vocabulary_source"]');
        const variantSelect = document.querySelector('select[name="variant_preference"]');
        
        if (vocabularySourceSelect && variantSelect) {
            vocabularySourceSelect.addEventListener('change', function() {
                updateVariantOptions(this.value, variantSelect);
            });
        }
    }
    
    function submitParseForm(form) {
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        // 显示加载状态
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading"></span> 解析中...';
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage('解析成功！', 'success');
                // 刷新页面或更新内容
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showMessage(data.error || '解析失败', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('网络错误，请重试', 'error');
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        });
    }
    
    function updatePreview(content) {
        const previewContainer = document.getElementById('content-preview');
        if (previewContainer && content.trim()) {
            // 简单的预览更新
            previewContainer.innerHTML = content.replace(/\n/g, '<br>');
        }
    }
    
    function updateVariantOptions(vocabularySource, variantSelect) {
        // 根据词库来源更新变体选项
        const variantOptions = {
            'oxford': ['british', 'american'],
            'cambridge': ['british', 'american'],
            'collins': ['british', 'american', 'australian'],
            'custom': ['default']
        };
        
        const options = variantOptions[vocabularySource] || ['default'];
        
        variantSelect.innerHTML = '';
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option.charAt(0).toUpperCase() + option.slice(1);
            variantSelect.appendChild(optionElement);
        });
    }
    
    // 键盘快捷键
    function initializeKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + 组合键
            if (e.ctrlKey || e.metaKey) {
                switch(e.key.toLowerCase()) {
                    case 's':
                        e.preventDefault();
                        saveContent();
                        break;
                    case 'p':
                        e.preventDefault();
                        triggerParse();
                        break;
                    case 'h':
                        e.preventDefault();
                        toggleHighlight();
                        break;
                    case 't':
                        e.preventDefault();
                        toggleTooltips();
                        break;
                    case 'f':
                        e.preventDefault();
                        focusSearch();
                        break;
                }
            }
            
            // ESC键
            if (e.key === 'Escape') {
                hideTooltip();
                closeModals();
            }
        });
    }
    
    function saveContent() {
        const form = document.querySelector('form');
        if (form) {
            form.submit();
        }
    }
    
    function triggerParse() {
        const parseBtn = document.querySelector('.btn-parse');
        if (parseBtn) {
            parseBtn.click();
        }
    }
    
    function toggleHighlight() {
        highlightEnabled = !highlightEnabled;
        showMessage(
            `词汇高亮已${highlightEnabled ? '启用' : '禁用'}`,
            'info'
        );
    }
    
    function toggleTooltips() {
        tooltipsEnabled = !tooltipsEnabled;
        if (!tooltipsEnabled) {
            hideTooltip();
        }
        showMessage(
            `工具提示已${tooltipsEnabled ? '启用' : '禁用'}`,
            'info'
        );
    }
    
    function focusSearch() {
        const searchInput = document.querySelector('input[type="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    function closeModals() {
        const modals = document.querySelectorAll('.word-details-modal');
        modals.forEach(modal => modal.remove());
    }
    
    // 工具函数
    function getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    function showMessage(text, type = 'info') {
        // 移除现有消息
        const existingMessages = document.querySelectorAll('.message');
        existingMessages.forEach(msg => msg.remove());
        
        const message = document.createElement('div');
        message.className = `message ${type}`;
        message.textContent = text;
        
        // 插入到页面顶部
        const content = document.getElementById('content-main') || document.body;
        content.insertBefore(message, content.firstChild);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (message.parentNode) {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.remove();
                }, 300);
            }
        }, 3000);
    }
    
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // 导出全局函数供模板使用
    window.ArticleFactory = {
        showTooltip,
        hideTooltip,
        toggleHighlight,
        toggleTooltips,
        showMessage,
        scrollToParagraph,
        highlightParagraph
    };
    
})();

// 额外的CSS样式（通过JavaScript添加）
const additionalStyles = `
.paragraph-highlight {
    background-color: #fff3cd !important;
    border: 2px solid #ffc107 !important;
    border-radius: 4px;
    transition: all 0.3s ease;
}

.word.highlighted {
    background-color: #ffeb3b !important;
    font-weight: bold;
    box-shadow: 0 0 5px rgba(255, 235, 59, 0.5);
}

.word-details-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10000;
}

.modal-content {
    background: white;
    border-radius: 8px;
    max-width: 500px;
    width: 90%;
    max-height: 80%;
    overflow-y: auto;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
}

.modal-header h3 {
    margin: 0;
    color: #333;
}

.modal-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #999;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-close:hover {
    color: #333;
}

.modal-body {
    padding: 20px;
}

.word-info h4 {
    margin: 0 0 15px 0;
    color: #007cba;
    font-size: 18px;
}

.word-info p {
    margin: 8px 0;
    line-height: 1.5;
}

.tooltip {
    opacity: 0;
    transform: translateY(-10px);
    transition: all 0.2s ease;
}

.tooltip-bottom::after {
    top: -6px;
    border-color: transparent transparent #667eea transparent;
}

.tooltip-frequency {
    font-size: 11px;
    color: #ccc;
    margin-top: 4px;
}
`;

// 添加样式到页面
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);