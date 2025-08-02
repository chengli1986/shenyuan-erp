#!/bin/bash

# 申源ERP系统状态检查脚本
echo "======================================"
echo "申源ERP系统状态检查"
echo "======================================"
echo ""

# 检查后端服务
echo "1. 检查后端服务状态..."
BACKEND_PID=$(ps aux | grep -E "uvicorn|app.main:app" | grep -v grep | awk '{print $2}')
if [ ! -z "$BACKEND_PID" ]; then
    echo "   ✅ 后端服务运行中 (PID: $BACKEND_PID)"
    # 测试后端API
    echo "   测试后端API响应..."
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200"; then
        echo "   ✅ 后端API响应正常"
    else
        echo "   ❌ 后端API无响应"
    fi
else
    echo "   ❌ 后端服务未运行"
fi
echo ""

# 检查前端服务
echo "2. 检查前端服务状态..."
# 检查生产模式服务
SERVE_PID=$(ps aux | grep "serve -s build" | grep -v grep | awk '{print $2}')
if [ ! -z "$SERVE_PID" ]; then
    echo "   ✅ 前端服务（生产模式）运行中 (PID: $SERVE_PID)"
    FRONTEND_RUNNING=true
fi

# 检查开发模式服务
DEV_PID=$(ps aux | grep "npm start" | grep -v grep | awk '{print $2}')
if [ ! -z "$DEV_PID" ]; then
    echo "   ✅ 前端服务（开发模式）运行中 (PID: $DEV_PID)"
    FRONTEND_RUNNING=true
fi

if [ "$FRONTEND_RUNNING" = true ]; then
    # 测试前端访问
    echo "   测试前端页面响应..."
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
        echo "   ✅ 前端页面响应正常"
    else
        echo "   ❌ 前端页面无响应"
    fi
else
    echo "   ❌ 前端服务未运行"
fi
echo ""

# 显示访问信息
echo "3. 访问信息："
echo "   服务器公网IP: 18.219.25.24"
echo "   前端界面: http://18.219.25.24:3000"
echo "   后端API文档: http://18.219.25.24:8000/docs"
echo ""

# 安全组提醒
echo "4. AWS安全组检查提醒："
echo "   请确保AWS EC2安全组已开放以下端口："
echo "   - 8000 (后端API)"
echo "   - 3000 (前端界面)"
echo "   - 22 (SSH)"
echo ""

# 查看日志提示
echo "5. 查看日志："
echo "   后端日志: tail -f /home/ubuntu/shenyuan-erp/backend/backend.log"
echo "   前端日志: tail -f /home/ubuntu/shenyuan-erp/frontend/frontend.log"
echo ""