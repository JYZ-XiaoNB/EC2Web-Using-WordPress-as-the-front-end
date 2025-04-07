import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://nw-restriction.nttdocomo.co.jp/"
URL_PATHS = {
    'top': 'top.php',
    'search': 'search.php',
    'result': 'result.php'
}


def lambda_handler(event, context):
    """Lambda 入口函数"""
    try:
        if 'body' in event:
            # 如果通过API Gateway调用，参数在body中
            data = json.loads(event['body'])
        else:
            # 直接调用Lambda时，参数可能在event中
            data = event

        imei = data.get('imei')

        if not imei or len(imei) != 15 or not imei.isdigit():
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'IMEI必须为15位数字'
                })
            }

        session = requests.Session()
        session.get(BASE_URL + URL_PATHS['top'])  # 初始化会话

        response = session.post(
            BASE_URL + URL_PATHS['search'],
            data={'productno': imei}
        )

        # 解析结果
        soup = BeautifulSoup(response.text, 'html.parser')
        result_span = soup.find_all('div', class_='result-panel')

        if len(result_span) >= 2:  # 确保至少有两个匹配项
            true_panel = result_span[1]  # 取第二个（索引 1）
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'imei': imei,
                    'result': true_panel.text.strip()
                })
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'success': False,
                    'error': '验证失败，请重试'
                })
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }