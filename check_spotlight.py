"""
Check if Spotlight is accessible and find its location
"""
import pyautogui
import time

print("=== Spotlight Troubleshooting ===\n")

# Get screen size
screen_width, screen_height = pyautogui.size()
print(f"Screen resolution: {screen_width}x{screen_height}")

# Check current mouse position
print("\n1. Move your mouse over the Spotlight icon (magnifying glass)")
print("   and we'll tell you the coordinates.\n")

for i in range(10, 0, -1):
    pos = pyautogui.position()
    print(f"   {i}s - Mouse position: ({pos.x}, {pos.y})", end='\r')
    time.sleep(1)

final_pos = pyautogui.position()
print(f"\n\n✓ Final position: ({final_pos.x}, {final_pos.y})")
print(f"   Use this coordinate to click Spotlight!")

print("\n2. Testing Cmd+Space keyboard shortcut...")
print("   Watch if Spotlight opens...")
time.sleep(2)

# Try opening Spotlight
print("   Pressing Cmd+Space now...")
pyautogui.hotkey('command', 'space')
time.sleep(2)

print("\n3. Did Spotlight open? (Check your screen)")
print("\nIf Spotlight didn't open, check:")
print("   • System Settings > Keyboard > Keyboard Shortcuts > Spotlight")
print("   • Make sure 'Show Spotlight search' is enabled")
print("   • Check if the shortcut is set to Cmd+Space")

