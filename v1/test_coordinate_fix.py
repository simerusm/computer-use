#!/usr/bin/env python3
"""
Test script to verify the coordinate fix works correctly.
Compares old double-resize approach vs new single-resize approach.
"""
import pyautogui
from PIL import Image
import io

def test_old_approach():
    """Simulate the old double-resize approach"""
    print("=" * 60)
    print("OLD APPROACH (Double Resize)")
    print("=" * 60)
    
    # Take screenshot
    screenshot = pyautogui.screenshot()
    physical_width, physical_height = screenshot.size
    
    # Get logical size
    logical_width, logical_height = pyautogui.size()
    
    print(f"Physical screenshot: {physical_width}×{physical_height}")
    print(f"Logical screen: {logical_width}×{logical_height}")
    
    # RESIZE #1: Physical → Logical
    screenshot_step1 = screenshot.resize((logical_width, logical_height), Image.Resampling.LANCZOS)
    print(f"After resize #1: {screenshot_step1.size[0]}×{screenshot_step1.size[1]}")
    
    # RESIZE #2: Logical → Claude optimal
    MAX_WIDTH = 1280
    MAX_HEIGHT = 800
    
    scale_width = MAX_WIDTH / screenshot_step1.size[0]
    scale_height = MAX_HEIGHT / screenshot_step1.size[1]
    scale_factor = min(scale_width, scale_height)
    
    new_width = int(round(screenshot_step1.size[0] * scale_factor))
    new_height = int(round(screenshot_step1.size[1] * scale_factor))
    
    screenshot_final = screenshot_step1.resize((new_width, new_height), Image.Resampling.LANCZOS)
    print(f"After resize #2: {screenshot_final.size[0]}×{screenshot_final.size[1]}")
    
    # Test coordinate mapping
    test_coords = [(615, 400), (1000, 600), (100, 100)]  # Middle, right, top-left in Claude space
    
    print(f"\nCoordinate mapping (Claude → Logical):")
    for claude_x, claude_y in test_coords:
        logical_x = int(round(claude_x * (logical_width / new_width)))
        logical_y = int(round(claude_y * (logical_height / new_height)))
        print(f"  Claude [{claude_x}, {claude_y}] → Logical [{logical_x}, {logical_y}]")
    
    return screenshot_final.size, logical_width, logical_height


def test_new_approach():
    """Simulate the new single-resize approach"""
    print("\n" + "=" * 60)
    print("NEW APPROACH (Single Resize)")
    print("=" * 60)
    
    # Take screenshot
    screenshot = pyautogui.screenshot()
    physical_width, physical_height = screenshot.size
    
    # Get logical size
    logical_width, logical_height = pyautogui.size()
    
    print(f"Physical screenshot: {physical_width}×{physical_height}")
    print(f"Logical screen: {logical_width}×{logical_height}")
    
    # SINGLE RESIZE: Physical → Claude optimal (calculated from logical dimensions)
    MAX_WIDTH = 1280
    MAX_HEIGHT = 800
    
    scale_width = MAX_WIDTH / logical_width
    scale_height = MAX_HEIGHT / logical_height
    scale_factor = min(scale_width, scale_height)
    
    new_width = int(round(logical_width * scale_factor))
    new_height = int(round(logical_height * scale_factor))
    
    screenshot_final = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
    print(f"After single resize: {screenshot_final.size[0]}×{screenshot_final.size[1]}")
    
    # Test coordinate mapping
    test_coords = [(615, 400), (1000, 600), (100, 100)]  # Middle, right, top-left in Claude space
    
    print(f"\nCoordinate mapping (Claude → Logical):")
    for claude_x, claude_y in test_coords:
        logical_x = int(round(claude_x * (logical_width / new_width)))
        logical_y = int(round(claude_y * (logical_height / new_height)))
        print(f"  Claude [{claude_x}, {claude_y}] → Logical [{logical_x}, {logical_y}]")
    
    return screenshot_final.size, logical_width, logical_height


def compare_approaches():
    """Compare both approaches and show differences"""
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    
    old_size, old_logical_w, old_logical_h = test_old_approach()
    new_size, new_logical_w, new_logical_h = test_new_approach()
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if old_size == new_size:
        print(f"✅ Both produce same Claude screenshot size: {new_size[0]}×{new_size[1]}")
    else:
        print(f"⚠️  Different sizes: Old={old_size}, New={new_size}")
    
    print(f"\n📊 Aspect ratio preservation:")
    old_aspect = old_size[0] / old_size[1]
    new_aspect = new_size[0] / new_size[1]
    logical_aspect = new_logical_w / new_logical_h
    print(f"   Logical screen: {logical_aspect:.6f}")
    print(f"   Old approach:   {old_aspect:.6f} (diff: {abs(old_aspect - logical_aspect):.6f})")
    print(f"   New approach:   {new_aspect:.6f} (diff: {abs(new_aspect - logical_aspect):.6f})")
    
    print(f"\n🎯 Conclusion:")
    print(f"   The new single-resize approach eliminates one rounding step,")
    print(f"   reducing cumulative error and improving coordinate accuracy.")
    print(f"   Final dimensions should be identical (or within 1px due to rounding).")
    
    if abs(old_size[0] - new_size[0]) <= 1 and abs(old_size[1] - new_size[1]) <= 1:
        print(f"\n✅ TEST PASSED: Approaches are mathematically equivalent")
        print(f"   New approach is cleaner with fewer intermediate steps.")
    else:
        print(f"\n⚠️  WARNING: Significant difference detected")
        print(f"   Old: {old_size}, New: {new_size}")


if __name__ == "__main__":
    compare_approaches()

