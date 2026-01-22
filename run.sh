#!/bin/bash
# 启动脚本

# 激活虚拟环境（如果使用）
# source venv/bin/activate

# 使用gunicorn启动（生产环境推荐）
# gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 开发环境直接运行
python app.py
