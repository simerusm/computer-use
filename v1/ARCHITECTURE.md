# Architecture Documentation

## System Overview

The Computer Use Desktop Agent is a three-tier system that enables Claude AI to autonomously control your desktop.

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│  (HTTP API, WebSocket, CLI)                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Orchestrator Layer                         │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  FastAPI Service (orchestrator.py)                      │  │
│  │  - HTTP REST API endpoints                              │  │
│  │  - WebSocket for real-time updates                      │  │
│  │  - Task coordination and execution loop                 │  │
│  └─────────────────────────────────────────────────────────┘  │
│                         │                │                       │
│          ┌──────────────┴────────┐       └──────────┐          │
│          ▼                       ▼                   ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   Claude     │    │   Logger     │    │   Action     │     │
│  │   Client     │    │              │    │   Queue      │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Desktop Agent Layer                         │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  DesktopAgent (agent.py)                                │  │
│  │  - Screenshot capture                                    │  │
│  │  - Mouse control (move, click)                          │  │
│  │  - Keyboard control (type, keypress)                    │  │
│  │  - Action execution and validation                      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                         │                                        │
│          ┌──────────────┴────────────────┐                     │
│          ▼                                ▼                     │
│  ┌──────────────┐                ┌──────────────┐             │
│  │  PyAutoGUI   │                │    Pillow    │             │
│  │  (Control)   │                │  (Images)    │             │
│  └──────────────┘                └──────────────┘             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Operating System                           │
│  (macOS / Windows / Linux)                                     │
│  - Screen capture APIs                                         │
│  - Input event injection                                       │
│  - Accessibility framework                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Desktop Agent (`agent.py`)

**Purpose**: Low-level interface to the operating system for screen control.

**Key Classes**:
- `DesktopAgent`: Main agent class

**Capabilities**:
- `screenshot()`: Capture screen as PNG
- `click(x, y)`: Click at coordinates
- `type_text(text)`: Type text
- `key_press(key)`: Press keyboard keys
- `move_mouse(x, y)`: Move mouse cursor
- `execute_action(action)`: Execute action from dictionary

**Dependencies**:
- `pyautogui`: Cross-platform GUI automation
- `PIL/Pillow`: Image processing

**Safety Features**:
- Coordinate validation
- Failsafe (move to corner to abort)
- Configurable delays between actions

### 2. Orchestrator (`orchestrator.py`)

**Purpose**: Coordinates between Claude AI and the Desktop Agent.

**Key Components**:
- FastAPI web service
- WebSocket server for real-time updates
- Task execution loop
- Action queue management

**API Endpoints**:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| POST | `/screenshot` | Take screenshot |
| POST | `/action` | Execute single action |
| POST | `/task` | Execute task via Claude |
| GET | `/logs/summary` | Get session summary |
| WS | `/ws` | WebSocket for updates |

**Task Execution Flow**:
```
1. Receive task request
2. Take initial screenshot
3. Send to Claude with task description
4. Loop until task complete or max iterations:
   a. Receive tool use from Claude
   b. Execute action via Desktop Agent
   c. Log action and result
   d. Send result back to Claude
   e. Broadcast update via WebSocket
5. Return final result
```

### 3. Claude Client (`claude_client.py`)

**Purpose**: Interface to Anthropic's Claude API with computer use tools.

**Key Classes**:
- `ClaudeComputerClient`: Claude API wrapper

**Features**:
- Manages conversation history
- Formats screenshots for Claude
- Parses tool use responses
- Handles multi-turn conversations

**Claude Tools**:
- `computer_20241022`: Computer control (screenshot, click, type)
- `text_editor_20241022`: Text editing (not implemented)
- `bash_20241022`: Shell commands (not implemented)

**API Model**: `claude-3-5-sonnet-20241022`

### 4. Logger (`logger.py`)

**Purpose**: Comprehensive logging of all actions and events.

**Key Classes**:
- `ActionLogger`: Action and event logger

**Features**:
- JSONL format logs (one JSON per line)
- Screenshot archival
- Session tracking
- Action statistics

**Log Types**:
- Session start/end
- Actions and results
- Messages and errors
- Task start/complete

**Log Location**: `logs/session_TIMESTAMP.jsonl`

## Data Flow

### Autonomous Task Execution

```
User
  │
  │ POST /task {"task": "Open Notepad"}
  │
  ▼
Orchestrator
  │
  │ 1. Take screenshot
  │
  ▼
Claude API
  │ "I need to open Start Menu"
  │ tool_use: click([10, 1070])
  │
  ▼
Orchestrator
  │
  │ 2. Execute click action
  │
  ▼
Desktop Agent
  │ pyautogui.click(10, 1070)
  │
  ▼
OS (Click Start Button)
  │
  │ 3. Take new screenshot
  │
  ▼
Claude API
  │ "Now I'll type 'notepad'"
  │ tool_use: type("notepad")
  │
  ▼
... (continues until task complete)
```

### Manual Action Execution

```
User
  │
  │ POST /action {"action": "type", "text": "Hello"}
  │
  ▼
Orchestrator
  │
  ▼
Desktop Agent
  │ pyautogui.write("Hello")
  │
  ▼
OS (Types text)
  │
  │ Return result
  │
  ▼
User
```

## Communication Protocols

### HTTP REST API

- **Format**: JSON
- **Authentication**: None (local only)
- **Timeouts**: 30s for actions, 120s for tasks

### WebSocket

- **Protocol**: ws://
- **Messages**: JSON
- **Purpose**: Real-time action updates

**Message Types**:
```json
{
  "type": "connected",
  "message": "Connected to orchestrator",
  "timestamp": "2024-11-21T10:30:00"
}

{
  "type": "action_executed",
  "action": {"action": "type", "text": "Hello"},
  "result": {"success": true, "length": 5}
}
```

## Security Considerations

### Current Implementation (Attended Mode)

- **No authentication**: Local use only
- **No sandboxing**: Full system access
- **No rate limiting**: Unlimited actions
- **Visibility**: All actions visible to user

### Safety Mechanisms

1. **Failsafe**: Move mouse to corner to abort
2. **Attended mode**: User can intervene anytime
3. **Coordinate validation**: Prevents out-of-bounds clicks
4. **Action delays**: Prevents rapid-fire actions
5. **Logging**: Full audit trail

### For Production Use

To make this production-ready, you would need:

1. **Authentication**: API keys, OAuth
2. **Sandboxing**: Restricted file/network access
3. **Rate limiting**: Prevent abuse
4. **Action whitelist**: Only allow specific actions
5. **Permissions system**: Fine-grained control
6. **Monitoring**: Action anomaly detection
7. **Encryption**: TLS for all communication

## Performance Characteristics

### Latency

- **Screenshot**: ~100-200ms (depends on resolution)
- **Click action**: ~50-100ms
- **Type action**: ~50ms per character
- **Claude API call**: ~1-3 seconds
- **Full task iteration**: ~2-5 seconds

### Resource Usage

- **Memory**: ~100MB base + ~50MB per conversation turn
- **CPU**: Low (< 5%) except during screenshots
- **Disk**: ~1MB per screenshot, ~10KB per log entry
- **Network**: ~1-2MB per Claude API call

### Scalability

Current limitations:
- Single desktop at a time
- Sequential action execution
- No action queuing
- Limited to one task at a time

## Error Handling

### Agent Layer

- Invalid coordinates → Return error, don't execute
- PyAutoGUI failure → Return error with details
- Screenshot failure → Retry once, then fail

### Orchestrator Layer

- Agent not initialized → HTTP 500
- Claude API error → Return error, preserve logs
- Timeout → Cancel task, return partial results

### Recovery

- Each action is independent
- Conversation history preserved
- Logs enable post-mortem analysis

## Extension Points

### Adding New Actions

1. Add method to `DesktopAgent`
2. Update `execute_action()` dispatcher
3. Document in API

### Adding New Tools

1. Add tool definition to `claude_client.py`
2. Add handler in orchestrator task loop
3. Test with Claude

### Adding Authentication

1. Add middleware to FastAPI
2. Implement API key validation
3. Update client examples

## Testing Strategy

### Unit Tests (Not Implemented)

- Agent action validation
- Logger output format
- Claude client message formatting

### Integration Tests

- `test_agent.py`: Basic agent functionality
- `example_notepad.py`: End-to-end task

### Manual Testing

1. Run test_agent.py
2. Start orchestrator
3. Run example task
4. Verify logs and screenshots

## Deployment

### Local Development

```bash
python orchestrator.py
python example_notepad.py
```

### Docker (Not Implemented)

Would need:
- X11 forwarding or VNC
- Accessibility permissions
- GUI environment

### Cloud (Not Recommended)

This is designed for local use. Cloud deployment would require:
- Virtual desktop (VNC/RDP)
- Headless mode
- Security hardening

## Future Enhancements

### Planned

- [ ] Web-based UI for task submission
- [ ] Action queue with priorities
- [ ] Multi-desktop support
- [ ] Recording and replay
- [ ] Visual action confirmation
- [ ] Better error recovery

### Nice to Have

- [ ] Computer vision for element detection
- [ ] Browser-specific automation
- [ ] Mobile device support
- [ ] Collaborative sessions
- [ ] Action templates

## Dependencies

See `requirements.txt` for versions.

**Core**:
- `anthropic`: Claude API client
- `fastapi`: Web framework
- `pyautogui`: Desktop automation
- `pillow`: Image processing

**Supporting**:
- `uvicorn`: ASGI server
- `websockets`: WebSocket support
- `httpx`: HTTP client
- `pydantic`: Data validation
- `python-dotenv`: Environment variables

## License

MIT - Use at your own risk

## Contributing

To contribute:
1. Test on your platform
2. Add error handling
3. Document changes
4. Submit PR

## Support

For issues:
1. Check logs in `logs/`
2. Read troubleshooting in README.md
3. Verify accessibility permissions
4. Test with `test_agent.py`

