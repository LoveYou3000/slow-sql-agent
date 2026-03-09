# 本地日志配置说明

## 📝 更新内容

本次更新为项目添加了本地化日志支持，现在日志文件可以输出到项目根目录下的 `logs/` 目录，而不是 Coze 平台的默认路径。

---

## 🚀 快速使用

### Linux / macOS

```bash
# 方式 1: 使用启动脚本（推荐）
./scripts/start_local.sh

# 方式 2: 手动设置环境变量
export LOG_FILE="./logs/app.log"
mkdir -p logs
python src/main.py
```

### Windows

```bash
# 使用启动脚本
scripts\start_local.bat
```

---

## 📂 新增文件

| 文件 | 说明 |
|------|------|
| `scripts/start_local.sh` | Linux/macOS 启动脚本 |
| `scripts/start_local.bat` | Windows 启动脚本 |
| `scripts/test_log_config.py` | 日志配置测试脚本 |
| `docs/LOCAL_RUN_GUIDE.md` | 完整的本地运行指南 |

---

## 🔧 修改内容

### src/main.py

在导入日志模块后添加了环境变量检查：

```python
# 支持通过环境变量自定义日志路径（用于本地开发）
LOCAL_LOG_FILE = os.getenv('LOG_FILE') or os.getenv('LOCAL_LOG_FILE')
if LOCAL_LOG_FILE:
    LOG_FILE = LOCAL_LOG_FILE
    # 确保日志目录存在
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
```

---

## 📊 日志目录对比

| 环境 | 日志路径 | 配置方式 |
|------|---------|---------|
| **本地运行** | `./logs/app.log` | 通过 `LOG_FILE` 环境变量 |
| **Coze 平台** | `/app/work/logs/bypass/app.log` | 默认配置 |

---

## 🧪 测试验证

运行测试脚本验证配置：

```bash
python scripts/test_log_config.py
```

**预期输出**：
```
============================================================
测试日志配置
============================================================
项目根目录: /workspace/projects
环境变量 LOG_FILE: /workspace/projects/logs/app.log
默认 LOG_FILE: /app/work/logs/bypass/app.log
✅ 环境变量 LOG_FILE 已设置
   实际日志路径: /workspace/projects/logs/app.log

日志目录: /workspace/projects/logs
✅ 日志目录已存在

测试日志写入...
这是一条测试日志
✅ 日志文件已创建: /workspace/projects/logs/app.log

============================================================
✅ 日志配置测试完成
============================================================
```

---

## 🔍 验证日志文件

```bash
# 查看日志文件
ls -lh logs/

# 查看日志内容
tail -f logs/app.log

# 搜索错误日志
grep "ERROR" logs/app.log
```

---

## 💡 自定义日志路径

如果需要使用其他日志目录：

```bash
# 设置自定义路径
export LOG_FILE="/path/to/your/logs/app.log"

# 或在 .env 文件中配置
echo "LOG_FILE=/path/to/your/logs/app.log" >> .env
```

---

## 📚 详细文档

完整的本地运行指南请参考：[docs/LOCAL_RUN_GUIDE.md](./docs/LOCAL_RUN_GUIDE.md)

---

## ✅ 验证清单

运行 Agent 前请确认：

- [ ] Python 3.8+ 已安装
- [ ] 依赖已安装：`pip install -r requirements.txt`
- [ ] 数据库已配置：参考 `assets/LOCAL_DATABASE_SETUP.md`
- [ ] 环境变量已设置：`PGDATABASE_URL`
- [ ] 日志目录已创建：`mkdir -p logs`

---

## 🆘 常见问题

### Q: 为什么之前有警告 "Using fallback log directory"？

**A**: 因为之前没有自定义日志路径，系统尝试使用 Coze 平台的默认路径 `/app/work/logs/bypass/app.log`，该路径在本地环境中不存在，所以系统自动使用了备用路径。

现在通过设置 `LOG_FILE` 环境变量，日志会直接输出到 `./logs/app.log`，不再出现警告。

### Q: 我不使用启动脚本，如何设置日志路径？

**A**: 在运行前设置环境变量：

```bash
# Linux/macOS
export LOG_FILE="./logs/app.log"
python src/main.py

# Windows (PowerShell)
$env:LOG_FILE = "./logs/app.log"
python src/main.py

# Windows (CMD)
set LOG_FILE=./logs/app.log
python src/main.py
```

### Q: 日志文件太大怎么办？

**A**: 日志已配置轮转机制：
- 最大文件大小：100MB
- 备份文件数：5 个
- 超过限制后会自动创建新文件

如果仍然太大，可以调整日志级别：

```bash
# 在 .env 文件中设置
LOG_LEVEL=WARN
```

---

## 🎯 总结

✅ **本地化配置完成！**

- 日志输出到 `logs/app.log`
- 启动脚本自动创建日志目录
- 环境变量配置灵活
- 完整的文档支持

现在你可以愉快地在本地运行 Agent 了！🎉
