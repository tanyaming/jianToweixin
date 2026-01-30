# -*- coding: utf-8 -*-
"""
创建微信公众号自定义菜单
"""
import requests
from config import Config
import json

def get_access_token():
    """获取access_token"""
    url = 'https://api.weixin.qq.com/cgi-bin/token'
    params = {
        'grant_type': 'client_credential',
        'appid': Config.WECHAT_APPID,
        'secret': Config.WECHAT_APPSECRET
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'access_token' in data:
        return data['access_token']
    else:
        print(f'获取access_token失败: {data}')
        return None


def create_menu(access_token):
    """创建自定义菜单"""
    url = f'https://api.weixin.qq.com/cgi-bin/menu/create?access_token={access_token}'
    
    # 菜单配置
    menu_data = {
        "button": [
            {
                "type": "view",
                "name": "身份绑定",
                "url": "https://htjc.shop/get_openid"
            },
            {
                "name": "日报管理",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "填写日报",
                        "url": "https://www.jiandaoyun.com"
                    },
                    {
                        "type": "view",
                        "name": "查看日报",
                        "url": "https://www.jiandaoyun.com"
                    }
                ]
            }
        ]
    }
    
    print('创建菜单配置:')
    print(json.dumps(menu_data, indent=2, ensure_ascii=False))
    
    # 使用 data 参数并指定编码，而不是 json 参数
    response = requests.post(
        url, 
        data=json.dumps(menu_data, ensure_ascii=False).encode('utf-8'),
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )
    result = response.json()
    
    print('\n微信API响应:')
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get('errcode') == 0:
        print('\n✓ 菜单创建成功！')
        print('提示：菜单可能需要24小时后才会生效，或者取消关注后重新关注立即生效')
        return True
    else:
        print(f'\n✗ 菜单创建失败: {result.get("errmsg")}')
        return False


def get_current_menu(access_token):
    """查询当前菜单"""
    url = f'https://api.weixin.qq.com/cgi-bin/menu/get?access_token={access_token}'
    
    response = requests.get(url)
    result = response.json()
    
    print('当前菜单配置:')
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result


def delete_menu(access_token):
    """删除当前菜单"""
    url = f'https://api.weixin.qq.com/cgi-bin/menu/delete?access_token={access_token}'
    
    response = requests.get(url)
    result = response.json()
    
    if result.get('errcode') == 0:
        print('✓ 菜单删除成功')
        return True
    else:
        print(f'✗ 菜单删除失败: {result.get("errmsg")}')
        return False


if __name__ == '__main__':
    print('=' * 60)
    print('微信公众号自定义菜单管理工具')
    print('=' * 60)
    
    # 获取access_token
    print('\n1. 获取access_token...')
    access_token = get_access_token()
    
    if not access_token:
        print('无法获取access_token，请检查AppID和AppSecret配置')
        exit(1)
    
    print(f'✓ access_token: {access_token[:20]}...')
    
    # 菜单操作
    print('\n请选择操作:')
    print('1. 创建菜单')
    print('2. 查询当前菜单')
    print('3. 删除菜单')
    print('4. 删除并重新创建菜单')
    
    choice = input('\n请输入选项 (1-4): ').strip()
    
    if choice == '1':
        print('\n2. 创建自定义菜单...')
        create_menu(access_token)
    elif choice == '2':
        print('\n2. 查询当前菜单...')
        get_current_menu(access_token)
    elif choice == '3':
        print('\n2. 删除菜单...')
        delete_menu(access_token)
    elif choice == '4':
        print('\n2. 删除旧菜单...')
        delete_menu(access_token)
        print('\n3. 创建新菜单...')
        create_menu(access_token)
    else:
        print('无效选项')
