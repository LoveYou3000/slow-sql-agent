# 禁用 Coze Trace 上传

## 🐛 问题描述

在本地运行时，可能会看到以下错误日志：

```
HTTP Request: POST https://api.coze.cn/v1/loop/traces/ingest "HTTP/1.1 401 Unauthorized"
```

这是因为 `cozeloop` 库会自动尝试向 Coze 平台发送 trace 数据，但本地环境没有有效的认证信息。

---

## 🔧 解决方案

### 方式 1: 使用禁用 Trace 的启动脚本（推荐）⭐

```bash
python scripts/start_local_no_trace.py
```

这个脚本会自动：
- ✅ 设置 `COZE_DISABLE_TRACE=1` 环境变量
- ✅ 清空 `COZE_TRACE_ENDPOINT` 环境变量
- ✅ 配置日志目录
- ✅ 启动 Agent 服务

### 方式 2: 手动设置环境变量

在启动 Agent 前，设置以下环境变量：

```bash
# Linux/macOS
export COZE_DISABLE_TRACE=1
export COZE_TRACE_ENDPOINT=

# 启动 Agent
python src/main.py
```

或在 `.env` 文件中添加：

```bash
COZE_DISABLE_TRACE=1
COZE_TRACE_ENDPOINT=
```

### 方式 3: 使用启动脚本包装

创建一个启动脚本：

```bash
#!/bin/bash
# 禁用 Coze Trace
export COZE_DISABLE_TRACE=1
export COZE_TRACE_ENDPOINT=

# 设置日志目录
export LOG_FILE="./logs/app.log"

# 启动 Agent
python src/main.py "$@"
```

---

## ✅ 验证禁用效果

启动 Agent 后，如果不再看到 `401 Unauthorized` 错误，说明 trace 上传已成功禁用。

```bash
# 启动 Agent
python scripts/start_local_no_trace.py

# 在另一个终端查看日志
tail -f logs/app.log | grep -i "401\|trace"
```

如果没有输出，说明 trace 上传已禁用。

---

## 📝 环境变量说明

| 环境变量 | 说明 | 推荐值（本地） |
|---------|------|---------------|
| `COZE_DISABLE_TRACE` | 禁用 trace 上传 | `1` |
| `COZE_TRACE_ENDPOINT` | Trace 端点 URL | ``（空字符串） |

---

## 🎯 完整的本地环境配置

推荐在 `.env` 文件中配置完整的本地环境：

```bash
# 数据库配置
PGDATABASE_URL=postgresql://postgres:password@localhost:5432/agent_db

# 日志配置
LOG_FILE=./logs/app.log
LOG_LEVEL=INFO

# 禁用 Coze Trace（本地环境不需要）
COZE_DISABLE_TRACE=1
COZE_TRACE_ENDPOINT=

# 模型配置（如果使用配置文件）
# api_key 和 base_url 在 config/agent_llm_config.json 中配置
```

---

## 💡 为什么需要禁用 Trace？

1. **避免 401 错误**: 本地环境没有 Coze 平台的认证信息
2. **减少网络请求**: 避免不必要的网络调用
3. **提高性能**: 不需要等待 trace 上传
4. **保护隐私**: 本地数据不会发送到外部平台

---

## 📚 相关文件

- `scripts/start_local_no_trace.py` - 禁用 trace 的启动脚本
- `src/main.py` - 主程序入口（使用 cozeloop 库）
- `.env` - 环境变量配置文件

---

## 🔍 更多信息

如果需要启用 trace（例如在 Coze 平台上运行），请确保：

1. ✅ 设置有效的 `COZE_WORKLOAD_IDENTITY_TOKEN`
2. ✅ 设置正确的 `COZE_TRACE_ENDPOINT`
3. ✅ 不设置 `COZE_DISABLE_TRACE=1`
