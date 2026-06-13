#!/bin/bash
# AI 语音绘图工具 - 启动脚本

cd "$(dirname "$0")"

echo "🚀 启动 AI 语音绘图工具..."

# 启动后端
echo "📡 启动后端服务 (端口 8000)..."
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# 启动前端
echo "🎨 启动前端服务 (端口 5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# 保存 PID
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "✅ 启动完成！"
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo ""
echo "停止请运行: ./stop.sh"
