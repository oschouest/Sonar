@echo off
:start
echo 🎯 AUDIORADAR-HUD - Production Edition 🎯
echo =========================================
echo.
echo [1] Launch AudioRadar (config.json settings) - RECOMMENDED
echo [2] Setup Guide (First Time)
echo [3] Show Available Audio Devices  
echo [4] Exit
echo.
set /p choice="Choose option (1-4): "

if "%choice%"=="1" goto option1
if "%choice%"=="2" goto option2
if "%choice%"=="3" goto option3
if "%choice%"=="4" goto exit
echo Invalid choice. Please try again.
goto start

:option1
echo.
echo 🚀 Launching AudioRadar-HUD...
echo ✨ Loading settings from config.json
echo 🎨 Anti-cheat safe, Always-on-top HUD
echo 📡 Production-ready 7.1 audio radar
echo 🎯 Press F1 or M in-game to open menu
echo.
python hud_launcher.py
goto end

:option2
echo.
echo 🔧 Running Setup Guide...
echo This will help you configure audio routing
echo.
python passthrough_setup_helper.py
echo.
pause
cls
goto start

:option3
echo.
echo 🎵 Available Audio Devices:
echo.
python hud_launcher.py --list-devices
echo.
pause
cls
goto start

:exit
echo.
echo 👋 Thanks for using AudioRadar-HUD!
echo.
pause
exit

:end
echo.
echo 📝 AudioRadar-HUD has closed.
echo.
pause
cls
goto start
