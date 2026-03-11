@echo off
chcp 65001 >nul

echo ========================================
echo   wxauto-channel 配置管理
echo ========================================
echo.

cd /d "%~dp0..\wxauto-channel"
python config_manager.py

pause
