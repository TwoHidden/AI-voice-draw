#!/bin/bash
# AI 语音绘图工具 - 停止脚本

cd "$(dirname "$0")"

echo "🛑 停止 AI 语音绘图工具..."

# 停止后端
if [ -f .backend.pid ]; then
    kill $(cat .backend.pid) 2>/dev/null
    rm .backend.pid
    echo "   ✅ 后端已停止"
fi

# 停止前端
if [ -f .frontend.pid ]; then
    kill $(cat .frontend.pid) 2>/dev/null
    rm .frontend.pid
    echo "   ✅ 前端已停止"
fi

# 兜底：杀掉所有相关进程
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null

echo ""
echo "✅ 已停止所有服务"
