@echo off
rem acctest fixture plugin: the check command on Windows. Runs the PowerShell script that sits beside it.
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0acctest_users.ps1"
exit /b %ERRORLEVEL%
