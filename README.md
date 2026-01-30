# 简道云日报提醒系统

基于简道云和微信服务号的自动化日报提醒系统，实现员工身份关联和每日日报提醒功能。

## 项目概述

本系统通过微信服务号与简道云API集成，实现：
- 员工通过手机号绑定微信OpenID
- 每日定时检查日报填写情况
- 自动发送微信提醒消息
- 管理员接收员工日报提交通知

## 技术栈

- **开发语言**: Python 3.8+
- **Web框架**: Flask
- **定时任务**: APScheduler
- **第三方API**: 简道云API、微信服务号API

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置信息

确认 `config.py` 中的配置正确：
- 简道云 APP_ID 和 API_KEY
- 微信服务号 APPID 和 APPSECRET
- 表单ID（员工档案表、日报数据表）

### 3. 测试功能

```bash
# 运行测试脚本
python test_api.py

# 启动应用
python app.py

# 手动触发日报检查
curl -X POST http://localhost:5000/api/test_reminder
```

## 核心功能

### 功能一：员工身份绑定

- 用户关注微信服务号
- 通过手机号查询简道云员工档案
- 绑定微信OpenID到员工档案

**API接口**: `POST /api/bind`

```json
{
  "phone": "手机号",
  "openid": "微信OpenID"
}
```

### 功能二：日报提醒

- 每天18:00自动执行
- 检查所有员工的日报填写情况
- 根据状态发送不同消息：
  - **已填写**: 通知员工本人 + 通知所有管理员
  - **未填写**: 仅通知员工本人填写

## 项目结构

```
.
├── app.py                  # Flask主应用
├── config.py              # 配置文件
├── scheduler.py           # 定时任务调度器
├── test_api.py           # API测试脚本
├── requirements.txt      # Python依赖
├── run.sh               # 启动脚本
├── utils/
│   ├── jiandaoyun_api.py  # 简道云API封装
│   └── wechat_api.py      # 微信API封装
├── templates/
│   └── bind.html          # 绑定页面
├── 产品需求文档.md        # 详细需求文档
├── 部署指南.md            # 部署说明
└── 快速开始.md            # 快速开始指南
```

## 开发状态

### 已完成
- ✅ 简道云API集成（查询员工、更新OpenID、查询日报）
- ✅ 微信API集成（获取token、发送模板消息）
- ✅ 员工身份绑定接口
- ✅ 定时任务调度器
- ✅ 日报检查和提醒逻辑
- ✅ 测试脚本和工具

### 待完成（域名通过后）
- ⏳ 微信服务号服务器配置
- ⏳ 自定义菜单配置
- ⏳ 网页授权配置
- ⏳ 完整流程测试

## 文档

- [产品需求文档](产品需求文档.md) - 详细的功能需求和接口说明
- [部署指南](部署指南.md) - 服务器部署和配置说明
- [快速开始](快速开始.md) - 本地开发和测试指南

## API接口

### 1. 首页
- **GET** `/` - 系统状态检查

### 2. 微信服务号
- **GET/POST** `/wechat` - 微信消息处理接口

### 3. 身份绑定
- **GET** `/bind` - 绑定页面
- **POST** `/api/bind` - 绑定手机号
- **GET** `/api/check_bind` - 检查绑定状态

### 4. 测试接口
- **POST** `/api/test_reminder` - 手动触发日报检查

## 定时任务

- **执行时间**: 每天18:00
- **任务内容**: 检查所有员工日报并发送提醒
- **日志输出**: 控制台显示详细执行过程

## 测试

### 运行测试脚本

```bash
python test_api.py
```

提供以下测试选项：
1. 测试简道云API
2. 测试微信API
3. 测试定时任务
4. 全部测试

### 手动触发日报检查

```bash
# 启动应用
python app.py

# 在另一个终端
curl -X POST http://localhost:5000/api/test_reminder
```

## 部署

### 开发环境

```bash
python app.py
```

### 生产环境

```bash
# 使用gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 后台运行
nohup gunicorn -w 4 -b 0.0.0.0:5000 app:app > gunicorn.log 2>&1 &
```

详细部署说明请参考 [部署指南](部署指南.md)

## 配置说明

### 简道云配置
- APP_ID: 应用ID
- API_KEY: API密钥
- EMPLOYEE_ENTRY_ID: 员工档案表ID
- DAILY_REPORT_ENTRY_ID: 日报数据表ID

### 微信服务号配置
- APPID: 服务号AppID
- APPSECRET: 服务号AppSecret
- TEMPLATE_ID: 模板消息ID

## 注意事项

1. **域名配置**: 微信服务号需要域名备案通过后才能配置
2. **OpenID获取**: 需要用户授权后才能获取真实OpenID
3. **消息发送**: 模板消息需要用户关注服务号
4. **定时任务**: 确保服务器时间正确

## 安全建议

- 生产环境修改 `SECRET_KEY`
- 使用HTTPS协议
- 不要将敏感信息提交到代码仓库
- 定期备份数据
- 限制API访问频率

## 许可证

本项目仅供内部使用

## 联系方式

如有问题，请联系项目负责人

---

**服务器**: 8.137.123.168
**版本**: v1.0  
**更新日期**: 2026-01-23
