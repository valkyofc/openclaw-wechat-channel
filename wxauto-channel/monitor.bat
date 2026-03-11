@echo off
chcp 65001 >nul
echo [wxauto-channel 监控] 实时查看日志...
echo 按 Ctrl+C 退出
echo.
cd /d "%~dp0"
powershell -Command "Get-Content channel.log -Wait -Tail 20"
