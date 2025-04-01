<?php
/*
Plugin Name: IMEI验证工具
Description: 通过Python服务验证IMEI状态
Version: 2.0
*/

defined('ABSPATH') or die('禁止直接访问');

function imei_checker_shortcode() {
    // 加载资源
    wp_enqueue_style(
        'imei-checker-css', 
        plugins_url('style.css', __FILE__),
        array(),
        filemtime(__DIR__.'/style.css')
    );
    
    wp_enqueue_script(
        'imei-checker-js',
        plugins_url('imei-checker.js', __FILE__),
        array('jquery'),
        filemtime(__DIR__.'/imei-checker.js'),
        true
    );

    // 传递参数给JS
    wp_localize_script(
        'imei-checker-js',
        'imeiCheckerVars',
        array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('imei_checker_nonce')
        )
    );

    // 返回HTML结构
    return '
    <div class="imei-checker-container">
        <form id="imeiCheckForm">
            <div class="form-group">
                <label for="imei_input">请输入IMEI号码：</label>
                <input type="text" id="imei_input" pattern="\d{15}" required>
            </div>
            <button type="submit" class="submit-btn">立即验证</button>
        </form>
        <div id="imeiResult" class="result-container">
            <div id="resultContent"></div>
        </div>
    </div>';
}
add_shortcode('imei_checker', 'imei_checker_shortcode');

// AJAX处理
add_action('wp_ajax_imei_check', 'handle_imei_check');
add_action('wp_ajax_nopriv_imei_check', 'handle_imei_check');
function handle_imei_check() {
    check_ajax_referer('imei_checker_nonce', 'nonce');
    
    $imei = sanitize_text_field($_POST['imei'] ?? '');
    if (!preg_match('/^\d{15}$/', $imei)) {
        wp_send_json_error(['error' => 'IMEI必须是15位数字']);
    }

    $response = wp_remote_post('http://localhost:5000/verify_imei', [
        'headers' => ['Content-Type' => 'application/json'],
        'body' => json_encode(['imei' => $imei]),
        'timeout' => 15
    ]);

    if (is_wp_error($response)) {
        wp_send_json_error(['error' => '服务不可用']);
    }

    wp_send_json(json_decode($response['body'], true));
}