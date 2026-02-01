# -*- coding: utf-8 -*-
"""
测试日报数据结构和工作内容提取
"""
from utils.jiandaoyun_api import JiandaoyunAPI
from datetime import datetime
import json

def test_daily_report():
    """测试获取日报数据"""
    jdy_api = JiandaoyunAPI()
    
    # 使用你的手机号和今天的日期
    phone = '17608248238'
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f'查询日报: 手机号={phone}, 日期={today}')
    print('=' * 60)
    
    daily_report = jdy_api.get_daily_report(phone, today)
    
    if daily_report:
        print('✅ 找到日报数据')
        print('\n完整数据结构:')
        print(json.dumps(daily_report, ensure_ascii=False, indent=2))
        
        print('\n' + '=' * 60)
        print('字段列表:')
        for key in daily_report.keys():
            print(f'  - {key}')
        
        print('\n' + '=' * 60)
        print('提取工作内容测试:')
        
        # 提取工作内容（从mrgzhb数组中）
        work_content = ''
        if 'mrgzhb' in daily_report and isinstance(daily_report['mrgzhb'], list):
            work_items = []
            for item in daily_report['mrgzhb']:
                if isinstance(item, dict):
                    gzsx = item.get('gzsx', '')  # 工作事项
                    gznr = item.get('gznr', '')  # 工作内容
                    gzjd = item.get('gzjd', '')  # 工作进度
                    
                    print(f'\n工作项:')
                    print(f'  事项: {gzsx}')
                    print(f'  内容: {gznr}')
                    print(f'  进度: {gzjd}')
                    
                    if gzsx or gznr:
                        # 组合工作事项和内容
                        if gzsx and gznr:
                            work_items.append(f"{gzsx}: {gznr}")
                        elif gzsx:
                            work_items.append(gzsx)
                        elif gznr:
                            work_items.append(gznr)
            
            # 用换行符连接所有工作项
            work_content = '\n'.join(work_items)
        
        print('\n' + '=' * 60)
        print('最终提取的工作内容:')
        print(work_content if work_content else '(空)')
        
        print('\n' + '=' * 60)
        print('消息预览（前200字符）:')
        if work_content:
            preview = work_content[:200] + '...' if len(work_content) > 200 else work_content
            print(preview)
        else:
            print('(无工作内容)')
            
    else:
        print('❌ 未找到日报数据')

if __name__ == '__main__':
    test_daily_report()
