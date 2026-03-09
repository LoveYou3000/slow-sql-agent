"""
Graph 适配层

这个文件将 agents.agent 适配为 graphs.graph 接口
用于兼容 src/main.py 的调用

注意：graph_helper.get_graph_instance() 会通过 inspect.getmembers 查找 CompiledStateGraph 实例
"""

import sys
import os

# 确保项目根目录在 Python 路径中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.agent import build_agent

def build_graph(ctx=None):
    """
    构建图实例（兼容接口）

    Args:
        ctx: 上下文对象

    Returns:
        CompiledStateGraph 实例
    """
    return build_agent(ctx)

# 创建图实例
graph = build_graph()

# 导出所有接口
__all__ = ['graph', 'build_graph']
