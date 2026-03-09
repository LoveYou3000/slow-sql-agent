# 本地化 PostgreSQL 数据库配置指南

本指南将帮助您将 SQL 问题检测智能体的数据存储完全迁移到本地 PostgreSQL 数据库。

---

## 📋 概述

当前项目使用 PostgreSQL 数据库存储以下数据：
- **对话历史和状态**（通过 LangGraph Checkpoint 实现）
- **未来的业务数据扩展**

---

## 🚀 快速开始

### 1. 准备本地 PostgreSQL 数据库

确保您的本地环境已安装 PostgreSQL（推荐版本 14+）：

```bash
# 检查 PostgreSQL 版本
psql --version

# 或在 Windows 上检查
# postgres --version
```

### 2. 创建数据库

连接到您的 PostgreSQL 服务器并创建数据库：

```bash
# 使用 psql 连接到 PostgreSQL（默认端口 5432）
psql -U postgres

# 创建数据库
CREATE DATABASE agent_db;

# 创建专用用户（可选但推荐）
CREATE USER agent_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE agent_db TO agent_user;
\q
```

### 3. 导入表结构

执行提供的 SQL 脚本创建必要的表：

```bash
# 方式 1: 使用 psql 命令
psql -U postgres -d agent_db -f assets/langgraph_checkpoint_schema.sql

# 方式 2: 如果创建了专用用户
psql -U agent_user -d agent_db -f assets/langgraph_checkpoint_schema.sql
```

**预期输出**：
```
CREATE SCHEMA
SET
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
CREATE TABLE
CREATE INDEX
CREATE INDEX
 table_name  | row_count
-------------+----------
 checkpoints |        0
(1 row)

 table_name      | row_count
-----------------+----------
 checkpoint_writes|        0
(1 row)
```

### 4. 配置环境变量

在项目根目录创建或编辑 `.env` 文件：

```bash
# 方式 1: 使用 postgres 用户
PGDATABASE_URL=postgresql://postgres:your_password@localhost:5432/agent_db

# 方式 2: 使用专用用户
PGDATABASE_URL=postgresql://agent_user:your_secure_password@localhost:5432/agent_db

# 注意事项：
# - 替换 your_password 或 your_secure_password 为实际密码
# - 如果 PostgreSQL 在其他机器上，替换 localhost 为实际 IP 地址
# - 如果使用非默认端口（5432），在主机后添加 :端口号
```

**示例**：
```bash
# Windows 示例
PGDATABASE_URL=postgresql://postgres:MyPass123@localhost:5432/agent_db

# macOS/Linux 示例
PGDATABASE_URL=postgresql://agent_user:SecurePass@localhost:5432/agent_db
```

### 5. 验证连接

启动 Agent 并验证数据库连接：

```bash
# 运行测试
python src/main.py

# 或使用交互式测试
python -c "
from storage.memory.memory_saver import get_memory_saver
from storage.database.db import get_engine

print('测试数据库连接...')
engine = get_engine()
with engine.connect() as conn:
    result = conn.execute('SELECT COUNT(*) FROM memory.checkpoints')
    print(f'checkpoints 表记录数: {result.scalar()}')

print('测试成功！')
"
```

---

## 🔧 高级配置

### 使用 Docker 快速搭建 PostgreSQL

如果您希望使用 Docker 快速搭建本地数据库：

```bash
# 创建 docker-compose.yml 文件
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: agent_postgres
    environment:
      POSTGRES_USER: agent_user
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: agent_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agent_user -d agent_db"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
EOF

# 启动数据库
docker-compose up -d

# 等待数据库启动
sleep 5

# 导入表结构
docker exec -i agent_postgres psql -U agent_user -d agent_db < assets/langgraph_checkpoint_schema.sql

# 配置环境变量
echo "PGDATABASE_URL=postgresql://agent_user:secure_password@localhost:5432/agent_db" >> .env
```

### 连接参数详解

完整的 PostgreSQL 连接字符串格式：

```
postgresql://[用户名]:[密码]@[主机]:[端口]/[数据库名]?[参数]

# 示例
postgresql://agent_user:pass123@localhost:5432/agent_db?connect_timeout=10

# 常用参数：
# - connect_timeout: 连接超时时间（秒）
# - sslmode: SSL 模式（disable/require/prefer）
# - options: 附加选项
```

### 使用 Unix Socket 连接（Linux/macOS）

```bash
# 使用 Unix Socket 而不是 TCP/IP
PGDATABASE_URL=postgresql:///agent_db?host=/var/run/postgresql

# 或指定用户
PGDATABASE_URL=postgresql://agent_user@/agent_db?host=/var/run/postgresql
```

---

## 📊 数据管理

### 查看表数据

```sql
-- 查看对话线程
SELECT
    thread_id,
    COUNT(*) AS checkpoint_count,
    MIN(created_at) AS first_message,
    MAX(created_at) AS last_message
FROM memory.checkpoints
GROUP BY thread_id
ORDER BY last_message DESC;

-- 查看特定线程的对话历史
SELECT
    checkpoint_id,
    type,
    checkpoint,
    metadata,
    created_at
FROM memory.checkpoints
WHERE thread_id = 'your-thread-id'
ORDER BY created_at;

-- 查看工具调用记录
SELECT
    cw.thread_id,
    cw.checkpoint_id,
    cw.task_id,
    cw.channel,
    cw.value,
    cw.created_at
FROM memory.checkpoint_writes cw
ORDER BY cw.created_at DESC
LIMIT 20;
```

### 清空对话历史

```sql
-- 删除特定线程的所有数据
DELETE FROM memory.checkpoint_writes
WHERE thread_id = 'your-thread-id';

DELETE FROM memory.checkpoints
WHERE thread_id = 'your-thread-id';

-- ⚠️ 警告：清空所有对话历史
DELETE FROM memory.checkpoint_writes;
DELETE FROM memory.checkpoints;
```

### 备份和恢复

```bash
# 备份数据库
pg_dump -U postgres -d agent_db > backup_$(date +%Y%m%d).sql

# 恢复数据库
psql -U postgres -d agent_db < backup_20241211.sql

# 仅备份 schema（表结构）
pg_dump -U postgres -d agent_db --schema-only > schema_backup.sql

# 仅备份数据
pg_dump -U postgres -d agent_db --data-only > data_backup.sql
```

---

## 🔍 故障排查

### 问题 1: 连接超时

**错误信息**：
```
Database connection failed after 20s: could not connect to server
```

**解决方案**：
1. 检查 PostgreSQL 服务是否运行：
   ```bash
   # Linux/macOS
   sudo systemctl status postgresql

   # Windows
   # 检查服务列表中的 PostgreSQL 服务
   ```

2. 检查防火墙设置：
   ```bash
   # Linux (允许 5432 端口)
   sudo ufw allow 5432/tcp
   ```

3. 验证连接字符串中的主机、端口、用户名和密码

### 问题 2: 权限不足

**错误信息**：
```
permission denied for schema memory
```

**解决方案**：
```sql
-- 授予用户所有权限
GRANT ALL PRIVILEGES ON SCHEMA memory TO agent_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA memory TO agent_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA memory TO agent_user;
```

### 问题 3: 表不存在

**错误信息**：
```
relation "memory.checkpoints" does not exist
```

**解决方案**：
```sql
-- 检查 schema 是否存在
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'memory';

-- 检查表是否存在
SELECT table_name FROM information_schema.tables WHERE table_schema = 'memory';

-- 重新执行表创建脚本
\i assets/langgraph_checkpoint_schema.sql
```

### 问题 4: SSL 错误

**错误信息**：
```
sslmode=prefer did not work
```

**解决方案**：
```bash
# 在连接字符串中添加 sslmode=disable
PGDATABASE_URL=postgresql://agent_user:password@localhost:5432/agent_db?sslmode=disable
```

### 问题 5: type 字段不存在

**错误信息**：
```
psycopg.errors.UndefinedColumn: column cw.type does not exist
LINE 20: ...array[cw.task_id::text::bytea, cw.channel::bytea, cw.type::b...
                                                              ^
```

**原因**：旧版本的表结构缺少 `type` 字段，LangGraph 需要这个字段。

**解决方案 - 方式 1（推荐）: 使用迁移脚本**
```bash
# 运行迁移脚本
python scripts/migrate_add_type_column.py
```

**解决方案 - 方式 2: 手动执行 SQL**
```sql
-- 连接到数据库
psql -U postgres -d agent_db

-- 添加 type 字段
ALTER TABLE memory.checkpoint_writes
ADD COLUMN IF NOT EXISTS type VARCHAR(255) NOT NULL DEFAULT '';

-- 更新现有数据
UPDATE memory.checkpoint_writes
SET type = 'unknown'
WHERE type = '';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_type
ON memory.checkpoint_writes(type);
```

**解决方案 - 方式 3: 重建表（会清空数据）**
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

## 📚 相关文件说明

| 文件 | 说明 |
|------|------|
| `assets/langgraph_checkpoint_schema.sql` | LangGraph Checkpoint 表结构定义 |
| `src/storage/database/db.py` | 数据库连接管理逻辑 |
| `src/storage/memory/memory_saver.py` | 短期记忆存储实现 |
| `src/storage/database/shared/model.py` | 数据模型基类（可扩展） |

---

## 🎯 验证本地化配置

完成配置后，运行以下命令验证：

```bash
# 测试数据库连接
python -c "
from storage.database.db import get_engine, get_session

print('1. 测试数据库连接...')
engine = get_engine()
with engine.connect() as conn:
    result = conn.execute('SELECT version()')
    print(f'   PostgreSQL 版本: {result.scalar()}')

print('2. 测试表结构...')
session = get_session()
result = session.execute('SELECT COUNT(*) FROM memory.checkpoints')
print(f'   checkpoints 表记录数: {result.scalar()}')

result = session.execute('SELECT COUNT(*) FROM memory.checkpoint_writes')
print(f'   checkpoint_writes 表记录数: {result.scalar()}')

session.close()
print('✅ 所有测试通过！')
"

# 测试 Agent 对话记忆功能
python -c "
from src.agents.agent import build_agent

print('3. 测试 Agent 记忆功能...')
agent = build_agent()

# 发送消息
response = agent.invoke({'messages': [('user', '你好，我是测试用户')]})
print(f'   回复: {response[\"messages\"][-1].content}')

# 再次发送消息（测试是否记住上下文）
response = agent.invoke({'messages': [('user', '我的名字是什么？')]})
print(f'   回复: {response[\"messages\"][-1].content}')

print('✅ 记忆功能正常！')
"
```

---

## 📝 注意事项

1. **密码安全**：不要在代码中硬编码密码，始终使用环境变量
2. **备份策略**：定期备份生产数据库
3. **性能优化**：根据对话量考虑定期清理旧数据
4. **监控告警**：监控数据库连接数和磁盘空间
5. **版本兼容**：确保 PostgreSQL 版本 ≥ 14

---

## 🆘 需要帮助？

如果遇到问题：
1. 查看日志：`tail -f /app/work/logs/bypass/app.log`
2. 检查数据库日志
3. 验证环境变量是否正确设置
4. 参考 [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
