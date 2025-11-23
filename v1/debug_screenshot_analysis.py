"""
Debug Screenshot Analysis

Take a screenshot and mark where Claude thinks things are vs where they actually are.
"""
import pyautogui
from PIL import Image, ImageDraw, ImageFont
from agent import DesktopAgent
import time


def analyze_menu_bar_screenshot():
    """Take screenshot and analyze menu bar area"""
    print("=== Screenshot Analysis Tool ===\n")
    
    # Take screenshot using agent (same as Claude sees)
    agent = DesktopAgent(log_dir="logs")
    result = agent.screenshot()
    
    print(f"✓ Screenshot taken: {result['path']}")
    print(f"  Size: {result['width']}x{result['height']}")
    
    # Load the screenshot
    screenshot = Image.open(result['path'])
    
    # Create a copy to draw on
    debug_img = screenshot.copy()
    draw = ImageDraw.Draw(debug_img)
    
    # Known Spotlight location (what you found)
    spotlight_x = 1315
    spotlight_y = 16
    
    # Where Claude has been trying
    claude_guesses = [
        (1234, 16, "Battery (Claude's 1st try)"),
        (1244, 16, "Claude's 2nd try"),
    ]
    
    # Draw the actual Spotlight location in GREEN
    box_size = 30
    draw.rectangle(
        [spotlight_x - box_size//2, spotlight_y - box_size//2,
         spotlight_x + box_size//2, spotlight_y + box_size//2],
        outline="green",
        width=3
    )
    draw.text((spotlight_x - 50, spotlight_y + 40), 
              f"ACTUAL Spotlight\n({spotlight_x}, {spotlight_y})",
              fill="green")
    
    # Draw Claude's guesses in RED
    for x, y, label in claude_guesses:
        draw.rectangle(
            [x - box_size//2, y - box_size//2,
             x + box_size//2, y + box_size//2],
            outline="red",
            width=2
        )
        draw.text((x - 40, y + 60), 
                  f"{label}\n({x}, {y})",
                  fill="red")
    
    # Draw entire menu bar highlight
    draw.rectangle([0, 0, result['width'], 40], outline="yellow", width=2)
    draw.text((10, 50), "Menu Bar Area (y: 0-40)", fill="yellow")
    
    # Save annotated screenshot
    output_path = "logs/debug_menubar_analysis.png"
    debug_img.save(output_path)
    
    print(f"\n✓ Annotated screenshot saved: {output_path}")
    print(f"\nOpen this file to see:")
    print(f"  🟢 GREEN box = Actual Spotlight location ({spotlight_x}, {spotlight_y})")
    print(f"  🔴 RED boxes = Where Claude has been clicking")
    print(f"\n💡 This shows what Claude is 'seeing' vs reality")
    
    return output_path


def take_menu_bar_closeup():
    """Take a closeup of just the menu bar"""
    print("\n=== Taking Menu Bar Closeup ===\n")
    
    agent = DesktopAgent(log_dir="logs")
    result = agent.screenshot()
    
    # Load and crop to just menu bar
    screenshot = Image.open(result['path'])
    
    # Crop to menu bar (y: 0-80 for some context)
    menu_bar_closeup = screenshot.crop((0, 0, result['width'], 80))
    
    # Save
    output_path = "logs/debug_menubar_closeup.png"
    menu_bar_closeup.save(output_path)
    
    print(f"✓ Menu bar closeup saved: {output_path}")
    print(f"  Shows pixels 0-{result['width']} × 0-80")
    print(f"\n💡 Open this to see what icons Claude is analyzing")
    
    return output_path


def show_pixel_coordinates():
    """Help find icon coordinates interactively"""
    print("\n=== Interactive Coordinate Finder ===\n")
    print("Move your mouse over the Spotlight icon and I'll tell you the coordinates!")
    print("Press Ctrl+C when done\n")
    
    try:
        last_pos = None
        while True:
            pos = pyautogui.position()
            
            # Only print if position changed
            if pos != last_pos:
                if pos.y < 40:  # In menu bar
                    print(f"\r📍 Menu bar position: ({pos.x}, {pos.y})    ", end='', flush=True)
                else:
                    print(f"\r   Current position: ({pos.x}, {pos.y})    ", end='', flush=True)
                last_pos = pos
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\n\n✓ Final position: ({pos.x}, {pos.y})")


def compare_screenshots():
    """Compare what Claude sees vs actual screen"""
    print("\n=== Comparison Analysis ===\n")
    
    # Take two screenshots
    print("Taking screenshot 1 (raw PyAutoGUI)...")
    raw_screenshot = pyautogui.screenshot()
    raw_width, raw_height = raw_screenshot.size
    
    print("Taking screenshot 2 (via Agent - what Claude sees)...")
    agent = DesktopAgent(log_dir="logs")
    agent_result = agent.screenshot()
    agent_screenshot = Image.open(agent_result['path'])
    agent_width, agent_height = agent_screenshot.size
    
    print(f"\nComparison:")
    print(f"  Raw PyAutoGUI:  {raw_width} × {raw_height}")
    print(f"  Agent (Claude): {agent_width} × {agent_height}")
    
    if raw_width == agent_width and raw_height == agent_height:
        print(f"  ✅ Sizes MATCH - scaling is correct")
    else:
        print(f"  ⚠️  Sizes DIFFER - scaling issue!")
        print(f"  Scale factor: {raw_width/agent_width:.2f}x")
    
    # Save both for visual comparison
    raw_screenshot.save("logs/debug_raw_screenshot.png")
    print(f"\n✓ Raw screenshot:   logs/debug_raw_screenshot.png")
    print(f"✓ Agent screenshot: {agent_result['path']}")
    print(f"\n💡 Open both and compare - they should look identical!")


def main():
    """Main menu"""
    print("\n" + "="*60)
    print("  SCREENSHOT DEBUG TOOL")
    print("  Why is Claude clicking the wrong icon?")
    print("="*60)
    
    print("\nOptions:")
    print("  1. Analyze menu bar (show actual vs Claude's clicks)")
    print("  2. Take menu bar closeup (see what Claude sees)")
    print("  3. Find coordinates interactively (hover over icons)")
    print("  4. Compare screenshots (verify scaling)")
    print("  5. Run all tests")
    print("  q. Quit")
    
    choice = input("\nChoice: ").strip()
    
    if choice == '1':
        analyze_menu_bar_screenshot()
    elif choice == '2':
        take_menu_bar_closeup()
    elif choice == '3':
        show_pixel_coordinates()
    elif choice == '4':
        compare_screenshots()
    elif choice == '5':
        print("\n🔍 Running all tests...\n")
        compare_screenshots()
        analyze_menu_bar_screenshot()
        take_menu_bar_closeup()
        print("\n✅ All tests complete! Check logs/ folder for images.")
    elif choice.lower() in ['q', 'quit']:
        return
    else:
        print("❌ Invalid choice")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

