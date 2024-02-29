@echo off
for /f "delims=" %%A in ('PowerShell.exe -ExecutionPolicy Bypass -File "ClearBrowsingHistory.ps1"') do (
    set "output=%%A"
    echo !output!
)
pause
