#!/usr/bin/env python3
"""
Advanced 7.1 Audio Radar HUD - Real Audio Only
DIRECTIONAL BLENDING RADAR - Shows estimated sound direction
"""

import tkinter as tk
import time
import threading
import math
import numpy as np
from audio_radar import AudioRadar

class RealAudioTkinterHUD:
    def __init__(self):
        self.running = True
        self.volumes = {"FL": 0, "FR": 0, "C": 0, "LFE": 0, "RL": 0, "RR": 0, "SL": 0, "SR": 0}
        self.audio_radar = None
        self.using_real_audio = False  # Flag to track if real audio is working
        
        # Create tkinter window
        self.root = tk.Tk()
        self.root.title("7.1 AUDIO RADAR HUD")
        self.root.geometry("450x450+100+100")
        
        # FORCE TOPMOST - WORKING VERSION
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.85)  # 85% opacity
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Set background
        self.root.configure(bg='#001100')  # Dark green
        
        # Create canvas for radar
        self.canvas = tk.Canvas(
            self.root, 
            width=430, 
            height=400, 
            bg='#001100', 
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=40)
        
        # Title label
        self.title_label = tk.Label(
            self.root,
            text="🎯 7.1 AUDIO RADAR HUD 🎯",
            fg='#00ff00',
            bg='#001100',
            font=('Arial', 14, 'bold')
        )
        self.title_label.place(x=80, y=5)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="🎵 Initializing audio...",
            fg='#ffff00',
            bg='#001100',
            font=('Arial', 10)
        )
        self.status_label.place(x=10, y=25)
        
        # Instructions
        self.inst_label = tk.Label(
            self.root,
            text="🖱️ Right-click: Close | ⌨️ ESC: Quit | 🎮 DIRECTIONAL RADAR",
            fg='#00ffff',
            bg='#001100',
            font=('Arial', 9)
        )
        self.inst_label.place(x=10, y=425)
        
        # Bind events
        self.root.bind('<Button-3>', self.close_window)  # Right click
        self.root.bind('<Escape>', self.close_window)
        self.root.bind('<KeyPress>', self.handle_keypress)
        self.root.focus_set()  # Allow keyboard events
        
        # Setup continuous topmost enforcement
        self.enforce_topmost()
        
        # Start audio capture
        self.start_audio_capture()
        
        print("🎯 DIRECTIONAL AUDIO RADAR READY!")
        print("🎵 Features:")
        print("   ✅ Real 7.1 surround sound capture")
        print("   ✅ Directional blending radar")
        print("   ✅ Always on top")
        print("   ✅ Semi-transparent")
        print("   ✅ Frameless design")
        print("📋 Controls:")
        print("   🖱️ Right-click to close")
        print("   ⌨️ ESC to quit")
        print("   🎮 Ready for tactical gaming!")
    
    def enforce_topmost(self):
        """Continuously enforce topmost status"""
        def enforcer():
            while self.running:
                try:
                    self.root.attributes('-topmost', True)
                    self.root.lift()
                    time.sleep(0.1)  # 100ms intervals
                except:
                    break
        
        enforcer_thread = threading.Thread(target=enforcer, daemon=True)
        enforcer_thread.start()
    
    def start_audio_capture(self, preferred_device=None):
        """Start real audio capture"""
        def audio_callback(volumes):
            """Called when new audio data is available"""
            self.volumes.update(volumes)
            self.using_real_audio = True  # Mark that real audio is working
        
        # Use preferred device if specified, otherwise try defaults
        if preferred_device is not None:
            device_attempts = [(preferred_device, f"Device {preferred_device}")]
        else:
            device_attempts = [
                (38, "VoiceMeeter Out B1 Alt"),
                (91, "VoiceMeeter Alt"),
                (8, "VoiceMeeter Main"),
                (12, "VoiceMeeter A1"),
                (42, "VoiceMeeter A1 Alt"),
                (None, "Default Device")
            ]
        
        for device_id, device_name in device_attempts:
            try:
                print(f"🔍 Trying {device_name} (ID: {device_id})...")
                self.audio_radar = AudioRadar(device=device_id, volume_callback=audio_callback)
                self.audio_radar.start()
                self.update_status(f"🎵 {device_name}: ACTIVE")
                print(f"✅ Real audio capture started ({device_name})")
                break  # Success, exit the loop
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                if self.audio_radar:
                    try:
                        self.audio_radar.stop()
                    except:
                        pass
                    self.audio_radar = None
                continue
        
        else:
            # All devices failed
            print("❌ All audio devices failed - NO SIMULATION")
            self.update_status("❌ Audio: FAILED - NO DEVICES FOUND")
            # DO NOT START SIMULATION - REAL AUDIO ONLY
        
        # Start display updates
        self.update_display()
    
    def start_simulation(self):
        """DISABLED - NO SIMULATION ALLOWED"""
        print("⚠️ SIMULATION DISABLED - REAL AUDIO ONLY")
        return
    
    def update_status(self, text):
        """Update status label"""
        try:
            self.status_label.config(text=text)
        except:
            pass
    
    def update_display(self):
        """Update the radar display with DIRECTIONAL BLENDING"""
        if not self.running:
            return
            
        try:
            # Clear canvas
            self.canvas.delete("all")
            
            center_x, center_y = 215, 200
            radius = 160
            
            # Draw grid circles
            colors = ['#003300', '#004400', '#005500']
            for i, r in enumerate([60, 110, 160]):
                self.canvas.create_oval(
                    center_x - r, center_y - r,
                    center_x + r, center_y + r,
                    outline=colors[i], width=2
                )
            
            # Draw center dot
            self.canvas.create_oval(
                center_x - 4, center_y - 4,
                center_x + 4, center_y + 4,
                fill='white', outline='white', width=2
            )
            
            # Draw cross lines
            self.canvas.create_line(
                center_x - radius, center_y,
                center_x + radius, center_y,
                fill='#00aa00', width=1
            )
            self.canvas.create_line(
                center_x, center_y - radius,
                center_x, center_y + radius,
                fill='#00aa00', width=1
            )
            
            # PROPER 7.1 CHANNEL DIRECTIONAL MAPPING
            CHANNEL_ANGLES = {
                "C": 0,       # Front center (top)
                "FR": 45,     # Front right 
                "SR": 90,     # Side right
                "RR": 135,    # Rear right
                "RL": 225,    # Rear left  
                "SL": 270,    # Side left
                "FL": 315,    # Front left
                "LFE": None   # Center (special)
            }
            
            # Convert angles to (x, y) positions for labels
            positions = {}
            for channel, angle in CHANNEL_ANGLES.items():
                if angle is not None:
                    angle_rad = math.radians(angle - 90)  # Convert to math coords
                    dx = math.cos(angle_rad)
                    dy = math.sin(angle_rad)
                    positions[channel] = (dx, dy)
                else:
                    positions[channel] = (0, 0)  # LFE at center
            
            # Draw channel labels
            for channel, (dx, dy) in positions.items():
                if channel != "LFE":
                    label_x = center_x + dx * (radius + 25)
                    label_y = center_y + dy * (radius + 25)
                    
                    # Color based on current volume
                    volume = self.volumes.get(channel, 0)
                    if volume > 0.3:
                        color = '#ff0000'  # Red for high
                    elif volume > 0.1:
                        color = '#ffff00'  # Yellow for medium
                    else:
                        color = '#00ffff'  # Cyan for low/none
                    
                    self.canvas.create_text(
                        label_x, label_y,
                        text=channel,
                        fill=color,
                        font=('Arial', 12, 'bold')
                    )
            
            # ADVANCED DIRECTIONAL BLENDING - Calculate composite direction
            current_time = time.time()
            total_weight = 0
            weighted_x = 0
            weighted_y = 0
            
            # Calculate composite direction from all channels
            for channel, angle in CHANNEL_ANGLES.items():
                if angle is not None:  # Skip LFE for directional calculation
                    volume = self.volumes.get(channel, 0)
                    if volume > 0.01:  # Only consider significant volumes
                        angle_rad = math.radians(angle - 90)  # Convert to math coords
                        
                        # Weight by volume squared for better sensitivity
                        weight = volume * volume
                        
                        # Add to composite vector
                        weighted_x += math.cos(angle_rad) * weight
                        weighted_y += math.sin(angle_rad) * weight
                        total_weight += weight
            
            # Draw composite directional blip if we have audio
            if total_weight > 0:
                # Calculate final direction
                final_angle = math.atan2(weighted_y, weighted_x)
                final_intensity = min(math.sqrt(weighted_x**2 + weighted_y**2), 1.0)
                
                # Position the main blip
                distance_factor = 0.4 + (final_intensity * 0.4)  # 40% to 80% of radius
                blip_x = center_x + math.cos(final_angle) * radius * distance_factor
                blip_y = center_y + math.sin(final_angle) * radius * distance_factor
                
                # Dynamic blip size with pulsing effect
                pulse = 1.0 + 0.4 * math.sin(current_time * 8 * final_intensity)
                base_size = max(8, int(final_intensity * 120))
                blip_size = int(base_size * pulse)
                
                # Color mapping based on intensity
                if final_intensity > 0.6:
                    color = '#ffffff'  # White hot
                    glow_color = '#ff0000'  # Red glow
                elif final_intensity > 0.4:
                    color = '#ff2200'  # Red-orange
                    glow_color = '#ff6600'  # Orange glow
                elif final_intensity > 0.2:
                    color = '#ff8800'  # Orange
                    glow_color = '#ffaa00'  # Yellow glow
                elif final_intensity > 0.1:
                    color = '#ffff00'  # Yellow
                    glow_color = '#88ff00'  # Green glow
                else:
                    color = '#00ff00'  # Green
                    glow_color = '#44ff44'  # Light green glow
                
                # Draw main directional blip
                # Outer glow
                glow_size = blip_size + 8
                self.canvas.create_oval(
                    blip_x - glow_size, blip_y - glow_size,
                    blip_x + glow_size, blip_y + glow_size,
                    fill=glow_color, outline='', stipple='gray25'
                )
                
                # Inner core
                self.canvas.create_oval(
                    blip_x - blip_size, blip_y - blip_size,
                    blip_x + blip_size, blip_y + blip_size,
                    fill=color, outline='white', width=2
                )
                
                # Direction indicator line
                line_end_x = center_x + math.cos(final_angle) * radius * 0.9
                line_end_y = center_y + math.sin(final_angle) * radius * 0.9
                self.canvas.create_line(
                    center_x, center_y,
                    line_end_x, line_end_y,
                    fill=color, width=2, stipple='gray50'
                )
            
            # Draw dim individual channel indicators
            for channel, (dx, dy) in positions.items():
                volume = self.volumes.get(channel, 0)
                if volume > 0.02:
                    if channel == "LFE":
                        # LFE center pulse
                        lfe_size = max(3, int(volume * 40))
                        self.canvas.create_oval(
                            center_x - lfe_size, center_y - lfe_size,
                            center_x + lfe_size, center_y + lfe_size,
                            fill='#4444ff', outline='#6666ff', width=1
                        )
                    else:
                        # Dim channel dots
                        dot_x = center_x + dx * radius * 0.85
                        dot_y = center_y + dy * radius * 0.85
                        dot_size = max(2, int(volume * 20))
                        
                        if volume > 0.3:
                            dot_color = '#664444'  # Dim red
                        elif volume > 0.1:
                            dot_color = '#666644'  # Dim yellow
                        else:
                            dot_color = '#444466'  # Dim blue
                        
                        self.canvas.create_oval(
                            dot_x - dot_size, dot_y - dot_size,
                            dot_x + dot_size, dot_y + dot_size,
                            fill=dot_color, outline='', stipple='gray75'
                        )
            
            # Status display
            active_channels = sum(1 for v in self.volumes.values() if v > 0.01)
            if active_channels > 0:
                status_text = f"📊 Active: {active_channels} channels"
                self.canvas.create_text(
                    center_x, center_y + radius + 25,
                    text=status_text,
                    fill='#00ff00',
                    font=('Arial', 10, 'bold')
                )
        
        except Exception as e:
            print(f"❌ Display error: {e}")
        
        # Schedule next update
        if self.running:
            try:
                self.root.after(50, self.update_display)  # 20 FPS
            except:
                pass
    
    def handle_keypress(self, event):
        """Handle key press events"""
        if event.keysym == 'Escape':
            self.close_window()
    
    def close_window(self, event=None):
        """Close the window and stop audio"""
        print("🛑 Closing radar HUD...")
        self.running = False
        
        # Stop audio capture
        if self.audio_radar:
            try:
                self.audio_radar.stop()
            except:
                pass
        
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
    
    def run(self):
        """Start the main loop"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='7.1 Audio Radar HUD')
    parser.add_argument('--device', type=int, help='Audio device ID to use')
    parser.add_argument('--frameless', action='store_true', help='Remove window frame')
    parser.add_argument('--always-on-top', action='store_true', help='Keep window on top')
    parser.add_argument('--transparent', action='store_true', help='Make window transparent')
    parser.add_argument('--opacity', type=float, default=0.85, help='Window opacity (0.0-1.0)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--demo', action='store_true', help='Demo mode with fake audio')
    
    args = parser.parse_args()
    
    print("🎯 STARTING DIRECTIONAL AUDIO RADAR HUD")
    print("======================================")
    if args.device:
        print(f"🎵 Using device: {args.device}")
    if args.debug:
        print("🔍 Debug mode enabled")
    print("🎮 REAL AUDIO ONLY - NO SIMULATION")
    print()
    
    # Create and run HUD
    hud = RealAudioTkinterHUD()
    
    # Override device if specified
    if args.device:
        hud.start_audio_capture(args.device)
    
    hud.run()
