@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:menu
cls
echo ========================================
echo   wxauto-openclaw-channel 管理面板
echo ========================================
echo.
echo 1. 安装依赖
echo 2. 启动所有服务
echo 3. 停止所有服务
echo 4. 配置管理
echo 5. 监控日志
echo 6. 查看服务状态
echo 7. 打开文档
echo 0. 退出
echo.
echo ========================================
set /p choice="请选择操作 (0-7): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto start
if "%choice%"=="3" goto stop
if "%choice%"=="4" goto config
if "%choice%"=="5" goto monitor
if "%choice%"=="6" goto status
if "%choice%"=="7" goto docs
if "%choice%"=="0" goto end
goto menu

:install
echo.
echo 正在安装依赖...
call scripts\install.bat
pause
goto menu

:start
echo.
echo 正在启动服务...
call scripts\start-all.bat
goto menu

:stop
echo.
echo 正在停止服务...
call scripts\stop-all.bat
goto menu

:config
echo.
call scripts\config.bat
goto menu

:monitor
echo.
echo 正在打开日志监控...
start cmd /k "cd wxauto-channel && monitor.bat"
pause
goto menu

:status
cls
echo ========================================
echo   服务状态检查
echo ========================================
echo.

echo [1/3] 检查 wxauto-restful-api...
netstat -ano | findstr ":8001" >nul 2>&1
if errorlevel 1 (
    echo [×] wxauto-restful-api 未运行
) else (
    echo [√] wxauto-restful-api 正在运行 (端口 8001)
)
echo.

echo [2/3] 检查 OpenClaw Gateway...
curl -s http://127.0.0.1:18789/health >nul 2>&1
if errorlevel 1 (
    echo [×] OpenClaw Gateway 未运行
) else (
    echo [√] OpenClaw Gateway 正在运行 (端口 18789)
)
echo.

echo [3/3] 检查 wxauto-channel...
wmic process where "name='python.exe' and CommandLine like '%%wxauto_channel%%'" get ProcessId 2>nul | findstr /R "[0-9]" >nul
if errorlevel 1 (
    echo [×] wxauto-channel 未运行
) else (
    echo [√] wxauto-channel 正在运行
)
echo.

echo ========================================
pause
goto menu

:docs
echo.
echo 正在打开文档...
start README.md
start docs\INSTALL.md
pause
goto menu

:end
echo.
echo 再见！
timeout /t 2 >nul
exit
