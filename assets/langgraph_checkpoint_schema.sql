-- ============================================================================
-- LangGraph PostgreSQL Checkpoint 表结构
-- 这是 LangGraph PostgresSaver 使用的表结构
-- 用于存储 Agent 的对话历史和状态
-- ============================================================================

-- 创建 schema（如果不存在）
CREATE SCHEMA IF NOT EXISTS memory;

-- 设置搜索路径
SET search_path TO memory;

-- ============================================================================
-- 表 1: checkpoints
-- 存储对话检查点的主要数据
-- ============================================================================
CREATE TABLE IF NOT EXISTS checkpoints (
    -- 主键：线程ID（thread_id）+ 检查点ID（checkpoint_ns + checkpoint_id）
    thread_id VARCHAR(255) NOT NULL,
    checkpoint_ns VARCHAR(255) NOT NULL DEFAULT '',
    checkpoint_id VARCHAR(255) NOT NULL,

    -- 检查点元数据（JSON格式）
    parent_checkpoint_id VARCHAR(255),
    type VARCHAR(255) NOT NULL,
    checkpoint JSONB NOT NULL,
    metadata JSONB NOT NULL,

    -- 创建和更新时间
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- 主键约束
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_checkpoints_thread_id
    ON checkpoints(thread_id);

CREATE INDEX IF NOT EXISTS idx_checkpoints_parent_id
    ON checkpoints(parent_checkpoint_id);

CREATE INDEX IF NOT EXISTS idx_checkpoints_created_at
    ON checkpoints(created_at DESC);

-- ============================================================================
-- 表 2: checkpoint_writes
-- 存储检查点相关的写入操作
-- ============================================================================
CREATE TABLE IF NOT EXISTS checkpoint_writes (
    -- 外键：关联到 checkpoints 表
    thread_id VARCHAR(255) NOT NULL,
    checkpoint_ns VARCHAR(255) NOT NULL DEFAULT '',
    checkpoint_id VARCHAR(255) NOT NULL,

    -- 任务ID
    task_id VARCHAR(255),

    -- 写入操作类型（例如：tool_call, error, result等）
    idx INTEGER NOT NULL,
    channel VARCHAR(255) NOT NULL,

    -- 写入的数据（JSONB格式）
    value JSONB NOT NULL,

    -- 创建时间
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- 外键约束和主键
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx),
    FOREIGN KEY (thread_id, checkpoint_ns, checkpoint_id)
        REFERENCES checkpoints(thread_id, checkpoint_ns, checkpoint_id)
        ON DELETE CASCADE
);

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_thread_id
    ON checkpoint_writes(thread_id);

CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_task_id
    ON checkpoint_writes(task_id);

-- ============================================================================
-- 注释说明
-- ============================================================================

COMMENT ON SCHEMA memory IS 'LangGraph 检查点存储 schema';

COMMENT ON TABLE checkpoints IS '存储 Agent 对话的检查点数据，用于实现对话记忆和状态恢复';

COMMENT ON TABLE checkpoint_writes IS '存储检查点相关的写入操作日志';

COMMENT ON COLUMN checkpoints.thread_id IS '对话线程ID，唯一标识一个对话会话';

COMMENT ON COLUMN checkpoints.checkpoint_id IS '检查点ID，唯一标识一个检查点';

COMMENT ON COLUMN checkpoints.checkpoint IS '检查点数据（JSONB格式），包含对话状态和消息历史';

COMMENT ON COLUMN checkpoints.metadata IS '检查点元数据（JSONB格式），包含额外的上下文信息';

COMMENT ON COLUMN checkpoint_writes.task_id IS '任务ID，标识一个具体的工具调用或操作';

COMMENT ON COLUMN checkpoint_writes.channel IS '通道名称，标识写入的数据类型';

COMMENT ON COLUMN checkpoint_writes.value IS '写入的数据值（JSONB格式）';

-- ============================================================================
-- 授权（根据需要调整）
-- ============================================================================
-- 如果需要给特定用户授权，可以取消下面的注释并修改用户名
-- GRANT ALL PRIVILEGES ON SCHEMA memory TO your_username;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA memory TO your_username;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA memory TO your_username;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA memory GRANT ALL ON TABLES TO your_username;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA memory GRANT ALL ON SEQUENCES TO your_username;

-- ============================================================================
-- 验证表结构
-- ============================================================================
SELECT
    'memory.checkpoints' AS table_name,
    COUNT(*) AS row_count
FROM memory.checkpoints;

SELECT
    'memory.checkpoint_writes' AS table_name,
    COUNT(*) AS row_count
FROM memory.checkpoint_writes;
