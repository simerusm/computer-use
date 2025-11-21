# Computer Use Desktop Agent

A simple desktop agent that allows you to type in a task and it will autonomously execute it using Claude's computer use capabilities.

## Features

- **Desktop Control**: Screenshot, click, type, and keyboard actions
- **Claude Integration**: Uses Claude's computer use API (beta) for autonomous task execution
- **HTTP/WebSocket API**: Orchestrator service for task coordination
- **Logging**: Comprehensive logging of all actions and screenshots
- **Attended Mode**: Watch the agent work in real-time on your desktop

> **Note**: Computer use is currently in beta. This implementation uses the `computer-use-2025-01-24` beta header with Claude 3.5 Sonnet (claude-3-5-sonnet-20241022).

## Architecture

```
┌─────────────────┐
│  Claude API     │  (Task understanding & planning)
└────────┬────────┘
         │
┌────────▼────────┐
│  Orchestrator   │  (HTTP/WebSocket service)
└────────┬────────┘
         │
┌────────▼────────┐
│ Desktop Agent   │  (Screen control)
└─────────────────┘
```

## Installation

1. **Clone or navigate to the project directory**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:

Create a `.env` file in the project root:
```bash
ANTHROPIC_API_KEY=your_api_key_here
ORCHESTRATOR_HOST=localhost
ORCHESTRATOR_PORT=8000
```

4. **Grant accessibility permissions** (macOS):
   - System Preferences → Security & Privacy → Privacy → Accessibility
   - Add Terminal or your Python interpreter to allowed apps

## Quick Start

### 1. Start the Orchestrator

```bash
python orchestrator.py
```

The orchestrator will start on `http://localhost:8000`. You can view the API docs at `http://localhost:8000/docs`.

### 2. Run the Example Task

In a new terminal:

```bash
python example_notepad.py
```

This will execute the example task: "Open TextEdit/Notepad and type 'Hello from Claude'"

**Note**: The agent will control your mouse and keyboard. Make sure you're ready!

## Usage

### Using Claude Integration (Autonomous Mode)

With Claude integration, the agent can understand and execute complex tasks:

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/task",
        json={
            "task": "Open TextEdit and type 'Hello from Claude'",
            "max_iterations": 15
        },
        timeout=120.0
    )
    result = response.json()
    print(f"Task completed: {result['success']}")
```

### Manual Action Execution

You can also execute individual actions:

```python
import httpx

async with httpx.AsyncClient() as client:
    # Take a screenshot
    response = await client.post("http://localhost:8000/screenshot")
    screenshot = response.json()
    
    # Click at coordinates
    response = await client.post(
        "http://localhost:8000/action",
        json={
            "action": "left_click",
            "coordinate": [100, 200]
        }
    )
    
    # Type text
    response = await client.post(
        "http://localhost:8000/action",
        json={
            "action": "type",
            "text": "Hello, World!"
        }
    )
    
    # Press a key
    response = await client.post(
        "http://localhost:8000/action",
        json={
            "action": "key",
            "text": "return"
        }
    )
```

### WebSocket for Real-time Updates

```python
import websockets
import json

async with websockets.connect("ws://localhost:8000/ws") as websocket:
    # Receive real-time action updates
    async for message in websocket:
        data = json.loads(message)
        print(f"Event: {data['type']}")
```

## API Endpoints

### HTTP Endpoints

- `GET /` - Service info
- `GET /health` - Health check
- `POST /screenshot` - Take a screenshot
- `POST /action` - Execute a single action
- `POST /task` - Execute a task using Claude
- `GET /logs/summary` - Get session summary

### WebSocket

- `WS /ws` - Real-time action updates

## Available Actions

The agent supports the following actions:

### Computer Actions (used by Claude)
- `screenshot` - Capture the screen
- `mouse_move` - Move mouse to coordinates
- `left_click` - Left click at coordinates
- `right_click` - Right click at coordinates
- `double_click` - Double click at coordinates
- `type` - Type text
- `key` - Press a key (e.g., "return", "command+c")

### Keyboard Keys

Common keys you can use:
- `return` / `enter`
- `space`
- `escape`
- `tab`
- Arrow keys: `up`, `down`, `left`, `right`
- Modifiers: `shift`, `command` (macOS), `ctrl`, `alt`
- Combos: `command+c`, `ctrl+v`, etc.

## Logging

All actions and screenshots are logged to the `logs/` directory:

- `logs/session_TIMESTAMP.jsonl` - JSON lines log of all actions
- `logs/screenshot_TIMESTAMP_N.png` - Screenshots taken during execution

View session summary:
```bash
curl http://localhost:8000/logs/summary
```

## Platform Support

- **macOS**: Fully supported (tested on macOS 14+)
- **Windows**: Should work (not tested yet)
- **Linux**: Should work with X11 or Wayland

## Safety Features

- **Failsafe**: Move mouse to screen corner to abort (pyautogui.FAILSAFE)
- **Action delays**: 0.5s pause between actions to prevent issues
- **Coordinate validation**: Ensures clicks are within screen bounds
- **Attended mode**: You can watch and intervene if needed

## Troubleshooting

### "Agent not initialized" error
- Make sure the orchestrator is running: `python orchestrator.py`

### "Claude client not available" error
- Set `ANTHROPIC_API_KEY` in your `.env` file
- Verify the API key is valid

### Accessibility permissions error (macOS)
- Grant accessibility permissions to Terminal/Python in System Preferences

### Agent is too slow
- Adjust `pyautogui.PAUSE` in `agent.py` (currently 0.5 seconds)

### Actions are not working
- Check the logs in `logs/session_*.jsonl` for detailed error messages
- Ensure screen coordinates are correct for your display

## Example Tasks

Here are some tasks you can try:

1. **Simple text editing**:
   - "Open TextEdit and type 'Hello from Claude'"
   - "Open Calculator and compute 15 * 23"

2. **File operations**:
   - "Create a new text file named 'test.txt' and write 'This is a test' in it"

3. **Web browsing**:
   - "Open Safari and navigate to google.com"

4. **Application control**:
   - "Open System Preferences and show Display settings"

**Note**: Complex tasks work better with higher `max_iterations` values.

## Development

### Project Structure

```
computer-use/
├── agent.py              # Desktop agent (screenshot, click, type)
├── orchestrator.py       # HTTP/WebSocket service
├── claude_client.py      # Claude API integration
├── logger.py            # Action logging
├── example_notepad.py   # Example task
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── logs/               # Action logs and screenshots
```

### Adding New Actions

To add a new action to the agent:

1. Add method to `DesktopAgent` class in `agent.py`
2. Update `execute_action()` method to handle the new action
3. Test with manual action execution via `/action` endpoint

### Extending Claude Integration

The orchestrator supports these Claude tools:
- `computer_20241022` - Computer control (implemented)
- `text_editor_20241022` - Text editing (not implemented)
- `bash_20241022` - Bash commands (not implemented)

You can extend the orchestrator to handle additional tools.

## Contributing

This is a simple example project. Feel free to:
- Add more sophisticated error handling
- Implement retry logic for failed actions
- Add support for more computer use tools
- Improve the UI with a web frontend
- Add support for unattended mode with sandboxing

## License

MIT License - feel free to use and modify as needed.

## Disclaimer

This agent can control your computer. Use with caution:
- Only run trusted tasks
- Don't use in production without proper sandboxing
- Keep the failsafe enabled (move mouse to corner to abort)
- Review the code before running

## Resources

- [Anthropic Computer Use Documentation](https://docs.anthropic.com/claude/docs/computer-use)
- [PyAutoGUI Documentation](https://pyautogui.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

