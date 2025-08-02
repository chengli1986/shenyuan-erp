#!/bin/bash

# 申源ERP系统启动脚本
echo "======================================"
echo "欢迎使用申源ERP系统启动脚本"
echo "======================================"
echo ""

# 显示服务器信息
echo "服务器公网IP: 18.219.25.24"
echo ""

# 启动后端服务
echo "1. 启动后端服务..."
cd /home/ubuntu/shenyuan-erp/backend
echo "   使用Python虚拟环境..."
echo "   启动FastAPI服务..."
nohup bash -c 'source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload' > backend.log 2>&1 &
BACKEND_PID=$!
echo "   后端服务已启动 (PID: $BACKEND_PID)"
echo "   后端地址: http://18.219.25.24:8000"
echo ""

# 等待后端启动
sleep 3

# 启动前端服务
echo "2. 启动前端服务..."
cd /home/ubuntu/shenyuan-erp/frontend
echo "   检查前端依赖..."
if [ ! -d "node_modules" ]; then
    echo "   安装前端依赖..."
    npm install
fi
echo "   构建生产版本..."
npm run build
echo "   使用serve启动生产服务器..."
# 先安装serve如果没有
if ! command -v serve &> /dev/null; then
    npm install -g serve
fi
export HOST=0.0.0.0
export REACT_APP_API_BASE_URL=http://18.219.25.24:8000
nohup /home/ubuntu/.npm-global/bin/serve -s build -l tcp://0.0.0.0:8080 > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   前端服务已启动 (PID: $FRONTEND_PID)"
echo ""

# 等待前端启动
echo "3. 等待服务启动完成..."
sleep 10

echo "======================================"
echo "✅ 系统启动完成！"
echo "======================================"
echo ""
echo "访问方式："
echo "前端界面: http://18.219.25.24:8080"
echo "后端API文档: http://18.219.25.24:8000/docs"
echo ""
echo "查看日志："
echo "后端日志: tail -f /home/ubuntu/shenyuan-erp/backend/backend.log"
echo "前端日志: tail -f /home/ubuntu/shenyuan-erp/frontend/frontend.log"
echo ""
echo "停止服务："
echo "运行: /home/ubuntu/shenyuan-erp/stop-erp.sh"
echo ""