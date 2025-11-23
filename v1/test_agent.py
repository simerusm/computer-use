"""
Simple test script to verify the agent works
"""
from agent import DesktopAgent
from logger import ActionLogger
import time


def test_agent():
    """Test basic agent functionality"""
    print("=== Testing Desktop Agent ===\n")
    
    # Initialize
    agent = DesktopAgent(log_dir="logs")
    logger = ActionLogger(log_dir="logs")
    
    # Test 1: Get screen info
    print("1. Testing screen info...")
    screen_info = agent.get_screen_size()
    print(f"   ✓ Screen size: {screen_info['width']}x{screen_info['height']}")
    
    # Test 2: Take screenshot
    print("\n2. Testing screenshot...")
    result = agent.screenshot()
    logger.log_action({"action": "screenshot"}, result)
    print(f"   ✓ Screenshot saved: {result['path']}")
    print(f"   ✓ Image size: {result['width']}x{result['height']}")
    
    # Test 3: Get mouse position
    print("\n3. Current mouse position:")
    import pyautogui
    pos = pyautogui.position()
    print(f"   Mouse at: ({pos.x}, {pos.y})")
    
    # Test 4: Move mouse (safe area - center of screen)
    print("\n4. Testing mouse move (will move to center of screen)...")
    center_x = screen_info['width'] // 2
    center_y = screen_info['height'] // 2
    result = agent.move_mouse(center_x, center_y, duration=1.0)
    logger.log_action({"action": "move_mouse", "x": center_x, "y": center_y}, result)
    if result['success']:
        print(f"   ✓ Mouse moved to ({center_x}, {center_y})")
    else:
        print(f"   ✗ Error: {result.get('error')}")
    
    # Test 5: Logger summary
    print("\n5. Testing logger...")
    summary = logger.get_summary()
    print(f"   ✓ Session ID: {summary['session_id']}")
    print(f"   ✓ Total actions: {summary['total_actions']}")
    print(f"   ✓ Log file: {summary['log_file']}")
    
    print("\n=== Tests Complete ===")
    print("\nNote: For full functionality tests, run:")
    print("  python orchestrator.py")
    print("  python example_notepad.py")


if __name__ == "__main__":
    try:
        test_agent()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("\nMake sure you have:")
        print("  1. Installed all dependencies: pip install -r requirements.txt")
        print("  2. Granted accessibility permissions (macOS)")

