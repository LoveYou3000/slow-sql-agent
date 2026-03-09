#!/usr/bin/env python3
"""
本地运行启动脚本 - 禁用 Coze Trace 上传

这个脚本会禁用向 Coze 平台发送 trace 数据的功能
"""

import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)

# 设置环境变量，禁用 Coze Trace 上传
os.environ['COZE_DISABLE_TRACE'] = '1'
os.environ['COZE_TRACE_ENDPOINT'] = ''  # 禁用 trace 端点

# 设置日志目录（当前项目下的 logs 目录）
if 'LOG_FILE' not in os.environ:
    os.environ['LOG_FILE'] = os.path.join(project_root, 'logs', 'app.log')

# 创建日志目录（如果不存在）
log_dir = os.path.dirname(os.environ['LOG_FILE'])
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

print("="*60)
print("  SQL 问题检测 Agent - 本地启动（禁用 Trace）")
print("="*60)
print(f"项目目录: {project_root}")
print(f"日志目录: {log_dir}")
print("Coze Trace: 已禁用")
print("="*60)
print()

# 导入并启动
if __name__ == '__main__':
    from src.main import app
    import uvicorn

    # 检查 Python 环境
    try:
        import langchain
        import langgraph
    except ImportError as e:
        print(f"❌ 错误: 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)

    print("✅ 依赖检查完成")
    print()

    # 启动服务
    print("启动 Agent 服务...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
