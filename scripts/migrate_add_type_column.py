#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加 type 字段到 checkpoint_writes 表

这个脚本用于修复缺少 type 字段的问题
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


def check_type_column():
    """检查 type 字段是否存在"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'memory'
                  AND table_name = 'checkpoint_writes'
                  AND column_name = 'type'
            """))
            exists = result.scalar() is not None
            return exists
    except Exception as e:
        logger.error(f"检查字段失败: {e}")
        return False


def add_type_column():
    """添加 type 字段"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 添加 type 字段
            conn.execute(text("""
                ALTER TABLE memory.checkpoint_writes
                ADD COLUMN IF NOT EXISTS type VARCHAR(255) NOT NULL DEFAULT ''
            """))
            conn.commit()
            logger.info("✅ type 字段添加成功")

            # 为现有数据设置默认值
            conn.execute(text("""
                UPDATE memory.checkpoint_writes
                SET type = 'unknown'
                WHERE type = ''
            """))
            conn.commit()
            logger.info("✅ 现有数据已更新")

            # 创建索引
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_type
                ON memory.checkpoint_writes(type)
            """))
            conn.commit()
            logger.info("✅ 索引创建成功")

        return True
    except Exception as e:
        logger.error(f"添加字段失败: {e}")
        return False


def verify_migration():
    """验证迁移结果"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 检查字段是否存在
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'memory'
                  AND table_name = 'checkpoint_writes'
                  AND column_name = 'type'
            """))
            row = result.fetchone()
            if row:
                logger.info("✅ 字段验证成功:")
                logger.info(f"   字段名: {row[0]}")
                logger.info(f"   数据类型: {row[1]}")
                logger.info(f"   可为空: {row[2]}")
                return True
            else:
                logger.error("❌ 字段未找到")
                return False
    except Exception as e:
        logger.error(f"验证失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("     数据库迁移 - 添加 type 字段")
    print("="*60 + "\n")

    # 检查字段是否存在
    logger.info("步骤 1: 检查 type 字段是否存在...")
    if check_type_column():
        logger.info("✅ type 字段已存在，无需迁移")
        return 0

    logger.info("⚠️  type 字段不存在，需要进行迁移")
    print()

    # 确认是否继续
    response = input("是否继续迁移？(y/n): ").strip().lower()
    if response != 'y':
        logger.info("迁移已取消")
        return 1

    print()

    # 执行迁移
    logger.info("步骤 2: 添加 type 字段...")
    if not add_type_column():
        logger.error("迁移失败")
        return 1

    print()

    # 验证迁移
    logger.info("步骤 3: 验证迁移结果...")
    if not verify_migration():
        logger.error("验证失败")
        return 1

    print("\n" + "="*60)
    print("✅ 迁移完成！")
    print("="*60 + "\n")

    logger.info("现在可以正常使用 Agent 了")
    return 0


if __name__ == "__main__":
    sys.exit(main())
