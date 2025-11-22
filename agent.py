"""
Desktop Agent - Performs screen actions (screenshot, click, type)
"""
import pyautogui
import base64
from io import BytesIO
from PIL import Image
from typing import Tuple, Optional
import time
import json
from datetime import datetime
from pathlib import Path


class DesktopAgent:
    """Agent that can interact with the desktop environment"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.action_count = 0
        
        # Safety: enable failsafe (move mouse to corner to abort)
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5  # Add small delay between actions
        
    def screenshot(self) -> dict:
        """Take a screenshot and return as base64 encoded image"""
        screenshot = pyautogui.screenshot()

        # RETINA FIX: Scale down to logical coordinates
        # Get logical screen size (what PyAutoGUI uses)
        logical_width, logical_height = pyautogui.size()
        
        print(f"📸 Screenshot: Physical={screenshot.size}, Logical=({logical_width}, {logical_height})")
         
        # If screenshot is larger than logical size, scale it down
        if screenshot.size[0] > logical_width or screenshot.size[1] > logical_height:
            # Resize to match logical coordinates (for Retina displays)
            screenshot = screenshot.resize((logical_width, logical_height), Image.Resampling.LANCZOS)
            print(f"   ✓ Scaled to logical coordinates: {logical_width}x{logical_height}")
        
        # CLAUDE OPTIMIZATION: Further scale to Claude's optimal resolution (≤1280×800)
        # Claude performs best at WXGA resolution or below
        MAX_WIDTH = 1280
        MAX_HEIGHT = 800
        
        current_width, current_height = screenshot.size
        
        if current_width > MAX_WIDTH or current_height > MAX_HEIGHT:
            # Calculate scale factor to fit within MAX dimensions while maintaining aspect ratio
            scale_width = MAX_WIDTH / current_width
            scale_height = MAX_HEIGHT / current_height
            scale_factor = min(scale_width, scale_height)
            
            new_width = int(current_width * scale_factor)
            new_height = int(current_height * scale_factor)
            
            screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"   ✓ Scaled for Claude optimal performance: {new_width}x{new_height}")
            print(f"   Scale factor: {scale_factor:.3f} (coordinates will be scaled back)")
        
        # Save screenshot to logs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = self.log_dir / f"screenshot_{timestamp}_{self.action_count}.png"
        screenshot.save(screenshot_path)
        
        # Convert to base64
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Get screen dimensions (after all scaling)
        width, height = screenshot.size
        
        # Calculate scale factor for coordinate conversion
        # Claude will return coordinates in the scaled screenshot space
        # We need to convert back to logical space for PyAutoGUI
        scale_factor = width / logical_width  # Should be ≤1.0
        
        self.action_count += 1
        
        return {
            "type": "screenshot",
            "data": img_base64,
            "width": width,
            "height": height,
            "logical_width": logical_width,  # Original logical size
            "logical_height": logical_height,
            "scale_factor": scale_factor,  # For coordinate conversion
            "timestamp": timestamp,
            "path": str(screenshot_path)
        }
    
    def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
        """Click at specified coordinates"""
        try:
            # Validate coordinates
            screen_width, screen_height = pyautogui.size()
            print(f"🖱️  Click at ({x}, {y}) - Screen bounds: {screen_width}x{screen_height}")
            
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                print(f"   ❌ Out of bounds!")
                return {
                    "type": "click",
                    "success": False,
                    "error": f"Coordinates ({x}, {y}) out of screen bounds ({screen_width}x{screen_height})"
                }
            
            # Perform click (NO SCALING - coordinates already in logical space)
            pyautogui.click(x, y, clicks=clicks, button=button)
            print(f"   ✓ Clicked successfully")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.action_count += 1
            
            return {
                "type": "click",
                "success": True,
                "x": x,
                "y": y,
                "button": button,
                "clicks": clicks,
                "timestamp": timestamp
            }
        except Exception as e:
            return {
                "type": "click",
                "success": False,
                "error": str(e)
            }
    
    def type_text(self, text: str, interval: float = 0.05) -> dict:
        """Type text with specified interval between keystrokes"""
        try:
            pyautogui.write(text, interval=interval)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.action_count += 1
            
            return {
                "type": "type",
                "success": True,
                "text": text,
                "length": len(text),
                "timestamp": timestamp
            }
        except Exception as e:
            return {
                "type": "type",
                "success": False,
                "error": str(e)
            }
    
    def key_press(self, key: str) -> dict:
        """Press a specific key (e.g., 'enter', 'space', 'command')"""
        try:
            print(f"⌨️  Key press: {key}")
            
            # Handle key combinations (e.g., 'cmd+space', 'ctrl+c', 'command+space')
            if '+' in key:
                # Split the key combination and use hotkey
                keys = key.split('+')
                # Normalize 'cmd' to 'command' for consistency
                keys = ['command' if k == 'cmd' else k for k in keys]
                print(f"   Using hotkey: {keys}")
                pyautogui.hotkey(*keys)
            else:
                # Single key press
                print(f"   Using press: {key}")
                pyautogui.press(key)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.action_count += 1
            
            print(f"   ✓ Key press successful")
            
            return {
                "type": "key_press",
                "success": True,
                "key": key,
                "timestamp": timestamp
            }
        except Exception as e:
            return {
                "type": "key_press",
                "success": False,
                "error": str(e)
            }
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> dict:
        """Move mouse to specified coordinates"""
        try:
            screen_width, screen_height = pyautogui.size()
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                return {
                    "type": "move_mouse",
                    "success": False,
                    "error": f"Coordinates ({x}, {y}) out of screen bounds"
                }
            
            pyautogui.moveTo(x, y, duration=duration)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.action_count += 1
            
            return {
                "type": "move_mouse",
                "success": True,
                "x": x,
                "y": y,
                "timestamp": timestamp
            }
        except Exception as e:
            return {
                "type": "move_mouse",
                "success": False,
                "error": str(e)
            }
    
    def get_screen_size(self) -> dict:
        """Get screen dimensions"""
        width, height = pyautogui.size()
        return {
            "type": "screen_info",
            "width": width,
            "height": height
        }
    
    def execute_action(self, action: dict) -> dict:
        """Execute an action based on the action dictionary"""
        action_type = action.get("action")
        
        if action_type == "screenshot":
            return self.screenshot()
        elif action_type == "mouse_move":
            return self.move_mouse(action["coordinate"][0], action["coordinate"][1])
        elif action_type == "left_click":
            return self.click(action["coordinate"][0], action["coordinate"][1])
        elif action_type == "right_click":
            return self.click(action["coordinate"][0], action["coordinate"][1], button="right")
        elif action_type == "double_click":
            return self.click(action["coordinate"][0], action["coordinate"][1], clicks=2)
        elif action_type == "type":
            return self.type_text(action["text"])
        elif action_type == "key":
            return self.key_press(action["text"])
        else:
            return {
                "type": "error",
                "success": False,
                "error": f"Unknown action type: {action_type}"
            }


if __name__ == "__main__":
    # Simple test
    agent = DesktopAgent()
    print("Desktop Agent initialized")
    print(f"Screen size: {agent.get_screen_size()}")
    
    # Take a test screenshot
    result = agent.screenshot()
    print(f"Screenshot saved to: {result['path']}")

