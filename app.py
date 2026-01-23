# -*- coding: utf-8 -*-
"""
Flask应用主文件
"""
from flask import Flask, request, jsonify, render_template, session
from config import Config
from utils.jiandaoyun_api import JiandaoyunAPI
from utils.wechat_api import WeChatAPI
from scheduler import DailyReportScheduler
import hashlib
import xml.etree.ElementTree as ET
import time

mytoken = "MyWeChat2026htjiac"

app = Flask(__name__)
app.config.from_object(Config)

# 初始化API客户端
jdy_api = JiandaoyunAPI()
wechat_api = WeChatAPI()

# 初始化定时任务
scheduler = DailyReportScheduler()

#test

@app.route('/')
def index():
    """首页"""
    return jsonify({
        'status': 'ok',
        'message': '简道云日报提醒系统运行中'
    })


@app.route('/wechat', methods=['GET', 'POST'])
def wechat_handler():
    """
    微信服务号消息处理接口
    GET: 验证服务器
    POST: 接收用户消息
    """
    if request.method == 'GET':
        # 微信服务器验证
        return verify_wechat_server()
    else:
        # 处理用户消息
        return handle_wechat_message()


def verify_wechat_server():
    """验证微信服务器"""
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echostr = request.args.get('echostr', '')
    
    # 这里需要配置你的微信Token
    token = mytoken
    
    # 验证签名
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    tmp_str = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
    
    if tmp_str == signature:
        return echostr
    else:
        return 'Invalid signature', 403


def handle_wechat_message():
    """处理微信消息"""
    xml_data = request.data
    
    try:
        root = ET.fromstring(xml_data)
        msg_type = root.find('MsgType').text
        from_user = root.find('FromUser').text
        
        # 用户关注事件
        if msg_type == 'event':
            event = root.find('Event').text
            if event == 'subscribe':
                # 用户关注，引导绑定
                return response_text_message(
                    from_user,
                    '欢迎关注！请点击菜单"身份绑定"完成手机号绑定。'
                )
        
        # 文本消息
        elif msg_type == 'text':
            content = root.find('Content').text
            # 可以在这里处理其他文本消息
            return response_text_message(from_user, '收到您的消息')
        
        return 'success'
        
    except Exception as e:
        print(f'处理微信消息失败: {e}')
        return 'error', 500


def response_text_message(to_user: str, content: str) -> str:
    """返回文本消息"""
    return f"""
    <xml>
        <ToUserName><![CDATA[{to_user}]]></ToUserName>
        <FromUserName><![CDATA[{Config.WECHAT_APPID}]]></FromUserName>
        <CreateTime>{int(time.time())}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{content}]]></Content>
    </xml>
    """


@app.route('/bind', methods=['GET'])
def bind_page():
    """身份绑定页面"""
    openid = request.args.get('openid', '')
    
    if not openid:
        return jsonify({
            'success': False,
            'message': '缺少OpenID参数'
        }), 400
    
    # 保存openid到session
    session['openid'] = openid
    
    return render_template('bind.html', openid=openid)


@app.route('/get_openid', methods=['GET'])
def get_openid():
    """
    获取OpenID测试页面
    用于微信网页授权获取用户OpenID
    """
    code = request.args.get('code', '')
    
    # 如果没有code，重定向到微信授权页面
    if not code:
        redirect_uri = request.url_root + 'get_openid'
        auth_url = f'https://open.weixin.qq.com/connect/oauth2/authorize?appid={Config.WECHAT_APPID}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
        return f'<script>window.location.href="{auth_url}"</script>'
    
    # 使用code换取openid
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        params = {
            'appid': Config.WECHAT_APPID,
            'secret': Config.WECHAT_APPSECRET,
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        response = requests.get(url, params=params, timeout=10, verify=False)
        data = response.json()
        
        if 'openid' in data:
            openid = data['openid']
            return f'''
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>获取OpenID</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .openid {{ 
                        background: #f0f0f0; 
                        padding: 15px; 
                        border-radius: 5px; 
                        word-break: break-all;
                        margin: 20px 0;
                    }}
                    .btn {{ 
                        background: #07c160; 
                        color: white; 
                        padding: 10px 20px; 
                        border: none; 
                        border-radius: 5px; 
                        cursor: pointer;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>您的OpenID</h2>
                    <div class="openid">{openid}</div>
                    <button class="btn" onclick="copyOpenID()">复制OpenID</button>
                    <p style="color: #666; margin-top: 20px;">
                        提示：您可以使用这个OpenID进行测试
                    </p>
                </div>
                <script>
                    function copyOpenID() {{
                        const openid = '{openid}';
                        navigator.clipboard.writeText(openid).then(() => {{
                            alert('OpenID已复制到剪贴板');
                        }});
                    }}
                </script>
            </body>
            </html>
            '''
        else:
            return f'<h3>获取OpenID失败</h3><pre>{data}</pre>'
            
    except Exception as e:
        return f'<h3>错误</h3><p>{str(e)}</p>'


@app.route('/api/bind', methods=['POST'])
def bind_phone():
    """
    绑定手机号接口
    
    请求参数:
        phone: 手机号码
        openid: 微信OpenID
    
    返回:
        success: 是否成功
        message: 提示信息
        data: 员工信息（成功时）
    """
    data = request.get_json()
    phone = data.get('phone', '').strip()
    openid = data.get('openid', '').strip()
    
    # 参数验证
    if not phone or not openid:
        return jsonify({
            'success': False,
            'message': '手机号和OpenID不能为空'
        }), 400
    
    # 手机号格式验证
    if len(phone) != 11 or not phone.isdigit():
        return jsonify({
            'success': False,
            'message': '手机号格式不正确'
        }), 400
    
    # 查询员工信息
    employee = jdy_api.query_employee_by_phone(phone)
    
    if not employee:
        return jsonify({
            'success': False,
            'message': '未找到该手机号对应的员工档案，请联系组织管理员添加员工档案'
        }), 404
    
    # 更新OpenID
    data_id = employee.get('_id')
    success = jdy_api.update_employee_openid(data_id, openid)
    
    if success:
        return jsonify({
            'success': True,
            'message': '绑定成功！',
            'data': {
                'name': employee.get('name', {}).get('name', ''),
                'phone': phone
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '绑定失败，请稍后重试'
        }), 500


@app.route('/api/check_bind', methods=['GET'])
def check_bind():
    """
    检查用户是否已绑定
    
    参数:
        openid: 微信OpenID
    
    返回:
        bound: 是否已绑定
        employee: 员工信息（已绑定时）
    """
    openid = request.args.get('openid', '')
    
    if not openid:
        return jsonify({
            'success': False,
            'message': '缺少OpenID参数'
        }), 400
    
    # 这里可以添加查询逻辑，检查该openid是否已绑定
    # 暂时返回未绑定状态
    return jsonify({
        'success': True,
        'bound': False
    })


@app.route('/api/test_reminder', methods=['POST'])
def test_reminder():
    """
    测试接口：立即执行一次日报检查
    仅用于开发测试
    """
    try:
        scheduler.run_now()
        return jsonify({
            'success': True,
            'message': '日报检查任务已执行，请查看控制台日志'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'执行失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    # 启动定时任务
    scheduler.start()
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except (KeyboardInterrupt, SystemExit):
        # 停止定时任务
        scheduler.stop()
