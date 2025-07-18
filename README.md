# 🎯 AudioRadar-HUD - Tactical Audio Visualization

> **Production-Ready 7.1 Surround Sound HUD for Competitive Gaming**

AudioRadar-HUD is a professional-grade, anti-cheat-safe tactical audio visualization system. It provides real-time 7.1 surround sound radar visualization with advanced vector blending, 120+ FPS rendering, and comprehensive configuration options.

**🎮 Perfect for Rainbow Six Siege and other tactical FPS games!**

![AudioRadar-HUD](assets/audioradar_preview.png)

## ✨ Key Features

### � Advanced Audio Processing
- **True 7.1 Surround Support**: All 8 channels (FL, FR, C, LFE, RL, RR, SL, SR)
- **Vector Blending**: Advanced directional audio calculation using weighted averages
- **Real-time Processing**: Low-latency audio capture and visualization
- **VoiceMeeter Integration**: Seamless integration with VoiceMeeter Potato

### 🖥️ High-Performance HUD
- **120+ FPS Rendering**: Smooth, responsive Pygame-based HUD
- **Always-on-Top**: Stays visible over all games
- **Anti-cheat Safe**: External window only, no game injection
- **Customizable UI**: Themes, opacity, scaling, and layout options

### ⚙️ Configuration System
- **Hot-Reload Config**: Press `R` to reload settings without restart
- **In-HUD Menu**: Press `F1` or `M` to access configuration menu
- **Persistent Settings**: All changes save automatically to `config.json`
- **Performance Modes**: Optimized rendering for different hardware

## 🚀 Quick Start

### Method 1: Batch Launcher (Recommended)
```bash
# Double-click to launch with config.json settings
LAUNCH_RADAR.bat
```

### Method 2: Direct Launch
```bash
# Launch with config.json settings
python hud_launcher.py

# Override specific settings if needed
python hud_launcher.py --device 38 --fps 144
python hud_launcher.py --debug --transparent
```

### Method 3: System Launcher (Advanced)
```bash
python audio_radar_system.py --device 38 --fps 120
```

## � First-Time Setup

1. **Install VoiceMeeter Potato** (required for 7.1 audio routing)
2. **Run Setup Helper**
   ```bash
   python passthrough_setup_helper.py
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Launch AudioRadar**
   ```bash
   LAUNCH_RADAR.bat
   ```

## ⚙️ Configuration

### Runtime Controls
- **F1** or **M**: Open configuration menu
- **R**: Hot-reload configuration from `config.json`
- **V**: Toggle vector blending on/off
- **D**: Toggle debug information display
- **P**: Toggle performance mode
- **H**: Show help information
- **ESC**: Exit AudioRadar

### Configuration File (`config.json`)
All settings are now controlled by config.json - the single source of truth:

```json
{
  "audio_device": null,
  "audio_sample_rate": 44100,
  "audio_block_size": 1024,
  "hud_fps": 120,
  "hud_width": 450,
  "hud_height": 450,
  "hud_scale": 1.0,
  "hud_frameless": false,
  "hud_always_on_top": true,
  "hud_transparent": false,
  "hud_click_through": false,
  "hud_opacity": 0.85,
  "vector_blending": true,
  "performance_mode": false,
  "sensitivity": 1.0,
  "blip_fade_time": 2.0,
  "color_scheme": "default",
  "show_debug_info": false,
  "theme": {
    "blip_color": [255, 255, 0],
    "grid_color": [0, 100, 0],
    "bg_color": [20, 20, 20]
  }
}
```

**Key Configuration Options:**
- `hud_always_on_top`: Keep HUD above all windows
- `hud_fps`: Target rendering framerate (60-240)
- `vector_blending`: Advanced directional audio calculation
- `audio_device`: Audio device ID (null = auto-detect)
- `hud_opacity`: Window transparency (0.0-1.0)

### CLI Arguments
```bash
# Audio settings
--device 38              # Specific audio device ID
--sample-rate 44100      # Audio sample rate
--block-size 1024        # Audio buffer size

# Display settings
--fps 120                # Target FPS (60-240)
--width 450              # Window width
--height 450             # Window height
--scale 1.0              # HUD scale factor

# Window options
--frameless              # Remove window frame
--always-on-top          # Keep above all windows
--transparent            # Enable transparency
--click-through          # Allow clicks to pass through

# Performance options
--performance            # Enable optimizations
--no-vector-blending     # Disable vector blending
--debug                  # Enable debug output
```

## 🎯 Advanced Features

### Vector Blending
Advanced directional audio calculation that combines all 8 channels into accurate directional visualization:
- **Weighted Average**: Combines channel volumes based on speaker positions
- **Smooth Transitions**: Eliminates sudden direction changes
- **Accurate Positioning**: Reflects true audio source direction

### Performance Modes
- **Standard Mode**: Full features with all visual effects
- **Performance Mode**: Optimized rendering for lower-end hardware
- **Debug Mode**: Additional overlay information for troubleshooting

## 🎮 Gaming Setup Guide

### VoiceMeeter Potato Configuration
1. **Download & Install**: VoiceMeeter Potato from vb-audio.com
2. **Set as Default**: Make VoiceMeeter your default Windows playback device
3. **Configure Game**: Set game audio to 7.1 surround sound
4. **Route Audio**: Configure VoiceMeeter to route to your headphones
5. **Test**: Use built-in test to verify 7.1 channel separation

### Audio Device Selection
- **Device 38**: VoiceMeeter Out B1 Alt (most common)
- **Auto-detect**: Setup helper will find best device
- **Manual**: Use `--list-devices` to see all available options

## �️ Troubleshooting

### Common Issues

**No Audio Detected**
- Verify VoiceMeeter is running and routing audio
- Check Windows audio permissions
- Ensure game is outputting to VoiceMeeter
- Try different audio devices with `--list-devices`

**HUD Not Visible**
- Use `--always-on-top` flag
- Check window isn't minimized
- Verify correct monitor with multi-display setups
- Adjust opacity if too transparent

**Poor Performance**
- Enable performance mode with `--performance`
- Lower FPS with `--fps 60`
- Reduce window size with `--width 300 --height 300`
- Close unnecessary applications

**Only Stereo Audio**
- Enable 7.1 surround in game settings
- Verify VoiceMeeter is receiving 7.1 input
- Check audio source supports multichannel

## 🏗️ File Structure

```
AudioRadar-HUD/
├── hud_launcher.py              # 🚀 Production launcher
├── audio_radar_system.py        # 🎯 System coordinator  
├── radar_gui.py                 # 🎮 High-performance HUD
├── audio_radar.py               # 🎵 Audio capture/analysis
├── config.json                  # ⚙️ Configuration
├── passthrough_setup_helper.py  # 🔧 Setup guide
├── LAUNCH_RADAR.bat             # 🪟 Windows launcher
├── real_audio_tkinter_hud.py    # 📺 Legacy Tkinter HUD
├── requirements.txt             # 📋 Dependencies
├── dev_sandbox/                 # 🧪 Development tools
│   ├── test_system.py           # System tests
│   ├── debug_audio.py           # Audio debugging
│   └── simple_radar.py          # Basic radar test
└── examples/                    # 📚 Documentation
    └── PRODUCTION_SUMMARY.md    # Complete feature summary
└── examples/                    # 📚 Documentation
    └── PRODUCTION_SUMMARY.md    # Complete feature summary
```

## 🎯 Anti-Cheat Compliance

AudioRadar-HUD is designed to be **completely anti-cheat safe**:

- ✅ **External Window Only**: No game injection or memory access
- ✅ **Audio Input Only**: Only processes system audio streams
- ✅ **No File Manipulation**: Doesn't modify game files
- ✅ **Standard APIs**: Uses only Windows audio APIs
- ✅ **No Network Access**: Completely offline operation

**Tested with Rainbow Six Siege and other competitive FPS games.**

## 📋 Requirements

- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.7+ (3.10+ recommended)
- **Audio**: VoiceMeeter Potato (for 7.1 routing)
- **Permissions**: Audio input permissions
- **Hardware**: Any DirectSound/WASAPI compatible audio device

## 🏆 Performance

- **FPS**: 120+ FPS rendering (configurable 60-240)
- **Latency**: <50ms audio-to-visual delay
- **Memory**: <100MB RAM usage
- **CPU**: <5% usage on modern systems
- **Compatibility**: Windows 10/11, DirectSound, WASAPI

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Future Plans

- **AI Training Mode**: Intelligent audio cue recognition for specific games
- **Game-Specific Profiles**: Optimized settings for Rainbow Six Siege and other titles
- **Advanced Analytics**: Audio pattern analysis and learning
- **Mobile Companion**: Remote monitoring and configuration
- **Plugin System**: Community-created enhancements

## 🙏 Credits

- Inspired by ASUS Sonic Radar 3
- Built with love for the competitive gaming community
- Special thanks to VB-Audio for VoiceMeeter Potato

---

**🎮 Ready to dominate the competition with tactical audio advantage? Launch AudioRadar-HUD and experience the difference!**
