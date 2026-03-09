#!/bin/bash

# =============================================================================
# 本地启动脚本
# 用于在本地环境中运行 Agent，日志输出到 logs/ 目录
# =============================================================================

# 设置项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 设置日志目录（当前项目下的 logs 目录）
export LOG_DIR="$PROJECT_ROOT/logs"
export LOG_FILE="$LOG_DIR/app.log"

# 创建日志目录（如果不存在）
mkdir -p "$LOG_DIR"

echo "=========================================="
echo "  SQL 问题检测 Agent - 本地启动"
echo "=========================================="
echo "项目目录: $PROJECT_ROOT"
echo "日志目录: $LOG_DIR"
echo "日志文件: $LOG_FILE"
echo "=========================================="
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
python3 -c "import langchain; import langgraph; import sqlalchemy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  警告: 部分依赖未安装，正在安装..."
    pip3 install -r requirements.txt
fi

echo "✅ 依赖检查完成"
echo ""

# 启动 Agent
echo "启动 Agent..."
python3 src/main.py "$@"
