# 快速修复指南 - type 字段缺失问题

## 🐛 问题描述

如果你遇到以下错误：

```
psycopg.errors.UndefinedColumn: column cw.type does not exist
LINE 20: ...array[cw.task_id::text::bytea, cw.channel::bytea, cw.type::b...
                                                              ^
```

这说明你的数据库表结构缺少 `type` 字段。

---

## 🔧 快速修复（3种方式）

### 方式 1: 自动迁移脚本（推荐）⭐

```bash
python scripts/migrate_add_type_column.py
```

脚本会自动：
1. ✅ 检查 `type` 字段是否存在
2. ✅ 添加 `type` 字段（如果不存在）
3. ✅ 更新现有数据
4. ✅ 创建必要的索引
5. ✅ 验证迁移结果

---

### 方式 2: 手动执行 SQL

```bash
# 连接到数据库
psql -U postgres -d agent_db

# 执行以下 SQL
ALTER TABLE memory.checkpoint_writes
ADD COLUMN IF NOT EXISTS type VARCHAR(255) NOT NULL DEFAULT '';

UPDATE memory.checkpoint_writes
SET type = 'unknown'
WHERE type = '';

CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_type
ON memory.checkpoint_writes(type);

-- 验证
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'memory'
  AND table_name = 'checkpoint_writes'
  AND column_name = 'type';
```

---

### 方式 3: 重建表（会清空所有对话历史）⚠️

```bash
# ⚠️ 警告：此操作会删除所有对话历史

# 连接到数据库
psql -U postgres -d agent_db

# 删除旧表
DROP TABLE IF EXISTS memory.checkpoint_writes CASCADE;
DROP TABLE IF EXISTS memory.checkpoints CASCADE;

# 重新导入表结构
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
    result = conn.execute(text('''
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = \"memory\"
          AND table_name = \"checkpoint_writes\"
          AND column_name = \"type\"
    '''))
    row = result.fetchone()
    if row:
        print('✅ type 字段已成功添加')
        print(f'   字段名: {row[0]}')
        print(f'   数据类型: {row[1]}')
        print(f'   可为空: {row[2]}')
    else:
        print('❌ type 字段未找到')
"
```

**预期输出**：
```
✅ type 字段已成功添加
   字段名: type
   数据类型: character varying
   可为空: NO
```

---

## 🔍 查看表结构

```bash
# 查看 checkpoint_writes 表的完整结构
psql -U postgres -d agent_db -c "\d memory.checkpoint_writes"
```

**预期输出**（包含 type 字段）：
```
                               Table "memory.checkpoint_writes"
     Column      |         Type          | Collation | Nullable | Default
-----------------+-----------------------+-----------+----------+---------
 thread_id       | character varying(255) |           | not null |
 checkpoint_ns   | character varying(255) |           | not null | ''
 checkpoint_id   | character varying(255) |           | not null |
 task_id         | character varying(255) |           |          |
 idx             | integer               |           | not null |
 channel         | character varying(255) |           | not null |
 type            | character varying(255) |           | not null |  ⬅️ 新增
 value           | jsonb                 |           | not null |
 created_at      | timestamp with time zone |           |          | now()
Indexes:
    "checkpoint_writes_pkey" PRIMARY KEY, btree (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
    "idx_checkpoint_writes_task_id" btree (task_id)
    "idx_checkpoint_writes_thread_id" btree (thread_id)
    "idx_checkpoint_writes_type" btree (type)  ⬅️ 新增
Foreign-key constraints:
    "checkpoint_writes_thread_id_fkey" FOREIGN KEY (thread_id, checkpoint_ns, checkpoint_id)
        REFERENCES memory.checkpoints(thread_id, checkpoint_ns, checkpoint_id) ON DELETE CASCADE
```

---

## 💡 预防措施

### 更新表结构脚本

如果是从旧版本升级，建议使用最新的表结构脚本：

```bash
# 备份现有数据（可选）
pg_dump -U postgres -d agent_db > backup_$(date +%Y%m%d).sql

# 重新导入表结构
psql -U postgres -d agent_db -f assets/langgraph_checkpoint_schema.sql
```

### 使用自动化脚本

推荐使用 `scripts/init_local_db.py` 进行初始化，它会自动处理表结构问题：

```bash
python scripts/init_local_db.py
```

---

## 📚 相关文档

- [完整数据库配置指南](./LOCAL_DATABASE_SETUP.md)
- [表结构说明](../assets/langgraph_checkpoint_schema.sql)
- [迁移脚本](../scripts/migrate_add_type_column.py)

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
