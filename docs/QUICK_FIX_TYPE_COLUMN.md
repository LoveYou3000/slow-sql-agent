# 快速修复指南 - 表结构缺失问题

## 🐛 问题描述

如果你遇到以下错误之一：

### 错误 1: 缺少 type 字段
```
psycopg.errors.UndefinedColumn: column cw.type does not exist
LINE 20: ...array[cw.task_id::text::bytea, cw.channel::bytea, cw.type::b...
                                                              ^
```

### 错误 2: 缺少 blob 字段
```
psycopg.errors.UndefinedColumn: column cw.blob does not exist
LINE 20: ...::text::bytea, cw.channel::bytea, cw.type::bytea, cw.blob] o...
                                                              ^
```

### 错误 3: 缺少 checkpoint_blobs 表
```
relation "memory.checkpoint_blobs" does not exist
```

这些错误说明你的数据库表结构不完整，缺少 LangGraph 需要的字段或表。

---

## 🔧 快速修复（3种方式）

### 方式 1: 自动迁移脚本（推荐）⭐

```bash
# 完整迁移脚本（包含所有缺失的字段和表）
python scripts/migrate_complete_schema.py
```

脚本会自动：
1. ✅ 检查所有必需的字段和表
2. ✅ 添加 `type` 字段（如果不存在）
3. ✅ 添加 `blob` 字段（如果不存在）
4. ✅ 创建 `checkpoint_blobs` 表（如果不存在）
5. ✅ 更新现有数据
6. ✅ 验证迁移结果

---

### 方式 2: 手动执行 SQL

```bash
# 连接到数据库
psql -U postgres -d agent_db

-- 添加 type 字段
ALTER TABLE memory.checkpoint_writes
ADD COLUMN IF NOT EXISTS type VARCHAR(255) NOT NULL DEFAULT '';

UPDATE memory.checkpoint_writes
SET type = 'unknown' WHERE type = '';

-- 添加 blob 字段
ALTER TABLE memory.checkpoint_writes
ADD COLUMN IF NOT EXISTS blob BYTEA NOT NULL DEFAULT '';

UPDATE memory.checkpoint_writes
SET blob = '' WHERE blob IS NULL OR blob = '';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_type
ON memory.checkpoint_writes(type);

-- 创建 checkpoint_blobs 表
CREATE TABLE IF NOT EXISTS memory.checkpoint_blobs (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    channel TEXT NOT NULL,
    version TEXT NOT NULL,
    type TEXT NOT NULL,
    blob BYTEA,
    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
);

-- 验证
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'memory'
  AND table_name = 'checkpoint_writes'
  AND column_name IN ('type', 'blob');
```

---

### 方式 3: 重建表（会清空所有对话历史）⚠️

```bash
# ⚠️ 警告：此操作会删除所有对话历史

# 连接到数据库
psql -U postgres -d agent_db

# 删除旧表
DROP TABLE IF EXISTS memory.checkpoint_writes CASCADE;
DROP TABLE IF EXISTS memory.checkpoint_blobs CASCADE;
DROP TABLE IF EXISTS memory.checkpoints CASCADE;
DROP TABLE IF EXISTS memory.checkpoint_migrations CASCADE;

# 重新导入表结构（完整版）
\i assets/langgraph_checkpoint_schema.sql
```

---

## ✅ 验证修复

修复后，运行以下命令验证：

```bash
python -c "
from storage.database.db import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    # 检查 type 和 blob 字段
    result = conn.execute(text('''
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = \"memory\"
          AND table_name = \"checkpoint_writes\"
          AND column_name IN (\"type\", \"blob\")
        ORDER BY column_name
    '''))
    rows = result.fetchall()
    if rows:
        print('✅ 字段验证成功:')
        for row in rows:
            print(f'   字段名: {row[0]}, 类型: {row[1]}, 可为空: {row[2]}')
    else:
        print('❌ 字段未找到')

    # 检查 checkpoint_blobs 表
    result = conn.execute(text('''
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = \"memory\"
          AND table_name = \"checkpoint_blobs\"
    '''))
    table_name = result.scalar()
    if table_name:
        print('✅ checkpoint_blobs 表验证成功')
    else:
        print('❌ checkpoint_blobs 表未找到')
"
```

**预期输出**：
```
✅ 字段验证成功:
   字段名: blob, 类型: bytea, 可为空: NO
   字段名: type, 类型: character varying, 可为空: YES
✅ checkpoint_blobs 表验证成功
```

---

## 🔍 查看表结构

```bash
# 查看 checkpoint_writes 表的完整结构
psql -U postgres -d agent_db -c "\d memory.checkpoint_writes"

# 查看 checkpoint_blobs 表的完整结构
psql -U postgres -d agent_db -c "\d memory.checkpoint_blobs"

# 查看所有表
psql -U postgres -d agent_db -c "\dt memory.*"
```

**预期输出** - checkpoint_writes 表：
```
                               Table "memory.checkpoint_writes"
     Column      |         Type          | Collation | Nullable | Default
-----------------+-----------------------+-----------+----------+---------
 thread_id       | text                  |           | not null |
 checkpoint_ns   | text                  |           | not null | ''
 checkpoint_id   | text                  |           | not null |
 task_id         | text                  |           | not null |
 idx             | integer               |           | not null |
 channel         | text                  |           | not null |
 type            | text                  |           |          |  ⬅️ 新增
 blob            | bytea                 |           | not null |  ⬅️ 新增
Indexes:
    "checkpoint_writes_pkey" PRIMARY KEY, btree (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
    "idx_checkpoint_writes_task_id" btree (task_id)
    "idx_checkpoint_writes_thread_id" btree (thread_id)
    "idx_checkpoint_writes_type" btree (type)  ⬅️ 新增
Foreign-key constraints:
    "checkpoint_writes_thread_id_fkey" FOREIGN KEY (thread_id, checkpoint_ns, checkpoint_id)
        REFERENCES memory.checkpoints(thread_id, checkpoint_ns, checkpoint_id) ON DELETE CASCADE
```

**预期输出** - checkpoint_blobs 表：
```
                               Table "memory.checkpoint_blobs"
     Column      |         Type          | Collation | Nullable | Default
-----------------+-----------------------+-----------+----------+---------
 thread_id       | text                  |           | not null |
 checkpoint_ns   | text                  |           | not null | ''
 channel         | text                  |           | not null |
 version         | text                  |           | not null |
 type            | text                  |           | not null |
 blob            | bytea                 |           |          |  ⬅️ 新增
Indexes:
    "checkpoint_blobs_pkey" PRIMARY KEY, btree (thread_id, checkpoint_ns, channel, version)
```

---

## 💡 预防措施

### 更新表结构脚本

如果是从旧版本升级，建议使用最新的完整表结构脚本：

```bash
# 备份现有数据（可选）
pg_dump -U postgres -d agent_db > backup_$(date +%Y%m%d).sql

# 重新导入完整表结构
psql -U postgres -d agent_db -f assets/langgraph_checkpoint_schema.sql
```

### 使用自动化脚本

推荐使用 `scripts/init_local_db.py` 进行初始化，它会自动处理表结构问题：

```bash
python scripts/init_local_db.py
```

### 推荐方式：使用 LangGraph 自动创建表

LangGraph 提供了 `PostgresSaver.setup()` 方法，可以自动创建和管理表结构：

```python
from storage.database.db import get_engine
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import os

# 使用 LangGraph 自动创建表
db_url = os.getenv('PGDATABASE_URL')
pool = AsyncConnectionPool(conninfo=db_url, min_size=1, max_idle=300)
checkpointer = AsyncPostgresSaver(pool)
checkpointer.setup()  # ⭐ 自动创建所有必需的表和字段
```

这样可以确保表结构与 LangGraph 版本完全匹配。

---

## 📚 相关文档

- [完整数据库配置指南](../assets/LOCAL_DATABASE_SETUP.md)
- [最新表结构说明](../assets/langgraph_checkpoint_schema.sql)
- [完整迁移脚本](../scripts/migrate_complete_schema.py)
- [旧版迁移脚本（仅 type 字段）](../scripts/migrate_add_type_column.py)

---

## 🔄 版本历史

### v2.0 (2026-03-09)
- ✅ 添加 `blob` 字段
- ✅ 添加 `checkpoint_blobs` 表
- ✅ 更新为完整的 LangGraph 表结构

### v1.0 (2026-03-09)
- ✅ 添加 `type` 字段

---

## 🆘 仍然遇到问题？

如果修复后仍然遇到问题，请检查：

1. **数据库连接**：确保 `PGDATABASE_URL` 环境变量正确配置
2. **权限问题**：确保数据库用户有足够的权限
3. **Schema 问题**：确保 `memory` schema 存在
4. **版本问题**：确保 PostgreSQL 版本 ≥ 14

```bash
# 检查数据库连接
python -c "from storage.database.db import get_engine; engine = get_engine(); print('✅ 连接成功')"

# 检查 schema
psql -U postgres -d agent_db -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'memory';"

# 检查 PostgreSQL 版本
psql --version
```
