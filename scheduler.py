# -*- coding: utf-8 -*-
"""
定时任务调度器
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from utils.jiandaoyun_api import JiandaoyunAPI
from utils.wechat_api import WeChatAPI
from config import Config


class DailyReportScheduler:
    """日报提醒定时任务"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jdy_api = JiandaoyunAPI()
        self.wechat_api = WeChatAPI()
    
    def check_and_send_reminders(self):
        """检查日报并发送提醒"""
        print(f'[{datetime.now()}] 开始执行日报检查任务...')
        
        try:
            # 1. 获取所有有OpenID的成员
            all_members = self.jdy_api.get_all_employees_with_openid()
            
            if not all_members:
                print('未找到已绑定OpenID的成员')
                return
            
            print(f'找到 {len(all_members)} 个已绑定成员')
            
            # 2. 筛选管理员列表
            admins = [m for m in all_members if m.get('juese') == '管理员']
            print(f'管理员数量: {len(admins)}')
            
            # 3. 获取今天的日期
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 4. 遍历每个成员检查日报
            for member in all_members:
                phone = member.get('phonenumber')
                openid = member.get('wxopenid')  # 已在 API 层标准化为字符串
                name = member.get('name', {}).get('name', '未知')
                role = member.get('juese', '员工')
                
                if not phone or not openid:
                    print(f'  跳过成员 {name}: 缺少手机号或OpenID')
                    continue
                
                print(f'  使用 OpenID: {openid[:10]}...')
                
                print(f'检查成员: {name} ({role}) - {phone}')
                
                # 查询今日日报
                daily_report = self.jdy_api.get_daily_report(phone, today)
                
                # 构造日报链接（根据实际情况调整）
                report_url = f'https://www.jiandaoyun.com/app/{Config.JIANDAOYUN_APP_ID}/entry/{Config.JIANDAOYUN_DAILY_REPORT_ENTRY_ID}'
                
                if daily_report:
                    # 已填写日报
                    print(f'  ✓ {name} 已填写日报')
                    
                    # 通知员工本人
                    success = self.wechat_api.send_daily_report_reminder(
                        openid, name, 'submitted', report_url
                    )
                    if success:
                        print(f'  → 已通知员工本人')
                    else:
                        print(f'  → 通知员工本人失败')
                    
                    # 通知所有管理员
                    for admin in admins:
                        admin_openid = admin.get('wxopenid')  # 已标准化为字符串
                        admin_name = admin.get('name', {}).get('name', '管理员')
                        
                        if admin_openid and admin_openid != openid:  # 不重复通知自己
                            success = self.wechat_api.send_daily_report_reminder(
                                admin_openid, name, 'admin_notify', report_url
                            )
                            if success:
                                print(f'  → 已通知管理员: {admin_name}')
                            else:
                                print(f'  → 通知管理员失败: {admin_name}')
                else:
                    # 未填写日报
                    print(f'  ✗ {name} 未填写日报')
                    
                    # 仅通知员工本人
                    success = self.wechat_api.send_daily_report_reminder(
                        openid, name, 'pending', report_url
                    )
                    if success:
                        print(f'  → 已发送提醒')
                    else:
                        print(f'  → 发送提醒失败')
            
            print(f'[{datetime.now()}] 日报检查任务完成')
            
        except Exception as e:
            print(f'执行日报检查任务失败: {e}')
            import traceback
            traceback.print_exc()
    
    def start(self):
        """启动定时任务"""
        # 每天18:00执行
        self.scheduler.add_job(
            self.check_and_send_reminders,
            'cron',
            hour=18,
            minute=0,
            id='daily_report_reminder'
        )
        
        self.scheduler.start()
        print('定时任务已启动，每天18:00执行日报检查')
    
    def stop(self):
        """停止定时任务"""
        self.scheduler.shutdown()
        print('定时任务已停止')
    
    def run_now(self):
        """立即执行一次（用于测试）"""
        print('手动触发日报检查任务...')
        self.check_and_send_reminders()
