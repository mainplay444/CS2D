@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo =============================================
echo LAST ROUND - WebSocket server
echo =============================================
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 --version
  if errorlevel 1 goto usepython
  py -3 -m pip install websockets
  if errorlevel 1 goto failed
  py -3 server.py
  goto end
)
:usepython
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.10 or newer and enable Add Python to PATH.
  pause
  goto end
)
python --version
python -m pip install websockets
if errorlevel 1 goto failed
python server.py
goto end
:failed
echo Could not install the websockets package. Check internet access and Python installation.
pause
:end
pause
