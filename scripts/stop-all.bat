@echo off
chcp 65001 >nul

echo ========================================
echo   停止 wxauto-openclaw-channel
echo ========================================
echo.

:: 停止 wxauto-channel
echo [1/2] 停止 wxauto-channel...
wmic process where "name='python.exe' and CommandLine like '%%wxauto_channel%%'" delete 2>nul
if errorlevel 1 (
    echo [OK] wxauto-channel 未运行或已停止
) else (
    echo [OK] wxauto-channel 已停止
)
echo.

:: 停止 wxauto-restful-api
echo [2/2] 停止 wxauto-restful-api...
cd /d "%~dp0..\wxauto-restful-api"
call stop.bat
echo.

:: 提示
echo ========================================
echo   所有服务已停止
echo ========================================
echo.
echo 注意: OpenClaw Gateway 仍在运行
echo 如需停止: openclaw gateway stop
echo.
pause
