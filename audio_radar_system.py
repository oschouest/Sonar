#!/usr/bin/env python3
"""
Audio Radar System - Ties together audio capture and HUD logic
Sonar compliance: Combines audio + HUD with anti-cheat safety
"""

import sys
import os
import threading
import time
import json
import logging
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_radar import AudioRadar
from radar_gui import AudioRadarHUD

@dataclass
class SystemConfig:
    """System configuration settings"""
    audio_device: Optional[int] = None
    audio_sample_rate: int = 44100
    audio_block_size: int = 1024
    hud_fps: int = 120
    hud_width: int = 450
    hud_height: int = 450
    hud_scale: float = 1.0
    hud_frameless: bool = False
    hud_always_on_top: bool = True
    hud_transparent: bool = False
    hud_click_through: bool = False
    hud_opacity: float = 0.85
    enable_logging: bool = False
    log_level: str = "INFO"
    performance_mode: bool = False
    vector_blending: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'audio_device': self.audio_device,
            'audio_sample_rate': self.audio_sample_rate,
            'audio_block_size': self.audio_block_size,
            'hud_fps': self.hud_fps,
            'hud_width': self.hud_width,
            'hud_height': self.hud_height,
            'hud_scale': self.hud_scale,
            'hud_frameless': self.hud_frameless,
            'hud_always_on_top': self.hud_always_on_top,
            'hud_transparent': self.hud_transparent,
            'hud_click_through': self.hud_click_through,
            'hud_opacity': self.hud_opacity,
            'enable_logging': self.enable_logging,
            'log_level': self.log_level,
            'performance_mode': self.performance_mode,
            'vector_blending': self.vector_blending
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SystemConfig':
        """Create from dictionary"""
        return cls(**data)


class AudioRadarSystem:
    """
    Main system class that coordinates audio capture and HUD display
    
    Sonar compliance:
    - Anti-cheat safe (external window only)
    - 100+ FPS capable
    - Vector blending for directional audio
    - Config.json support with hot-reload
    - All 8 channels (7.1 surround)
    """
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = SystemConfig()
        self.audio_radar = None
        self.radar_gui = None
        self.running = False
        self.audio_thread = None
        self.hud_thread = None
        self.logger = None
        
        # Thread synchronization
        self.audio_lock = threading.Lock()
        self.volume_data = {}
        
        # Performance tracking
        self.stats = {
            'audio_fps': 0,
            'hud_fps': 0,
            'audio_drops': 0,
            'hud_drops': 0,
            'last_audio_time': 0,
            'last_hud_time': 0
        }
        
        # Load configuration
        self._load_config()
        
        # Setup logging
        if self.config.enable_logging:
            self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging system"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('audio_radar_system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AudioRadarSystem')
        self.logger.info("Logging initialized")
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.config = SystemConfig.from_dict(data)
                    if self.logger:
                        self.logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self._save_config()
                if self.logger:
                    self.logger.info(f"Created default configuration at {self.config_path}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to load config: {e}")
            print(f"⚠️ Config load failed: {e}")
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2)
            if self.logger:
                self.logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save config: {e}")
            print(f"⚠️ Config save failed: {e}")
    
    def reload_config(self):
        """Hot-reload configuration"""
        old_config = self.config
        self._load_config()
        
        # Apply changes that can be changed on-the-fly
        if self.radar_gui:
            self.radar_gui.fps_cap = self.config.hud_fps
            self.radar_gui.use_vector_blending = self.config.vector_blending
            self.radar_gui.performance_mode = self.config.performance_mode
            self.radar_gui.hud_opacity = self.config.hud_opacity
            
            # Update GUI config
            self.radar_gui.config.update({
                'fps_cap': self.config.hud_fps,
                'vector_blending': self.config.vector_blending,
                'performance_mode': self.config.performance_mode,
                'hud_opacity': self.config.hud_opacity
            })
        
        if self.logger:
            self.logger.info("Configuration reloaded")
        
        return True
    
    def initialize_audio(self) -> bool:
        """Initialize audio capture system"""
        try:
            def audio_callback(volumes):
                """Audio callback with thread safety"""
                with self.audio_lock:
                    self.volume_data = volumes.copy()
                    self.stats['last_audio_time'] = time.time()
                
                # Update GUI if available
                if self.radar_gui:
                    self.radar_gui.update_volumes(volumes)
            
            self.audio_radar = AudioRadar(
                device=self.config.audio_device,
                sample_rate=self.config.audio_sample_rate,
                block_size=self.config.audio_block_size,
                volume_callback=audio_callback
            )
            
            if self.logger:
                self.logger.info("Audio system initialized")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Audio initialization failed: {e}")
            print(f"❌ Audio init failed: {e}")
            return False
    
    def initialize_hud(self) -> bool:
        """Initialize HUD system"""
        try:
            self.radar_gui = AudioRadarHUD(
                window_size=(self.config.hud_width, self.config.hud_height),
                fps_cap=self.config.hud_fps,
                scale_factor=self.config.hud_scale,
                frameless=self.config.hud_frameless,
                always_on_top=self.config.hud_always_on_top,
                transparent_bg=self.config.hud_transparent,
                click_through=self.config.hud_click_through,
                hud_opacity=self.config.hud_opacity
            )
            
            # Configure HUD options
            self.radar_gui.use_vector_blending = self.config.vector_blending
            self.radar_gui.performance_mode = self.config.performance_mode
            
            # Set system callbacks
            self.radar_gui.on_config_change = self._on_config_change
            self.radar_gui.on_reload_config = self.reload_config
            
            if self.logger:
                self.logger.info("HUD system initialized")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"HUD initialization failed: {e}")
            print(f"❌ HUD init failed: {e}")
            return False
    
    def _on_config_change(self, key: str, value):
        """Handle configuration changes from HUD"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self._save_config()
            
            if self.logger:
                self.logger.info(f"Config changed: {key} = {value}")
    
    def start(self) -> bool:
        """Start the audio radar system"""
        if self.running:
            return False
        
        print("🎯 Starting AudioRadar System...")
        
        # Initialize audio
        if not self.initialize_audio():
            print("⚠️ Audio initialization failed - continuing in demo mode")
        
        # Initialize HUD
        if not self.initialize_hud():
            print("❌ HUD initialization failed")
            return False
        
        # Start audio capture
        if self.audio_radar:
            try:
                self.audio_radar.start()
                print("✅ Audio capture started")
            except Exception as e:
                print(f"⚠️ Audio start failed: {e}")
        
        # Start HUD in main thread
        self.running = True
        
        try:
            print("🎮 Starting HUD...")
            print()
            print("📋 System Controls:")
            print("   F1/M: Configuration menu")
            print("   R: Hot-reload config")
            print("   V: Toggle vector blending")
            print("   D: Debug/stats info")
            print("   P: Performance mode")
            print("   H: Help")
            print("   ESC: Quit")
            print()
            print("🎯 AudioRadar System is now running!")
            
            # Run HUD main loop
            self.radar_gui.run()
            
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        except Exception as e:
            if self.logger:
                self.logger.error(f"System runtime error: {e}")
            print(f"❌ System error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Stop the audio radar system"""
        if not self.running:
            return
        
        print("🛑 Stopping AudioRadar System...")
        self.running = False
        
        # Stop audio capture
        if self.audio_radar:
            try:
                self.audio_radar.stop()
                print("✅ Audio capture stopped")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Audio stop error: {e}")
        
        # Save configuration
        try:
            self._save_config()
            print("✅ Configuration saved")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Config save error: {e}")
        
        if self.logger:
            self.logger.info("AudioRadar System stopped")
        
        print("✅ System stopped")
    
    def get_stats(self) -> Dict:
        """Get system performance statistics"""
        with self.audio_lock:
            return {
                'running': self.running,
                'audio_active': self.audio_radar is not None and self.audio_radar.is_running(),
                'hud_active': self.radar_gui is not None,
                'audio_device': self.config.audio_device,
                'hud_fps': self.config.hud_fps,
                'vector_blending': self.config.vector_blending,
                'performance_mode': self.config.performance_mode,
                'last_audio_time': self.stats['last_audio_time'],
                'volume_data': self.volume_data.copy()
            }
    
    def list_audio_devices(self) -> List[Dict]:
        """List available audio devices"""
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
            if self.logger:
                self.logger.error(f"Device list error: {e}")
        
        return devices


def main():
    """Main entry point for direct execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AudioRadar System')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--list-devices', action='store_true', help='List audio devices')
    parser.add_argument('--device', type=int, help='Audio device ID')
    parser.add_argument('--fps', type=int, help='Target FPS')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Create system
    system = AudioRadarSystem(args.config)
    
    # Override config with command line args
    if args.device is not None:
        system.config.audio_device = args.device
    if args.fps is not None:
        system.config.hud_fps = args.fps
    if args.debug:
        system.config.enable_logging = True
        system.config.log_level = "DEBUG"
        system._setup_logging()
    
    # List devices if requested
    if args.list_devices:
        devices = system.list_audio_devices()
        print("🎵 Available Audio Devices:")
        print("=" * 50)
        for device in devices:
            print(f"  {device['id']:2d}: {device['name']}")
            print(f"      Channels: {device['channels']}")
            print(f"      Sample Rate: {device['sample_rate']}")
            print()
        return 0
    
    # Start system
    try:
        system.start()
        return 0
    except Exception as e:
        print(f"❌ System failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
