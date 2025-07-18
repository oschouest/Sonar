#!/usr/bin/env python3
"""
WORKING AUDIO RADAR - Simplified and bulletproof version

DEV_SANDBOX: This is a development test tool for basic radar functionality.
Purpose: Simple radar implementation for testing core audio visualization concepts.
Status: Functional - used for basic radar testing during development.
"""
import tkinter as tk
import sounddevice as sd
import numpy as np
import threading
import time
import math

class SimpleAudioRadar:
    def __init__(self):
        self.running = True
        self.volumes = {}
        
        # Create window
        self.root = tk.Tk()
        self.root.title("🎯 SONAR AUDIO RADAR")
        self.root.geometry("400x450")
        self.root.configure(bg='black')
        self.root.attributes('-topmost', True)
        
        # Create canvas
        self.canvas = tk.Canvas(self.root, width=380, height=380, bg='black')
        self.canvas.pack(pady=10)
        
        # Status label
        self.status = tk.Label(self.root, text="Starting...", fg='white', bg='black')
        self.status.pack()
        
        # Audio device
        self.device = 38  # Start with device 38
        self.audio_thread = None
        
        # Start audio capture
        self.start_audio()
        
        # Update display
        self.update_display()
        
        # Handle close
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        
    def start_audio(self):
        """Start audio capture in background thread"""
        def audio_worker():
            try:
                def callback(indata, frames, time, status):
                    if status:
                        print(f"Audio status: {status}")
                    
                    # Get number of channels
                    num_channels = indata.shape[1]
                    
                    # Calculate RMS for each channel
                    new_volumes = {}
                    for i in range(min(num_channels, 8)):
                        rms = np.sqrt(np.mean(indata[:, i]**2))
                        channel_names = ["FL", "FR", "C", "LFE", "RL", "RR", "SL", "SR"]
                        if i < len(channel_names):
                            new_volumes[channel_names[i]] = rms
                    
                    # Update volumes
                    self.volumes = new_volumes
                
                # Try to start audio stream
                print(f"🎵 Starting audio stream on device {self.device}...")
                with sd.InputStream(callback=callback, device=self.device, channels=8, samplerate=44100):
                    print(f"✅ Audio stream started successfully!")
                    self.status.config(text=f"✅ Active - Device {self.device}")
                    while self.running:
                        time.sleep(0.1)
                        
            except Exception as e:
                print(f"❌ Audio error: {e}")
                self.status.config(text=f"❌ Error: {e}")
                
                # Try backup devices
                for backup_device in [91, 8, 12, 42]:
                    try:
                        print(f"🔄 Trying backup device {backup_device}...")
                        with sd.InputStream(callback=callback, device=backup_device, channels=8, samplerate=44100):
                            print(f"✅ Backup device {backup_device} works!")
                            self.status.config(text=f"✅ Active - Device {backup_device}")
                            self.device = backup_device
                            while self.running:
                                time.sleep(0.1)
                            break
                    except:
                        continue
                else:
                    print("❌ No working audio devices found")
                    self.status.config(text="❌ No audio devices work")
        
        self.audio_thread = threading.Thread(target=audio_worker, daemon=True)
        self.audio_thread.start()
    
    def update_display(self):
        """Update the radar display"""
        if not self.running:
            return
            
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw radar circles
        center_x, center_y = 190, 190
        for radius in [50, 100, 150]:
            self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                outline='green', width=1
            )
        
        # Draw crosshairs
        self.canvas.create_line(center_x, 40, center_x, 340, fill='green', width=1)
        self.canvas.create_line(40, center_y, 340, center_y, fill='green', width=1)
        
        # Channel positions (degrees from top)
        positions = {
            "FL": 315, "FR": 45, "C": 0, "LFE": 180,
            "RL": 225, "RR": 135, "SL": 270, "SR": 90
        }
        
        # Draw channel labels and blips
        for channel, angle in positions.items():
            # Calculate position
            label_radius = 160
            blip_radius = 120
            
            angle_rad = math.radians(angle - 90)  # Adjust for top = 0
            
            # Label position
            label_x = center_x + label_radius * math.cos(angle_rad)
            label_y = center_y + label_radius * math.sin(angle_rad)
            
            # Blip position
            blip_x = center_x + blip_radius * math.cos(angle_rad)
            blip_y = center_y + blip_radius * math.sin(angle_rad)
            
            # Draw label
            self.canvas.create_text(label_x, label_y, text=channel, fill='white', font=('Arial', 8))
            
            # Draw blip if volume is present
            volume = self.volumes.get(channel, 0)
            if volume > 0.001:  # Very low threshold
                # Color based on volume
                if volume > 0.1:
                    color = 'red'
                elif volume > 0.05:
                    color = 'orange'
                elif volume > 0.01:
                    color = 'yellow'
                else:
                    color = 'green'
                
                # Size based on volume
                size = max(3, int(volume * 100))
                
                # Draw blip
                self.canvas.create_oval(
                    blip_x - size, blip_y - size,
                    blip_x + size, blip_y + size,
                    fill=color, outline=color
                )
        
        # Show volume info
        volume_text = ", ".join([f"{ch}: {vol:.3f}" for ch, vol in self.volumes.items() if vol > 0.001])
        if volume_text:
            self.canvas.create_text(190, 20, text=volume_text, fill='cyan', font=('Arial', 8))
        
        # Schedule next update
        self.root.after(50, self.update_display)
    
    def close(self):
        """Close the application"""
        print("🔴 Closing radar...")
        self.running = False
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        print("🚀 Starting Simple Audio Radar...")
        self.root.mainloop()

if __name__ == "__main__":
    radar = SimpleAudioRadar()
    radar.run()
