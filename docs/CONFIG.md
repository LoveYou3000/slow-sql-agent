# 配置文件说明

## 概述

`config/agent_llm_config.json` 是 SQL 问题检测 Agent 的主配置文件，包含了模型配置、系统提示词和工具配置。

---

## 配置文件结构

```json
{
  "api_key": "your_api_key_here",
  "base_url": "https://api.example.com/v1",
  "config": {
    "model": "gpt-4",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_completion_tokens": 4000,
    "timeout": 600,
    "thinking": "disabled"
  },
  "sp": "你是专业的SQL代码审查专家...",
  "tools": []
}
```

---

## 配置字段说明

### 1. api_key
- **类型**: String
- **说明**: 大模型 API 的访问密钥
- **示例**: `"sk-xxxxxxxxxxxxxxxx"`
- **注意**: 请妥善保管，不要泄露

### 2. base_url
- **类型**: String
- **说明**: 大模型 API 的基础 URL
- **示例**: `"https://api.openai.com/v1"`
- **常见值**:
  - OpenAI: `https://api.openai.com/v1`
  - Azure OpenAI: `https://your-resource.openai.azure.com/`
  - 其他兼容 OpenAI API 的服务: `https://your-api-endpoint/v1`

### 3. config.model
- **类型**: String
- **说明**: 使用的模型名称
- **示例**:
  - OpenAI: `"gpt-4"`, `"gpt-4-turbo"`, `"gpt-3.5-turbo"`
  - 豆包: `"doubao-seed-1-6-251015"`
  - 其他: 根据你的 API 提供商指定

### 4. config.temperature
- **类型**: Float
- **范围**: 0.0 - 2.0
- **说明**: 控制输出的随机性
- **推荐值**:
  - `0.0 - 0.3`: 更确定性，适合需要精确回答的任务
  - `0.4 - 0.7`: 平衡创造性和确定性（推荐）
  - `0.8 - 1.0`: 更创造性，适合创意任务

### 5. config.top_p
- **类型**: Float
- **范围**: 0.0 - 1.0
- **说明**: 核采样参数，控制输出的多样性
- **推荐值**: `0.9`

### 6. config.max_completion_tokens
- **类型**: Integer
- **说明**: 最大输出 Token 数
- **推荐值**:
  - `4000`: 一般任务
  - `8000`: 复杂任务
  - `16000`: 超长任务

### 7. config.timeout
- **类型**: Integer
- **单位**: 秒
- **说明**: 请求超时时间
- **推荐值**: `600`（10分钟）

### 8. config.thinking
- **类型**: String
- **可选值**: `"disabled"`, `"enabled"`
- **说明**: 是否启用思考模式（部分模型支持）
- **推荐值**: `"disabled"`

### 9. sp
- **类型**: String
- **说明**: 系统提示词，定义 Agent 的角色和行为
- **注意**: 这是一个很长的文本，包含完整的角色定义和任务说明

### 10. tools
- **类型**: Array
- **说明**: Agent 可用的工具列表
- **示例**: `["search", "calculator"]`
- **当前值**: `[]`（暂无工具）

---

## 配置优先级

配置加载遵循以下优先级（从高到低）：

1. **配置文件**: `config/agent_llm_config.json` 中的 `api_key` 和 `base_url`
2. **环境变量**: `COZE_WORKLOAD_IDENTITY_API_KEY` 和 `COZE_INTEGRATION_MODEL_BASE_URL`

如果配置文件中 `api_key` 或 `base_url` 为空，系统会尝试从环境变量读取。

---

## 首次配置步骤

### 1. 复制示例配置文件

```bash
cp config/agent_llm_config.json.example config/agent_llm_config.json
```

### 2. 编辑配置文件

```bash
# Linux/macOS
nano config/agent_llm_config.json

# Windows
notepad config\agent_llm_config.json
```

### 3. 填写实际配置

```json
{
  "api_key": "sk-your-actual-api-key-here",
  "base_url": "https://api.openai.com/v1",
  "config": {
    "model": "gpt-4",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_completion_tokens": 4000,
    "timeout": 600,
    "thinking": "disabled"
  },
  "sp": "你是专业的SQL代码审查专家...",
  "tools": []
}
```

### 4. 保存文件

确保文件是有效的 JSON 格式（可以使用在线 JSON 验证工具检查）。

---

## 常见配置示例

### OpenAI GPT-4 配置

```json
{
  "api_key": "sk-xxxxxxxxxxxxxxxx",
  "base_url": "https://api.openai.com/v1",
  "config": {
    "model": "gpt-4",
    "temperature": 0.3,
    "top_p": 0.9,
    "max_completion_tokens": 4000,
    "timeout": 600,
    "thinking": "disabled"
  },
  "sp": "...",
  "tools": []
}
```

### Azure OpenAI 配置

```json
{
  "api_key": "your-azure-api-key",
  "base_url": "https://your-resource.openai.azure.com/openai/deployments/your-deployment",
  "config": {
    "model": "gpt-4",
    "temperature": 0.3,
    "top_p": 0.9,
    "max_completion_tokens": 4000,
    "timeout": 600,
    "thinking": "disabled"
  },
  "sp": "...",
  "tools": []
}
```

### 豆包模型配置

```json
{
  "api_key": "your-doubao-api-key",
  "base_url": "https://ark.cn-beijing.volces.com/api/v3",
  "config": {
    "model": "doubao-seed-1-6-251015",
    "temperature": 0.3,
    "top_p": 0.9,
    "max_completion_tokens": 8000,
    "timeout": 600,
    "thinking": "disabled"
  },
  "sp": "...",
  "tools": []
}
```

### 本地 Ollama 配置

```json
{
  "api_key": "ollama",
  "base_url": "http://localhost:11434/v1",
  "config": {
    "model": "llama2",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_completion_tokens": 4000,
    "timeout": 600,
    "thinking": "disabled"
  },
  "sp": "...",
  "tools": []
}
```

---

## 安全注意事项

### ⚠️ 重要提醒

1. **不要提交配置文件到 Git**
   - `config/agent_llm_config.json` 已添加到 `.gitignore`
   - 确保你的 API Key 不会被泄露

2. **使用环境变量（可选）**
   - 如果不希望使用配置文件，可以在 `.env` 文件中设置：
   ```bash
   COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key_here
   COZE_INTEGRATION_MODEL_BASE_URL=https://api.example.com/v1
   ```

3. **定期轮换 API Key**
   - 建议定期更换 API Key 以提高安全性

4. **限制 API 权限**
   - 为 API Key 设置适当的权限和限额

---

## 验证配置

配置完成后，可以运行以下命令验证：

```bash
# 测试配置文件格式
python -c "import json; json.load(open('config/agent_llm_config.json')); print('✅ 配置文件格式正确')"

# 测试 Agent 初始化
python -c "from src.agents.agent import build_agent; agent = build_agent(); print('✅ Agent 初始化成功')"
```

如果看到 `✅` 提示，说明配置正确。

---

## 故障排查

### 问题 1: 配置文件格式错误

**错误信息**: `JSONDecodeError`

**解决方案**: 使用 JSON 验证工具检查配置文件格式

### 问题 2: API Key 无效

**错误信息**: `401 Unauthorized`

**解决方案**:
- 检查 API Key 是否正确
- 确认 API Key 是否有足够的权限
- 检查 API Key 是否已过期

### 问题 3: Base URL 连接失败

**错误信息**: `Connection refused` 或 `Timeout`

**解决方案**:
- 检查 Base URL 是否正确
- 确认网络连接是否正常
- 检查防火墙设置

---

## 相关文件

- `config/agent_llm_config.json` - 实际配置文件（不提交到 Git）
- `config/agent_llm_config.json.example` - 配置文件示例
- `.gitignore` - Git 忽略规则（包含配置文件）
- `.env` - 环境变量配置（可选）

---

## 需要帮助？

如果遇到配置问题，请查看：
- [故障排查文档](./LOCAL_DATABASE_SETUP.md)
- [日志文件](../logs/app.log)
- [项目 README](../README.md)
