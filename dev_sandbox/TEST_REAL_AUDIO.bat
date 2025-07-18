@echo off
REM DEV_SANDBOX: This is a development test batch file for real audio testing
REM Purpose: Test real audio capture with VoiceMeeter device 38
REM Status: Development tool - used for audio validation testing
echo 🎯 LAUNCHING REAL AUDIO RADAR HUD
echo ================================
echo Device: 38 (VoiceMeeter Out B1 Alt)
echo Mode: REAL AUDIO ONLY - NO SIMULATION
echo.
echo 🎮 Starting HUD...
python real_audio_tkinter_hud.py --device 38
pause
