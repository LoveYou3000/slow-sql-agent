# 本地运行指南

本指南帮助你在本地环境中运行 SQL 问题检测 Agent。

---

## 🚀 快速开始

### 方式 1: 使用启动脚本（推荐）

#### Linux / macOS
```bash
# 赋予执行权限（首次运行时需要）
chmod +x scripts/start_local.sh

# 启动 Agent
./scripts/start_local.sh
```

#### Windows
```bash
# 双击运行或在命令行中执行
scripts\start_local.bat
```

**启动脚本会自动**：
- ✅ 设置日志目录为 `logs/`（项目根目录下）
- ✅ 检查 Python 环境
- ✅ 检查并安装依赖
- ✅ 创建日志目录
- ✅ 启动 Agent

### 方式 2: 手动启动

```bash
# 1. 设置环境变量
export LOG_FILE="./logs/app.log"

# 2. 创建日志目录
mkdir -p logs

# 3. 启动 Agent
python src/main.py
```

---

## 📁 日志配置

### 默认日志目录

| 环境 | 日志目录 | 说明 |
|------|---------|------|
| **本地运行** | `./logs/app.log` | 项目根目录下的 logs 目录 |
| **Coze 平台** | `/app/work/logs/bypass/app.log` | Coze 运行环境的日志目录 |

### 日志配置参数

- **最大文件大小**: 100 MB
- **备份文件数**: 5 个（app.log.1, app.log.2, ...）
- **日志级别**: INFO（可通过环境变量配置）
- **格式**: JSON 格式（便于解析）

### 自定义日志目录

如果需要自定义日志目录，可以通过环境变量设置：

```bash
# 设置自定义日志路径
export LOG_FILE="/path/to/your/logs/app.log"

# 或创建自定义启动脚本
cat > run_custom.sh << 'EOF'
#!/bin/bash
export LOG_FILE="/custom/path/app.log"
mkdir -p "$(dirname $LOG_FILE)"
python src/main.py
EOF
chmod +x run_custom.sh
```

---

## 🔧 环境配置

### 必需环境变量

```bash
# PostgreSQL 数据库连接（必需）
PGDATABASE_URL=postgresql://user:password@localhost:5432/agent_db
```

### 可选环境变量

```bash
# 日志文件路径（默认：./logs/app.log）
LOG_FILE=./logs/app.log

# 日志级别（默认：INFO）
LOG_LEVEL=DEBUG
```

### 配置文件示例

在项目根目录创建 `.env` 文件：

```bash
# 数据库配置
PGDATABASE_URL=postgresql://postgres:your_password@localhost:5432/agent_db

# 日志配置（可选）
LOG_FILE=./logs/app.log
LOG_LEVEL=INFO
```

---

## 📊 查看日志

### 实时查看日志

```bash
# 查看最新的日志
tail -f logs/app.log

# 查看最近 50 行
tail -n 50 logs/app.log

# 搜索错误日志
grep "ERROR" logs/app.log
```

### 查看历史日志

```bash
# 查看所有日志文件
ls -lh logs/

# 查看备份日志
tail -f logs/app.log.1

# 搜索特定关键词
grep "SQL" logs/app.log*
```

### 格式化查看 JSON 日志

由于日志是 JSON 格式，可以使用 `jq` 工具格式化查看：

```bash
# 安装 jq（如果尚未安装）
# macOS: brew install jq
# Ubuntu/Debian: sudo apt-get install jq

# 格式化查看日志
tail -f logs/app.log | jq '.'

# 查看特定字段
tail -f logs/app.log | jq '.message, .level'
```

---

## 🛠️ 常见问题

### 问题 1: 日志目录不存在

**错误信息**：
```
No such file or directory: './logs/app.log'
```

**解决方案**：
```bash
# 创建日志目录
mkdir -p logs

# 或使用启动脚本（会自动创建）
./scripts/start_local.sh
```

### 问题 2: 权限不足

**错误信息**：
```
Permission denied: './logs/app.log'
```

**解决方案**：
```bash
# 检查目录权限
ls -ld logs/

# 修改权限
chmod 755 logs

# 或切换到有写权限的目录
```

### 问题 3: 日志文件过大

如果日志文件增长过快，可以调整日志配置：

在 `.env` 文件中添加：
```bash
# 日志级别（INFO 比 DEBUG 产生的日志少）
LOG_LEVEL=WARN

# 或修改 src/main.py 中的 max_bytes 参数
```

### 问题 4: 无法查看日志

```bash
# 检查日志文件是否存在
ls -lh logs/app.log

# 检查文件内容
cat logs/app.log

# 检查进程是否正在写入
lsof logs/app.log
```

---

## 📝 日志内容说明

日志文件采用 JSON 格式，包含以下字段：

```json
{
  "timestamp": "2024-03-09T10:30:00.123Z",
  "level": "INFO",
  "logger": "app",
  "message": "Agent started",
  "context": {
    "user_id": "user123",
    "thread_id": "thread456"
  }
}
```

### 常见日志级别

| 级别 | 说明 | 使用场景 |
|------|------|---------|
| DEBUG | 调试信息 | 开发调试 |
| INFO | 一般信息 | 正常运行信息 |
| WARNING | 警告信息 | 潜在问题 |
| ERROR | 错误信息 | 运行时错误 |
| CRITICAL | 严重错误 | 系统崩溃 |

---

## 🔍 调试技巧

### 1. 启用 DEBUG 日志

```bash
# 临时启用 DEBUG 日志
LOG_LEVEL=DEBUG ./scripts/start_local.sh

# 或在 .env 中设置
echo "LOG_LEVEL=DEBUG" >> .env
```

### 2. 查看特定组件日志

```bash
# 查看数据库相关日志
grep -i "database\|postgres\|sql" logs/app.log

# 查看 Agent 相关日志
grep -i "agent\|checkpoint" logs/app.log

# 查看错误日志
grep -i "error\|exception" logs/app.log
```

### 3. 导出日志分析

```bash
# 导出错误日志到文件
grep "ERROR" logs/app.log > errors.log

# 统计日志级别分布
grep -o '"level": "[A-Z]*"' logs/app.log | sort | uniq -c
```

---

## 📚 相关文件

| 文件 | 说明 |
|------|------|
| `scripts/start_local.sh` | Linux/macOS 启动脚本 |
| `scripts/start_local.bat` | Windows 启动脚本 |
| `src/main.py` | 主程序入口（日志配置） |
| `.env` | 环境变量配置文件 |
| `logs/app.log` | 日志文件（运行后生成） |

---

## 🎯 完整运行流程

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置数据库（参考 assets/LOCAL_DATABASE_SETUP.md）
python scripts/init_local_db.py

# 3. 配置环境变量
echo "PGDATABASE_URL=postgresql://postgres:password@localhost:5432/agent_db" > .env

# 4. 启动 Agent
./scripts/start_local.sh

# 5. 查看日志
tail -f logs/app.log
```

---

## 💡 提示

1. **日志轮转**: 日志文件达到 100MB 会自动轮转，最多保留 5 个备份
2. **JSON 格式**: 日志采用 JSON 格式，便于程序化处理和分析
3. **实时监控**: 使用 `tail -f` 可以实时查看日志
4. **性能影响**: 在生产环境中，建议将日志级别设置为 INFO 或 WARN，避免 DEBUG 日志影响性能

需要帮助？查看 [README.md](../README.md) 或 [故障排查文档](../assets/LOCAL_DATABASE_SETUP.md)。
