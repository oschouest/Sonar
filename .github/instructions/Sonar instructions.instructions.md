---
applyTo: '**'
---

📡 Project Context: AudioRadar-HUD
This project is a tactical audio visualization tool that reads 7.1 surround sound in real-time and displays a dynamic radar-style HUD to assist gamers — especially those with hearing impairments — with spatial awareness.

It is inspired by ASUS Sonic Radar 3 and commercial AudioRadar systems. This implementation is entirely external and anti-cheat compliant.

✅ Coding Guidelines
🔐 Anti-Cheat Safety
Never read, write, hook, or inject into game memory or processes
Do not use DirectX, Vulkan, OpenGL, or GDI overlays
Do not simulate mouse/keyboard input
The radar must remain a separate, topmost window using only system-legal APIs
🎯 Radar Logic
Always support all 8 channels (7.1): FL, FR, C, LFE, RL, RR, SL, SR
Convert directional audio using vector blending, not static channel-to-angle
Visual blips should:
Scale with volume
Fade over time
Reflect accurate direction from audio mix (weighted average of vectors)
FPS target is 100 or higher, but should remain adjustable
🖥️ GUI Guidelines
Use Pygame for rendering (do not switch to another GUI library unless explicitly asked)
Maintain HUD clarity: radar grid, labels, blips, and optional debug overlay
GUI must be always-on-top but not a system-level overlay
⚙️ Config + UX
All major parameters (blip fade time, theme, fps, sensitivity) must be:
Loadable from config.json
Changeable via in-HUD menu (F1 or M)
Hot-reloadable if possible
Menu changes must persist to config.json
📂 File Structure Standards
Maintain this structure and keep roles distinct:

audio_radar.py: 7.1 audio capture + RMS volume processing
radar_gui.py: HUD rendering + blip logic
hud_launcher.py: Primary launcher
audio_radar_system.py: Orchestrates full stack
real_audio_tkinter_hud.py: Legacy fallback HUD (Tkinter)
passthrough_setup_helper.py: Audio device guide
requirements.txt: Clean dependency list
README.md: Must be updated with each new feature or module
🧪 Temporary & Test Files
Any experimental, debug, or throwaway files (e.g. test_*.py, scratchpad.py) must go into a /dev_sandbox/ or /tmp/ folder inside the project root
If the test file is no longer useful, it must be deleted automatically or flagged for removal
If it may have value, move it to /examples/ with a header comment explaining purpose
🧹 Workspace Hygiene
Never clutter the root folder with test files, backups, or temp experiments
Do not create .pyc, .log, .bak, or ~ files outside of .venv/ or /tmp/
Maintain .gitignore to avoid accidental commits of temp files
📘 README Maintenance
Always update README.md after any feature, setting, or usage change
Add new configuration keys to the config section
Document new menu options, CLI flags, or hotkeys
If behavior changes, reflect it immediately in README usage and feature list
💾 GitHub Commit Standards
Automatically stage and commit changes to the local GitHub repo with clean, informative messages
Group related file changes (e.g. “Add config reload system + update radar GUI to match”)
Push only when changes are validated locally
Never commit broken, half-baked, or sandbox-only experiments to main
💬 Communication with Agent
If unsure, ask before deleting or replacing a system
Respect working code; never overwrite functional logic unless explicitly instructed
Assume persistent memory — don’t repeat mistakes across sessions
Follow any prompt files in /prompts/*.md as the source of truth for task logic
📦 Deployment
Final output should support .exe packaging (Batch file fine for now dont worry about this)
System must run from a single script or batch file
No installation required beyond Python + VoiceMeeter
🏁 Project Goal
Build a production-ready, accessible, anti-cheat-safe audio radar HUD that rivals commercial visualizers like ASUS Sonic Radar 3 and AudioRadar — but is fully open-source, customizable, and runs on any modern PC.

Eventually want to add training mode or ai mode or upload audio ques or something to make it intelligent for specefic titles like Rainbow Six Siege X.