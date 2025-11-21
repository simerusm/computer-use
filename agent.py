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
        
        # Save screenshot to logs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = self.log_dir / f"screenshot_{timestamp}_{self.action_count}.png"
        screenshot.save(screenshot_path)
        
        # Convert to base64
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Get screen dimensions
        width, height = screenshot.size
        
        self.action_count += 1
        
        return {
            "type": "screenshot",
            "data": img_base64,
            "width": width,
            "height": height,
            "timestamp": timestamp,
            "path": str(screenshot_path)
        }
    
    def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
        """Click at specified coordinates"""
        try:
            # Validate coordinates
            screen_width, screen_height = pyautogui.size()
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                return {
                    "type": "click",
                    "success": False,
                    "error": f"Coordinates ({x}, {y}) out of screen bounds ({screen_width}x{screen_height})"
                }
            
            # Perform click
            pyautogui.click(x, y, clicks=clicks, button=button)
            
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
            pyautogui.press(key)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.action_count += 1
            
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

