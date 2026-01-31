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
import logging
from logging.handlers import RotatingFileHandler
import os

mytoken = "MyWeChat2026htjiac"

app = Flask(__name__)
app.config.from_object(Config)

# 配置日志
if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240000, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('应用启动')

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


@app.route('/MP_verify_<filename>.txt')
def wechat_verify(filename):
    """微信公众号域名验证文件"""
    # 从微信公众平台获取验证码，替换下面的内容
    verify_code = "请替换为你的验证码"
    return verify_code, 200, {'Content-Type': 'text/plain'}


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
        app.logger.error(f'处理微信消息失败: {e}')
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
    
    app.logger.info(f'访问绑定页面 - OpenID: {openid if openid else "无"}')
    
    if not openid:
        app.logger.warning('访问绑定页面但缺少 OpenID')
        return '''
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>参数错误</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; text-align: center; }
                .error { color: #d32f2f; background: #ffebee; padding: 15px; border-radius: 5px; margin: 20px; }
            </style>
        </head>
        <body>
            <h3>参数错误</h3>
            <div class="error">
                <p>缺少 OpenID 参数</p>
                <p>请从微信公众号菜单进入</p>
            </div>
        </body>
        </html>
        ''', 400
    
    # 验证 OpenID 格式（微信 OpenID 通常是 28 位字母数字组合）
    if openid == 'OPENID' or len(openid) < 20:
        app.logger.warning(f'OpenID 格式不正确: {openid}')
        return '''
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>授权失败</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; text-align: center; }
                .error { color: #d32f2f; background: #ffebee; padding: 15px; border-radius: 5px; margin: 20px; }
            </style>
        </head>
        <body>
            <h3>授权失败</h3>
            <div class="error">
                <p>未能获取到有效的用户授权</p>
                <p>请重新从微信公众号菜单进入</p>
            </div>
        </body>
        </html>
        ''', 400
    
    # 保存openid到session
    session['openid'] = openid
    
    return render_template('bind.html', openid=openid)


@app.route('/get_openid', methods=['GET'])
def get_openid():
    """
    获取OpenID并跳转到绑定页面
    用于微信网页授权获取用户OpenID
    
    流程：
    1. 用户点击菜单 -> 访问此页面（无code）
    2. 重定向到微信授权页面
    3. 用户授权后微信回调此页面（带code）
    4. 用code换取openid
    5. 跳转到绑定页面
    """
    code = request.args.get('code', '')
    
    app.logger.info(f'访问 /get_openid - code: {code if code else "无"}')
    
    # 如果没有code，重定向到微信授权页面
    if not code:
        import urllib.parse
        # 使用完整的 HTTPS URL
        redirect_uri = urllib.parse.quote(f'https://{request.host}/get_openid', safe='')
        auth_url = f'https://open.weixin.qq.com/connect/oauth2/authorize?appid={Config.WECHAT_APPID}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_base&state=bind#wechat_redirect'
        
        app.logger.info(f'重定向到微信授权: {auth_url}')
        return f'''
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>正在跳转...</title>
        </head>
        <body>
            <p style="text-align:center; padding:50px;">正在获取授权...</p>
            <script>window.location.href="{auth_url}"</script>
        </body>
        </html>
        '''
    
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
        
        app.logger.info(f'用 code 换取 OpenID: {code}')
        response = requests.get(url, params=params, timeout=10, verify=False)
        data = response.json()
        app.logger.info(f'微信 API 响应: {data}')
        
        if 'openid' in data:
            openid = data['openid']
            app.logger.info(f'✓ 成功获取 OpenID: {openid}')
            
            # 跳转到绑定页面
            import urllib.parse
            bind_url = f'/bind?openid={urllib.parse.quote(openid)}'
            return f'''
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>正在跳转...</title>
            </head>
            <body>
                <p style="text-align:center; padding:50px;">授权成功，正在跳转到绑定页面...</p>
                <script>window.location.href="{bind_url}"</script>
            </body>
            </html>
            '''
        else:
            error_msg = data.get('errmsg', '未知错误')
            app.logger.error(f'✗ 获取 OpenID 失败: {data}')
            return f'''
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>获取授权失败</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    .error {{ color: #d32f2f; background: #ffebee; padding: 15px; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <h3>获取授权失败</h3>
                <div class="error">
                    <p>错误信息: {error_msg}</p>
                    <p>错误代码: {data.get('errcode', 'N/A')}</p>
                </div>
                <p>请联系管理员或重试</p>
            </body>
            </html>
            '''
            
    except Exception as e:
        app.logger.error(f'✗ 获取 OpenID 异常: {e}')
        import traceback
        app.logger.error(traceback.format_exc())
        return f'''
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>系统错误</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .error {{ color: #d32f2f; background: #ffebee; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h3>系统错误</h3>
            <div class="error">
                <p>{str(e)}</p>
            </div>
            <p>请联系管理员</p>
        </body>
        </html>
        '''


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
    
    app.logger.info(f'收到绑定请求 - data员工信息: {data} , 手机号: {phone}, OpenID: {openid}')
    
    # 参数验证
    if not phone or not openid:
        app.logger.warning('绑定失败: 手机号或OpenID为空')
        return jsonify({
            'success': False,
            'message': '手机号和OpenID不能为空'
        }), 400
    
    # 手机号格式验证
    if len(phone) != 11 or not phone.isdigit():
        app.logger.warning(f'绑定失败: 手机号格式不正确 - {phone}')
        return jsonify({
            'success': False,
            'message': '手机号格式不正确'
        }), 400
    
    # 查询员工信息
    app.logger.info(f'查询员工信息: {phone}')
    employee = jdy_api.query_employee_by_phone(phone)
    
    if not employee:
        app.logger.warning(f'绑定失败: 未找到员工 - {phone}')
        return jsonify({
            'success': False,
            'message': '未找到该手机号对应的员工档案，请联系组织管理员添加员工档案'
        }), 404
    
    # 更新OpenID
    data_id = employee.get('_id')
    employee_name = employee.get('name', {}).get('name', '未知')
    app.logger.info(f'找到员工: {employee_name}, data_id: {data_id}')
    app.logger.info(f'开始更新 OpenID: {openid}')
    
    success = jdy_api.update_employee_openid(data_id, openid)
    
    if success:
        app.logger.info(f'绑定成功: {employee_name} - {phone} - {openid}')
        return jsonify({
            'success': True,
            'message': '绑定成功！',
            'data': {
                'name': employee_name,
                'phone': phone
            }
        })
    else:
        app.logger.error(f'绑定失败: 更新 OpenID 失败 - {employee_name}')
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
        app.run(host='0.0.0.0', port=5008, debug=True)
    except (KeyboardInterrupt, SystemExit):
        # 停止定时任务
        scheduler.stop()
