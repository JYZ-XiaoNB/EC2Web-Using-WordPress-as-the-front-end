import os
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from PIL import Image
import hashlib
import ddddocr  # 确保已安装：pip install ddddocr

app = Flask(__name__)

# 固定配置（原代码中的URL）
BASE_URL = "http://nw-restriction.nttdocomo.co.jp/"
URL_PATHS = {
    'top': 'top.php',
    'search': 'search.php',
    'result': 'result.php'
}

def filehash(filepath):
    """计算文件MD5"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()
"""
def download_captcha(session):
    try:
        response = session.get(BASE_URL + URL_PATHS['search'])
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = soup.find('img', src="gifcat/call.php")
        
        if not img_tag:
            return None

        img_url = BASE_URL + "gifcat/call.php"
        img_data = session.get(img_url).content
        os.makedirs('captchas', exist_ok=True)
        
        gif_path = 'captchas/captcha.gif'
        with open(gif_path, 'wb') as f:
            f.write(img_data)
        
        # GIF转PNG
        with Image.open(gif_path) as img:
            png_path = f'captchas/captcha_{filehash(gif_path)}.png'
            img.save(png_path)
        
        return png_path
    except Exception as e:
        print(f"123: {str(e)}")
        return None

def recognize_captcha(img_path):
    ocr = ddddocr.DdddOcr()
    with open(img_path, 'rb') as f:
        img_bytes = f.read()
    return ocr.classification(img_bytes)
"""
@app.route('/verify_imei', methods=['POST'])
def verify_imei():
    """API入口"""
    try:
        data = request.json
        imei = data.get('imei')
        
        if not imei or len(imei) != 15 or not imei.isdigit():
            return jsonify({'success': False, 'error': 'IMEI必须为15位数字'})

        session = requests.Session()
        session.get(BASE_URL + URL_PATHS['top'])  # 初始化会话
        
        # 1. 获取验证码
      #  captcha_path = download_captcha(session)
       # if not captcha_path:
        #    return jsonify({'success': False, 'error': '获取验证码失败'})
        
        # 2. 识别验证码
        #captcha_code = recognize_captcha(captcha_path)
        
        # 3. 提交验证
        response = session.post(
            BASE_URL + URL_PATHS['search'],
            data={'productno': imei}
        )
        
        # 4. 解析结果
        soup = BeautifulSoup(response.text, 'html.parser')
        #result_span = soup.find('result-panel', style='width:250px; display:inline-block; font-size: 3em; padding: 4px; border: 2px solid #CC0033;')
        result_span = soup.find_all('div', class_='result-panel')
        if len(result_span) >= 2:  # 确保至少有两个匹配项
            true_panel = result_span[1]  # 取第二个（索引 1）
        if result_span:
            return jsonify({
                'success': True,
                'imei': imei,
                'result': true_panel.text.strip()
            })
        else:
            return jsonify({'success': False, 'error': '验证失败，请重试'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # 创建必要目录
    os.makedirs('captchas', exist_ok=True)
    
    # 启动服务（生产环境建议用gunicorn）
    app.run(host='0.0.0.0', port=5000, debug=False)