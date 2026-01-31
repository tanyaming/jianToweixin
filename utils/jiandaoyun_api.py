# -*- coding: utf-8 -*-
"""
简道云API封装
"""
import requests
from typing import Dict, List, Optional
from config import Config
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class JiandaoyunAPI:
    """简道云API客户端"""
    
    def __init__(self):
        self.base_url = Config.JIANDAOYUN_API_BASE_URL
        self.api_key = Config.JIANDAOYUN_API_KEY
        self.app_id = Config.JIANDAOYUN_APP_ID
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def query_employee_by_phone(self, phone: str) -> Optional[Dict]:
        """
        通过手机号查询员工信息
        
        Args:
            phone: 手机号码
            
        Returns:
            员工信息字典，未找到返回None
        """
        url = f'{self.base_url}/app/entry/data/list'
        payload = {
            'app_id': self.app_id,
            'entry_id': Config.JIANDAOYUN_EMPLOYEE_ENTRY_ID,
            'fields': ['name', 'phonenumber'],
            'filter': {
                'rel': 'and',
                'cond': [{
                    'field': 'phonenumber',
                    'type': 'text',
                    'method': 'eq',
                    'value': [phone]
                }]
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                return data['data'][0]
            return None
            
        except requests.exceptions.RequestException as e:
            print(f'查询员工信息失败: {e}')
            return None
    
    def update_employee_openid(self, data_id: str, openid: str) -> bool:
        """
        更新员工档案的微信OpenID
        
        Args:
            data_id: 员工数据ID
            openid: 微信OpenID
            
        Returns:
            更新成功返回True，失败返回False
        """
        url = f'{self.base_url}/app/entry/data/update'
        payload = {
            'app_id': self.app_id,
            'entry_id': Config.JIANDAOYUN_EMPLOYEE_ENTRY_ID,
            'data_id': data_id,
            'data': {
                'wxopenid': {
                    'value': openid
                }
            }
        }
        
        print(f'[DEBUG] 更新 OpenID 请求:')
        print(f'  URL: {url}')
        print(f'  data_id: {data_id}')
        print(f'  openid: {openid}')
        print(f'  payload: {payload}')
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10, verify=False)
            print(f'[DEBUG] 响应状态码: {response.status_code}')
            print(f'[DEBUG] 响应内容: {response.text[:500]}...')  # 只打印前500字符
            
            response.raise_for_status()
            result = response.json()
            
            # 简道云更新接口成功时返回更新后的数据对象
            # 检查返回的data中是否包含wxopenid字段
            if 'data' in result and '_id' in result['data']:
                updated_openid = result['data'].get('wxopenid')
                if updated_openid == openid:
                    print(f'[DEBUG] ✅ OpenID 更新成功: {openid}')
                    return True
                else:
                    print(f'[DEBUG] ✅ OpenID 已更新（返回数据包含_id）')
                    return True
            # 如果有错误码，说明失败
            elif 'code' in result and result['code'] != 0:
                print(f'[DEBUG] ❌ OpenID 更新失败: {result}')
                return False
            else:
                print(f'[DEBUG] ⚠️ 无法确认更新状态: {result}')
                return False
            
        except requests.exceptions.RequestException as e:
            print(f'❌ 更新员工OpenID失败: {e}')
            if hasattr(e, 'response') and e.response is not None:
                print(f'[DEBUG] 错误响应: {e.response.text}')
            return False
    
    def get_all_employees_with_openid(self) -> List[Dict]:
        """
        获取所有有OpenID的员工列表
        
        Returns:
            员工信息列表（wxopenid字段已标准化为字符串）
        """
        url = f'{self.base_url}/app/entry/data/list'
        payload = {
            'app_id': self.app_id,
            'entry_id': Config.JIANDAOYUN_EMPLOYEE_ENTRY_ID,
            'fields': ['wxopenid', 'juese', 'phonenumber', 'name']
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            
            # 过滤出有OpenID的员工，并标准化数据格式
            employees = []
            for emp in data.get('data', []):
                openid_field = emp.get('wxopenid')
                
                # 处理不同的数据格式
                if isinstance(openid_field, dict):
                    openid = openid_field.get('value', '')
                elif isinstance(openid_field, str):
                    openid = openid_field
                else:
                    openid = ''
                
                # 只添加有有效 openid 的员工
                if openid:
                    # 标准化 openid 为字符串格式
                    emp['wxopenid'] = openid
                    employees.append(emp)
            
            return employees
            
        except requests.exceptions.RequestException as e:
            print(f'获取员工列表失败: {e}')
            return []
    
    def get_daily_report(self, phone: str, date: str) -> Optional[Dict]:
        """
        查询指定员工指定日期的日报
        
        Args:
            phone: 员工手机号
            date: 日期，格式：YYYY-MM-DD
            
        Returns:
            日报信息字典，未找到返回None
        """
        url = f'{self.base_url}/app/entry/data/list'
        payload = {
            'app_id': self.app_id,
            'entry_id': Config.JIANDAOYUN_DAILY_REPORT_ENTRY_ID,
            'fields': ['phonenumber', 'rbdate', 'ygxm', 'szbm', 'gznr', 'gzjd', 'mrgzhb'],
            'filter': {
                'rel': 'and',
                'cond': [
                    {
                        'field': 'phonenumber',
                        'type': 'text',
                        'method': 'eq',
                        'value': [phone]
                    },
                    {
                        'field': 'rbdate',
                        'type': 'datetime',
                        'method': 'eq',
                        'value': [date]
                    }
                ]
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                return data['data'][0]
            return None
            
        except requests.exceptions.RequestException as e:
            print(f'查询日报失败: {e}')
            return None
