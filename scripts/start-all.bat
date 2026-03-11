@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   启动 wxauto-openclaw-channel
echo ========================================
echo.

:: 检查微信
echo [1/4] 检查微信...
tasklist /FI "IMAGENAME eq WeChat.exe" 2>NUL | find /I /N "WeChat.exe">NUL
if errorlevel 1 (
    echo [警告] 微信未运行，请先登录微信
    echo.
    choice /C YN /M "是否继续启动服务"
    if errorlevel 2 exit /b 0
)
echo [OK] 微信已运行
echo.

:: 检查 OpenClaw Gateway
echo [2/4] 检查 OpenClaw Gateway...
curl -s http://127.0.0.1:18789/health >nul 2>&1
if errorlevel 1 (
    echo [警告] OpenClaw Gateway 未运行
    echo 正在启动 OpenClaw Gateway...
    openclaw gateway start
    timeout /t 3 >nul
    curl -s http://127.0.0.1:18789/health >nul 2>&1
    if errorlevel 1 (
        echo [错误] OpenClaw Gateway 启动失败
        pause
        exit /b 1
    )
)
echo [OK] OpenClaw Gateway 已运行
echo.

:: 启动 wxauto-restful-api
echo [3/4] 启动 wxauto-restful-api...
cd /d "%~dp0..\wxauto-restful-api"

:: 检查是否已运行
netstat -ano | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo [OK] wxauto-restful-api 已在运行
) else (
    echo 正在启动 wxauto-restful-api...
    start "wxauto-restful-api" cmd /k "python run.py"
    timeout /t 5 >nul

    netstat -ano | findstr ":8001" >nul 2>&1
    if errorlevel 1 (
        echo [错误] wxauto-restful-api 启动失败
        pause
        exit /b 1
    )
    echo [OK] wxauto-restful-api 已启动
)
echo.

:: 启动 wxauto-channel
echo [4/4] 启动 wxauto-channel...
cd /d "%~dp0..\wxauto-channel"

:: 检查是否已运行
wmic process where "name='python.exe' and CommandLine like '%%wxauto_channel%%'" get ProcessId 2>nul | findstr /R "[0-9]" >nul
if not errorlevel 1 (
    echo [OK] wxauto-channel 已在运行
) else (
    echo 正在启动 wxauto-channel...
    start "wxauto-channel" cmd /k "python wxauto_channel.py"
    timeout /t 3 >nul
    echo [OK] wxauto-channel 已启动
)
echo.

:: 完成
echo ========================================
echo   所有服务已启动！
echo ========================================
echo.
echo 服务状态:
echo - wxauto-restful-api: http://localhost:8001/docs
echo - OpenClaw Gateway: http://127.0.0.1:18789/health
echo - wxauto-channel: 运行中
echo.
echo 监控日志:
echo   cd wxauto-channel
echo   monitor.bat
echo.
echo 停止服务:
echo   scripts\stop-all.bat
echo.
pause
