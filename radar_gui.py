"""
Standalone Pygame Audio Radar HUD
A high-performance, frameless, always-on-top radar that displays 7.1 surround sound audio data
as a circular radar/compass interface. Anti-cheat compatible.
"""

import pygame
import math
import threading
import queue
import time
import sys
import os
from typing import Dict, Optional, Tuple
from collections import deque
import json

# Windows-specific imports for window management
if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes
        import ctypes.wintypes
        HAS_WIN32 = True
    except ImportError:
        HAS_WIN32 = False
        print("Warning: Windows API not available. Some features may be limited.")
else:
    HAS_WIN32 = False


class AudioRadarHUD:
    """
    High-performance, frameless, always-on-top audio radar HUD.
    Displays 7.1 audio channels as a circular compass with directional blips.
    """
    
    # Channel positions in degrees (0° = North/Front)
    CHANNEL_POSITIONS = {
        "FL": 315,   # Front Left (NW)
        "C": 0,      # Center (N)
        "FR": 45,    # Front Right (NE)
        "SR": 90,    # Side Right (E)
        "RR": 135,   # Rear Right (SE)
        "LFE": 180,  # LFE/Sub (S) - center bottom
        "RL": 225,   # Rear Left (SW)
        "SL": 270    # Side Left (W)
    }
    
    # Color schemes
    COLOR_SCHEMES = {
        "dark": {
            "background": (20, 20, 30),
            "grid": (60, 60, 80),
            "text": (200, 200, 220),
            "center": (40, 40, 60),
            "blip_low": (0, 255, 100),
            "blip_med": (255, 255, 0),
            "blip_high": (255, 100, 100)
        },
        "light": {
            "background": (240, 240, 250),
            "grid": (180, 180, 200),
            "text": (40, 40, 60),
            "center": (220, 220, 240),
            "blip_low": (0, 150, 50),
            "blip_med": (200, 150, 0),
            "blip_high": (200, 50, 50)
        }
    }
    
    def __init__(self, 
                 window_size: Tuple[int, int] = (400, 400),
                 fps_cap: int = 120,
                 fade_time: float = 2.0,
                 scale_factor: float = 1.0,
                 theme: str = "dark",
                 frameless: bool = True,
                 always_on_top: bool = True,
                 transparent_bg: bool = False,
                 click_through: bool = False,
                 hud_opacity: float = 0.8):
        """
        Initialize the Audio Radar HUD.
        
        Args:
            window_size: (width, height) of the window
            fps_cap: Maximum FPS for the display (default 120 for Sonar compliance)
            fade_time: Time in seconds for blips to fade out
            scale_factor: Scale multiplier for the radar size
            theme: Color theme ("dark" or "light")
            frameless: Remove window borders and title bar
            always_on_top: Keep window above all others
            transparent_bg: Use transparent background (Windows only)
            click_through: Allow clicks to pass through (Windows only)
            hud_opacity: Overall HUD opacity (0.0-1.0)
        """
        # HUD settings
        self.frameless = frameless
        self.always_on_top = always_on_top
        self.transparent_bg = transparent_bg and HAS_WIN32
        self.click_through = click_through and HAS_WIN32
        self.hud_opacity = max(0.1, min(1.0, hud_opacity))
        
        # Initialize Pygame
        pygame.init()
        pygame.mixer.quit()  # Disable audio to avoid conflicts
        
        # Set environment variable for frameless window
        if self.frameless:
            os.environ['SDL_WINDOWID'] = ''
            os.environ['SDL_VIDEO_WINDOW_POS'] = 'centered'
        
        # Window settings
        self.window_size = window_size
        self.center = (window_size[0] // 2, window_size[1] // 2)
        self.fps_cap = fps_cap
        self.fade_time = fade_time
        self.scale_factor = scale_factor
        self.theme = theme
        
        # Calculate radar dimensions
        self.radar_radius = min(window_size) // 2 - 30  # Smaller margins for HUD
        self.radar_radius = int(self.radar_radius * scale_factor)
        
        # Pygame setup with appropriate flags
        pygame_flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        if self.frameless:
            pygame_flags |= pygame.NOFRAME
        if self.transparent_bg:
            pygame_flags |= pygame.SRCALPHA
            
        self.screen = pygame.display.set_mode(window_size, pygame_flags)
        pygame.display.set_caption("AudioRadar-HUD - Always-On-Top")
        
        # High performance settings
        pygame.event.set_blocked([pygame.MOUSEMOTION, pygame.JOYAXISMOTION, 
                                pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP])
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)  # Smaller font for HUD
        self.small_font = pygame.font.Font(None, 16)
        
        # Initialize Windows-specific features
        self.hwnd = None
        self.topmost_running = False  # Flag for aggressive topmost thread
        if HAS_WIN32:
            self._setup_windows_features()
        
        # Colors with opacity support
        self.colors = self._get_colors_with_opacity()
        
        # Load configuration
        self.config = self._load_config()
        
        # Menu system
        self.menu_visible = False
        self.menu_items = [
            "Sensitivity",
            "Fade Time", 
            "Blip Size",
            "FPS Limit",
            "Vector Blending",
            "Save Config",
            "Exit"
        ]
        self.menu_selected = 0
        
        # Vector blending for directional audio
        self.use_vector_blending = self.config.get('vector_blending', True)
        self.composite_blip = {'angle': 0, 'intensity': 0, 'active': False}
        
        # Audio data management
        self.volume_queue = queue.Queue(maxsize=200)  # Larger queue for high FPS
        self.current_volumes = {ch: 0.0 for ch in self.CHANNEL_POSITIONS.keys()}
        self.volume_history = {ch: deque(maxlen=int(fps_cap * fade_time)) 
                              for ch in self.CHANNEL_POSITIONS.keys()}
        
        # Control flags
        self.running = True
        self.show_debug = False
        self.auto_scale = True
        self.max_volume_seen = 0.1  # For auto-scaling
        self.show_help = False
        
        # Performance tracking
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.current_fps = 0
        self.performance_mode = True  # Optimize for speed
        
        # Position tracking for dragging (when not click-through)
        self.dragging = False
        self.drag_offset = (0, 0)
        
    def _setup_windows_features(self):
        """Setup Windows-specific features with aggressive always-on-top."""
        try:
            # Give pygame time to create the window
            pygame.display.flip()
            time.sleep(0.1)  # Brief delay to ensure window is created
            
            # Get window handle using pygame
            wm_info = pygame.display.get_wm_info()
            if 'window' in wm_info:
                self.hwnd = wm_info['window']
                print(f"✅ Got window handle: {self.hwnd}")
            else:
                print("❌ No window handle in wm_info")
                return
                
            # Check if force_topmost is enabled in config
            force_topmost = self.config.get('force_topmost', True)
            
            if self.always_on_top and force_topmost:
                self._setup_aggressive_topmost()
            elif self.always_on_top:
                self._setup_basic_topmost()
            
            # Setup transparency if requested
            if self.transparent_bg or self.click_through:
                self._setup_transparency()
                
        except Exception as e:
            print(f"❌ Windows features setup failed: {e}")
            
    def _setup_aggressive_topmost(self):
        """Setup aggressive always-on-top with persistent thread."""
        try:
            # Windows API constants
            HWND_TOPMOST = -1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOACTIVATE = 0x0010
            
            # Initial topmost call
            result = ctypes.windll.user32.SetWindowPos(
                self.hwnd, HWND_TOPMOST, 0, 0, 0, 0, 
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            )
            
            if result:
                print("✅ Initial SetWindowPos successful")
            else:
                error_code = ctypes.windll.kernel32.GetLastError()
                print(f"❌ Initial SetWindowPos failed - Error: {error_code}")
            
            # Steal focus once with SetForegroundWindow
            focus_result = ctypes.windll.user32.SetForegroundWindow(self.hwnd)
            if focus_result:
                print("✅ SetForegroundWindow successful - Focus stolen")
            else:
                error_code = ctypes.windll.kernel32.GetLastError()
                print(f"⚠️ SetForegroundWindow failed - Error: {error_code}")
            
            # Start persistent topmost thread
            self.topmost_running = True
            self.topmost_thread = threading.Thread(target=self._aggressive_topmost_thread, daemon=True)
            self.topmost_thread.start()
            print("✅ Aggressive topmost thread started")
            
        except Exception as e:
            print(f"❌ Aggressive topmost setup failed: {e}")
            
    def _aggressive_topmost_thread(self):
        """Persistent thread that enforces always-on-top every 500ms."""
        HWND_TOPMOST = -1
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOACTIVATE = 0x0010
        
        while self.topmost_running:
            try:
                if self.hwnd:
                    result = ctypes.windll.user32.SetWindowPos(
                        self.hwnd, HWND_TOPMOST, 0, 0, 0, 0, 
                        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
                    )
                    
                    if not result:
                        error_code = ctypes.windll.kernel32.GetLastError()
                        print(f"⚠️ Topmost refresh failed - Error: {error_code}")
                        
                time.sleep(0.5)  # Wait 500ms before next enforcement
                
            except Exception as e:
                print(f"❌ Topmost thread error: {e}")
                time.sleep(1.0)  # Wait longer on error
                
    def _setup_basic_topmost(self):
        """Setup basic always-on-top (single call)."""
        try:
            HWND_TOPMOST = -1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            
            result = ctypes.windll.user32.SetWindowPos(
                self.hwnd, HWND_TOPMOST, 0, 0, 0, 0, 
                SWP_NOMOVE | SWP_NOSIZE
            )
            
            if result:
                print("✅ Basic always-on-top: ENABLED")
            else:
                error_code = ctypes.windll.kernel32.GetLastError()
                print(f"❌ Basic SetWindowPos failed - Error: {error_code}")
                
        except Exception as e:
            print(f"❌ Basic topmost setup failed: {e}")
            
    def _setup_transparency(self):
        """Setup window transparency and click-through."""
        try:
            if not self.hwnd:
                return
                
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x80000
            WS_EX_TRANSPARENT = 0x20
            
            current_style = ctypes.windll.user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
            new_style = current_style | WS_EX_LAYERED
            
            if self.click_through:
                new_style |= WS_EX_TRANSPARENT
            
            ctypes.windll.user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, new_style)
            
            if self.transparent_bg:
                # Set transparency
                ctypes.windll.user32.SetLayeredWindowAttributes(
                    self.hwnd, 0, int(255 * self.hud_opacity), 0x02
                )
            print("✅ Transparency applied")
            
        except Exception as e:
            print(f"❌ Transparency setup failed: {e}")
            print("⚠️ Continuing without Windows-specific features")
            import traceback
            traceback.print_exc()
    
    def _load_config(self):
        """Load configuration from config.json (Sonar compliance)"""
        default_config = {
            "sensitivity": 1.0,
            "fade_time": 0.5,
            "blip_size_multiplier": 1.0,
            "fps_limit": 120,
            "vector_blending": True,
            "show_individual_channels": True,
            "show_direction_line": True,
            "auto_scale": True,
            "theme": "dark",
            "force_topmost": True
        }
        
        config_path = "config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    print("✅ Configuration loaded from config.json")
                    return config
            except Exception as e:
                print(f"⚠️ Config load error: {e}")
        else:
            print("📄 Creating default config.json")
            self._save_config(default_config)
        
        return default_config
    
    def _save_config(self, config=None):
        """Save configuration to config.json (Sonar compliance)"""
        if config is None:
            config = self.config
        
        try:
            with open("config.json", 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Configuration saved to config.json")
        except Exception as e:
            print(f"❌ Config save error: {e}")
    
    def _calculate_composite_direction(self):
        """Calculate weighted composite direction from all channels (Vector Blending)"""
        if not self.use_vector_blending:
            return
        
        total_weight = 0
        weighted_x = 0
        weighted_y = 0
        
        sensitivity = self.config.get('sensitivity', 1.0)
        
        for channel, angle in self.CHANNEL_POSITIONS.items():
            if channel == "LFE":  # Skip LFE for directional calculation
                continue
                
            volume = self.current_volumes.get(channel, 0) * sensitivity
            if volume > 0.01:  # Threshold for significant audio
                angle_rad = math.radians(angle)
                
                # Weight by volume squared for better sensitivity
                weight = volume * volume
                
                # Convert to unit vector and add to composite
                weighted_x += math.cos(angle_rad) * weight
                weighted_y += math.sin(angle_rad) * weight
                total_weight += weight
        
        if total_weight > 0:
            # Calculate final direction and intensity
            final_angle = math.atan2(weighted_y, weighted_x)
            final_intensity = min(math.sqrt(weighted_x**2 + weighted_y**2), 1.0)
            
            self.composite_blip = {
                'angle': math.degrees(final_angle),
                'intensity': final_intensity,
                'active': True
            }
        else:
            self.composite_blip['active'] = False
    
    def _handle_menu_navigation(self, key):
        """Handle menu navigation keys (Sonar compliance)"""
        if key == pygame.K_UP:
            self.menu_selected = (self.menu_selected - 1) % len(self.menu_items)
        elif key == pygame.K_DOWN:
            self.menu_selected = (self.menu_selected + 1) % len(self.menu_items)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            self._handle_menu_selection()
        elif key == pygame.K_LEFT:
            self._adjust_menu_value(-1)
        elif key == pygame.K_RIGHT:
            self._adjust_menu_value(1)
    
    def _adjust_menu_value(self, direction):
        """Adjust the value of the selected menu item"""
        selected_item = self.menu_items[self.menu_selected]
        
        if selected_item == "Sensitivity":
            current = self.config.get('sensitivity', 1.0)
            self.config['sensitivity'] = max(0.1, min(5.0, current + direction * 0.1))
        elif selected_item == "Fade Time":
            current = self.config.get('fade_time', 0.5)
            self.config['fade_time'] = max(0.1, min(2.0, current + direction * 0.1))
        elif selected_item == "Blip Size":
            current = self.config.get('blip_size_multiplier', 1.0)
            self.config['blip_size_multiplier'] = max(0.5, min(3.0, current + direction * 0.1))
        elif selected_item == "FPS Limit":
            current = self.config.get('fps_limit', 120)
            self.config['fps_limit'] = max(60, min(240, current + direction * 10))
            self.fps_cap = self.config['fps_limit']
        elif selected_item == "Vector Blending":
            self.use_vector_blending = not self.use_vector_blending
            self.config['vector_blending'] = self.use_vector_blending
    
    def _handle_menu_selection(self):
        """Handle menu item selection"""
        selected_item = self.menu_items[self.menu_selected]
        
        if selected_item == "Save Config":
            self._save_config()
        elif selected_item == "Exit":
            self.running = False
        elif selected_item == "Vector Blending":
            self.use_vector_blending = not self.use_vector_blending
            self.config['vector_blending'] = self.use_vector_blending
    
    def _draw_menu(self):
        """Draw the configuration menu (Sonar compliance)"""
        if not self.menu_visible:
            return
        
        # Menu background
        menu_width = 280
        menu_height = len(self.menu_items) * 35 + 60
        menu_x = (self.window_size[0] - menu_width) // 2
        menu_y = (self.window_size[1] - menu_height) // 2
        
        # Semi-transparent background
        menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        menu_surface.fill((0, 0, 0, 180))
        self.screen.blit(menu_surface, (menu_x, menu_y))
        
        # Menu border
        pygame.draw.rect(self.screen, (0, 255, 0), (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Menu title
        title_text = self.font.render("🎯 RADAR CONFIG", True, (0, 255, 255))
        title_rect = title_text.get_rect(centerx=menu_x + menu_width//2, y=menu_y + 15)
        self.screen.blit(title_text, title_rect)
        
        # Menu items
        for i, item in enumerate(self.menu_items):
            item_y = menu_y + 50 + i * 35
            color = (255, 255, 0) if i == self.menu_selected else (255, 255, 255)
            
            # Get current value for some items
            if item == "Sensitivity":
                display_text = f"{item}: {self.config.get('sensitivity', 1.0):.1f}"
            elif item == "Fade Time":
                display_text = f"{item}: {self.config.get('fade_time', 0.5):.1f}s"
            elif item == "Blip Size":
                display_text = f"{item}: {self.config.get('blip_size_multiplier', 1.0):.1f}x"
            elif item == "FPS Limit":
                display_text = f"{item}: {self.config.get('fps_limit', 120)}"
            elif item == "Vector Blending":
                status = "ON" if self.config.get('vector_blending', True) else "OFF"
                display_text = f"{item}: {status}"
            else:
                display_text = item
            
            item_text = self.small_font.render(display_text, True, color)
            item_rect = item_text.get_rect(centerx=menu_x + menu_width//2, y=item_y)
            self.screen.blit(item_text, item_rect)
        
        # Instructions
        instructions = [
            "↑↓ Navigate  ←→ Adjust  Enter/Space Select",
            "F1/M Toggle Menu  R Hot-reload Config",
            "ESC Close Menu"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = self.small_font.render(instruction, True, (128, 128, 128))
            inst_rect = inst_text.get_rect(centerx=menu_x + menu_width//2, 
                                         y=menu_y + menu_height - 45 + i * 15)
            self.screen.blit(inst_text, inst_rect)
    
    def _draw_composite_blip(self):
        """Draw the composite directional blip (Vector Blending)"""
        if not self.use_vector_blending or not self.composite_blip['active']:
            return
        
        angle = self.composite_blip['angle']
        intensity = self.composite_blip['intensity']
        
        # Convert angle to position
        angle_rad = math.radians(angle)
        distance = self.radar_radius * (0.4 + intensity * 0.4)  # 40% to 80% of radius
        
        x = self.center[0] + math.cos(angle_rad) * distance
        y = self.center[1] + math.sin(angle_rad) * distance
        
        # Dynamic blip size with pulsing
        current_time = time.time()
        pulse = 1.0 + 0.3 * math.sin(current_time * 8 * intensity)
        base_size = max(8, int(intensity * 80 * self.config.get('blip_size_multiplier', 1.0)))
        blip_size = int(base_size * pulse)
        
        # Color based on intensity
        if intensity > 0.6:
            color = (255, 255, 255)  # White hot
            glow_color = (255, 0, 0)  # Red glow
        elif intensity > 0.4:
            color = (255, 100, 0)  # Orange
            glow_color = (255, 150, 0)  # Orange glow
        elif intensity > 0.2:
            color = (255, 255, 0)  # Yellow
            glow_color = (255, 255, 100)  # Yellow glow
        else:
            color = (0, 255, 0)  # Green
            glow_color = (100, 255, 100)  # Green glow
        
        # Draw glow effect
        glow_size = blip_size + 12
        pygame.draw.circle(self.screen, glow_color, (int(x), int(y)), glow_size)
        
        # Draw main blip
        pygame.draw.circle(self.screen, color, (int(x), int(y)), blip_size)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(y)), blip_size, 2)
        
        # Draw direction line
        if self.config.get('show_direction_line', True):
            line_end_x = self.center[0] + math.cos(angle_rad) * self.radar_radius * 0.9
            line_end_y = self.center[1] + math.sin(angle_rad) * self.radar_radius * 0.9
            pygame.draw.line(self.screen, color, self.center, (int(line_end_x), int(line_end_y)), 2)
            
    def _get_colors_with_opacity(self):
        """Get color scheme with opacity adjustments for HUD mode - IMPROVED TRANSPARENCY."""
        base_colors = self.COLOR_SCHEMES[self.theme].copy()
        
        if self.transparent_bg:
            # Fully transparent background
            base_colors["background"] = (0, 0, 0, 0)
        else:
            # Semi-transparent background for HUD - MUCH MORE TRANSPARENT
            bg = base_colors["background"]
            alpha = int(50 * self.hud_opacity)  # Much more transparent (was 128)
            base_colors["background"] = (*bg, alpha)
        
        # Make other colors more visible against transparent background
        for key in ["grid", "text", "center"]:
            color = base_colors[key]
            alpha = int(255 * min(1.0, self.hud_opacity + 0.2))  # Boost visibility
            base_colors[key] = (*color, alpha)
        
        # Make blips more vibrant
        for key in ["blip_low", "blip_med", "blip_high"]:
            color = base_colors[key]
            # Boost RGB values for better visibility
            enhanced_color = tuple(min(255, int(c * 1.2)) for c in color)
            base_colors[key] = enhanced_color
        
        return base_colors
        
    def update_volumes(self, volumes: Dict[str, float]):
        """
        Thread-safe method to update volume data.
        Can be called from the audio radar callback.
        
        Args:
            volumes: Dictionary with channel volumes
        """
        try:
            # Add to queue without blocking
            self.volume_queue.put_nowait(volumes.copy())
        except queue.Full:
            # Queue is full, skip this update
            pass
    
    def _process_volume_updates(self):
        """Process all pending volume updates from the queue."""
        updates_processed = 0
        
        # Process all queued updates
        while not self.volume_queue.empty() and updates_processed < 10:
            try:
                volumes = self.volume_queue.get_nowait()
                
                # Update current volumes and history
                for channel, volume in volumes.items():
                    if channel in self.current_volumes:
                        self.current_volumes[channel] = volume
                        self.volume_history[channel].append({
                            'volume': volume,
                            'timestamp': time.time()
                        })
                        
                        # Track max volume for auto-scaling
                        if volume > self.max_volume_seen:
                            self.max_volume_seen = volume
                
                updates_processed += 1
                
            except queue.Empty:
                break
    
    def _draw_radar_grid(self):
        """Draw the radar grid optimized for HUD performance."""
        # Use simpler grid for better performance
        grid_color = self.colors["grid"][:3]  # Remove alpha for basic drawing
        
        # Draw concentric circles (fewer for performance)
        for i in range(1, 3):  # Only 2 circles instead of 3
            radius = (self.radar_radius // 2) * i
            pygame.draw.circle(self.screen, grid_color, self.center, radius, 1)
        
        # Draw cardinal direction lines only (N, E, S, W)
        if not self.performance_mode:
            for angle in range(0, 360, 90):  # Only 4 lines instead of 8
                end_x = self.center[0] + self.radar_radius * math.cos(math.radians(angle - 90))
                end_y = self.center[1] + self.radar_radius * math.sin(math.radians(angle - 90))
                pygame.draw.line(self.screen, grid_color, self.center, (end_x, end_y), 1)
        
        # Draw center dot
        center_color = self.colors["center"][:3]
        pygame.draw.circle(self.screen, center_color, self.center, 6, 0)
    
    def _draw_channel_labels(self):
        """Draw channel labels optimized for HUD."""
        if self.performance_mode and self.current_fps < 80:
            return  # Skip labels if performance is low
            
        text_color = self.colors["text"][:3]
        
        for channel, angle in self.CHANNEL_POSITIONS.items():
            # Calculate label position (closer to radar for HUD)
            label_distance = self.radar_radius + 20
            label_x = self.center[0] + label_distance * math.cos(math.radians(angle - 90))
            label_y = self.center[1] + label_distance * math.sin(math.radians(angle - 90))
            
            # Render smaller labels for HUD
            text = self.small_font.render(channel, True, text_color)
            text_rect = text.get_rect(center=(label_x, label_y))
            self.screen.blit(text, text_rect)
    
    def _get_blip_color(self, volume: float) -> Tuple[int, int, int]:
        """Get color for a blip based on volume level."""
        if volume > 0.3:
            return self.colors["blip_high"]
        elif volume > 0.1:
            return self.colors["blip_med"]
        else:
            return self.colors["blip_low"]
    
    def _draw_channel_blip(self, channel: str, volume: float):
        """Draw a volume blip optimized for high FPS."""
        if volume < 0.01:  # Skip very quiet channels
            return
            
        angle = self.CHANNEL_POSITIONS[channel]
        
        # Calculate blip position
        if self.auto_scale and self.max_volume_seen > 0:
            normalized_volume = min(1.0, volume / self.max_volume_seen)
        else:
            normalized_volume = min(1.0, volume)
        
        # Blip distance from center (proportional to volume)
        blip_distance = 15 + (self.radar_radius - 25) * normalized_volume
        blip_x = self.center[0] + blip_distance * math.cos(math.radians(angle - 90))
        blip_y = self.center[1] + blip_distance * math.sin(math.radians(angle - 90))
        
        # Blip size based on volume (smaller for HUD)
        blip_size = int(3 + 10 * normalized_volume)
        
        # Get color
        color = self._get_blip_color(volume)
        
        if self.performance_mode:
            # Simple blip for high performance
            pygame.draw.circle(self.screen, color, (int(blip_x), int(blip_y)), blip_size)
            # Add simple glow ring
            if blip_size > 5:
                pygame.draw.circle(self.screen, color, (int(blip_x), int(blip_y)), blip_size + 2, 1)
        else:
            # Full glow effect for lower FPS mode
            for i in range(2):  # Reduced glow layers
                alpha = 255 - (i * 80)
                glow_size = blip_size + i * 2
                glow_color = (*color, max(50, alpha))
                
                # Create surface for alpha blending
                glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, glow_color, 
                                 (glow_size, glow_size), glow_size)
                
                self.screen.blit(glow_surface, 
                               (blip_x - glow_size, blip_y - glow_size),
                               special_flags=pygame.BLEND_ALPHA_SDL2)
            
            # Draw main blip
            pygame.draw.circle(self.screen, color, (int(blip_x), int(blip_y)), blip_size)
    
    def _draw_fading_blips(self):
        """Draw fading blips optimized for performance."""
        if self.performance_mode and self.current_fps < 60:
            return  # Skip fade trails if performance is low
            
        current_time = time.time()
        
        for channel, history in self.volume_history.items():
            if not history:
                continue
                
            angle = self.CHANNEL_POSITIONS[channel]
            
            # Only draw recent history for performance
            recent_history = [entry for entry in history 
                            if current_time - entry['timestamp'] < self.fade_time * 0.5]
            
            for entry in recent_history:
                age = current_time - entry['timestamp']
                if age > self.fade_time:
                    continue
                    
                volume = entry['volume']
                if volume < 0.02:  # Higher threshold for fade trails
                    continue
                
                # Calculate fade alpha
                fade_alpha = 1.0 - (age / self.fade_time)
                
                # Calculate position
                if self.auto_scale and self.max_volume_seen > 0:
                    normalized_volume = min(1.0, volume / self.max_volume_seen)
                else:
                    normalized_volume = min(1.0, volume)
                
                blip_distance = 15 + (self.radar_radius - 25) * normalized_volume
                blip_x = self.center[0] + blip_distance * math.cos(math.radians(angle - 90))
                blip_y = self.center[1] + blip_distance * math.sin(math.radians(angle - 90))
                
                # Simplified faded blip
                blip_size = max(1, int((2 + 6 * normalized_volume) * fade_alpha))
                color = self._get_blip_color(volume)
                
                # Simple fade without alpha blending for performance
                fade_factor = fade_alpha * 0.6
                faded_color = (
                    int(color[0] * fade_factor),
                    int(color[1] * fade_factor), 
                    int(color[2] * fade_factor)
                )
                
                pygame.draw.circle(self.screen, faded_color, 
                                 (int(blip_x), int(blip_y)), blip_size)
    
    def _draw_debug_info(self):
        """Draw debug information optimized for HUD."""
        if not self.show_debug:
            return
            
        debug_y = 5
        text_color = self.colors["text"][:3]
        
        # Essential debug info only
        debug_texts = [
            f"FPS: {self.current_fps:.0f}/{self.fps_cap}",
            f"Mode: {'Perf' if self.performance_mode else 'Quality'}",
            f"Max Vol: {self.max_volume_seen:.2f}",
        ]
        
        if self.show_debug:  # Extended debug
            debug_texts.extend([
                f"Queued: {self.volume_queue.qsize()}",
                f"Top: {self.always_on_top}",
                f"Click: {'Through' if self.click_through else 'Normal'}"
            ])
        
        for text in debug_texts:
            debug_surface = self.small_font.render(text, True, text_color)
            self.screen.blit(debug_surface, (5, debug_y))
            debug_y += 14
    
    def _draw_controls_help(self):
        """Draw minimal help text for HUD mode."""
        if not self.show_help:
            return
            
        help_texts = [
            "ESC-Quit", "D-Debug", "T-Theme", 
            "P-Performance", "H-Help", "F-Frame"
        ]
        
        text_color = self.colors["text"][:3]
        help_text = " | ".join(help_texts)
        help_surface = self.small_font.render(help_text, True, text_color)
        
        # Bottom of screen
        help_rect = help_surface.get_rect()
        help_rect.centerx = self.window_size[0] // 2
        help_rect.bottom = self.window_size[1] - 5
        self.screen.blit(help_surface, help_rect)
    
    def _handle_events(self):
        """Handle Pygame events optimized for HUD mode."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.menu_visible:
                        self.menu_visible = False
                    else:
                        self.running = False
                elif event.key == pygame.K_F1 or event.key == pygame.K_m:
                    # Menu hotkey (Sonar compliance)
                    self.menu_visible = not self.menu_visible
                elif self.menu_visible:
                    self._handle_menu_navigation(event.key)
                else:
                    # Regular hotkeys when menu is not visible
                    if event.key == pygame.K_d:
                        self.show_debug = not self.show_debug
                    elif event.key == pygame.K_t:
                        self.theme = "light" if self.theme == "dark" else "dark"
                        self.colors = self._get_colors_with_opacity()
                    elif event.key == pygame.K_a:
                        self.auto_scale = not self.auto_scale
                    elif event.key == pygame.K_r:
                        self.max_volume_seen = 0.1
                        self.config = self._load_config()  # Hot reload config
                        print("🔄 Configuration reloaded")
                    elif event.key == pygame.K_p:
                        self.performance_mode = not self.performance_mode
                        print(f"Performance mode: {self.performance_mode}")
                    elif event.key == pygame.K_h:
                        self.show_help = not self.show_help
                    elif event.key == pygame.K_f:
                        # Toggle frameless mode
                        self._toggle_frameless()
                    elif event.key == pygame.K_v:
                        # Toggle vector blending
                        self.use_vector_blending = not self.use_vector_blending
                        self.config['vector_blending'] = self.use_vector_blending
                        print(f"Vector blending: {self.use_vector_blending}")
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        # Increase FPS cap
                        self.fps_cap = min(200, self.fps_cap + 10)
                        self.config['fps_limit'] = self.fps_cap
                        print(f"FPS cap: {self.fps_cap}")
                    elif event.key == pygame.K_MINUS:
                        # Decrease FPS cap
                        self.fps_cap = max(30, self.fps_cap - 10)
                        self.config['fps_limit'] = self.fps_cap
                        print(f"FPS cap: {self.fps_cap}")
                    
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.click_through:
                if event.button == 1:  # Left click
                    self.dragging = True
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    win_x, win_y = pygame.display.get_surface().get_abs_offset()
                    self.drag_offset = (mouse_x, mouse_y)
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.dragging = False
                    
            elif event.type == pygame.MOUSEMOTION and self.dragging and not self.click_through:
                # Handle window dragging
                if HAS_WIN32 and self.hwnd:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    screen_x = mouse_x - self.drag_offset[0] 
                    screen_y = mouse_y - self.drag_offset[1]
                    
                    # Move window
                    ctypes.windll.user32.SetWindowPos(
                        self.hwnd, 0, screen_x, screen_y, 0, 0, 0x0001 | 0x0004  # SWP_NOSIZE | SWP_NOZORDER
                    )
    
    def _toggle_frameless(self):
        """Toggle frameless mode."""
        self.frameless = not self.frameless
        print(f"Frameless mode: {self.frameless}")
        
        # Note: Pygame doesn't support runtime frame toggle
        # This would require recreating the window
        print("Note: Restart required for frameless toggle to take effect")
    
    def _update_fps(self):
        """Update FPS calculation."""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def run(self):
        """High-performance HUD main loop."""
        print("Starting Audio Radar HUD...")
        print(f"Target FPS: {self.fps_cap}")
        print(f"Frameless: {self.frameless}")
        print(f"Always on top: {self.always_on_top}")
        print(f"Click-through: {self.click_through}")
        print("Controls: ESC=Quit, D=Debug, P=Performance, H=Help, +/-=FPS")
        
        # Performance optimization flags
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, 
                                pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION])
        
        while self.running:
            # Handle events (minimal processing)
            self._handle_events()
            
            # Process volume updates (with limit for performance)
            self._process_volume_updates()
            
            # Calculate composite direction (Vector Blending - Sonar compliance)
            self._calculate_composite_direction()
            
            # Clear screen
            if self.transparent_bg:
                self.screen.fill((0, 0, 0, 0))  # Transparent
            else:
                bg_color = self.colors["background"]
                if len(bg_color) > 3:  # Has alpha
                    # Create transparent surface
                    temp_surface = pygame.Surface(self.window_size, pygame.SRCALPHA)
                    temp_surface.fill(bg_color)
                    self.screen.fill((0, 0, 0))  # Clear with black first
                    self.screen.blit(temp_surface, (0, 0))
                else:
                    self.screen.fill(bg_color[:3])
            
            # Draw radar components (performance optimized)
            self._draw_radar_grid()
            
            # Conditional rendering based on performance
            if self.current_fps > 80 or not self.performance_mode:
                self._draw_channel_labels()
                self._draw_fading_blips()
            
            # Always draw current blips
            for channel, volume in self.current_volumes.items():
                self._draw_channel_blip(channel, volume)
            
            # Draw composite directional blip (Vector Blending - Sonar compliance)
            self._draw_composite_blip()
            
            # Draw UI elements
            self._draw_debug_info()
            if self.show_help:
                self._draw_controls_help()
            
            # Draw menu (Sonar compliance)
            self._draw_menu()
            
            # Update display
            pygame.display.flip()
            
            # Update FPS and maintain target
            self._update_fps()
            self.clock.tick(self.fps_cap)
        
        pygame.quit()
        print("Audio Radar HUD closed.")
    
    def set_position(self, x: int, y: int):
        """Set HUD position on screen."""
        if HAS_WIN32 and self.hwnd:
            ctypes.windll.user32.SetWindowPos(
                self.hwnd, 0, x, y, 0, 0, 0x0001 | 0x0004  # SWP_NOSIZE | SWP_NOZORDER
            )
    
    def set_opacity(self, opacity: float):
        """Set HUD opacity (0.0 - 1.0)."""
        self.hud_opacity = max(0.1, min(1.0, opacity))
        if HAS_WIN32 and self.hwnd and (self.click_through or self.transparent_bg):
            ctypes.windll.user32.SetLayeredWindowAttributes(
                self.hwnd, 0, int(255 * self.hud_opacity), 2
            )
        self.colors = self._get_colors_with_opacity()
    
    def toggle_always_on_top(self):
        """Toggle always-on-top behavior."""
        self.always_on_top = not self.always_on_top
        if HAS_WIN32 and self.hwnd:
            if self.always_on_top:
                HWND_TOPMOST = -1
            else:
                HWND_NOTOPMOST = -2
            
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            ctypes.windll.user32.SetWindowPos(
                self.hwnd, 
                HWND_TOPMOST if self.always_on_top else HWND_NOTOPMOST,
                0, 0, 0, 0, 
                SWP_NOMOVE | SWP_NOSIZE
            )


def main():
    """Example usage of the AudioRadarHUD."""
    print("Audio Radar HUD Demo")
    print("=" * 30)
    
    # Create the HUD
    radar_hud = AudioRadarHUD(
        window_size=(350, 350),
        fps_cap=100,
        fade_time=2.0,
        scale_factor=0.9,
        theme="dark",
        frameless=True,
        always_on_top=True,
        transparent_bg=False,
        click_through=False,
        hud_opacity=0.9
    )
    
    # Example: Simulate some audio data for testing
    import threading
    import random
    
    def simulate_audio_data():
        """Simulate high-frequency audio data for HUD testing."""
        channels = list(radar_hud.CHANNEL_POSITIONS.keys())
        
        while radar_hud.running:
            # Generate random volume data with more realistic patterns
            volumes = {}
            
            # Simulate occasional audio events
            for channel in channels:
                base_volume = random.random() * 0.02  # Low base noise
                
                # 15% chance of significant activity per channel
                if random.random() > 0.85:
                    if channel in ["FL", "FR", "C"]:  # Front channels more active
                        base_volume += random.random() * 0.6
                    elif channel in ["RL", "RR"]:  # Rear channels
                        base_volume += random.random() * 0.4
                    elif channel == "LFE":  # Subwoofer
                        base_volume += random.random() * 0.3
                    else:  # Side channels
                        base_volume += random.random() * 0.5
                
                volumes[channel] = min(1.0, base_volume)
            
            # Update the HUD with new volume data
            radar_hud.update_volumes(volumes)
            
            time.sleep(0.01)  # 100 Hz update rate for smooth animation
    
    # Start simulation thread
    simulation_thread = threading.Thread(target=simulate_audio_data, daemon=True)
    simulation_thread.start()
    
    print("Starting HUD...")
    print("Use P to toggle performance mode")
    print("Use +/- to adjust FPS cap")
    print("Click and drag to move (if not click-through)")
    
    # Run the HUD
    radar_hud.run()


if __name__ == "__main__":
    main()

# Backward compatibility alias
AudioRadarGUI = AudioRadarHUD
