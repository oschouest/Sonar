@echo off
:start
echo 🎯 AUDIORADAR-HUD - Production Edition 🎯
echo =========================================
echo.
echo [1] Launch AudioRadar (Auto-detect) - RECOMMENDED
echo [2] Launch with Device 38 (VoiceMeeter)
echo [3] Setup Guide (First Time)
echo [4] Show Available Audio Devices  
echo [5] Exit
echo.
set /p choice="Choose option (1-5): "

if "%choice%"=="1" goto option1
if "%choice%"=="2" goto option2
if "%choice%"=="3" goto option3
if "%choice%"=="4" goto option4
if "%choice%"=="5" goto exit
echo Invalid choice. Please try again.
goto start

:option1
echo.
echo 🚀 Launching AudioRadar-HUD (Auto-detect)...
echo ✨ Features: 120 FPS, Vector blending, Config menu
echo 🎨 Anti-cheat safe, Always-on-top HUD
echo 📡 Production-ready 7.1 audio radar
echo.
python hud_launcher.py --fps 120 --always-on-top
goto end

:option2
echo.
echo � Launching AudioRadar-HUD (Device 38)...
echo ✨ Using VoiceMeeter Out B1 Alt device
echo 📡 Optimized for VoiceMeeter Potato
echo.
python hud_launcher.py --device 38 --fps 120 --always-on-top
goto end

:option3
echo.
echo 🔧 Running Setup Guide...
echo This will help you configure audio routing
echo.
python passthrough_setup_helper.py
echo.
pause
cls
goto start

:option4
echo.
echo 📋 Available Audio Devices:
python -c "import sounddevice as sd; print('\\n'.join([f'{i}: {dev[\"name\"]}' for i, dev in enumerate(sd.query_devices())]))"
echo.
pause
cls
goto start

:exit
echo.
echo 👋 Goodbye!
exit /b 0

:end
echo.
echo AudioRadar-HUD closed.
pause
