"""
Desktop Agent - Handles all desktop interactions
"""
import pyautogui
import base64
import time
from io import BytesIO
from PIL import Image
from typing import Tuple, Dict, Any
from datetime import datetime
from pathlib import Path


class DesktopAgent:
    """Agent that can interact with the desktop environment"""
    
    def __init__(self, target_width: int = 1024, target_height: int = 768, log_dir: str = "logs"):
        """
        Initialize the desktop agent
        
        Args:
            target_width: Width to resize screenshots to for Claude
            target_height: Height to resize screenshots to for Claude
            log_dir: Directory to save screenshot logs
        """
        self.target_width = target_width
        self.target_height = target_height
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.action_count = 0
        
        # Safety: enable failsafe (move mouse to corner to abort)
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5  # Add small delay between actions
        
        print(f"[Agent] Initialized with target resolution: {target_width}x{target_height}")
        print(f"[Agent] Screen size: {self.get_screen_size()}")
        print(f"[Agent] Logs directory: {self.log_dir}")
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get the current screen size"""
        return pyautogui.size()
    
    def scale_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """
        Scale coordinates from Claude space to real screen space
        
        Args:
            x: X coordinate in Claude space (target_width)
            y: Y coordinate in Claude space (target_height)
            
        Returns:
            Tuple of (real_x, real_y) for PyAutoGUI
        """
        real_w, real_h = self.get_screen_size()
        scale_x = real_w / self.target_width
        scale_y = real_h / self.target_height
        real_x = int(x * scale_x)
        real_y = int(y * scale_y)
        
        print(f"[Agent] Coordinate scaling: Claude [{x}, {y}] → Screen [{real_x}, {real_y}]")
        print(f"[Agent]   Scale factors: X={scale_x:.4f}, Y={scale_y:.4f}")
        
        return real_x, real_y
    
    def take_screenshot(self) -> str:
        """
        Take a screenshot and return as base64 encoded image
        
        Returns:
            Base64 encoded JPEG string
        """
        print(f"\n[Agent] Taking screenshot...")
        screenshot = pyautogui.screenshot()
        original_size = screenshot.size
        
        # Resize for Claude (single resize operation)
        screenshot_resized = screenshot.resize(
            (self.target_width, self.target_height), 
            Image.Resampling.LANCZOS
        )
        
        print(f"[Agent]   Original size: {original_size[0]}x{original_size[1]}")
        print(f"[Agent]   Resized to: {self.target_width}x{self.target_height}")
        
        # Convert to RGB if RGBA (common on macOS)
        if screenshot_resized.mode == 'RGBA':
            screenshot_resized = screenshot_resized.convert('RGB')
            print(f"[Agent]   Converted RGBA → RGB")
        
        # Save to logs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = self.log_dir / f"screenshot_{timestamp}_{self.action_count}.png"
        screenshot_resized.save(screenshot_path)
        print(f"[Agent]   Saved to: {screenshot_path.name}")
        
        # Convert to base64 JPEG
        buffered = BytesIO()
        screenshot_resized.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        self.action_count += 1
        
        return img_str
    
    def mouse_move(self, x: int, y: int) -> str:
        """Move mouse to coordinates"""
        print(f"\n[Agent] Mouse move: [{x}, {y}] (Claude space)")
        real_x, real_y = self.scale_coordinates(x, y)
        pyautogui.moveTo(real_x, real_y)
        print(f"[Agent]   ✓ Moved to [{real_x}, {real_y}]")
        return "moved mouse"
    
    def left_click(self, x: int = None, y: int = None) -> str:
        """Click at coordinates (or current position if no coords given)"""
        if x is not None and y is not None:
            print(f"\n[Agent] Left click at: [{x}, {y}] (Claude space)")
            real_x, real_y = self.scale_coordinates(x, y)
            pyautogui.click(real_x, real_y)
            print(f"[Agent]   ✓ Clicked at [{real_x}, {real_y}]")
        else:
            print(f"\n[Agent] Left click at current position")
            pyautogui.click()
            print(f"[Agent]   ✓ Clicked")
        return "clicked"
    
    def right_click(self, x: int = None, y: int = None) -> str:
        """Right click at coordinates"""
        if x is not None and y is not None:
            print(f"\n[Agent] Right click at: [{x}, {y}] (Claude space)")
            real_x, real_y = self.scale_coordinates(x, y)
            pyautogui.click(real_x, real_y, button='right')
            print(f"[Agent]   ✓ Right clicked at [{real_x}, {real_y}]")
        else:
            print(f"\n[Agent] Right click at current position")
            pyautogui.click(button='right')
            print(f"[Agent]   ✓ Right clicked")
        return "right clicked"
    
    def double_click(self, x: int = None, y: int = None) -> str:
        """Double click at coordinates"""
        if x is not None and y is not None:
            print(f"\n[Agent] Double click at: [{x}, {y}] (Claude space)")
            real_x, real_y = self.scale_coordinates(x, y)
            pyautogui.click(real_x, real_y, clicks=2)
            print(f"[Agent]   ✓ Double clicked at [{real_x}, {real_y}]")
        else:
            print(f"\n[Agent] Double click at current position")
            pyautogui.click(clicks=2)
            print(f"[Agent]   ✓ Double clicked")
        return "double clicked"
    
    def type_text(self, text: str) -> str:
        """Type text"""
        print(f"\n[Agent] Typing text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        pyautogui.write(text)
        print(f"[Agent]   ✓ Typed {len(text)} characters")
        return "typed text"
    
    def press_key(self, key_sequence: str) -> str:
        """
        Press keyboard key(s)
        
        Args:
            key_sequence: Single key or combination like "command+space"
        """
        print(f"\n[Agent] Key press: '{key_sequence}'")
        
        # Handle combinations like "command+space"
        keys = key_sequence.split('+')
        
        # Map common keys
        key_map = {
            "return": "enter",
            "super": "command",
            "cmd": "command",
            "command": "command",
            "ctl": "ctrl",
            "ctrl": "ctrl",
            "opt": "option",
            "option": "option"
        }
        
        mapped_keys = [key_map.get(k.lower(), k.lower()) for k in keys]
        print(f"[Agent]   Mapped keys: {mapped_keys}")
        
        # Press keys in sequence (for combinations)
        for key in mapped_keys:
            pyautogui.keyDown(key)
        
        time.sleep(0.1)  # Small delay
        
        # Release in reverse order
        for key in reversed(mapped_keys):
            pyautogui.keyUp(key)
        
        print(f"[Agent]   ✓ Pressed {key_sequence}")
        return f"pressed keys: {key_sequence}"
    
    def wait(self, duration: float = 1.0) -> str:
        """Wait for specified duration"""
        print(f"\n[Agent] Waiting {duration} seconds...")
        time.sleep(duration)
        print(f"[Agent]   ✓ Wait complete")
        return "waited"

