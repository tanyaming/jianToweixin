# 简道云日报提醒系统

基于Flask + 简道云 + 微信服务号的自动化日报提醒系统

## 功能特性

- ✅ 微信用户身份绑定
- ⏰ 每日定时日报提醒
- 📊 管理员日报通知

## 项目结构

```
.
├── app.py                  # Flask主应用
├── config.py              # 配置文件
├── requirements.txt       # 依赖包
├── utils/
│   ├── jiandaoyun_api.py # 简道云API封装
│   └── wechat_api.py     # 微信API封装
└── templates/
    └── bind.html         # 身份绑定页面
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `config.py` 文件，确认配置信息正确。

### 3. 运行应用

```bash
python app.py
```

应用将在 `http://0.0.0.0:5000` 启动。

## API接口

### 身份绑定

**POST** `/api/bind`

请求参数：
```json
{
  "phone": "17608248238",
  "openid": "user_openid"
}
```

响应：
```json
{
  "success": true,
  "message": "绑定成功！",
  "data": {
    "name": "员工姓名",
    "phone": "17608248238"
  }
}
```

## 部署说明

### 服务器部署

1. 上传代码到服务器 `8.137.123.138`
2. 安装依赖
3. 使用 gunicorn 或 uwsgi 运行
4. 配置 Nginx 反向代理

### 微信服务号配置

1. 登录微信公众平台
2. 配置服务器地址：`http://8.137.123.138:5000/wechat`
3. 配置自定义菜单，添加"身份绑定"按钮
4. 菜单跳转URL：`http://8.137.123.138:5000/bind?openid=OPENID`

## 注意事项

- 确保服务器防火墙开放5000端口
- 生产环境请修改 `SECRET_KEY`
- 建议使用HTTPS协议
