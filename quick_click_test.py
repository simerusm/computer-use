"""
Quick Click Test - Simple command line version

Usage:
    python quick_click_test.py 100 200       # Move to (100, 200)
    python quick_click_test.py 100 200 click # Move and click at (100, 200)
"""
import sys
import pyautogui
import time


def main():
    if len(sys.argv) < 3:
        print("Usage: python quick_click_test.py X Y [click]")
        print("\nExamples:")
        print("  python quick_click_test.py 756 491          # Move to center")
        print("  python quick_click_test.py 1200 20          # Move to menu bar")
        print("  python quick_click_test.py 100 100 click    # Move and click")
        print("\nScreen bounds:")
        w, h = pyautogui.size()
        print(f"  Width:  0 to {w}")
        print(f"  Height: 0 to {h}")
        print(f"  Center: ({w//2}, {h//2})")
        return
    
    try:
        x = int(sys.argv[1])
        y = int(sys.argv[2])
        should_click = len(sys.argv) > 3 and sys.argv[3].lower() == 'click'
        
        # Validate
        width, height = pyautogui.size()
        if not (0 <= x <= width and 0 <= y <= height):
            print(f"❌ Coordinates ({x}, {y}) out of bounds!")
            print(f"   Valid range: (0-{width}, 0-{height})")
            return
        
        # Move mouse
        print(f"🎯 Target: ({x}, {y})")
        print(f"   Screen: {width}x{height}")
        print("\n   Moving in 2 seconds...")
        
        for i in range(2, 0, -1):
            print(f"   {i}...", end=' ', flush=True)
            time.sleep(1)
        print()
        
        pyautogui.moveTo(x, y, duration=0.5)
        print(f"   ✅ Moved to ({x}, {y})")
        
        # Click if requested
        if should_click:
            time.sleep(0.3)
            pyautogui.click()
            print(f"   🖱️  Clicked!")
        
        # Show final position
        current = pyautogui.position()
        print(f"\n   📌 Final position: ({current.x}, {current.y})")
        
    except ValueError:
        print("❌ Invalid coordinates. Use numbers only.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()

