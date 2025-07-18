#!/usr/bin/env python3
"""
Simple Audio Blip Test - Shows blips in correct directions (ALWAYS ON TOP)
"""
import pygame
import math
import time
import ctypes
import ctypes.wintypes
import threading

# Windows API for topmost
if hasattr(ctypes, 'windll'):
    user32 = ctypes.windll.user32
    HWND_TOPMOST = -1
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040
    
    # Function prototypes
    SetWindowPos = user32.SetWindowPos
    SetWindowPos.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.wintypes.UINT]
    SetWindowPos.restype = ctypes.wintypes.BOOL
    
    SetForegroundWindow = user32.SetForegroundWindow
    SetForegroundWindow.argtypes = [ctypes.wintypes.HWND]
    SetForegroundWindow.restype = ctypes.wintypes.BOOL
    
    IsWindow = user32.IsWindow
    IsWindow.argtypes = [ctypes.wintypes.HWND]
    IsWindow.restype = ctypes.wintypes.BOOL

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = (500, 500)
CENTER = (250, 250)
RADAR_RADIUS = 200

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

def topmost_thread(hwnd):
    """Keep window on top"""
    while True:
        try:
            if hwnd and IsWindow(hwnd):
                SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, 
                           SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)
            time.sleep(0.5)
        except Exception:
            break

def angle_to_position(angle_degrees, radius):
    """Convert angle in degrees to x,y position"""
    # Convert to radians and adjust for pygame coordinate system
    angle_radians = math.radians(angle_degrees - 90)  # -90 to make 0° = North
    x = CENTER[0] + radius * math.cos(angle_radians)
    y = CENTER[1] + radius * math.sin(angle_radians)
    return (int(x), int(y))

def draw_radar_grid(screen):
    """Draw basic radar grid"""
    # Draw circles
    for radius in [RADAR_RADIUS // 3, RADAR_RADIUS * 2 // 3, RADAR_RADIUS]:
        pygame.draw.circle(screen, (60, 60, 80), CENTER, radius, 2)
    
    # Draw cross lines
    pygame.draw.line(screen, (60, 60, 80), 
                    (CENTER[0], CENTER[1] - RADAR_RADIUS),
                    (CENTER[0], CENTER[1] + RADAR_RADIUS), 2)
    pygame.draw.line(screen, (60, 60, 80), 
                    (CENTER[0] - RADAR_RADIUS, CENTER[1]),
                    (CENTER[0] + RADAR_RADIUS, CENTER[1]), 2)

def draw_channel_blip(screen, channel, volume, color):
    """Draw a blip for a specific channel"""
    if volume > 0:
        angle = CHANNEL_POSITIONS[channel]
        radius = int(RADAR_RADIUS * 0.8)  # Place blips near edge
        position = angle_to_position(angle, radius)
        
        # Blip size based on volume
        blip_size = int(10 + volume * 20)
        
        # Draw blip
        pygame.draw.circle(screen, color, position, blip_size)
        
        # Draw label
        font = pygame.font.Font(None, 24)
        text = font.render(channel, True, (255, 255, 255))
        text_pos = (position[0] - 10, position[1] - 30)
        screen.blit(text, text_pos)

def main():
    print("🎯 Simple Audio Blip Test - ALWAYS ON TOP")
    print("Testing channel positions and blip drawing")
    print("Press 1-8 to test different channels")
    print("Press ESC to exit")
    print("=" * 50)
    
    # Create window
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Audio Blip Test - ALWAYS ON TOP")
    pygame.display.flip()
    time.sleep(0.2)
    
    # Setup topmost
    try:
        wm_info = pygame.display.get_wm_info()
        if 'window' in wm_info:
            hwnd = wm_info['window']
            # Initial setup
            SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, 
                        SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
            SetForegroundWindow(hwnd)
            # Start topmost thread
            thread = threading.Thread(target=topmost_thread, args=(hwnd,), daemon=True)
            thread.start()
            print("✅ Window set to always-on-top")
        else:
            print("⚠️ Could not get window handle")
    except Exception as e:
        print(f"⚠️ Topmost setup failed: {e}")
    
    clock = pygame.time.Clock()
    
    # Test data - which channels to show (START WITH SOME BLIPS VISIBLE)
    test_channels = {
        "FL": 0.8, "C": 0.6, "FR": 0.8, "SR": 0.4,
        "RR": 0.0, "LFE": 0.3, "RL": 0.0, "SL": 0.4
    }
    
    # Channel colors
    colors = {
        "FL": (255, 100, 100),   # Red
        "C": (100, 255, 100),    # Green
        "FR": (100, 100, 255),   # Blue
        "SR": (255, 255, 100),   # Yellow
        "RR": (255, 100, 255),   # Magenta
        "LFE": (100, 255, 255),  # Cyan
        "RL": (255, 150, 100),   # Orange
        "SL": (150, 100, 255)    # Purple
    }
    
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    test_channels["FL"] = 1.0 if test_channels["FL"] == 0 else 0.0
                    print(f"FL (Front Left): {test_channels['FL']}")
                elif event.key == pygame.K_2:
                    test_channels["C"] = 1.0 if test_channels["C"] == 0 else 0.0
                    print(f"C (Center): {test_channels['C']}")
                elif event.key == pygame.K_3:
                    test_channels["FR"] = 1.0 if test_channels["FR"] == 0 else 0.0
                    print(f"FR (Front Right): {test_channels['FR']}")
                elif event.key == pygame.K_4:
                    test_channels["SR"] = 1.0 if test_channels["SR"] == 0 else 0.0
                    print(f"SR (Side Right): {test_channels['SR']}")
                elif event.key == pygame.K_5:
                    test_channels["RR"] = 1.0 if test_channels["RR"] == 0 else 0.0
                    print(f"RR (Rear Right): {test_channels['RR']}")
                elif event.key == pygame.K_6:
                    test_channels["LFE"] = 1.0 if test_channels["LFE"] == 0 else 0.0
                    print(f"LFE (Sub): {test_channels['LFE']}")
                elif event.key == pygame.K_7:
                    test_channels["RL"] = 1.0 if test_channels["RL"] == 0 else 0.0
                    print(f"RL (Rear Left): {test_channels['RL']}")
                elif event.key == pygame.K_8:
                    test_channels["SL"] = 1.0 if test_channels["SL"] == 0 else 0.0
                    print(f"SL (Side Left): {test_channels['SL']}")
                elif event.key == pygame.K_9:
                    # Test all channels
                    for channel in test_channels:
                        test_channels[channel] = 0.5
                    print("All channels ON")
                elif event.key == pygame.K_0:
                    # Clear all channels
                    for channel in test_channels:
                        test_channels[channel] = 0.0
                    print("All channels OFF")
        
        # Clear screen
        screen.fill((20, 20, 30))
        
        # Draw radar grid
        draw_radar_grid(screen)
        
        # Draw channel blips
        for channel, volume in test_channels.items():
            if volume > 0:
                draw_channel_blip(screen, channel, volume, colors[channel])
        
        # Draw instructions
        font = pygame.font.Font(None, 20)
        instructions = [
            "ALWAYS ON TOP - Press 1-8 to test channels:",
            "1=FL  2=C   3=FR  4=SR",
            "5=RR  6=LFE 7=RL  8=SL",
            "9=All ON  0=All OFF",
            "ESC=Exit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (10, 10 + i * 20))
        
        # Draw compass labels
        font_big = pygame.font.Font(None, 32)
        # North
        text = font_big.render("N", True, (255, 255, 255))
        screen.blit(text, (CENTER[0] - 10, CENTER[1] - RADAR_RADIUS - 30))
        # South
        text = font_big.render("S", True, (255, 255, 255))
        screen.blit(text, (CENTER[0] - 10, CENTER[1] + RADAR_RADIUS + 10))
        # East
        text = font_big.render("E", True, (255, 255, 255))
        screen.blit(text, (CENTER[0] + RADAR_RADIUS + 10, CENTER[1] - 10))
        # West
        text = font_big.render("W", True, (255, 255, 255))
        screen.blit(text, (CENTER[0] - RADAR_RADIUS - 30, CENTER[1] - 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    print("🎯 Audio blip test completed")
    pygame.quit()

if __name__ == "__main__":
    main()
