@echo off
cd /d "%~dp0\.."

python -m src.startup

echo.
echo Program exited with code %errorlevel%
pause