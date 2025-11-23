"""
Interactive Coordinate Click Tester

Test if mouse clicks go to the correct locations.
Enter coordinates and watch where the mouse goes!
"""
import pyautogui
import time
from agent import DesktopAgent


def show_screen_info():
    """Display screen information"""
    width, height = pyautogui.size()
    print("\n" + "="*60)
    print("  COORDINATE CLICK TESTER")
    print("="*60)
    print(f"\n📐 Screen Bounds: {width} × {height}")
    print(f"   Top-left:     (0, 0)")
    print(f"   Top-right:    ({width}, 0)")
    print(f"   Bottom-left:  (0, {height})")
    print(f"   Bottom-right: ({width}, {height})")
    print(f"   Center:       ({width//2}, {height//2})")
    print("\n💡 Tip: Menu bar is usually y=0-40")
    print("="*60 + "\n")


def get_coordinates():
    """Get coordinates from user input"""
    width, height = pyautogui.size()
    
    while True:
        try:
            coord_input = input("Enter coordinates (x,y) or 'q' to quit: ").strip()
            
            if coord_input.lower() in ['q', 'quit', 'exit']:
                return None, None
            
            # Handle common formats: "x,y" or "x y" or "(x,y)"
            coord_input = coord_input.replace('(', '').replace(')', '').replace(',', ' ')
            parts = coord_input.split()
            
            if len(parts) != 2:
                print("❌ Please enter two numbers: x y")
                continue
            
            x = int(parts[0])
            y = int(parts[1])
            
            # Validate bounds
            if not (0 <= x <= width and 0 <= y <= height):
                print(f"❌ Out of bounds! Must be within (0-{width}, 0-{height})")
                continue
            
            return x, y
            
        except ValueError:
            print("❌ Invalid input. Please enter numbers.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return None, None


def test_click(x, y, use_agent=False):
    """Test clicking at coordinates"""
    print(f"\n🎯 Testing coordinate: ({x}, {y})")
    print("   Moving mouse in 2 seconds...")
    
    for i in range(2, 0, -1):
        print(f"   {i}...", end=' ', flush=True)
        time.sleep(1)
    print()
    
    if use_agent:
        # Test with agent (includes validation)
        agent = DesktopAgent(log_dir="logs")
        result = agent.click(x, y)
        
        if result['success']:
            print(f"   ✅ Agent clicked at ({x}, {y})")
        else:
            print(f"   ❌ Agent error: {result.get('error')}")
    else:
        # Test with raw PyAutoGUI
        pyautogui.moveTo(x, y, duration=0.5)
        print(f"   📍 Mouse moved to ({x}, {y})")
        
        click = input("   Click here? (y/n): ").strip().lower()
        if click in ['y', 'yes']:
            pyautogui.click()
            print("   ✅ Clicked!")
    
    # Show current position
    current = pyautogui.position()
    print(f"   📌 Current position: ({current.x}, {current.y})")


def quick_test_mode():
    """Quick test with common coordinates"""
    print("\n🚀 Quick Test Mode")
    print("Testing common coordinates...\n")
    
    width, height = pyautogui.size()
    
    test_points = [
        (width//2, height//2, "Center"),
        (width//4, height//4, "Upper-left quadrant"),
        (width*3//4, height//4, "Upper-right quadrant"),
        (100, 20, "Menu bar left side"),
        (width-100, 20, "Menu bar right side"),
    ]
    
    for x, y, description in test_points:
        print(f"📍 {description}: ({x}, {y})")
        print("   Moving mouse...")
        pyautogui.moveTo(x, y, duration=0.5)
        time.sleep(1)
        
        input("   Press Enter for next point...")
    
    print("\n✅ Quick test complete!")


def show_menu():
    """Show menu options"""
    print("\nOptions:")
    print("  1. Enter coordinates manually")
    print("  2. Quick test (common coordinates)")
    print("  3. Show screen info again")
    print("  q. Quit")
    print()


def main():
    """Main interactive loop"""
    show_screen_info()
    
    # Ask about testing mode
    print("Test Mode:")
    print("  1. Move only (see where mouse goes)")
    print("  2. Move and click (actually click)")
    print("  3. Use Agent (test with agent.click())")
    
    mode = input("\nSelect mode (1/2/3): ").strip()
    
    use_click = mode == '2'
    use_agent = mode == '3'
    
    print(f"\n✓ Mode: {'Agent' if use_agent else 'Click' if use_click else 'Move only'}")
    
    while True:
        show_menu()
        choice = input("Choice: ").strip()
        
        if choice == '1':
            # Manual coordinate entry
            x, y = get_coordinates()
            if x is None:
                break
            
            test_click(x, y, use_agent=use_agent)
            
        elif choice == '2':
            # Quick test mode
            quick_test_mode()
            
        elif choice == '3':
            # Show info again
            show_screen_info()
            
        elif choice.lower() in ['q', 'quit', 'exit']:
            break
        
        else:
            print("❌ Invalid choice")
    
    print("\n👋 Thanks for testing! Goodbye.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")

