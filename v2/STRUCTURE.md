# v2 Project Structure

## 📁 Directory Layout

```
v2/
│
├── main.py                  # 🎯 Main orchestrator (220 lines)
│   ├── ComputerUseAgent class
│   │   ├── __init__()      # Initialize agent, logger, client
│   │   ├── execute_tool()  # Execute single action
│   │   └── run()           # Main execution loop
│   └── main()              # Entry point
│
├── agent.py                 # 🤖 Desktop interaction (200 lines)
│   └── DesktopAgent class
│       ├── __init__()           # Setup PyAutoGUI
│       ├── get_screen_size()    # Get screen dimensions
│       ├── scale_coordinates()  # Claude space → Screen space
│       ├── take_screenshot()    # Capture + resize + save
│       ├── mouse_move()         # Move mouse
│       ├── left_click()         # Left click
│       ├── right_click()        # Right click
│       ├── double_click()       # Double click
│       ├── type_text()          # Type text
│       ├── press_key()          # Press keyboard key(s)
│       └── wait()               # Wait for duration
│
├── logger.py                # 📝 Comprehensive logging (150 lines)
│   ├── SessionLogger class
│   │   ├── __init__()              # Create session log file
│   │   ├── log_event()             # Write to JSONL
│   │   ├── log_user_prompt()       # Log initial task
│   │   ├── log_iteration_start()   # Log iteration number
│   │   ├── log_claude_thinking()   # Log text responses
│   │   ├── log_tool_use()          # Log action request
│   │   ├── log_tool_result()       # Log action result
│   │   ├── log_api_error()         # Log API errors
│   │   ├── log_completion()        # Log task completion
│   │   └── log_stop_reason()       # Log why Claude stopped
│   └── ConsoleFormatter class
│       ├── header()            # Print header
│       ├── section()           # Print section
│       ├── success()           # Print success
│       ├── error()             # Print error
│       └── info()              # Print info
│
├── logs/                    # 📂 Output directory
│   └── session_YYYYMMDD_HHMMSS/  # Each session in its own folder
│       ├── session.jsonl         # Full session log
│       ├── screenshot_0.png      # Screenshots (numbered)
│       ├── screenshot_1.png
│       └── screenshot_2.png
│
├── .env                     # 🔐 Environment variables (not in git)
│   └── ANTHROPIC_API_KEY=sk-...
│
├── .gitignore              # 🚫 Git ignore rules
├── requirements.txt        # 📦 Python dependencies
├── README.md              # 📖 Main documentation
├── REFACTORING_SUMMARY.md # 📋 What changed and why
└── STRUCTURE.md           # 📐 This file
```

---

## 🔄 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           ComputerUseAgent.run(task)                 │    │
│  │                                                       │    │
│  │  1. User provides task                               │    │
│  │     │                                                 │    │
│  │     ↓                                                 │    │
│  │  2. Send to Claude API ──────────┐                  │    │
│  │     │                              │                  │    │
│  │     ↓                              │                  │    │
│  │  3. Claude responds                │                  │    │
│  │     ├─ Text (thinking)             │                  │    │
│  │     └─ Tool use (actions)          │                  │    │
│  │         │                           │                  │    │
│  │         ↓                           │                  │    │
│  │  4. Execute tools ────────┐        │                  │    │
│  │     │                      │        │                  │    │
│  │     ↓                      │        │                  │    │
│  │  5. Get results            │        │                  │    │
│  │     │                      │        │                  │    │
│  │     ↓                      │        │                  │    │
│  │  6. Send back to Claude ──┘        │                  │    │
│  │     │                               │                  │    │
│  │     └─ Repeat until complete       │                  │    │
│  │                                     │                  │    │
│  └─────────────────────────────────────┼──────────────────┘    │
│                                        │                       │
└────────────────────────────────────────┼───────────────────────┘
                                         │
            ┌────────────────────────────┼────────────────────────────┐
            │                            │                            │
            ↓                            ↓                            ↓
    ┌───────────────┐           ┌───────────────┐          ┌────────────────┐
    │  agent.py     │           │  logger.py    │          │  logs/         │
    │               │           │               │          │  session_*/    │
    │ • screenshot  │           │ • JSONL log   │          │                │
    │ • click       │◄──────────┤ • console     │─────────►│ • session.     │
    │ • type        │  actions  │   output      │  writes  │   jsonl        │
    │ • key press   │           │ • formatting  │          │ • screenshot_  │
    │ • coordinate  │           │ • session dir │          │   0.png        │
    │   scaling     │           │               │          │ • screenshot_  │
    │               │           │               │          │   1.png        │
    └───────────────┘           └───────────────┘          └────────────────┘
            │
            ↓
    ┌───────────────┐
    │  PyAutoGUI    │
    │               │
    │ • Move mouse  │
    │ • Click       │
    │ • Type        │
    │ • Press keys  │
    └───────────────┘
            │
            ↓
    ┌───────────────┐
    │  Desktop      │
    │  (macOS)      │
    └───────────────┘
```

---

## 🎭 Module Interactions

### main.py → agent.py

```python
# main.py creates agent
agent = DesktopAgent(TARGET_WIDTH, TARGET_HEIGHT, log_dir="logs")

# main.py calls agent methods
screenshot = agent.take_screenshot()
agent.left_click(x, y)
agent.type_text("hello")
agent.press_key("command+space")
```

### main.py → logger.py

```python
# main.py creates logger
logger = SessionLogger(log_dir="logs")

# main.py logs events
logger.log_user_prompt(task)
logger.log_iteration_start(iteration)
logger.log_claude_thinking(text_responses)
logger.log_tool_use(tool_name, tool_input, tool_id)
logger.log_completion(stop_reason, iterations)
```

### agent.py → logs/

```python
# agent saves screenshots
screenshot_path = self.log_dir / f"screenshot_{timestamp}_{count}.png"
screenshot_resized.save(screenshot_path)
```

### logger.py → logs/

```python
# logger writes JSONL
with open(self.session_file, 'a') as f:
    f.write(json.dumps(entry) + '\n')
```

---

## 📝 File Responsibilities

### main.py - Orchestrator

**Job:** Coordinate everything

**Responsibilities:**
- ✅ Initialize agent and logger
- ✅ Manage Claude API communication
- ✅ Execute tool use loop
- ✅ Handle errors
- ✅ Determine when to stop

**Does NOT:**
- ❌ Directly interact with desktop (that's agent.py)
- ❌ Format logs (that's logger.py)
- ❌ Save files (agent and logger do that)

### agent.py - Desktop Interface

**Job:** Interact with the desktop

**Responsibilities:**
- ✅ Take and resize screenshots
- ✅ Execute mouse actions
- ✅ Execute keyboard actions
- ✅ Scale coordinates
- ✅ Save screenshots to disk

**Does NOT:**
- ❌ Talk to Claude API (that's main.py)
- ❌ Manage conversation flow (that's main.py)
- ❌ Write session logs (that's logger.py)

### logger.py - Event Tracking

**Job:** Record everything that happens

**Responsibilities:**
- ✅ Write events to JSONL
- ✅ Format console output
- ✅ Track iteration numbers
- ✅ Provide structured logging

**Does NOT:**
- ❌ Execute actions (that's agent.py)
- ❌ Talk to Claude (that's main.py)
- ❌ Make decisions (just records)

---

## 🎯 Execution Flow

### 1. Initialization

```
User runs: python main.py
    ↓
main() function called
    ↓
ComputerUseAgent created
    ├─ Creates DesktopAgent
    ├─ Creates SessionLogger  
    └─ Initializes Anthropic client
    ↓
User enters task
    ↓
agent.run(task) called
```

### 2. Main Loop

```
Iteration N:
    │
    ├─ logger.log_iteration_start(N)
    │
    ├─ Send message to Claude API
    │   ├─ Messages history
    │   ├─ Tool definitions
    │   └─ Conversation context
    │
    ├─ Receive response
    │   ├─ Text (thinking)
    │   └─ Tool uses (actions)
    │
    ├─ Log text responses
    │   └─ logger.log_claude_thinking(texts)
    │
    ├─ For each tool use:
    │   ├─ logger.log_tool_use(...)
    │   ├─ execute_tool(...)
    │   │   └─ agent.{method}(...)
    │   │       └─ PyAutoGUI action
    │   ├─ logger.log_tool_result(...)
    │   └─ Collect result
    │
    ├─ Send results back to Claude
    │   └─ Add to messages history
    │
    └─ Check stop_reason
        ├─ tool_use → Continue loop
        ├─ end_turn → Complete
        └─ error → Log and exit
```

### 3. Completion

```
Task complete
    ↓
logger.log_completion(...)
    ↓
Display summary
    ├─ Stop reason
    ├─ Total iterations
    └─ Session log file
    ↓
Exit
```

---

## 🔍 Debugging Guide

### To Debug Coordinates

**Look at:**
1. Console output from `agent.py`:
   ```
   [Agent] Coordinate scaling: Claude [X,Y] → Screen [X',Y']
   [Agent]   Scale factors: X=..., Y=...
   ```

2. Screenshots in session folder:
   ```bash
   # Latest session
   ls -t logs/ | head -1 | xargs -I {} open logs/{}/screenshot_*.png
   
   # Specific session
   open logs/session_20251122_143022/screenshot_*.png
   ```

3. Tool use events in session log:
   ```bash
   # Latest session
   ls -t logs/ | head -1 | xargs -I {} cat logs/{}/session.jsonl | jq 'select(.event_type=="tool_use")'
   
   # Specific session
   cat logs/session_20251122_143022/session.jsonl | jq 'select(.event_type=="tool_use")'
   ```

### To Debug Claude's Thinking

**Look at:**
1. Console output:
   ```
   [Claude] Thinking:
   ────────────────────────────────────────
   [Claude's text response here]
   ────────────────────────────────────────
   ```

2. Session log:
   ```bash
   # Latest session
   ls -t logs/ | head -1 | xargs -I {} cat logs/{}/session.jsonl | jq -r 'select(.event_type=="claude_thinking") | .data.text_responses[]'
   
   # Specific session
   cat logs/session_20251122_143022/session.jsonl | jq -r 'select(.event_type=="claude_thinking") | .data.text_responses[]'
   ```

### To Debug Action Failures

**Look at:**
1. Console output from `agent.py`:
   ```
   [Agent] Left click at: ...
   [Agent]   ✓ Clicked at ...
   ```

2. Tool results in session log:
   ```bash
   # Latest session
   ls -t logs/ | head -1 | xargs -I {} cat logs/{}/session.jsonl | jq 'select(.event_type=="tool_result")'
   ```

3. Error events:
   ```bash
   # Latest session
   ls -t logs/ | head -1 | xargs -I {} cat logs/{}/session.jsonl | jq 'select(.event_type=="api_error")'
   ```

---

## 📊 Quick Reference

| Want to... | Edit this file... | Look at this section... |
|------------|-------------------|-------------------------|
| Add new action | `agent.py` | `DesktopAgent` methods |
| Change logging | `logger.py` | `SessionLogger` methods |
| Modify loop | `main.py` | `ComputerUseAgent.run()` |
| Change resolution | `main.py` | `TARGET_WIDTH`, `TARGET_HEIGHT` |
| Add API features | `main.py` | `client.beta.messages.create()` |
| Debug coordinates | `agent.py` | `scale_coordinates()` |
| Track new events | `logger.py` | Add new `log_*()` method |

---

**Pro tip:** Start reading from `main.py` → `agent.py` → `logger.py` to understand the full flow! 📖

