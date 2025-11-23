# Simple Computer Use Agent v2 - Modular Edition

A clean, modular implementation of Claude's computer use capabilities with comprehensive logging.

## 🆕 What's New in This Version

- ✅ **Modular Design**: Separated into `agent.py`, `logger.py`, and `main.py`
- ✅ **Comprehensive Logging**: Detailed console output + JSONL session logs
- ✅ **Better Debugging**: See exactly what Claude is thinking and doing
- ✅ **Cleaner Code**: Each module has a single responsibility
- ✅ **Easy to Extend**: Add new actions or logging features easily

---

## 📁 Project Structure

```
v2/
├── main.py          # Main orchestrator (runs the agent)
├── agent.py         # Desktop interaction functions
├── logger.py        # Comprehensive logging
├── logs/            # Session logs and screenshots
│   ├── session_YYYYMMDD_HHMMSS.jsonl  # Full session log
│   └── screenshot_*.png                 # Screenshots taken
├── .env             # Your ANTHROPIC_API_KEY (not in repo)
└── README.md        # This file
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install anthropic pyautogui pillow python-dotenv
```

### 2. Set API Key

Create a `.env` file:
```bash
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### 3. Run It

```bash
python main.py
```

You'll be prompted for a task, or press Enter for the default (calculator demo).

---

## 📦 Modules Explained

### `main.py` - Orchestrator

**What it does:**
- Initializes the agent and logger
- Manages conversation with Claude
- Handles tool execution loop
- Coordinates between modules

**Key class:** `ComputerUseAgent`

**Key method:** `run(task)` - Main execution loop

### `agent.py` - Desktop Interaction

**What it does:**
- Takes screenshots
- Moves and clicks mouse
- Types text and presses keys
- Scales coordinates from Claude space to screen space

**Key class:** `DesktopAgent`

**Key methods:**
- `take_screenshot()` - Capture and resize screen
- `left_click(x, y)` - Click at coordinates
- `type_text(text)` - Type text
- `press_key(key)` - Press keyboard keys
- `scale_coordinates(x, y)` - Map Claude coords → Screen coords

### `logger.py` - Comprehensive Logging

**What it does:**
- Logs all events to JSONL file
- Formats console output beautifully
- Tracks iterations and actions
- Makes debugging easy

**Key class:** `SessionLogger`

**Key methods:**
- `log_user_prompt(prompt)` - Log initial task
- `log_claude_thinking(texts)` - Log Claude's reasoning
- `log_tool_use(...)` - Log tool execution
- `log_completion(...)` - Log session end

**Bonus:** `ConsoleFormatter` for pretty printing

---

## 🎯 How It Works

### 1. Initialization

```python
agent = ComputerUseAgent(TARGET_WIDTH, TARGET_HEIGHT)
```

- Creates `DesktopAgent` (handles actions)
- Creates `SessionLogger` (tracks everything)
- Initializes Claude API client

### 2. Task Execution

```python
agent.run("Open calculator and compute 5+3")
```

**The loop:**
1. Send message to Claude
2. Claude responds with:
   - **Text** (thinking/reasoning) → Logged
   - **Tool use** (actions) → Executed
3. Execute tools (screenshot, click, type, etc.)
4. Send results back to Claude
5. Repeat until task complete

### 3. Coordinate System

```
┌─────────────────────────────────────┐
│ Your Screen: 1800×1169 (example)    │
│                                      │
│  ┌──────────────────────────┐       │
│  │ Claude sees: 1024×768    │       │
│  │ (resized screenshot)     │       │
│  │                          │       │
│  │ Claude clicks: [512,384] │       │
│  │ (center of 1024×768)     │       │
│  └──────────────────────────┘       │
│         ↓ scale_coordinates()       │
│  Agent clicks: [900, 585]           │
│  (center of 1800×1169)              │
└─────────────────────────────────────┘
```

**Formula:**
```python
real_x = claude_x × (screen_width / target_width)
real_y = claude_y × (screen_height / target_height)
```

---

## 🔍 Logging Output

### Console Output

**Iteration header:**
```
============================================================
                       ITERATION 1
============================================================
```

**Claude thinking:**
```
[Claude] Thinking:
────────────────────────────────────────────────────────────
I need to open Spotlight search first using Cmd+Space...
────────────────────────────────────────────────────────────
```

**Tool execution:**
```
[Claude] Tool Use:
  Tool: computer
  Action: key
  Text: 'command+space'

[Agent] Key press: 'command+space'
[Agent]   Mapped keys: ['command', 'space']
[Agent]   ✓ Pressed command+space
```

**Screenshot:**
```
[Agent] Taking screenshot...
[Agent]   Original size: 3024x1964
[Agent]   Resized to: 1024x768
[Agent]   Converted RGBA → RGB
[Agent]   Saved to: screenshot_20251122_143022_0.png
```

**Coordinate mapping:**
```
[Agent] Left click at: [512, 384] (Claude space)
[Agent] Coordinate scaling: Claude [512, 384] → Screen [900, 585]
[Agent]   Scale factors: X=1.7578, Y=1.5221
[Agent]   ✓ Clicked at [900, 585]
```

### JSONL Session Log

Each session creates: `logs/session_YYYYMMDD_HHMMSS.jsonl`

**Example entries:**

```json
{"timestamp": "2025-11-22T14:30:20", "event_type": "session_start", "data": {...}}
{"timestamp": "2025-11-22T14:30:21", "event_type": "user_prompt", "data": {"prompt": "..."}}
{"timestamp": "2025-11-22T14:30:22", "event_type": "iteration_start", "data": {"iteration": 1}}
{"timestamp": "2025-11-22T14:30:23", "event_type": "claude_thinking", "data": {"text_responses": [...]}}
{"timestamp": "2025-11-22T14:30:24", "event_type": "tool_use", "data": {...}}
{"timestamp": "2025-11-22T14:30:25", "event_type": "tool_result", "data": {...}}
{"timestamp": "2025-11-22T14:30:50", "event_type": "session_complete", "data": {...}}
```

**Analyze with:**
```bash
# Count tool uses
cat logs/session_*.jsonl | grep tool_use | wc -l

# Extract Claude's thinking
cat logs/session_*.jsonl | jq -r 'select(.event_type=="claude_thinking") | .data.text_responses[]'

# Get all coordinates clicked
cat logs/session_*.jsonl | jq -r 'select(.event_type=="tool_use" and .data.action=="left_click") | .data.tool_input.coordinate'
```

---

## 🎨 Configuration

### Change Resolution

Edit `main.py`:
```python
TARGET_WIDTH = 1024   # Claude sees this width
TARGET_HEIGHT = 768   # Claude sees this height
```

**Recommended:**
- 1024×768 (default, works well)
- 1280×800 (Claude's optimal max)
- 800×600 (faster, less accurate)

### Change Model

Set in `.env`:
```bash
MODEL_NAME=claude-sonnet-4-20250514
# or
MODEL_NAME=claude-3-5-sonnet-20250115
```

### Adjust Max Iterations

Edit `main.py`:
```python
MAX_ITERATIONS = 50  # Safety limit
```

---

## 🐛 Debugging

### Enable Verbose Logging

All logging is already enabled! Just check:
1. **Console output** - Real-time feedback
2. **Session JSONL** - Full event history
3. **Screenshots** - Every screenshot saved to `logs/`

### Common Issues

**"Module not found"**
```bash
pip install anthropic pyautogui pillow python-dotenv
```

**"API key not found"**
```bash
echo "ANTHROPIC_API_KEY=sk-..." > .env
```

**"Coordinates off target"**
- Check your screen resolution
- Verify `TARGET_WIDTH` and `TARGET_HEIGHT` are set correctly
- Look for coordinate scaling logs in console

**"PyAutoGUI FAILSAFE triggered"**
- This happens when mouse hits screen corner
- Check coordinate mapping (might be scaling incorrectly)
- Increase `pyautogui.PAUSE` in `agent.py`

---

## 📊 Example Session

```
============================================================
           Simple Computer Use Agent v2
============================================================

  • Model: claude-sonnet-4-20250514
  • Screen size: (1800, 1169)
  • Virtual size for Claude: 1024x768

============================================================
                       USER PROMPT:
============================================================
Open calculator and compute 5+3
============================================================

============================================================
                       ITERATION 1
============================================================

[Main] Sending request to Claude (iteration 1)...

[Claude] Stop reason: tool_use

[Claude] Thinking:
────────────────────────────────────────────────────────────
I'll start by taking a screenshot to see the current state
of the screen, then open Spotlight search to launch Calculator.
────────────────────────────────────────────────────────────

[Claude] Tool Use:
  Tool: computer
  Action: screenshot

[Agent] Taking screenshot...
[Agent]   Original size: 3024x1964
[Agent]   Resized to: 1024x768
[Agent]   Saved to: screenshot_20251122_143022_0.png

============================================================
                       ITERATION 2
============================================================

[Claude] Tool Use:
  Tool: computer
  Action: key
  Text: 'command+space'

[Agent] Key press: 'command+space'
[Agent]   ✓ Pressed command+space

[... continues until task complete ...]

============================================================
                      TASK COMPLETED
============================================================
Stop reason: end_turn
Total iterations: 8
Session log: logs/session_20251122_143022.jsonl
============================================================
```

---

## 🆚 Compared to v1 (orchestrator + agent + claude_client)

| Feature | v1 | v2 (This) |
|---------|-----|-----------|
| Architecture | FastAPI server | Single process |
| Complexity | High (3 services) | Low (3 modules) |
| Logging | Basic | **Comprehensive** |
| Debugging | Hard | **Easy** |
| Setup | Complex | **Simple** |
| Real-time | WebSocket | Console |
| Use case | Production | **Development/Testing** |

**Use v2 when:**
- ✅ Learning how computer use works
- ✅ Debugging coordinate issues
- ✅ Testing new prompts/tasks
- ✅ Quick iterations

**Use v1 when:**
- ✅ Production deployment
- ✅ Need API/WebSocket access
- ✅ Multiple concurrent tasks
- ✅ Integration with other services

---

## 🔧 Extending

### Add New Action

Edit `agent.py`:
```python
def middle_click(self, x: int = None, y: int = None) -> str:
    """Middle click at coordinates"""
    print(f"\n[Agent] Middle click...")
    if x is not None and y is not None:
        real_x, real_y = self.scale_coordinates(x, y)
        pyautogui.click(real_x, real_y, button='middle')
    else:
        pyautogui.click(button='middle')
    return "middle clicked"
```

Then add to `main.py`:
```python
elif action == "middle_click":
    coords = tool_input.get("coordinate")
    if coords:
        return self.agent.middle_click(coords[0], coords[1])
    else:
        return self.agent.middle_click()
```

### Add Custom Logging

Edit `logger.py`:
```python
def log_custom_event(self, event_data: Dict):
    """Log custom event"""
    print(f"[Custom] {event_data}")
    self.log_event("custom", event_data)
```

---

## 🎯 Tips for Success

1. **Start small** - Test with simple tasks (calculator, notepad)
2. **Read the logs** - Console shows exactly what's happening
3. **Check coordinates** - Look for scaling output to debug clicks
4. **Iterate quickly** - Session logs make it easy to understand failures
5. **Use screenshots** - Check `logs/` to see what Claude saw

---

## 📄 Files Summary

| File | Lines | Purpose |
|------|-------|---------|
| `main.py` | ~220 | Orchestration & loop |
| `agent.py` | ~200 | Desktop actions |
| `logger.py` | ~150 | Logging & formatting |
| **Total** | **~570** | Clean & modular |

---

## 🚀 Next Steps

1. **Run it:** `python main.py`
2. **Try simple tasks:** Calculator, Notepad, Spotlight
3. **Check logs:** See what Claude is thinking
4. **Experiment:** Try different tasks and resolutions
5. **Debug:** Use session logs to understand behavior

---

**Happy automating! 🤖**

If you have questions, check the session logs in `logs/` - they contain everything that happened!
