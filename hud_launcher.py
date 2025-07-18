#!/usr/bin/env python3
"""
HUD Launcher - Production entry point for AudioRadar-HUD
Sonar compliance: Launch entry point for production
"""

import sys
import os
import argparse
import threading
import time
from typing import Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_radar import AudioRadar
from radar_gui import AudioRadarHUD

class HUDLauncher:
    """Production launcher for AudioRadar-HUD system"""
    
    def __init__(self):
        self.audio_radar = None
        self.radar_gui = None
        self.running = False
        
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='AudioRadar-HUD - Tactical Audio Visualization',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python hud_launcher.py                    # Launch with defaults
  python hud_launcher.py --device 38        # Use specific audio device
  python hud_launcher.py --fps 144          # Set custom FPS
  python hud_launcher.py --frameless        # Remove window frame
  python hud_launcher.py --always-on-top    # Force always on top
  python hud_launcher.py --transparent      # Enable transparency
  python hud_launcher.py --debug            # Enable debug output
  
🎯 Sonar Instructions Compliance:
  - Anti-cheat safe (external window only)
  - 100+ FPS capable
  - Vector blending for directional audio
  - Config.json support with hot-reload
  - In-HUD menu (F1/M key)
  - Real-time 7.1 audio visualization
            """
        )
        
        # Audio settings
        parser.add_argument('--device', type=int, 
                          help='Audio device ID to use (use debug_audio.py to list)')
        parser.add_argument('--sample-rate', type=int, default=44100,
                          help='Audio sample rate (default: 44100)')
        parser.add_argument('--block-size', type=int, default=1024,
                          help='Audio block size (default: 1024)')
        
        # Display settings
        parser.add_argument('--fps', type=int, default=120,
                          help='Target FPS (default: 120, min: 60, max: 240)')
        parser.add_argument('--width', type=int, default=450,
                          help='Window width (default: 450)')
        parser.add_argument('--height', type=int, default=450,
                          help='Window height (default: 450)')
        parser.add_argument('--scale', type=float, default=1.0,
                          help='Radar scale factor (default: 1.0)')
        
        # Window options
        parser.add_argument('--frameless', action='store_true',
                          help='Remove window frame and title bar')
        parser.add_argument('--always-on-top', action='store_true',
                          help='Keep window above all others')
        parser.add_argument('--transparent', action='store_true',
                          help='Enable transparent background')
        parser.add_argument('--click-through', action='store_true',
                          help='Allow clicks to pass through window')
        parser.add_argument('--opacity', type=float, default=0.85,
                          help='Window opacity (0.0-1.0, default: 0.85)')
        
        # Performance options
        parser.add_argument('--performance', action='store_true',
                          help='Enable performance optimizations')
        parser.add_argument('--no-vector-blending', action='store_true',
                          help='Disable vector blending (use individual channel blips)')
        
        # Debug options
        parser.add_argument('--debug', action='store_true',
                          help='Enable debug output')
        parser.add_argument('--list-devices', action='store_true',
                          help='List available audio devices and exit')
        
        return parser.parse_args()
    
    def list_audio_devices(self):
        """List available audio devices"""
        print("🎵 Available Audio Devices:")
        print("=" * 50)
        
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            
            for i, device in enumerate(devices):
                device_type = "INPUT" if device['max_input_channels'] > 0 else "OUTPUT"
                if device['max_input_channels'] > 0:
                    print(f"  {i:2d}: {device['name']}")
                    print(f"      Type: {device_type}")
                    print(f"      Channels: {device['max_input_channels']}")
                    print(f"      Sample Rate: {device['default_samplerate']}")
                    print()
        except Exception as e:
            print(f"❌ Error listing devices: {e}")
    
    def launch(self, args):
        """Launch the HUD system"""
        print("🎯 AudioRadar-HUD Launcher")
        print("=" * 40)
        print(f"📊 Target FPS: {args.fps}")
        print(f"🎵 Audio Device: {args.device if args.device else 'Auto-detect'}")
        print(f"📐 Window Size: {args.width}x{args.height}")
        print(f"🎨 Frameless: {args.frameless}")
        print(f"⬆️ Always On Top: {args.always_on_top}")
        print(f"👻 Transparent: {args.transparent}")
        print(f"🎯 Vector Blending: {not args.no_vector_blending}")
        print()
        
        # Validate FPS
        fps = max(60, min(240, args.fps))
        if fps != args.fps:
            print(f"⚠️ FPS adjusted to {fps} (valid range: 60-240)")
        
        # Initialize GUI
        try:
            self.radar_gui = AudioRadarHUD(
                window_size=(args.width, args.height),
                fps_cap=fps,
                scale_factor=args.scale,
                frameless=args.frameless,
                always_on_top=args.always_on_top,
                transparent_bg=args.transparent,
                click_through=args.click_through,
                hud_opacity=args.opacity
            )
            
            # Configure vector blending
            if args.no_vector_blending:
                self.radar_gui.use_vector_blending = False
                self.radar_gui.config['vector_blending'] = False
            
            # Configure performance mode
            if args.performance:
                self.radar_gui.performance_mode = True
                print("🚀 Performance mode enabled")
            
            print("✅ GUI initialized")
            
        except Exception as e:
            print(f"❌ GUI initialization failed: {e}")
            return False
        
        # Initialize audio
        try:
            def audio_callback(volumes):
                """Audio callback to update GUI"""
                if self.radar_gui:
                    self.radar_gui.update_volumes(volumes)
            
            self.audio_radar = AudioRadar(
                device=args.device,
                sample_rate=args.sample_rate,
                block_size=args.block_size,
                volume_callback=audio_callback
            )
            
            self.audio_radar.start()
            print("✅ Audio capture started")
            
        except Exception as e:
            print(f"❌ Audio initialization failed: {e}")
            print("⚠️ Continuing without audio (demo mode)")
        
        # Start GUI
        self.running = True
        
        try:
            print("🎮 Starting HUD...")
            print()
            print("📋 Controls:")
            print("   F1/M: Configuration menu")
            print("   R: Hot-reload config")
            print("   V: Toggle vector blending")
            print("   D: Debug info")
            print("   H: Help")
            print("   ESC: Quit")
            print()
            print("🎯 HUD is now running!")
            
            # Run the GUI main loop
            self.radar_gui.run()
            
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        except Exception as e:
            print(f"❌ HUD runtime error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
        
        return True
    
    def cleanup(self):
        """Clean up resources"""
        print("🛑 Shutting down...")
        self.running = False
        
        if self.audio_radar:
            try:
                self.audio_radar.stop()
                print("✅ Audio capture stopped")
            except:
                pass
        
        if self.radar_gui:
            try:
                # Save config on exit
                self.radar_gui._save_config()
                print("✅ Configuration saved")
            except:
                pass
        
        print("✅ Cleanup complete")


def main():
    """Main entry point"""
    launcher = HUDLauncher()
    args = launcher.parse_arguments()
    
    if args.list_devices:
        launcher.list_audio_devices()
        return 0
    
    success = launcher.launch(args)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
