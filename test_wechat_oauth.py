#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信网页授权测试脚本
用于测试 wechat_api.py 中的网页授权功能
"""
from utils.wechat_api import WeChatAPI
from config import Config

def test_generate_auth_url():
    """测试生成授权URL"""
    print("=" * 60)
    print("测试1: 生成微信授权URL")
    print("=" * 60)
    
    wechat = WeChatAPI()
    
    # 测试snsapi_base（静默授权）
    redirect_uri = f"{Config.BASE_URL}/get_openid"
    auth_url = wechat.get_oauth_authorize_url(
        redirect_uri=redirect_uri,
        scope='snsapi_base',
        state='bind'
    )
    
    print(f"\n📋 回调地址: {redirect_uri}")
    print(f"\n🔗 授权URL (snsapi_base):")
    print(auth_url)
    print("\n✅ 用户访问此URL将进行静默授权（无需用户确认）")
    
    # 测试snsapi_userinfo（用户授权）
    auth_url_userinfo = wechat.get_oauth_authorize_url(
        redirect_uri=redirect_uri,
        scope='snsapi_userinfo',
        state='bind'
    )
    
    print(f"\n🔗 授权URL (snsapi_userinfo):")
    print(auth_url_userinfo)
    print("\n⚠️  用户访问此URL需要手动确认授权")
    
    return True

def test_exchange_code_for_openid():
    """测试用code换取openid"""
    print("\n" + "=" * 60)
    print("测试2: 用code换取OpenID")
    print("=" * 60)
    
    print("\n📝 说明:")
    print("1. code是微信授权回调时返回的参数")
    print("2. code有效期5分钟，只能使用一次")
    print("3. 需要真实的code才能测试此功能")
    
    code = input("\n请输入微信返回的code（直接回车跳过）: ").strip()
    
    if not code:
        print("⏭️  跳过此测试")
        return False
    
    wechat = WeChatAPI()
    
    print(f"\n🔄 正在用code换取OpenID...")
    oauth_data = wechat.get_oauth_access_token(code)
    
    if oauth_data:
        print("\n✅ 成功获取授权信息:")
        print(f"   OpenID: {oauth_data.get('openid')}")
        print(f"   Access Token: {oauth_data.get('access_token')[:20]}...")
        print(f"   Expires In: {oauth_data.get('expires_in')} 秒")
        print(f"   Scope: {oauth_data.get('scope')}")
        
        if oauth_data.get('scope') == 'snsapi_userinfo':
            # 如果是snsapi_userinfo，可以获取用户信息
            print("\n🔄 正在获取用户详细信息...")
            userinfo = wechat.get_oauth_userinfo(
                oauth_data.get('access_token'),
                oauth_data.get('openid')
            )
            if userinfo:
                print("\n✅ 用户信息:")
                print(f"   昵称: {userinfo.get('nickname')}")
                print(f"   性别: {userinfo.get('sex')}")
                print(f"   城市: {userinfo.get('city')}")
                print(f"   省份: {userinfo.get('province')}")
        
        return True
    else:
        print("\n❌ 获取OpenID失败")
        print("可能原因:")
        print("1. code已过期（5分钟有效期）")
        print("2. code已被使用过（只能使用一次）")
        print("3. APPID或APPSECRET配置错误")
        return False

def test_basic_access_token():
    """测试基础支持access_token"""
    print("\n" + "=" * 60)
    print("测试3: 获取基础支持access_token")
    print("=" * 60)
    
    print("\n📝 说明:")
    print("基础支持access_token用于主动调用微信API")
    print("如：发送模板消息、创建菜单等")
    print("注意：与网页授权access_token不同！")
    
    wechat = WeChatAPI()
    
    print(f"\n🔄 正在获取access_token...")
    access_token = wechat.get_access_token()
    
    if access_token:
        print(f"\n✅ 成功获取access_token:")
        print(f"   Token: {access_token[:20]}...")
        print(f"   有效期: 7200秒（2小时）")
        print(f"   用途: 发送模板消息、管理菜单等")
        return True
    else:
        print("\n❌ 获取access_token失败")
        print("请检查APPID和APPSECRET配置")
        return False

def show_config():
    """显示当前配置"""
    print("\n" + "=" * 60)
    print("当前配置信息")
    print("=" * 60)
    
    print(f"\n🔧 微信配置:")
    print(f"   APPID: {Config.WECHAT_APPID}")
    print(f"   APPSECRET: {Config.WECHAT_APPSECRET[:10]}...")
    print(f"   模板ID: {Config.WECHAT_TEMPLATE_ID}")
    
    print(f"\n🌐 域名配置:")
    print(f"   域名: {Config.DOMAIN}")
    print(f"   BASE_URL: {Config.BASE_URL}")
    
    print(f"\n📋 授权回调地址:")
    print(f"   {Config.BASE_URL}/get_openid")
    
    print(f"\n⚠️  重要提醒:")
    print(f"   1. 确保在微信公众平台配置网页授权域名: {Config.DOMAIN}")
    print(f"   2. 确保域名已配置SSL证书（HTTPS）")
    print(f"   3. 确保服务正常运行并可访问")

def show_complete_flow():
    """显示完整授权流程"""
    print("\n" + "=" * 60)
    print("完整授权流程演示")
    print("=" * 60)
    
    wechat = WeChatAPI()
    redirect_uri = f"{Config.BASE_URL}/get_openid"
    
    print("\n📱 步骤1: 用户点击微信菜单")
    print(f"   菜单URL: {Config.BASE_URL}/get_openid")
    
    print("\n🔄 步骤2: 系统生成授权URL")
    auth_url = wechat.get_oauth_authorize_url(
        redirect_uri=redirect_uri,
        scope='snsapi_base',
        state='bind'
    )
    print(f"   授权URL: {auth_url[:80]}...")
    
    print("\n✅ 步骤3: 用户授权（静默）")
    print(f"   微信回调: {redirect_uri}?code=CODE&state=bind")
    
    print("\n🔄 步骤4: 系统用code换取openid")
    print(f"   调用API: https://api.weixin.qq.com/sns/oauth2/access_token")
    
    print("\n📝 步骤5: 跳转到绑定页面")
    print(f"   绑定URL: {Config.BASE_URL}/bind?openid=OPENID")
    
    print("\n✅ 步骤6: 用户输入手机号完成绑定")

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("微信网页授权测试工具")
    print("=" * 60)
    
    while True:
        print("\n📋 请选择测试项目:")
        print("1. 查看当前配置")
        print("2. 生成授权URL")
        print("3. 用code换取OpenID（需要真实code）")
        print("4. 测试基础access_token")
        print("5. 查看完整授权流程")
        print("6. 运行所有测试")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-6): ").strip()
        
        if choice == '0':
            print("\n👋 再见！")
            break
        elif choice == '1':
            show_config()
        elif choice == '2':
            test_generate_auth_url()
        elif choice == '3':
            test_exchange_code_for_openid()
        elif choice == '4':
            test_basic_access_token()
        elif choice == '5':
            show_complete_flow()
        elif choice == '6':
            show_config()
            test_generate_auth_url()
            test_basic_access_token()
            test_exchange_code_for_openid()
            show_complete_flow()
        else:
            print("❌ 无效选项，请重新选择")

if __name__ == "__main__":
    main()