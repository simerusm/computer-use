# test_monitors.py
import pyautogui
from PIL import ImageGrab
import subprocess

print("=== Multi-Monitor Detection ===\n")

# Method 1: PyAutoGUI's view
pyautogui_size = pyautogui.size()
print(f"PyAutoGUI total virtual screen: {pyautogui_size}")

# Method 2: Screenshot actual size
screenshot = ImageGrab.grab()
print(f"Screenshot captures: {screenshot.size}")

# Method 3: Get all monitors on macOS
print("\n--- Individual Monitor Info (macOS) ---")
try:
    result = subprocess.run(
        ['system_profiler', 'SPDisplaysDataType'],
        capture_output=True,
        text=True
    )
    # Parse resolution info
    for line in result.stdout.split('\n'):
        if 'Resolution' in line or 'Display' in line:
            print(line.strip())
except Exception as e:
    print(f"Could not get monitor info: {e}")

# Method 4: Mouse position tells us which monitor
print("\n--- Current Mouse Position ---")
pos = pyautogui.position()
print(f"Mouse at: ({pos.x}, {pos.y})")
print(f"This tells us where (0,0) starts")

# Method 5: Take screenshot and save it
print("\n--- Saving test screenshot ---")
test_screenshot = pyautogui.screenshot()
test_screenshot.save("test_multimonitor.png")
print(f"Saved to test_multimonitor.png - Open it to see what's captured!")
print(f"Size: {test_screenshot.size}")

print("\n=== Analysis ===")
if screenshot.size[0] > 3000:
    print("⚠️  Large width detected - likely capturing multiple monitors")
    print("   Recommendation: Disable external monitor or specify primary display")
else:
    print("✓ Appears to be single monitor")