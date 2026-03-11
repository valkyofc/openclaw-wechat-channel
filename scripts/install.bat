@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   wxauto-openclaw-channel 一键安装
echo ========================================
echo.

:: 检查 Python
echo [1/5] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.11+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo [OK] Python 已安装
echo.

:: 检查 OpenClaw
echo [2/5] 检查 OpenClaw...
openclaw --version >nul 2>&1
if errorlevel 1 (
    echo [警告] 未检测到 OpenClaw
    echo 正在安装 OpenClaw...
    pip install openclaw
    if errorlevel 1 (
        echo [错误] OpenClaw 安装失败
        pause
        exit /b 1
    )
)
echo [OK] OpenClaw 已安装
echo.

:: 安装 wxauto-restful-api 依赖
echo [3/5] 安装 wxauto-restful-api 依赖...
cd /d "%~dp0..\wxauto-restful-api"

:: 尝试使用 uv
pip show uv >nul 2>&1
if errorlevel 1 (
    echo 正在安装 uv...
    pip install uv
)

echo 使用 uv 安装依赖...
uv sync
if errorlevel 1 (
    echo uv 安装失败，尝试使用 pip...
    pip install fastapi uvicorn wxautox pyyaml python-multipart websockets
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)
echo [OK] wxauto-restful-api 依赖已安装
echo.

:: 安装 wxauto-channel 依赖
echo [4/5] 安装 wxauto-channel 依赖...
cd /d "%~dp0..\wxauto-channel"
pip install requests websockets pyyaml
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [OK] wxauto-channel 依赖已安装
echo.

:: 启动 OpenClaw Gateway
echo [5/5] 启动 OpenClaw Gateway...
openclaw gateway start
if errorlevel 1 (
    echo [警告] OpenClaw Gateway 启动失败或已在运行
) else (
    echo [OK] OpenClaw Gateway 已启动
)
echo.

:: 获取 OpenClaw Token
echo ========================================
echo   获取 OpenClaw Token
echo ========================================
openclaw gateway token
echo.
echo 请将上面的 token 复制到 wxauto-channel\config.yaml 中
echo.

:: 提示配置
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 下一步：
echo 1. 编辑 wxauto-channel\config.yaml
echo    - 填写 OpenClaw token
echo    - 填写你的微信昵称 (my_nickname)
echo    - 配置监听对象
echo.
echo 2. 启动服务:
echo    scripts\start-all.bat
echo.
echo 3. 查看文档:
echo    README.md - 项目说明
echo    docs\INSTALL.md - 安装指南
echo    docs\CONFIG.md - 配置说明
echo.
pause
