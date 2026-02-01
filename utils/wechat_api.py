# -*- coding: utf-8 -*-
"""
微信API封装
包含：
1. 网页授权获取OpenID
2. 客服消息发送
3. 用户信息获取
"""
import requests
import time
from typing import Optional, Dict, Tuple
from config import Config
import urllib3
import urllib.parse

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WeChatAPI:
    """微信服务号API客户端"""
    
    def __init__(self):
        self.appid = Config.WECHAT_APPID
        self.appsecret = Config.WECHAT_APPSECRET
        self.access_token = None
        self.token_expires_at = 0
    
    def get_oauth_authorize_url(self, redirect_uri: str, scope: str = 'snsapi_base', 
                               state: str = 'STATE') -> str:
        """
        生成微信网页授权URL
        
        Args:
            redirect_uri: 授权后重定向的回调链接地址
            scope: 应用授权作用域
                   - snsapi_base: 静默授权，只能获取openid
                   - snsapi_userinfo: 需要用户手动同意，可获取用户基本信息
            state: 重定向后会带上state参数，可用于防止csrf攻击
            
        Returns:
            微信授权URL
        """
        # URL编码回调地址
        encoded_redirect_uri = urllib.parse.quote(redirect_uri, safe='')
        
        auth_url = (
            f"https://open.weixin.qq.com/connect/oauth2/authorize?"
            f"appid={self.appid}"
            f"&redirect_uri={encoded_redirect_uri}"
            f"&response_type=code"
            f"&scope={scope}"
            f"&state={state}"
            f"#wechat_redirect"
        )
        
        return auth_url
    
    def get_oauth_access_token(self, code: str) -> Optional[Dict]:
        """
        通过code换取网页授权access_token和openid
        
        注意：此access_token与基础支持的access_token不同
        
        Args:
            code: 微信授权回调返回的code参数
            
        Returns:
            包含access_token、openid等信息的字典，失败返回None
            返回示例：
            {
                'access_token': 'ACCESS_TOKEN',
                'expires_in': 7200,
                'refresh_token': 'REFRESH_TOKEN',
                'openid': 'OPENID',
                'scope': 'snsapi_base'
            }
        """
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        params = {
            'appid': self.appid,
            'secret': self.appsecret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            
            if 'openid' in data:
                return data
            else:
                print(f"获取网页授权access_token失败: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f'请求网页授权access_token失败: {e}')
            return None
    
    def get_oauth_userinfo(self, oauth_access_token: str, openid: str) -> Optional[Dict]:
        """
        拉取用户信息（需scope为snsapi_userinfo）
        
        Args:
            oauth_access_token: 网页授权接口调用凭证（注意：不是普通access_token）
            openid: 用户的唯一标识
            
        Returns:
            用户信息字典，失败返回None
        """
        url = 'https://api.weixin.qq.com/sns/userinfo'
        params = {
            'access_token': oauth_access_token,
            'openid': openid,
            'lang': 'zh_CN'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            
            if 'errcode' not in data:
                return data
            else:
                print(f"获取用户信息失败: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f'请求用户信息失败: {e}')
            return None
    
    def refresh_oauth_access_token(self, refresh_token: str) -> Optional[Dict]:
        """
        刷新网页授权access_token
        
        Args:
            refresh_token: 填写通过get_oauth_access_token获取到的refresh_token参数
            
        Returns:
            新的access_token信息，失败返回None
        """
        url = 'https://api.weixin.qq.com/sns/oauth2/refresh_token'
        params = {
            'appid': self.appid,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        try:
            response = requests.get(url, params=params, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            
            if 'openid' in data:
                return data
            else:
                print(f"刷新access_token失败: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f'刷新access_token请求失败: {e}')
            return None
    
    # ==================== 基础支持接口 ====================
    # 用于主动调用微信API（如发送模板消息）
    
    def get_access_token(self) -> Optional[str]:
        """
        获取基础支持的access_token（带缓存）
        用于主动调用微信API，如发送模板消息
        
        注意：此access_token与网页授权的access_token不同
        
        Returns:
            access_token字符串，失败返回None
        """
        # 检查缓存的token是否有效
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        # 请求新的token
        url = 'https://api.weixin.qq.com/cgi-bin/token'
        params = {
            'grant_type': 'client_credential',
            'appid': self.appid,
            'secret': self.appsecret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                # 提前5分钟过期，避免边界问题
                self.token_expires_at = time.time() + data.get('expires_in', 7200) - 300
                return self.access_token
            else:
                print(f"获取access_token失败: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f'请求access_token失败: {e}')
            return None
    
    def get_user_info(self, openid: str) -> Optional[Dict]:
        """
        获取用户基本信息
        
        Args:
            openid: 用户的OpenID
            
        Returns:
            用户信息字典，失败返回None
        """
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = 'https://api.weixin.qq.com/cgi-bin/user/info'
        params = {
            'access_token': access_token,
            'openid': openid,
            'lang': 'zh_CN'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            
            if 'errcode' not in data:
                return data
            else:
                print(f"获取用户信息失败: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f'请求用户信息失败: {e}')
            return None
    
    def send_custom_message(self, openid: str, content: str, msgtype: str = 'text') -> bool:
        """
        发送客服消息
        
        Args:
            openid: 接收者OpenID
            content: 消息内容
            msgtype: 消息类型（text/image/link等）
            
        Returns:
            发送成功返回True，失败返回False
        """
        import json
        
        access_token = self.get_access_token()
        if not access_token:
            return False
        
        api_url = f'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}'
        
        if msgtype == 'text':
            payload = {
                'touser': openid,
                'msgtype': 'text',
                'text': {
                    'content': content
                }
            }
        else:
            return False
        
        try:
            # 使用json.dumps确保不转义Unicode字符
            json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            response = requests.post(
                api_url, 
                data=json_data, 
                timeout=10, 
                verify=False,
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('errcode') == 0:
                return True
            else:
                errcode = result.get('errcode')
                errmsg = result.get('errmsg', '')
                
                # 特殊错误码提示
                if errcode == 45015:
                    print(f"发送客服消息失败: 超过48小时互动窗口，用户需要重新与公众号互动（发消息/点菜单）")
                elif errcode == 45047:
                    print(f"发送客服消息失败: 客服接口下行条数超过上限")
                else:
                    print(f"发送客服消息失败: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f'发送客服消息请求失败: {e}')
            return False
    

    
    def send_daily_report_reminder(self, openid: str, employee_name: str, 
                                   report_status: str, report_url: str = '', 
                                   work_content: str = '') -> bool:
        """
        发送日报提醒消息（使用客服消息）
        
        Args:
            openid: 接收者OpenID
            employee_name: 员工姓名
            report_status: 日报状态（submitted/pending/admin_notify）
            report_url: 日报链接（保留参数以兼容调用，但不使用）
            work_content: 工作内容（仅在submitted状态时使用）
            
        Returns:
            发送成功返回True，失败返回False
        """
        # 根据不同状态构造消息内容
        if report_status == 'submitted':
            # 员工本人 - 已提交
            message_text = f"✅ 日报提交成功\n\n您好，{employee_name}！\n您今日的工作日报已提交成功。\n\n提交时间：{time.strftime('%Y-%m-%d')}"
            
            # 如果有工作内容，添加工作内容摘要
            if work_content:
                # 限制工作内容长度，避免消息过长（微信客服消息限制2048字符）
                if len(work_content) > 200:
                    content_preview = work_content[:200] + '...'
                else:
                    content_preview = work_content
                message_text += f"\n\n📝 今日工作：\n{content_preview}"
            
            message_text += "\n\n感谢您的及时提交！"
            
        elif report_status == 'admin_notify':
            # 管理员 - 员工已提交通知
            message_text = f"📋 日报提交通知\n\n员工【{employee_name}】已提交今日工作日报。\n\n提交时间：{time.strftime('%Y-%m-%d')}"
            
            # 管理员通知也显示工作内容摘要
            if work_content:
                if len(work_content) > 150:
                    content_preview = work_content[:150] + '...'
                else:
                    content_preview = work_content
                message_text += f"\n\n📝 工作内容：\n{content_preview}"
                
        else:  # pending
            # 员工本人 - 未提交提醒
            message_text = f"⏰ 日报填写提醒\n\n您好，{employee_name}！\n\n请记得填写今日工作日报。\n日期：{time.strftime('%Y年%m月%d日')}\n\n请及时登录简道云填写日报，谢谢！"
        
        # 使用客服消息发送（无需订阅，48小时内互动过即可）
        return self.send_custom_message(openid, message_text)
