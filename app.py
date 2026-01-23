# -*- coding: utf-8 -*-
"""
Flask应用主文件
"""
from flask import Flask, request, jsonify, render_template, session
from config import Config
from utils.jiandaoyun_api import JiandaoyunAPI
from utils.wechat_api import WeChatAPI
import hashlib
import xml.etree.ElementTree as ET

mytoken = "MyWeChat2026htjiac"

app = Flask(__name__)
app.config.from_object(Config)

# 初始化API客户端
jdy_api = JiandaoyunAPI()
wechat_api = WeChatAPI()

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


if __name__ == '__main__':
    import time
    app.run(host='0.0.0.0', port=5000, debug=True)
