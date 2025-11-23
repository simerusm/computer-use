# Coordinate System - Correct Implementation

## The Flow (Following Claude's Recommendations)

### 1. **Screenshot Capture & Scaling** (in `agent.py`)
```
Physical pixels: 3024x1964 (Retina display)
       ↓ scale by 0.5
Logical pixels: 1512x982 (PyAutoGUI coordinates)
       ↓ scale to fit in 1280x800 (WXGA - Claude optimal)
Claude screenshot: 1231x800 (maintains aspect ratio)
```

**Scale factor** = 1231/1512 = **0.814**

### 2. **Claude Configuration** (in `orchestrator.py`)
```python
# Tell Claude the screen size MATCHES the screenshots
claude_client = ClaudeComputerClient(
    screen_width=1231,   # Same as screenshot width
    screen_height=800    # Same as screenshot height
)
```

✅ **Key Insight**: `display_width_px` and `display_height_px` should match the screenshot dimensions Claude receives, NOT the actual screen size!

### 3. **Claude Returns Coordinates**
- Claude sees screenshots at: **1231x800**
- Claude thinks screen is: **1231x800**  
- Claude returns coordinates in: **1231x800 space**
- Example: `[615, 400]` = center of screen in Claude's view

### 4. **Coordinate Scaling** (in `orchestrator.py`)
```python
# Scale UP from Claude space to PyAutoGUI space
logical_x = claude_x / scale_factor  # 615 / 0.814 = 756
logical_y = claude_y / scale_factor  # 400 / 0.814 = 491
```

**Formula**: `logical_coord = claude_coord / 0.814` (scale UP by ~1.23x)

### 5. **PyAutoGUI Execution**
- PyAutoGUI uses: **1512x982 space** (logical coordinates)
- Clicks at the scaled-up coordinates
- Everything aligns perfectly! ✅

## Why This Works

| Component | Coordinate Space | Size |
|-----------|-----------------|------|
| Physical Display | 3024x1964 | Retina pixels |
| **PyAutoGUI** | **1512x982** | **Logical pixels** |
| Screenshots sent to Claude | 1231x800 | Scaled for efficiency |
| **Claude's tool config** | **1231x800** | **Matches screenshots** |
| Claude's returned coordinates | 1231x800 | Same as input |
| **Final PyAutoGUI coords** | **1512x982** | **Scaled UP by 1.23x** |

## Benefits

1. ✅ **Follows Claude's recommendations**: Screenshots ≤ 1280x800 for best accuracy
2. ✅ **Consistent coordinate system**: Claude sees and returns coords in same space
3. ✅ **Simple scaling**: Single multiplication to convert to PyAutoGUI space
4. ✅ **Maintains aspect ratio**: No image distortion

## Example

Claude sees a button at `(1000, 650)` in 1231x800 screenshot:

```python
# Scale UP to logical space
logical_x = 1000 / 0.814 = 1229
logical_y = 650 / 0.814 = 799

# PyAutoGUI clicks at (1229, 799) on the 1512x982 screen ✓
```

## Testing

Run the orchestrator and verify the logs:
```bash
python orchestrator.py
```

You should see:
```
✓ Actual logical screen size: 1512x982
✓ Screenshots scaled to: 1231x800 (fits in Claude's optimal 1280x800)
✓ Scale factor: 0.814 (screenshot/logical)
✓ Claude tool config: display_width_px=1231, display_height_px=800
✓ Claude will return coordinates in 1231x800 space
✓ We'll scale coordinates UP to 1512x982 for PyAutoGUI
```

When Claude clicks:
```
📐 Coordinate scaling: [615, 400] (Claude space) → [756, 491] (PyAutoGUI space, scale: 1.23x)
```
