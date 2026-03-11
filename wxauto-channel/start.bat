@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [wxauto-channel] 启动中...
echo.
echo 依赖检查：
python -c "import requests, websockets, yaml; print('OK')" 2>nul || (
    echo 安装缺失依赖...
    pip install requests pyyaml websockets
)
echo.
echo 启动 wxauto_channel.py ...
python wxauto_channel.py
pause
