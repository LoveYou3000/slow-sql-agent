-- ============================================================================
-- LangGraph PostgreSQL Checkpoint 表结构（完整版）
-- 这是 LangGraph PostgresSaver 使用的表结构
-- 用于存储 Agent 的对话历史和状态
-- ============================================================================

-- 创建 schema（如果不存在）
CREATE SCHEMA IF NOT EXISTS memory;

-- 设置搜索路径
SET search_path TO memory;

-- ============================================================================
-- 表 1: checkpoint_migrations
-- 存储数据库迁移版本
-- ============================================================================
CREATE TABLE IF NOT EXISTS checkpoint_migrations (
    v INTEGER PRIMARY KEY
);

-- ============================================================================
-- 表 2: checkpoints
-- 存储对话检查点的主要数据
-- ============================================================================
CREATE TABLE IF NOT EXISTS checkpoints (
    -- 主键：线程ID（thread_id）+ 检查点ID（checkpoint_ns + checkpoint_id）
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,

    -- 检查点元数据
    parent_checkpoint_id TEXT,
    type TEXT,

    -- 检查点数据（JSON格式）
    checkpoint JSONB NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',

    -- 主键约束
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_checkpoints_thread_id
    ON checkpoints(thread_id);

CREATE INDEX IF NOT EXISTS idx_checkpoints_parent_id
    ON checkpoints(parent_checkpoint_id);

-- ============================================================================
-- 表 3: checkpoint_blobs
-- 存储二进制数据（如大文件等）
-- ============================================================================
CREATE TABLE IF NOT EXISTS checkpoint_blobs (
    -- 外键：关联到 checkpoints 表
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    channel TEXT NOT NULL,
    version TEXT NOT NULL,

    -- Blob 数据类型
    type TEXT NOT NULL,
    blob BYTEA,

    -- 主键约束
    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
);

-- ============================================================================
-- 表 4: checkpoint_writes
-- 存储检查点相关的写入操作
-- ============================================================================
CREATE TABLE IF NOT EXISTS checkpoint_writes (
    -- 外键：关联到 checkpoints 表
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,

    -- 任务信息
    task_id TEXT NOT NULL,
    idx INTEGER NOT NULL,

    -- 写入操作信息
    channel TEXT NOT NULL,
    type TEXT,
    blob BYTEA NOT NULL,  -- ⚠️ 重要：二进制数据字段

    -- 主键约束
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_thread_id
    ON checkpoint_writes(thread_id);

CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_task_id
    ON checkpoint_writes(task_id);

CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_type
    ON checkpoint_writes(type);

-- ============================================================================
-- 注释说明
-- ============================================================================

COMMENT ON SCHEMA memory IS 'LangGraph 检查点存储 schema';

COMMENT ON TABLE checkpoint_migrations IS '存储数据库迁移版本';

COMMENT ON TABLE checkpoints IS '存储 Agent 对话的检查点数据，用于实现对话记忆和状态恢复';

COMMENT ON TABLE checkpoint_blobs IS '存储二进制数据（如大文件等）';

COMMENT ON TABLE checkpoint_writes IS '存储检查点相关的写入操作日志';

COMMENT ON COLUMN checkpoints.thread_id IS '对话线程ID，唯一标识一个对话会话';

COMMENT ON COLUMN checkpoints.checkpoint_id IS '检查点ID，唯一标识一个检查点';

COMMENT ON COLUMN checkpoints.checkpoint IS '检查点数据（JSONB格式），包含对话状态和消息历史';

COMMENT ON COLUMN checkpoints.metadata IS '检查点元数据（JSONB格式），包含额外的上下文信息';

COMMENT ON COLUMN checkpoint_writes.task_id IS '任务ID，标识一个具体的工具调用或操作';

COMMENT ON COLUMN checkpoint_writes.channel IS '通道名称，标识写入的数据类型';

COMMENT ON COLUMN checkpoint_writes.type IS '写入操作类型（如：tool_call, error, result 等）';

COMMENT ON COLUMN checkpoint_writes.blob IS '二进制数据，存储序列化的消息内容';

-- ============================================================================
-- 初始化迁移版本
-- ============================================================================
INSERT INTO checkpoint_migrations (v) VALUES (0)
ON CONFLICT (v) DO NOTHING;

-- ============================================================================
-- 验证表结构
-- ============================================================================
SELECT
    'memory.checkpoints' AS table_name,
    COUNT(*) AS row_count
FROM memory.checkpoints;

SELECT
    'memory.checkpoint_blobs' AS table_name,
    COUNT(*) AS row_count
FROM memory.checkpoint_blobs;

SELECT
    'memory.checkpoint_writes' AS table_name,
    COUNT(*) AS row_count
FROM memory.checkpoint_writes;
