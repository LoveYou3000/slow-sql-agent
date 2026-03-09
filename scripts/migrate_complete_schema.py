#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加缺失的字段和表

这个脚本用于修复缺少 blob 字段和 checkpoint_blobs 表的问题
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


def check_blob_column():
    """检查 blob 字段是否存在"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'memory'
                  AND table_name = 'checkpoint_writes'
                  AND column_name = 'blob'
            """))
            exists = result.scalar() is not None
            return exists
    except Exception as e:
        logger.error(f"检查字段失败: {e}")
        return False


def check_checkpoint_blobs_table():
    """检查 checkpoint_blobs 表是否存在"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'memory'
                  AND table_name = 'checkpoint_blobs'
            """))
            exists = result.scalar() is not None
            return exists
    except Exception as e:
        logger.error(f"检查表失败: {e}")
        return False


def add_blob_column():
    """添加 blob 字段"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 添加 blob 字段
            conn.execute(text("""
                ALTER TABLE memory.checkpoint_writes
                ADD COLUMN IF NOT EXISTS blob BYTEA NOT NULL DEFAULT ''
            """))
            conn.commit()
            logger.info("✅ blob 字段添加成功")

            # 为现有数据设置默认值（空字节）
            conn.execute(text("""
                UPDATE memory.checkpoint_writes
                SET blob = ''
                WHERE blob IS NULL OR blob = ''
            """))
            conn.commit()
            logger.info("✅ 现有数据已更新")

        return True
    except Exception as e:
        logger.error(f"添加字段失败: {e}")
        return False


def create_checkpoint_blobs_table():
    """创建 checkpoint_blobs 表"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS memory.checkpoint_blobs (
                    thread_id TEXT NOT NULL,
                    checkpoint_ns TEXT NOT NULL DEFAULT '',
                    channel TEXT NOT NULL,
                    version TEXT NOT NULL,
                    type TEXT NOT NULL,
                    blob BYTEA,
                    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
                )
            """))
            conn.commit()
            logger.info("✅ checkpoint_blobs 表创建成功")

            # 添加注释
            conn.execute(text("""
                COMMENT ON TABLE memory.checkpoint_blobs IS '存储二进制数据（如大文件等）'
            """))
            conn.commit()
            logger.info("✅ 表注释添加成功")

        return True
    except Exception as e:
        logger.error(f"创建表失败: {e}")
        return False


def verify_migration():
    """验证迁移结果"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 检查 blob 字段
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'memory'
                  AND table_name = 'checkpoint_writes'
                  AND column_name = 'blob'
            """))
            blob_row = result.fetchone()
            if blob_row:
                logger.info("✅ blob 字段验证成功:")
                logger.info(f"   字段名: {blob_row[0]}")
                logger.info(f"   数据类型: {blob_row[1]}")
                logger.info(f"   可为空: {blob_row[2]}")
            else:
                logger.error("❌ blob 字段未找到")
                return False

            # 检查 checkpoint_blobs 表
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'memory'
                  AND table_name = 'checkpoint_blobs'
            """))
            table_name = result.scalar()
            if table_name:
                logger.info("✅ checkpoint_blobs 表验证成功")
            else:
                logger.error("❌ checkpoint_blobs 表未找到")
                return False

            return True
    except Exception as e:
        logger.error(f"验证失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("     数据库迁移 - 添加 blob 字段和 checkpoint_blobs 表")
    print("="*60 + "\n")

    # 检查 blob 字段是否存在
    logger.info("步骤 1: 检查 blob 字段是否存在...")
    has_blob = check_blob_column()
    if has_blob:
        logger.info("✅ blob 字段已存在")
    else:
        logger.info("⚠️  blob 字段不存在，需要添加")

    # 检查 checkpoint_blobs 表是否存在
    logger.info("步骤 2: 检查 checkpoint_blobs 表是否存在...")
    has_table = check_checkpoint_blobs_table()
    if has_table:
        logger.info("✅ checkpoint_blobs 表已存在")
    else:
        logger.info("⚠️  checkpoint_blobs 表不存在，需要创建")

    # 如果都已存在，无需迁移
    if has_blob and has_table:
        logger.info("\n✅ 所有表和字段已存在，无需迁移")
        return 0

    print()

    # 确认是否继续
    response = input("是否继续迁移？(y/n): ").strip().lower()
    if response != 'y':
        logger.info("迁移已取消")
        return 1

    print()

    # 添加 blob 字段
    if not has_blob:
        logger.info("步骤 3: 添加 blob 字段...")
        if not add_blob_column():
            logger.error("添加 blob 字段失败")
            return 1
        print()

    # 创建 checkpoint_blobs 表
    if not has_table:
        logger.info("步骤 4: 创建 checkpoint_blobs 表...")
        if not create_checkpoint_blobs_table():
            logger.error("创建 checkpoint_blobs 表失败")
            return 1
        print()

    # 验证迁移
    logger.info("步骤 5: 验证迁移结果...")
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
