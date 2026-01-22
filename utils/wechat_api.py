# -*- coding: utf-8 -*-
"""
微信API封装
"""
import requests
import time
from typing import Optional, Dict
from config import Config


class WeChatAPI:
    """微信服务号API客户端"""
    
    def __init__(self):
        self.appid = Config.WECHAT_APPID
        self.appsecret = Config.WECHAT_APPSECRET
        self.access_token = None
        self.token_expires_at = 0
    
    def get_access_token(self) -> Optional[str]:
        """
        获取微信access_token（带缓存）
        
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
            response = requests.get(url, params=params, timeout=10)
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
            response = requests.get(url, params=params, timeout=10)
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
    
    def send_template_message(self, openid: str, template_id: str, 
                            data: Dict, url: str = '') -> bool:
        """
        发送模板消息
        
        Args:
            openid: 接收者OpenID
            template_id: 模板ID
            data: 模板数据
            url: 跳转链接
            
        Returns:
            发送成功返回True，失败返回False
        """
        access_token = self.get_access_token()
        if not access_token:
            return False
        
        api_url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
        payload = {
            'touser': openid,
            'template_id': template_id,
            'url': url,
            'data': data
        }
        
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('errcode') == 0:
                return True
            else:
                print(f"发送模板消息失败: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f'发送模板消息请求失败: {e}')
            return False
