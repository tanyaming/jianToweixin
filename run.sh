#!/bin/bash
# 简道云日报提醒系统 - 启动脚本

echo "=========================================="
echo "简道云日报提醒系统"
echo "=========================================="

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "✓ 发现虚拟环境，正在激活..."
    source venv/bin/activate
else
    echo "⚠ 未发现虚拟环境，建议创建: python3 -m venv venv"
fi

# 检查依赖
echo ""
echo "检查依赖..."
python -c "import flask, requests, apscheduler" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ 依赖检查通过"
else
    echo "✗ 缺少依赖，请运行: pip install -r requirements.txt"
    exit 1
fi

# 选择运行模式
echo ""
echo "请选择运行模式:"
echo "1. 开发模式 (python app.py)"
echo "2. 生产模式 (gunicorn)"
echo "3. 测试模式 (python test_api.py)"
read -p "请输入选项 [1-3]: " mode

case $mode in
    1)
        echo ""
        echo "启动开发模式..."
        python app.py
        ;;
    2)
        echo ""
        echo "启动生产模式..."
        # 检查gunicorn是否安装
        python -c "import gunicorn" 2>/dev/null
        if [ $? -eq 0 ]; then
            gunicorn -w 4 -b 0.0.0.0:5000 app:app
        else
            echo "✗ 未安装gunicorn，请运行: pip install gunicorn"
            exit 1
        fi
        ;;
    3)
        echo ""
        echo "启动测试模式..."
        python test_api.py
        ;;
    *)
        echo "无效选项，默认使用开发模式"
        python app.py
        ;;
esac

