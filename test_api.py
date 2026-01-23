# -*- coding: utf-8 -*-
"""
API测试脚本
用于测试简道云和微信API功能
"""
from utils.jiandaoyun_api import JiandaoyunAPI
from utils.wechat_api import WeChatAPI
from datetime import datetime


def test_jiandaoyun():
    """测试简道云API"""
    print('=' * 50)
    print('测试简道云API')
    print('=' * 50)
    
    jdy = JiandaoyunAPI()
    
    # 测试1: 查询员工信息
    print('\n1. 测试查询员工信息（请输入测试手机号）:')
    phone = input('手机号: ').strip()
    
    if phone:
        employee = jdy.query_employee_by_phone(phone)
        print("++++++++++++++")
        print(employee)
        if employee:
            print(f'✓ 找到员工: {employee.get("name", {}).get("name", "未知")}')
            print(f'  数据ID: {employee.get("_id")}')
            print(f'  手机号: {employee.get("phonenumber")}')
        else:
            print('✗ 未找到该员工')
    
    # 测试2: 获取所有有OpenID的员工
    print('\n2. 测试获取所有已绑定OpenID的员工:')
    employees = jdy.get_all_employees_with_openid()
    print(f'✓ 找到 {len(employees)} 个已绑定员工')
    for emp in employees[:5]:  # 只显示前5个
        name = emp.get('name', {}).get('name', '未知')
        role = emp.get('juese', '未知')
        print(f'  - {name} ({role})')
    
    # 测试3: 查询日报
    print('\n3. 测试查询今日日报（请输入测试手机号）:')
    phone = input('手机号: ').strip()
    
    if phone:
        today = datetime.now().strftime('%Y-%m-%d')
        report = jdy.get_daily_report(phone, today)
        if report:
            print(f'✓ 找到今日日报')
            print(f'  员工: {report.get("ygxm", {}).get("name", "未知")}')
            print(f'  日期: {report.get("rbdate")}')
        else:
            print('✗ 未找到今日日报')


def test_wechat():
    """测试微信API"""
    print('\n' + '=' * 50)
    print('测试微信API')
    print('=' * 50)
    
    wechat = WeChatAPI()
    
    # 测试1: 获取access_token
    print('\n1. 测试获取access_token:')
    token = wechat.get_access_token()
    if token:
        print(f'✓ 获取成功: {token[:20]}...')
    else:
        print('✗ 获取失败')
    
    # 测试2: 发送测试消息（需要有效的OpenID）
    print('\n2. 测试发送模板消息（可选，需要OpenID）:')
    test_send = input('是否测试发送消息？(y/n): ').strip().lower()
    
    if test_send == 'y':
        openid = input('请输入测试OpenID: ').strip()
        if openid:
            success = wechat.send_daily_report_reminder(
                openid, '测试员工', 'pending', 'https://www.jiandaoyun.com'
            )
            if success:
                print('✓ 消息发送成功')
            else:
                print('✗ 消息发送失败')


def test_scheduler():
    """测试定时任务"""
    print('\n' + '=' * 50)
    print('测试定时任务')
    print('=' * 50)
    
    from scheduler import DailyReportScheduler
    
    print('\n是否立即执行一次日报检查？(y/n): ')
    test_run = input().strip().lower()
    
    if test_run == 'y':
        scheduler = DailyReportScheduler()
        scheduler.run_now()


if __name__ == '__main__':
    print('简道云日报提醒系统 - API测试工具')
    print('=' * 50)
    
    while True:
        print('\n请选择测试项目:')
        print('1. 测试简道云API')
        print('2. 测试微信API')
        print('3. 测试定时任务')
        print('4. 全部测试')
        print('0. 退出')
        
        choice = input('\n请输入选项: ').strip()
        
        if choice == '1':
            test_jiandaoyun()
        elif choice == '2':
            test_wechat()
        elif choice == '3':
            test_scheduler()
        elif choice == '4':
            test_jiandaoyun()
            test_wechat()
            test_scheduler()
        elif choice == '0':
            print('退出测试')
            break
        else:
            print('无效选项，请重新选择')
