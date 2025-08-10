(function($) {
    'use strict';
    
    $(document).ready(function() {
        // 获取word和conflicting_word字段
        var wordField = $('#id_word');
        var conflictingWordField = $('#id_conflicting_word');
        
        if (wordField.length && conflictingWordField.length) {
            // 当word字段值改变时，自动同步到conflicting_word字段
            wordField.on('change', function() {
                var selectedValue = $(this).val();
                if (selectedValue) {
                    conflictingWordField.val(selectedValue);
                    // 触发change事件以确保其他依赖逻辑正常工作
                    conflictingWordField.trigger('change');
                }
            });
            
            // 页面加载时如果word有值，自动设置conflicting_word
            var initialWordValue = wordField.val();
            if (initialWordValue && !conflictingWordField.val()) {
                conflictingWordField.val(initialWordValue);
            }
        }
    });
})(django.jQuery);