#!/usr/bin/env python3
"""
MINIMAL WORKING RADAR - Proof of concept
"""

import pygame
import sys
import os
import time
import ctypes

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_minimal_radar():
    """Create a minimal working radar that actually stays on top"""
    
    print("🎯 CREATING MINIMAL WORKING RADAR")
    print("=" * 40)
    
    # Initialize pygame
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("MINIMAL WORKING RADAR")
    
    # Get window handle and force always-on-top
    try:
        time.sleep(0.5)  # Give window time to create
        wm_info = pygame.display.get_wm_info()
        if 'window' in wm_info:
            hwnd = wm_info['window']
            
            # Force always-on-top
            HWND_TOPMOST = -1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            
            result = ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0, 
                SWP_NOMOVE | SWP_NOSIZE
            )
            
            if result:
                print("✅ ALWAYS-ON-TOP: SUCCESS")
            else:
                print("❌ ALWAYS-ON-TOP: FAILED")
        else:
            print("❌ Could not get window handle")
    except Exception as e:
        print(f"❌ Always-on-top failed: {e}")
    
    # Colors
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    
    # Test blips (simulated audio)
    test_blips = [
        (100, 100, 0.8),  # FL
        (300, 100, 0.6),  # FR
        (200, 80, 0.4),   # C
        (100, 300, 0.7),  # RL
        (300, 300, 0.5),  # RR
    ]
    
    clock = pygame.time.Clock()
    running = True
    
    print("✅ RADAR WINDOW CREATED")
    print("✅ Should be ALWAYS-ON-TOP")
    print("✅ Press ESC to quit")
    print("✅ You should see GREEN radar with YELLOW blips")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw radar grid
        center_x, center_y = 200, 200
        
        # Draw circles
        for radius in [50, 100, 150]:
            pygame.draw.circle(screen, GREEN, (center_x, center_y), radius, 2)
        
        # Draw cross
        pygame.draw.line(screen, GREEN, (center_x - 150, center_y), (center_x + 150, center_y), 2)
        pygame.draw.line(screen, GREEN, (center_x, center_y - 150), (center_x, center_y + 150), 2)
        
        # Draw test blips
        for x, y, intensity in test_blips:
            size = int(10 + intensity * 20)
            pygame.draw.circle(screen, YELLOW, (x, y), size)
        
        # Draw center dot
        pygame.draw.circle(screen, GREEN, (center_x, center_y), 3)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✅ RADAR CLOSED")

if __name__ == "__main__":
    create_minimal_radar()
