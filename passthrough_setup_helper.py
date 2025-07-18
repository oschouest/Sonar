#!/usr/bin/env python3
"""
Passthrough Setup Helper - Guides users to set up audio routing via VoiceMeeter
Sonar compliance: Guides users to set up audio routing via VoiceMeeter
"""

import sys
import os
import subprocess
import webbrowser
from typing import List, Dict, Optional

def print_header(title: str):
    """Print a formatted header"""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()

def print_step(step: int, title: str, description: str):
    """Print a formatted step"""
    print(f"📋 Step {step}: {title}")
    print(f"   {description}")
    print()

def check_voicemeeter_installed() -> bool:
    """Check if VoiceMeeter is installed"""
    common_paths = [
        r"C:\Program Files (x86)\VB\Voicemeeter\voicemeeter.exe",
        r"C:\Program Files\VB\Voicemeeter\voicemeeter.exe",
        r"C:\Program Files (x86)\VB\Voicemeeter\voicemeeterpro.exe",
        r"C:\Program Files\VB\Voicemeeter\voicemeeterpro.exe"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return True
    
    return False

def open_voicemeeter_download():
    """Open VoiceMeeter download page"""
    url = "https://vb-audio.com/Voicemeeter/potato.htm"
    webbrowser.open(url)
    print(f"🌐 Opening VoiceMeeter download page: {url}")

def get_audio_devices() -> List[Dict]:
    """Get available audio devices"""
    devices = []
    try:
        import sounddevice as sd
        device_list = sd.query_devices()
        
        for i, device in enumerate(device_list):
            if device['max_input_channels'] > 0:
                devices.append({
                    'id': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
                
    except Exception as e:
        print(f"❌ Error getting audio devices: {e}")
    
    return devices

def find_voicemeeter_devices(devices: List[Dict]) -> List[Dict]:
    """Find VoiceMeeter devices in the list"""
    voicemeeter_devices = []
    
    for device in devices:
        name_lower = device['name'].lower()
        if 'voicemeeter' in name_lower or 'vb-audio' in name_lower:
            voicemeeter_devices.append(device)
    
    return voicemeeter_devices

def test_audio_device(device_id: int) -> bool:
    """Test if an audio device is working"""
    try:
        import sounddevice as sd
        import numpy as np
        
        # Try to record a short sample
        duration = 0.1  # 100ms
        sample_rate = 44100
        
        data = sd.rec(int(duration * sample_rate), 
                     samplerate=sample_rate, 
                     channels=8, 
                     device=device_id)
        sd.wait()
        
        # Check if we got any data
        if np.any(data):
            return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    return False

def setup_guide():
    """Main setup guide"""
    print_header("🎯 AudioRadar-HUD Setup Guide")
    
    print("Welcome to the AudioRadar-HUD setup guide!")
    print("This tool will help you configure 7.1 surround sound audio routing")
    print("for optimal radar performance.")
    print()
    
    # Check if VoiceMeeter is installed
    print_step(1, "Check VoiceMeeter Installation", "Checking if VoiceMeeter is installed...")
    
    if check_voicemeeter_installed():
        print("✅ VoiceMeeter is installed!")
    else:
        print("❌ VoiceMeeter not found")
        print()
        print("VoiceMeeter is required for proper 7.1 audio routing.")
        print("Would you like to download it now? (y/n): ", end="")
        
        choice = input().lower().strip()
        if choice == 'y':
            open_voicemeeter_download()
            print()
            print("Please install VoiceMeeter Potato and restart this setup guide.")
            return False
        else:
            print("⚠️ Setup cannot continue without VoiceMeeter")
            return False
    
    # Get audio devices
    print_step(2, "Scan Audio Devices", "Scanning for available audio devices...")
    devices = get_audio_devices()
    
    if not devices:
        print("❌ No audio input devices found!")
        print("Please check your audio drivers and try again.")
        return False
    
    print(f"✅ Found {len(devices)} audio input devices")
    
    # Find VoiceMeeter devices
    print_step(3, "Find VoiceMeeter Devices", "Looking for VoiceMeeter audio devices...")
    voicemeeter_devices = find_voicemeeter_devices(devices)
    
    if not voicemeeter_devices:
        print("❌ No VoiceMeeter devices found!")
        print()
        print("This usually means VoiceMeeter is not running or not configured.")
        print("Please:")
        print("  1. Start VoiceMeeter Potato")
        print("  2. Configure it as your default audio device")
        print("  3. Restart this setup guide")
        return False
    
    print(f"✅ Found {len(voicemeeter_devices)} VoiceMeeter devices:")
    for device in voicemeeter_devices:
        print(f"   {device['id']:2d}: {device['name']} ({device['channels']} channels)")
    
    # Test devices
    print_step(4, "Test Audio Devices", "Testing VoiceMeeter devices for audio input...")
    
    working_devices = []
    for device in voicemeeter_devices:
        print(f"Testing device {device['id']}: {device['name']}...")
        if test_audio_device(device['id']):
            print("   ✅ Device is working!")
            working_devices.append(device)
        else:
            print("   ❌ Device is not receiving audio")
    
    if not working_devices:
        print("❌ No working VoiceMeeter devices found!")
        print()
        print("This means VoiceMeeter is not receiving audio input.")
        print("Please check your VoiceMeeter configuration:")
        print("  1. Set VoiceMeeter as your default Windows playback device")
        print("  2. Configure your game/application to use VoiceMeeter")
        print("  3. Ensure audio is playing through VoiceMeeter")
        return False
    
    # Configuration summary
    print_step(5, "Configuration Summary", "Setup complete!")
    
    print("🎯 Recommended AudioRadar Configuration:")
    print()
    
    best_device = working_devices[0]  # Use the first working device
    print(f"📊 Audio Device: {best_device['id']} ({best_device['name']})")
    print(f"🎵 Channels: {best_device['channels']}")
    print(f"📈 Sample Rate: {best_device['sample_rate']}")
    print()
    
    print("🚀 Launch Commands:")
    print(f"   python hud_launcher.py --device {best_device['id']}")
    print(f"   python audio_radar_system.py --device {best_device['id']}")
    print()
    
    print("🎮 VoiceMeeter Configuration Tips:")
    print("   1. Set VoiceMeeter as Windows default playback device")
    print("   2. Configure your game to use 7.1 surround sound")
    print("   3. Enable 'Exclusive Mode' in VoiceMeeter for best performance")
    print("   4. Adjust VoiceMeeter output to your headphones/speakers")
    print()
    
    print("📋 Next Steps:")
    print("   1. Start your game or audio application")
    print("   2. Launch AudioRadar with the command above")
    print("   3. Use F1 to open the configuration menu")
    print("   4. Adjust sensitivity and other settings as needed")
    print()
    
    # Create launch script
    print("Would you like to create a launch script? (y/n): ", end="")
    choice = input().lower().strip()
    if choice == 'y':
        create_launch_script(best_device['id'])
    
    return True

def create_launch_script(device_id: int):
    """Create a launch script with the recommended device"""
    script_content = f"""@echo off
echo 🎯 AudioRadar-HUD Launcher
echo ========================
echo Device: {device_id}
echo.
echo Starting AudioRadar...
python hud_launcher.py --device {device_id} --fps 120 --always-on-top
echo.
echo AudioRadar stopped.
pause
"""
    
    script_path = "LAUNCH_AUDIORADAR.bat"
    
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        print(f"✅ Launch script created: {script_path}")
        print("You can now double-click this file to start AudioRadar!")
        
    except Exception as e:
        print(f"❌ Failed to create launch script: {e}")

def advanced_setup():
    """Advanced setup options"""
    print_header("🔧 Advanced Setup Options")
    
    print("Advanced configuration options:")
    print()
    print("1. Test all audio devices")
    print("2. VoiceMeeter configuration guide")
    print("3. Performance optimization")
    print("4. Troubleshooting guide")
    print("5. Exit")
    print()
    
    choice = input("Select an option (1-5): ").strip()
    
    if choice == '1':
        test_all_devices()
    elif choice == '2':
        voicemeeter_guide()
    elif choice == '3':
        performance_guide()
    elif choice == '4':
        troubleshooting_guide()
    elif choice == '5':
        return
    else:
        print("Invalid choice. Please try again.")
        advanced_setup()

def test_all_devices():
    """Test all available audio devices"""
    print_header("🎵 Test All Audio Devices")
    
    devices = get_audio_devices()
    
    if not devices:
        print("❌ No audio devices found!")
        return
    
    print(f"Testing {len(devices)} audio devices:")
    print()
    
    for device in devices:
        print(f"Testing device {device['id']:2d}: {device['name']}")
        print(f"   Channels: {device['channels']}")
        print(f"   Sample Rate: {device['sample_rate']}")
        
        if test_audio_device(device['id']):
            print("   ✅ Working!")
        else:
            print("   ❌ Not working")
        print()

def voicemeeter_guide():
    """VoiceMeeter configuration guide"""
    print_header("🎛️ VoiceMeeter Configuration Guide")
    
    print("VoiceMeeter Potato Setup for 7.1 Audio:")
    print()
    print("1. Install VoiceMeeter Potato (not Basic or Banana)")
    print("2. Set VoiceMeeter Input as Windows default playback device")
    print("3. Configure your game to use 7.1 surround sound")
    print("4. In VoiceMeeter, set Hardware Out to your headphones/speakers")
    print("5. Enable 'Exclusive Mode' for better performance")
    print("6. Adjust levels so you can hear game audio normally")
    print()
    print("AudioRadar Setup:")
    print("1. Find 'VoiceMeeter Output' in audio devices")
    print("2. Use that device ID with AudioRadar")
    print("3. AudioRadar will capture the 7.1 mix from VoiceMeeter")
    print()
    print("Common Issues:")
    print("- If no audio: Check VoiceMeeter is default Windows device")
    print("- If only stereo: Enable 7.1 in game audio settings")
    print("- If crackling: Adjust buffer size in VoiceMeeter")
    print()

def performance_guide():
    """Performance optimization guide"""
    print_header("🚀 Performance Optimization")
    
    print("AudioRadar Performance Tips:")
    print()
    print("System:")
    print("- Close unnecessary programs")
    print("- Set AudioRadar to High Priority in Task Manager")
    print("- Use Performance power plan")
    print("- Disable Windows Game Mode if causing issues")
    print()
    print("AudioRadar Settings:")
    print("- Use --performance flag for optimized rendering")
    print("- Lower FPS cap if needed (--fps 60)")
    print("- Disable transparency (--no-transparent)")
    print("- Use smaller window size")
    print()
    print("Audio Settings:")
    print("- Use device with lowest latency")
    print("- Increase block size for stability (--block-size 2048)")
    print("- Use 44100 sample rate for compatibility")
    print()
    print("VoiceMeeter Settings:")
    print("- Enable 'Exclusive Mode'")
    print("- Use WDM drivers")
    print("- Adjust buffer size (try 512 or 1024)")
    print()

def troubleshooting_guide():
    """Troubleshooting guide"""
    print_header("🔧 Troubleshooting Guide")
    
    print("Common Issues and Solutions:")
    print()
    print("❌ 'No audio devices found':")
    print("   - Check audio drivers are installed")
    print("   - Restart Windows Audio service")
    print("   - Try different audio devices")
    print()
    print("❌ 'AudioRadar shows no blips':")
    print("   - Check audio is playing through VoiceMeeter")
    print("   - Verify correct device ID")
    print("   - Test with music/game audio")
    print("   - Check volume levels")
    print()
    print("❌ 'Only 2 blips instead of 7.1':")
    print("   - Enable 7.1 in game settings")
    print("   - Check VoiceMeeter is receiving 7.1 input")
    print("   - Verify audio source supports 7.1")
    print()
    print("❌ 'HUD not visible':")
    print("   - Check window is not minimized")
    print("   - Try --always-on-top flag")
    print("   - Check transparency settings")
    print("   - Verify correct monitor")
    print()
    print("❌ 'Poor performance/stuttering':")
    print("   - Lower FPS cap")
    print("   - Enable performance mode")
    print("   - Close other applications")
    print("   - Check CPU usage")
    print()
    print("❌ 'VoiceMeeter not found':")
    print("   - Download from vb-audio.com")
    print("   - Install VoiceMeeter Potato (not Basic)")
    print("   - Restart after installation")
    print()

def main():
    """Main entry point"""
    print_header("🎯 AudioRadar-HUD Setup Helper")
    
    print("Welcome to the AudioRadar setup helper!")
    print("This tool will guide you through setting up 7.1 audio routing.")
    print()
    print("Choose an option:")
    print("1. Quick Setup Guide (recommended)")
    print("2. Advanced Setup")
    print("3. Exit")
    print()
    
    choice = input("Select an option (1-3): ").strip()
    
    if choice == '1':
        if setup_guide():
            print("✅ Setup complete! You can now launch AudioRadar.")
        else:
            print("❌ Setup failed. Please try the advanced setup or troubleshooting guide.")
    elif choice == '2':
        advanced_setup()
    elif choice == '3':
        print("Goodbye!")
        return
    else:
        print("Invalid choice. Please try again.")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        import traceback
        traceback.print_exc()
