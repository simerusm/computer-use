"""
Test coordinate system sanity checks (from GPT recommendations)
"""
import pyautogui
import time
from agent import DesktopAgent

def test_1_print_sizes():
    """Test 1: Print sizes once"""
    print("=== Test 1: Verify Coordinate Systems ===\n")
    
    logical_w, logical_h = pyautogui.size()
    shot = pyautogui.screenshot()
    
    print(f"Logical (PyAutoGUI):   {logical_w} × {logical_h}")
    print(f"Physical (Screenshot): {shot.size[0]} × {shot.size[1]}")
    
    if shot.size[0] == logical_w * 2 and shot.size[1] == logical_h * 2:
        print("✓ Detected 2x Retina display (expected)")
    elif shot.size[0] == logical_w and shot.size[1] == logical_h:
        print("✓ No scaling needed (non-Retina)")
    else:
        print(f"⚠️  Unusual scaling: {shot.size[0] / logical_w}x")
    
    # Test agent's screenshot method
    print("\n--- Testing Agent Screenshot ---")
    agent = DesktopAgent(log_dir="logs")
    result = agent.screenshot()
    print(f"Agent returns:         {result['width']} × {result['height']}")
    
    if result['width'] == logical_w and result['height'] == logical_h:
        print("✅ PASS: Agent screenshot matches logical coordinates!")
    else:
        print(f"❌ FAIL: Agent screenshot doesn't match! Should be {logical_w}×{logical_h}")
    
    print()


def test_2_center_click():
    """Test 2: Hard-coded center click"""
    print("=== Test 2: Center Click Test ===\n")
    print("In 3 seconds, the mouse will move to screen center...")
    print("Watch if it goes to the actual center of your display!")
    
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    w, h = pyautogui.size()
    center_x, center_y = w // 2, h // 2
    
    print(f"\nMoving to center: ({center_x}, {center_y})")
    pyautogui.moveTo(center_x, center_y, duration=0.5)
    time.sleep(1)
    
    print("Did the mouse move to the CENTER of your screen?")
    print("  - YES → PyAutoGUI coordinates are working correctly ✓")
    print("  - NO  → Something is wrong with PyAutoGUI/macOS setup ✗")
    print()


def test_3_agent_click():
    """Test 3: Test agent click method"""
    print("=== Test 3: Agent Click Test ===\n")
    print("Testing agent click at center...")
    
    agent = DesktopAgent(log_dir="logs")
    w, h = pyautogui.size()
    center_x, center_y = w // 2, h // 2
    
    result = agent.click(center_x, center_y)
    
    if result['success']:
        print(f"✅ PASS: Agent clicked at ({center_x}, {center_y})")
        print(f"   Coordinates NOT scaled (as they should be)")
    else:
        print(f"❌ FAIL: {result.get('error')}")
    print()


def test_4_summary():
    """Test 4: Summary"""
    print("=== Summary ===\n")
    print("✅ What should be working now:")
    print("   1. Screenshots are scaled to logical coordinates")
    print("   2. Claude receives logical width/height")
    print("   3. Coordinates from Claude are NOT scaled")
    print("   4. PyAutoGUI clicks use coordinates directly")
    print()
    print("🐛 If clicks are still off:")
    print("   - Check Claude's coordinates in orchestrator debug output")
    print("   - Verify Spotlight shortcut is enabled in System Settings")
    print("   - Try the manual example with countdown")
    print()


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  COORDINATE SYSTEM SANITY CHECKS")
    print("="*60 + "\n")
    
    test_1_print_sizes()
    
    input("Press Enter to run center click test...")
    test_2_center_click()
    
    input("Press Enter to test agent click...")
    test_3_agent_click()
    
    test_4_summary()
    
    print("Tests complete!")


if __name__ == "__main__":
    main()

