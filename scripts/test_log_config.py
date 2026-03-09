#!/usr/bin/env python3
"""
测试日志配置脚本
验证日志目录是否正确配置到 logs/ 目录
"""

import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_log_config():
    """测试日志配置"""
    print("="*60)
    print("测试日志配置")
    print("="*60)

    # 模拟本地环境
    os.environ['LOG_FILE'] = os.path.join(project_root, 'logs', 'app.log')

    print(f"项目根目录: {project_root}")
    print(f"环境变量 LOG_FILE: {os.getenv('LOG_FILE')}")

    # 导入日志配置
    try:
        from coze_coding_utils.log.node_log import LOG_FILE as DEFAULT_LOG_FILE
        print(f"默认 LOG_FILE: {DEFAULT_LOG_FILE}")

        # 检查环境变量是否生效
        if os.getenv('LOG_FILE'):
            print(f"✅ 环境变量 LOG_FILE 已设置")
            print(f"   实际日志路径: {os.getenv('LOG_FILE')}")
        else:
            print(f"⚠️  环境变量 LOG_FILE 未设置")
            print(f"   使用默认路径: {DEFAULT_LOG_FILE}")

        # 测试日志目录创建
        log_file = os.getenv('LOG_FILE') or DEFAULT_LOG_FILE
        log_dir = os.path.dirname(log_file)

        print(f"\n日志目录: {log_dir}")

        if os.path.exists(log_dir):
            print(f"✅ 日志目录已存在")
        else:
            print(f"⚠️  日志目录不存在，尝试创建...")
            os.makedirs(log_dir, exist_ok=True)
            if os.path.exists(log_dir):
                print(f"✅ 日志目录创建成功")
            else:
                print(f"❌ 日志目录创建失败")

        # 测试日志写入
        print(f"\n测试日志写入...")
        import logging
        test_logger = logging.getLogger('test_logger')
        test_logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        test_logger.addHandler(handler)

        test_logger.info('这是一条测试日志')
        handler.close()

        if os.path.exists(log_file):
            print(f"✅ 日志文件已创建: {log_file}")
            with open(log_file, 'r') as f:
                lines = f.readlines()
                print(f"   日志内容预览: {lines[-1].strip()}")
        else:
            print(f"❌ 日志文件未创建")

        print("\n" + "="*60)
        print("✅ 日志配置测试完成")
        print("="*60)

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_log_config()
    sys.exit(0 if success else 1)
