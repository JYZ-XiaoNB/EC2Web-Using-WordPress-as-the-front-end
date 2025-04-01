jQuery(document).ready(function($) {
    const $form = $('#imeiCheckForm');
    const $result = $('#imeiResult');
    const $content = $('#resultContent');
    const $submitBtn = $('.submit-btn');

    // 调试：确认元素存在
    console.log('DOM元素检测:', {
        form: $form.length,
        result: $result.length,
        content: $content.length
    });

    $form.on('submit', function(e) {
        e.preventDefault();
        
        // 重置状态
        $submitBtn.prop('disabled', true).text('验证中...');
        $content.empty();
        $result.hide();

        // 发送请求
        $.ajax({
            url: imeiCheckerVars.ajax_url,
            type: 'POST',
            data: {
                action: 'imei_check',
                nonce: imeiCheckerVars.nonce,
                imei: $('#imei_input').val().trim()
            },
            success: function(res) {
                console.log('服务端响应:', res);
                
                // 确保 res.message 存在，否则使用默认值
                const message = res.message || '验证完成'; // 如果 res.message 是 undefined，则显示 "验证完成"
                
                // 渲染结果
                $content.html(`
                    <div class="result-message success">
                        <strong>验证结果：</strong> ${message}
                    </div>
                    <div class="debug-info">
                        <pre>${JSON.stringify(res, null, 2)}</pre>
                    </div>
                `);
                $result.slideDown();
            },
            error: function(xhr) {
                $content.html(`<div class="result-message error">请求失败: ${xhr.statusText}</div>`);
                $result.slideDown();
            },
            complete: function() {
                $submitBtn.prop('disabled', false).text('立即验证');
            }
        });
    });
});