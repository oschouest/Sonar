#!/usr/bin/env python3
"""
TKINTER REAL AUDIO HUD - Working version with actual 7.1 audio
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import math
from audio_radar import AudioRadar

class RealAudioTkinterHUD:
    def __init__(self):
        self.running = True
        self.volumes = {"FL": 0, "FR": 0, "C": 0, "LFE": 0, "RL": 0, "RR": 0, "SL": 0, "SR": 0}
        self.audio_radar = None
        
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
            text="🖱️ Right-click: Close | ⌨️ ESC: Quit | 🎮 ALWAYS ON TOP",
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
        
        print("🎯 REAL AUDIO TKINTER HUD READY!")
        print("🎵 Features:")
        print("   ✅ Real 7.1 surround sound capture")
        print("   ✅ Always on top (working!)")
        print("   ✅ Semi-transparent")
        print("   ✅ Frameless design")
        print("📋 Controls:")
        print("   🖱️ Right-click to close")
        print("   ⌨️ ESC to quit")
        print("   🎮 Ready for gaming!")
    
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
        
        # Use preferred device if specified, otherwise try defaults
        if preferred_device is not None:
            device_attempts = [(preferred_device, f"Device {preferred_device}")]
        else:
            device_attempts = [
                (122, "Stereo Mix (Realtek)"),  # Best for capturing system audio
                (0, "Default Input Device"),    # Windows default
                (11, "VoiceMeeter Out A1"),    # VoiceMeeter output
                (None, "System Default")       # Last resort
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
            print("❌ All audio devices failed, starting simulation")
            self.update_status("⚠️ Audio: SIMULATION MODE")
            self.start_simulation()
        
        # Start display updates
        self.update_display()
    
    def start_simulation(self):
        """Fallback simulation if audio fails"""
        import random
        def simulate():
            while self.running:
                if not self.audio_radar or not self.audio_radar.is_running():
                    self.volumes = {
                        "FL": random.random() * 0.7,
                        "FR": random.random() * 0.7,
                        "C": random.random() * 0.4,
                        "LFE": random.random() * 0.3,
                        "RL": random.random() * 0.6,
                        "RR": random.random() * 0.6,
                        "SL": random.random() * 0.5,
                        "SR": random.random() * 0.5
                    }
                time.sleep(0.1)
        
        sim_thread = threading.Thread(target=simulate, daemon=True)
        sim_thread.start()
    
    def update_status(self, text):
        """Update status label"""
        try:
            self.status_label.config(text=text)
        except:
            pass
    
    def update_display(self):
        """Update the radar display"""
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
            
            # Draw center dot (larger)
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
            
            # Channel positions (8-direction)
            positions = {
                "FL": (-0.707, -0.707),  # Front Left
                "FR": (0.707, -0.707),   # Front Right  
                "C": (0, -1),            # Center
                "LFE": (0, 0),           # Subwoofer (center)
                "RL": (-0.707, 0.707),   # Rear Left
                "RR": (0.707, 0.707),    # Rear Right
                "SL": (-1, 0),           # Side Left
                "SR": (1, 0)             # Side Right
            }
            
            # Draw channel labels
            for channel, (dx, dy) in positions.items():
                if channel != "LFE":  # Skip LFE label (center)
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
            
            # Draw volume blips with DYNAMIC COLORS and EFFECTS
            max_volume = max(self.volumes.values()) if self.volumes.values() else 0
            current_time = time.time()
            
            for channel, (dx, dy) in positions.items():
                volume = self.volumes.get(channel, 0)
                if volume > 0.005:  # MUCH lower threshold for maximum sensitivity
                    blip_x = center_x + dx * radius * 0.75
                    blip_y = center_y + dy * radius * 0.75
                    
                    # Dynamic blip size with pulsing effect
                    pulse = 1.0 + 0.3 * math.sin(current_time * 10 * volume)  # Faster pulse for louder sounds
                    base_size = max(6, int(volume * 100))
                    blip_size = int(base_size * pulse)
                    
                    # ADVANCED COLOR MAPPING based on volume intensity
                    if volume > 0.4:
                        # CRITICAL/LOUD - Bright red with white core
                        color = '#ffffff'  # White hot center
                        glow_color = '#ff0000'  # Red glow
                        ring_color = '#ff4444'  # Red ring
                    elif volume > 0.2:
                        # HIGH - Red to orange gradient
                        color = '#ff2200'  # Bright red-orange
                        glow_color = '#ff6600'  # Orange glow
                        ring_color = '#ff8844'  # Orange ring
                    elif volume > 0.1:
                        # MEDIUM - Orange to yellow
                        color = '#ff8800'  # Orange
                        glow_color = '#ffaa00'  # Yellow-orange glow
                        ring_color = '#ffcc44'  # Yellow ring
                    elif volume > 0.05:
                        # MODERATE - Yellow to green
                        color = '#ffff00'  # Yellow
                        glow_color = '#88ff00'  # Yellow-green glow
                        ring_color = '#aaff44'  # Light green ring
                    elif volume > 0.02:
                        # LOW - Green
                        color = '#00ff00'  # Green
                        glow_color = '#44ff44'  # Light green glow
                        ring_color = '#66ff66'  # Green ring
                    else:
                        # QUIET - Blue-green
                        color = '#00ffaa'  # Cyan-green
                        glow_color = '#44ffcc'  # Light cyan glow
                        ring_color = '#66ffdd'  # Cyan ring
                    
                    # MULTI-LAYER EFFECT for depth and impact
                    
                    # Outer glow (largest)
                    glow_size = blip_size + 6
                    self.canvas.create_oval(
                        blip_x - glow_size, blip_y - glow_size,
                        blip_x + glow_size, blip_y + glow_size,
                        fill=ring_color, outline='', stipple='gray25'
                    )
                    
                    # Middle glow
                    mid_size = blip_size + 3
                    self.canvas.create_oval(
                        blip_x - mid_size, blip_y - mid_size,
                        blip_x + mid_size, blip_y + mid_size,
                        fill=glow_color, outline='', stipple='gray50'
                    )
                    
                    # Main blip with intensity outline
                    outline_width = max(1, int(volume * 4))
                    self.canvas.create_oval(
                        blip_x - blip_size, blip_y - blip_size,
                        blip_x + blip_size, blip_y + blip_size,
                        fill=color, outline=glow_color, width=outline_width
                    )
                    
                    # HOT CENTER for very loud sounds
                    if volume > 0.15:
                        hot_size = max(2, blip_size // 3)
                        self.canvas.create_oval(
                            blip_x - hot_size, blip_y - hot_size,
                            blip_x + hot_size, blip_y + hot_size,
                            fill='#ffffff', outline=''
                    )
                    
                    # Show volume text for significant activity
                    if volume > 0.1:
                        vol_text = f"{volume:.1f}"
                        self.canvas.create_text(
                            blip_x, blip_y + blip_size + 15,
                            text=vol_text,
                            fill=color,
                            font=('Arial', 8)
                        )
                    
                    # DYNAMIC CHANNEL INDICATORS
                    # Add channel-specific effects
                    if channel in ['FL', 'FR']:  # Front channels - add direction arrows
                        arrow_size = 4
                        if channel == 'FL':
                            # Left arrow
                            self.canvas.create_line(
                                blip_x - blip_size - 8, blip_y,
                                blip_x - blip_size - 12, blip_y - 3,
                                fill=color, width=2
                            )
                            self.canvas.create_line(
                                blip_x - blip_size - 8, blip_y,
                                blip_x - blip_size - 12, blip_y + 3,
                                fill=color, width=2
                            )
                        else:  # FR
                            # Right arrow
                            self.canvas.create_line(
                                blip_x + blip_size + 8, blip_y,
                                blip_x + blip_size + 12, blip_y - 3,
                                fill=color, width=2
                            )
                            self.canvas.create_line(
                                blip_x + blip_size + 8, blip_y,
                                blip_x + blip_size + 12, blip_y + 3,
                                fill=color, width=2
                            )
                    
                    elif channel in ['RL', 'RR']:  # Rear channels - add rear indicators
                        self.canvas.create_rectangle(
                            blip_x - 2, blip_y + blip_size + 4,
                            blip_x + 2, blip_y + blip_size + 8,
                            fill=color, outline=''
                        )
                    
                    elif channel == 'C':  # Center - add center cross
                        cross_size = 6
                        self.canvas.create_line(
                            blip_x - cross_size, blip_y,
                            blip_x + cross_size, blip_y,
                            fill='#ffffff', width=2
                        )
                        self.canvas.create_line(
                            blip_x, blip_y - cross_size,
                            blip_x, blip_y + cross_size,
                            fill='#ffffff', width=2
                        )
                    
                    elif channel == 'LFE':  # Bass - add bass wave effect
                        wave_time = current_time * 5
                        for i in range(3):
                            wave_radius = blip_size + (i * 4) + int(3 * math.sin(wave_time + i))
                            self.canvas.create_oval(
                                blip_x - wave_radius, blip_y - wave_radius,
                                blip_x + wave_radius, blip_y + wave_radius,
                                outline=color, width=1, fill=''
                            )
            
            # COMBAT-STYLE THREAT LEVEL INDICATOR
            threat_level = max_volume * 5  # Scale up for better visibility
            
            # Threat meter background
            meter_x = center_x - 150
            meter_y = center_y + radius + 30
            meter_width = 300
            meter_height = 20
            
            self.canvas.create_rectangle(
                meter_x, meter_y, meter_x + meter_width, meter_y + meter_height,
                fill='#001100', outline='#00ff00', width=2
            )
            
            # Threat level bar with dynamic colors
            if threat_level > 0.01:
                bar_width = min(meter_width, int(threat_level * meter_width))
                
                if threat_level > 0.8:
                    bar_color = '#ff0000'  # RED ALERT
                    threat_text = "🚨 THREAT: CRITICAL 🚨"
                elif threat_level > 0.5:
                    bar_color = '#ff8800'  # ORANGE ALERT
                    threat_text = "⚠️ THREAT: HIGH ⚠️"
                elif threat_level > 0.3:
                    bar_color = '#ffff00'  # YELLOW ALERT
                    threat_text = "⚡ THREAT: MEDIUM ⚡"
                elif threat_level > 0.1:
                    bar_color = '#00ff00'  # GREEN ALERT
                    threat_text = "👁️ THREAT: LOW 👁️"
                else:
                    bar_color = '#00aaff'  # BLUE - QUIET
                    threat_text = "🔍 SCANNING..."
                
                # Animated threat bar
                pulse_intensity = 1.0 + 0.2 * math.sin(current_time * 8)
                self.canvas.create_rectangle(
                    meter_x, meter_y, meter_x + bar_width, meter_y + meter_height,
                    fill=bar_color, outline='', stipple='gray75'
                )
                
                # Threat level text
                self.canvas.create_text(
                    center_x, meter_y - 15,
                    text=threat_text,
                    fill=bar_color,
                    font=('Arial', 12, 'bold')
                )
            
            # AUDIO ACTIVITY COUNTER
            active_channels = sum(1 for v in self.volumes.values() if v > 0.01)
            activity_text = f"📡 ACTIVE CHANNELS: {active_channels}/8"
            self.canvas.create_text(
                center_x, meter_y + meter_height + 20,
                text=activity_text,
                fill='#00ff00',
                font=('Arial', 10, 'bold')
            )
            
            # Draw max volume indicator with pulse effect
            if max_volume > 0:
                pulse = 1.0 + 0.4 * math.sin(current_time * 12)
                max_color = '#ffffff' if max_volume > 0.3 else '#00ff00'
                max_text = f"PEAK: {max_volume:.3f}"
                self.canvas.create_text(
                    center_x, center_y + radius + 80,
                    text=max_text,
                    fill=max_color,
                    font=('Arial', int(10 * pulse), 'bold')
                )
            
            # Schedule next update
            if self.running:
                self.root.after(50, self.update_display)  # 20 FPS
                
        except Exception as e:
            print(f"Display error: {e}")
    
    def handle_keypress(self, event):
        """Handle keyboard events"""
        if event.keysym == 'Escape':
            self.close_window()
    
    def close_window(self, event=None):
        """Close the HUD"""
        print("👋 Closing HUD...")
        self.running = False
        
        # Stop audio capture
        if self.audio_radar:
            try:
                self.audio_radar.stop()
                print("✅ Audio capture stopped")
            except:
                pass
        
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
    
    def run(self):
        """Run the HUD"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"HUD error: {e}")
        finally:
            self.running = False
            if self.audio_radar:
                try:
                    self.audio_radar.stop()
                except:
                    pass

def main():
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
    
    print("🚀 LAUNCHING REAL AUDIO TKINTER HUD")
    print("=" * 50)
    print("🎯 Features:")
    print("   🎵 Real 7.1 surround sound capture")
    print("   🖼️ Always-on-top window (WORKING!)")
    print("   👻 Semi-transparent overlay")
    print("   🎮 Gaming-ready HUD")
    print("=" * 50)
    
    hud = RealAudioTkinterHUD()
    
    # Apply command line options
    if args.frameless:
        hud.root.overrideredirect(True)
    if args.always_on_top:
        hud.root.attributes('-topmost', True)
    if args.transparent:
        hud.root.attributes('-alpha', args.opacity)
    
    # Start with specified device
    if args.device:
        print(f"🎯 Using specified device: {args.device}")
        hud.start_audio_capture(preferred_device=args.device)
    else:
        hud.start_audio_capture()
    
    hud.run()
    
    print("🎯 Audio Radar HUD closed")

if __name__ == "__main__":
    main()
