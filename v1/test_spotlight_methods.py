"""
Test different methods to open Spotlight and Notes
"""
import pyautogui
import time
import subprocess

print("=== Testing Spotlight Methods ===\n")

# Give user time to prepare
print("Starting in 5 seconds...")
print("Click away from terminal or minimize it!\n")
for i in range(5, 0, -1):
    print(f"{i}...", end=' ', flush=True)
    time.sleep(1)
print("\nStarting now!\n")

# Method 1: Cmd+Space
print("Method 1: Trying Cmd+Space...")
pyautogui.hotkey('command', 'space')
time.sleep(2)
print("   Did Spotlight open? Check your screen.\n")
time.sleep(2)

# Close anything that opened
print("Pressing Escape to close...")
pyautogui.press('escape')
time.sleep(1)

# Method 2: Try with 'cmd' instead of 'command'
print("\nMethod 2: Trying 'cmd'+'space' (alternative)...")
pyautogui.hotkey('cmd', 'space')
time.sleep(2)
print("   Did Spotlight open?\n")
time.sleep(2)

pyautogui.press('escape')
time.sleep(1)

# Method 3: Direct AppleScript to open Notes
print("\nMethod 3: Opening Notes directly with AppleScript...")
try:
    subprocess.run(['osascript', '-e', 'tell application "Notes" to activate'], check=True)
    print("   ✓ Notes should be opening now!")
    time.sleep(3)
    
    # Create a new note
    print("\nCreating new note...")
    subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "n" using command down'], check=True)
    time.sleep(1)
    
    # Type hello
    print("Typing 'hello'...")
    subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "hello"'], check=True)
    print("   ✓ Done! Check Notes app for 'hello'")
    
except subprocess.CalledProcessError as e:
    print(f"   ✗ AppleScript failed: {e}")

print("\n=== Summary ===")
print("If Method 3 worked but Methods 1-2 didn't:")
print("  → Your Spotlight shortcut might be disabled or changed")
print("  → Check: System Settings > Keyboard > Keyboard Shortcuts > Spotlight")
print("\nIf Method 3 worked, we can use AppleScript as a workaround!")

