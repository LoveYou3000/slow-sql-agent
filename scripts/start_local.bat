@echo off
REM =============================================================================
REM 本地启动脚本 (Windows)
REM 用于在本地环境中运行 Agent，日志输出到 logs/ 目录
REM =============================================================================

REM 设置项目根目录
set "PROJECT_ROOT=%~dp0..\"
cd /d "%PROJECT_ROOT%"

REM 设置日志目录（当前项目下的 logs 目录）
set "LOG_DIR=%PROJECT_ROOT%logs"
set "LOG_FILE=%LOG_DIR%\app.log"

REM 创建日志目录（如果不存在）
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ==========================================
echo   SQL 问题检测 Agent - 本地启动
echo ==========================================
echo 项目目录: %PROJECT_ROOT%
echo 日志目录: %LOG_DIR%
echo 日志文件: %LOG_FILE%
echo ==========================================
echo.

REM 检查 Python 环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Python，请先安装 Python 3.8+
    exit /b 1
)

REM 检查依赖
echo 检查依赖...
python -c "import langchain; import langgraph; import sqlalchemy" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  警告: 部分依赖未安装，正在安装...
    pip install -r requirements.txt
)

echo ✅ 依赖检查完成
echo.

REM 启动 Agent
echo 启动 Agent...
python src/main.py %*
