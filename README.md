# 🎯 Sonar - Advanced Audio Radar

> **Real-time 7.1 Surround Sound Visualizer for Tactical Gaming**

Sonar is a real-time audio radar HUD designed for competitive FPS gaming, particularly Rainbow Six Siege. It visualizes directional audio cues with dynamic colors, pulsing effects, and combat-style threat indicators.

![Sonar HUD](assets/sonar_preview.png)

## ✨ Features

### 🎨 Enhanced Visual System
- **Dynamic Color Changes**: Blips change color based on sound intensity (quiet blue → green → yellow → orange → red → white hot)
- **Pulsing Effects**: Visual elements pulse in sync with audio levels
- **Multi-Layer Glow**: Sophisticated glow effects for better visibility
- **Combat Threat Meter**: Real-time threat level indicator with color-coded alerts

### 🎮 Gaming-Optimized
- **Always-on-top**: Stays visible over all games
- **Transparent**: See through the HUD while maintaining visibility
- **Anti-cheat Safe**: Uses only audio input, no game memory access
- **Click-through**: Won't interfere with mouse input
- **Frameless**: Clean, minimal overlay

### 📡 Advanced Audio Processing
- **7.1 Surround Mapping**: Intelligent stereo-to-surround conversion
- **Enhanced Sensitivity**: Detects even subtle audio cues
- **VoiceMeeter Integration**: Works perfectly with VoiceMeeter Potato
- **Real-time Processing**: Low-latency audio capture and display

## 🚀 Quick Start

1. **Install VoiceMeeter Potato** (recommended for best results)
2. **Clone this repository**
   ```bash
   git clone https://github.com/oschouest/Sonar.git
   cd Sonar
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Launch Sonar**
   ```bash
   # Windows
   LAUNCH_RADAR.bat
   
   # Or manually
   python real_audio_tkinter_hud.py --device 38 --frameless --always-on-top --transparent
   ```

## 📋 Requirements

- Windows 10/11
- Python 3.7+
- VoiceMeeter Potato (recommended for 7.1 audio)
- Audio input permissions

## 🎯 Combat HUD Features

### Visual Indicators
- **Front Channels (FL/FR)**: Directional arrows showing sound direction
- **Center Channel (C)**: White crosshair for dialogue/important sounds  
- **Rear Channels (RL/RR)**: Rear position indicators
- **Bass (LFE)**: Animated wave rings for low-frequency sounds
- **Side Channels (SL/SR)**: Side position indicators

### Threat Assessment System
- 🔍 **SCANNING** - Quiet environment
- 👁️ **LOW THREAT** - Minimal audio activity
- ⚡ **MEDIUM THREAT** - Moderate audio levels
- ⚠️ **HIGH THREAT** - Significant audio activity
- 🚨 **CRITICAL THREAT** - Maximum audio intensity

## 🛠️ Technical Specifications

- **Audio Processing**: Real-time RMS calculation with smoothing
- **Update Rate**: 20 FPS for smooth visual feedback
- **Sensitivity**: Optimized for gaming audio (threshold: 0.005)
- **Latency**: < 50ms audio-to-visual delay
- **Memory Usage**: < 50MB RAM
- **Compatibility**: Windows DirectSound and WASAPI

## 🎮 Recommended Setup for Rainbow Six Siege

1. Install and configure VoiceMeeter Potato
2. Set VoiceMeeter as your default audio device
3. Route Siege audio through VoiceMeeter 
4. Launch Sonar with Device 38 (VoiceMeeter Out B1 Alt)
5. Position HUD in a corner for optimal visibility

## 🔧 Troubleshooting

### No Audio Detected
- Try option 2 (auto-detect) in the launcher
- Verify VoiceMeeter is running and routing audio
- Check Windows audio permissions
- Ensure microphone permissions are enabled

### HUD Not Staying on Top
- Close other overlay applications
- Run as administrator if needed
- Try different audio device options

## 📝 Controls

- **ESC**: Close the HUD
- **Mouse**: Click-through enabled (won't interfere with gameplay)

## 🏗️ Architecture

- `real_audio_tkinter_hud.py` - Main HUD application with enhanced visuals
- `audio_radar.py` - Core audio processing and 7.1 channel mapping
- `radar_gui.py` - Alternative Pygame-based HUD (backup)
- `LAUNCH_RADAR.bat` - Windows launcher with device selection

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**Anti-Cheat Compliance**: Sonar uses only audio input and does not access game memory, inject into game processes, or modify game files. It operates as an external audio visualization tool, similar to having enhanced headphones with a visual display.

---

*Designed for competitive gaming, accessibility, and tactical awareness.*
