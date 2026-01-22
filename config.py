# -*- coding: utf-8 -*-
"""
配置文件
"""
import os

class Config:
    """应用配置"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 简道云配置
    JIANDAOYUN_APP_ID = '696f27462cf9e340d630dde9'
    JIANDAOYUN_API_KEY = 'EFVTRmkmb44rwFjuUyg1PXFPCWlJjd70'
    JIANDAOYUN_EMPLOYEE_ENTRY_ID = '6655515cbf78649a2284b627'  # 员工档案表
    JIANDAOYUN_DAILY_REPORT_ENTRY_ID = '66554fa622ee7dd0c7bb5492'  # 日报数据表
    JIANDAOYUN_API_BASE_URL = 'https://api.jiandaoyun.com/api/v5'
    
    # 微信服务号配置
    WECHAT_APPID = 'wx4fce2b77e1ad0638'
    WECHAT_APPSECRET = '8f1d12b6e8379e4aabe5b00fe95e7cd2'
    WECHAT_TEMPLATE_ID = 'bpXQnOahugVOBDYYLVY8dcfSxSO9-0PoV3qPEiY1u4E'
    
    # 服务器配置
    SERVER_IP = '8.137.123.138'
