@echo off
chcp 65001 >nul
echo [wxauto-channel] 停止中...
taskkill /F /FI "WINDOWTITLE eq wxauto_channel*" /IM python.exe 2>nul
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV /NH 2^>nul') do (
    wmic process where "ProcessId=%%~i and CommandLine like '%%wxauto_channel%%'" delete 2>nul
)
echo 已尝试停止所有 wxauto_channel 进程。
pause
