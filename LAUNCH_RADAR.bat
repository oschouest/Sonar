@echo off
echo 🎯 SIEGE AUDIO RADAR - Enhanced Combat Edition 🎯
echo ================================================
echo.
echo [1] Launch Enhanced Radar (Device 38) - RECOMMENDED
echo [2] Auto-detect Best Device
echo [3] Show Available Audio Devices  
echo [4] Exit
echo.
set /p choice="Choose option (1-4): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Launching Enhanced Combat Audio Radar...
    echo ✨ Features: Dynamic colors, pulsing effects, threat meter
    echo 🎨 Real-time color changes based on sound intensity
    echo 📡 Combat-style HUD with directional indicators
    echo.
    python real_audio_tkinter_hud.py --device 38 --frameless --always-on-top --transparent
) else if "%choice%"=="2" (
    echo.
    echo 🔍 Auto-detecting best VoiceMeeter device...
    echo.
    echo Trying Device 38 (VoiceMeeter Out B1 Alt)...
    python real_audio_tkinter_hud.py --device 38 --frameless --always-on-top --transparent
    if %ERRORLEVEL% NEQ 0 (
        echo Trying Device 91...
        python real_audio_tkinter_hud.py --device 91 --frameless --always-on-top --transparent
    )
    if %ERRORLEVEL% NEQ 0 (
        echo Trying Device 8...
        python real_audio_tkinter_hud.py --device 8 --frameless --always-on-top --transparent
    )
) else if "%choice%"=="3" (
    echo.
    echo 📋 Available Audio Devices:
    python -c "import sounddevice as sd; print('\\n'.join([f'{i}: {dev[\"name\"]}' for i, dev in enumerate(sd.query_devices())]))"
    echo.
    pause
    cls
    goto start
) else (
    echo.
    echo 👋 Goodbye!
    exit /b 0
)

echo.
echo Audio Radar closed.
pause

:start
goto start
