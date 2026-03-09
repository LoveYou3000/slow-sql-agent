#!/usr/bin/env python3
"""
本地数据库初始化脚本

这个脚本会：
1. 检查环境变量配置
2. 验证数据库连接
3. 创建必要的 schema 和表
4. 验证表结构
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from storage.database.db import get_engine, get_session
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_env():
    """检查环境变量配置"""
    logger.info("步骤 1: 检查环境变量配置...")

    db_url = os.getenv("PGDATABASE_URL")

    if not db_url:
        logger.error("❌ 错误: 未设置 PGDATABASE_URL 环境变量")
        logger.info("请在项目根目录创建 .env 文件，内容如下:")
        logger.info("PGDATABASE_URL=postgresql://postgres:password@localhost:5432/agent_db")
        return False

    logger.info(f"✅ 数据库连接字符串已配置: {mask_password(db_url)}")
    return True


def mask_password(db_url):
    """隐藏密码用于日志显示"""
    parts = db_url.split("@")
    if len(parts) == 2:
        credential_part = parts[0]
        if "://" in credential_part:
            _, creds = credential_part.split("://")
            if ":" in creds:
                username, _ = creds.split(":", 1)
                masked_creds = f"{username}:****@{parts[1]}"
                return f"{credential_part.split('://')[0]}://{masked_creds}"
    return db_url


def test_connection():
    """测试数据库连接"""
    logger.info("步骤 2: 测试数据库连接...")

    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"✅ 数据库连接成功!")
            logger.info(f"   PostgreSQL 版本: {version}")
        return True
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        logger.info("请检查:")
        logger.info("  1. PostgreSQL 服务是否运行")
        logger.info("  2. PGDATABASE_URL 是否正确")
        logger.info("  3. 网络连接是否正常")
        return False


def create_schema_and_tables():
    """创建 schema 和表"""
    logger.info("步骤 3: 创建 schema 和表...")

    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 创建 schema
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS memory"))
            conn.commit()
            logger.info("✅ 创建 schema: memory")

            # 设置搜索路径
            conn.execute(text("SET search_path TO memory"))
            conn.commit()

            # 创建 checkpoints 表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS memory.checkpoints (
                    thread_id VARCHAR(255) NOT NULL,
                    checkpoint_ns VARCHAR(255) NOT NULL DEFAULT '',
                    checkpoint_id VARCHAR(255) NOT NULL,
                    parent_checkpoint_id VARCHAR(255),
                    type VARCHAR(255) NOT NULL,
                    checkpoint JSONB NOT NULL,
                    metadata JSONB NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
                )
            """))
            conn.commit()
            logger.info("✅ 创建表: memory.checkpoints")

            # 创建索引
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_checkpoints_thread_id ON memory.checkpoints(thread_id)",
                "CREATE INDEX IF NOT EXISTS idx_checkpoints_parent_id ON memory.checkpoints(parent_checkpoint_id)",
                "CREATE INDEX IF NOT EXISTS idx_checkpoints_created_at ON memory.checkpoints(created_at DESC)",
            ]
            for idx_sql in indexes:
                conn.execute(text(idx_sql))
            conn.commit()
            logger.info("✅ 创建索引: checkpoints")

            # 创建 checkpoint_writes 表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS memory.checkpoint_writes (
                    thread_id VARCHAR(255) NOT NULL,
                    checkpoint_ns VARCHAR(255) NOT NULL DEFAULT '',
                    checkpoint_id VARCHAR(255) NOT NULL,
                    task_id VARCHAR(255),
                    idx INTEGER NOT NULL,
                    channel VARCHAR(255) NOT NULL,
                    value JSONB NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx),
                    FOREIGN KEY (thread_id, checkpoint_ns, checkpoint_id)
                        REFERENCES memory.checkpoints(thread_id, checkpoint_ns, checkpoint_id)
                        ON DELETE CASCADE
                )
            """))
            conn.commit()
            logger.info("✅ 创建表: memory.checkpoint_writes")

            # 创建索引
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_thread_id ON memory.checkpoint_writes(thread_id)",
                "CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_task_id ON memory.checkpoint_writes(task_id)",
            ]
            for idx_sql in indexes:
                conn.execute(text(idx_sql))
            conn.commit()
            logger.info("✅ 创建索引: checkpoint_writes")

        return True
    except Exception as e:
        logger.error(f"❌ 创建表失败: {e}")
        return False


def verify_tables():
    """验证表结构"""
    logger.info("步骤 4: 验证表结构...")

    try:
        session = get_session()

        # 检查 checkpoints 表
        result = session.execute(text("""
            SELECT COUNT(*) FROM memory.checkpoints
        """))
        count = result.scalar()
        logger.info(f"✅ memory.checkpoints 表存在，当前记录数: {count}")

        # 检查 checkpoint_writes 表
        result = session.execute(text("""
            SELECT COUNT(*) FROM memory.checkpoint_writes
        """))
        count = result.scalar()
        logger.info(f"✅ memory.checkpoint_writes 表存在，当前记录数: {count}")

        # 检查 schema 信息
        result = session.execute(text("""
            SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'memory'
        """))
        if result.scalar():
            logger.info("✅ memory schema 已创建")
        else:
            logger.warning("⚠️  memory schema 未找到")

        session.close()
        return True
    except Exception as e:
        logger.error(f"❌ 验证表结构失败: {e}")
        return False


def test_agent_memory():
    """测试 Agent 记忆功能"""
    logger.info("步骤 5: 测试 Agent 记忆功能...")

    try:
        from src.agents.agent import build_agent

        logger.info("正在初始化 Agent...")
        agent = build_agent()

        # 测试消息 1
        logger.info("发送测试消息 1...")
        response = agent.invoke({'messages': [('user', '你好，我是测试用户')]})
        logger.info(f"✅ 收到回复: {response['messages'][-1].content[:50]}...")

        # 测试消息 2（验证记忆）
        logger.info("发送测试消息 2...")
        response = agent.invoke({'messages': [('user', '我的名字是什么？')]})
        logger.info(f"✅ 收到回复: {response['messages'][-1].content[:50]}...")

        logger.info("✅ Agent 记忆功能正常!")
        return True
    except Exception as e:
        logger.error(f"❌ Agent 记忆功能测试失败: {e}")
        logger.info("提示: 这是可选测试，如果失败可能是因为模型配置问题")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("     本地数据库初始化脚本")
    print("="*60 + "\n")

    # 步骤 1: 检查环境变量
    if not check_env():
        sys.exit(1)

    # 步骤 2: 测试连接
    if not test_connection():
        sys.exit(1)

    # 步骤 3: 创建表
    if not create_schema_and_tables():
        sys.exit(1)

    # 步骤 4: 验证表
    if not verify_tables():
        sys.exit(1)

    # 步骤 5: 测试记忆功能（可选）
    test_agent_memory()

    print("\n" + "="*60)
    print("✅ 数据库初始化完成！")
    print("="*60 + "\n")

    print("下一步:")
    print("1. 启动 Agent: python src/main.py")
    print("2. 查看数据: psql -d agent_db -c \"SELECT * FROM memory.checkpoints;\"")
    print("3. 查看配置: cat .env")
    print()


if __name__ == "__main__":
    main()
