#!/bin/bash

# 申源ERP系统停止脚本
echo "======================================"
echo "停止申源ERP系统"
echo "======================================"
echo ""

# 停止后端服务
echo "1. 停止后端服务..."
BACKEND_PID=$(ps aux | grep -E "uvicorn|app.main:app" | grep -v grep | awk '{print $2}')
if [ ! -z "$BACKEND_PID" ]; then
    kill $BACKEND_PID
    echo "   后端服务已停止 (PID: $BACKEND_PID)"
else
    echo "   后端服务未运行"
fi

# 停止前端服务
echo "2. 停止前端服务..."
# 查找serve进程（生产模式）
SERVE_PID=$(ps aux | grep "serve -s build" | grep -v grep | awk '{print $2}')
if [ ! -z "$SERVE_PID" ]; then
    kill $SERVE_PID
    echo "   前端服务（生产模式）已停止 (PID: $SERVE_PID)"
fi

# 查找npm start进程（开发模式）
DEV_PID=$(ps aux | grep "npm start" | grep -v grep | awk '{print $2}')
if [ ! -z "$DEV_PID" ]; then
    kill $DEV_PID
    echo "   前端服务（开发模式）已停止 (PID: $DEV_PID)"
fi

if [ -z "$SERVE_PID" ] && [ -z "$DEV_PID" ]; then
    echo "   前端服务未运行"
fi

# 清理残留进程
echo "3. 清理残留进程..."
pkill -f "serve -s build" 2>/dev/null
pkill -f "node.*react-scripts" 2>/dev/null

echo ""
echo "✅ 系统已停止"
echo ""