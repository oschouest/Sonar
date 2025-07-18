@echo off
REM DEV_SANDBOX: This is a development debug batch file for real audio testing
REM Purpose: Test real audio capture with debug output enabled
REM Status: Development tool - used for audio debugging and validation
echo 🎯 LAUNCHING REAL AUDIO RADAR HUD (DEBUG)
echo =======================================
echo Device: 38 (VoiceMeeter Out B1 Alt)
echo Mode: REAL AUDIO ONLY - NO SIMULATION
echo Debug: ENABLED
echo.
echo 🎮 Starting HUD with debug output...
python real_audio_tkinter_hud.py --device 38 --debug
pause
