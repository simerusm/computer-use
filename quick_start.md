# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Or use the setup script:
```bash
./setup.sh
```

## Step 2: Configure API Key

Create a `.env` file with your Anthropic API key:

```bash
echo "ANTHROPIC_API_KEY=your_actual_key_here" > .env
echo "ORCHESTRATOR_HOST=localhost" >> .env
echo "ORCHESTRATOR_PORT=8000" >> .env
```

Get your API key from: https://console.anthropic.com/

## Step 3: Grant Permissions (macOS only)

1. Open **System Preferences** → **Security & Privacy** → **Privacy** → **Accessibility**
2. Click the lock icon and authenticate
3. Add **Terminal** (or your Python interpreter) to the list
4. Check the box to enable it

## Step 4: Test the Agent

Run the basic test:

```bash
python test_agent.py
```

This will:
- ✓ Check screen size
- ✓ Take a screenshot
- ✓ Test mouse movement
- ✓ Create log files

## Step 5: Start the Orchestrator

In one terminal window:

```bash
python orchestrator.py
```

You should see:
```
Starting Computer Use Orchestrator on localhost:8000
API docs available at http://localhost:8000/docs
```

## Step 6: Run the Example

In another terminal window:

```bash
python example_notepad.py
```

This will:
1. Connect to the orchestrator
2. Ask Claude to open TextEdit/Notepad
3. Type "Hello from Claude"
4. Save screenshots and logs

**Watch your screen!** The agent will control your mouse and keyboard.

## What's Next?

### Try Other Tasks

Edit `example_notepad.py` and change the task:

```python
task = "Open Calculator and compute 15 * 23"
# or
task = "Open Safari and search for 'Python tutorials'"
```

### View the API

While the orchestrator is running, visit:
- http://localhost:8000 - Status
- http://localhost:8000/docs - Interactive API documentation

### Check the Logs

All actions are logged in the `logs/` directory:

```bash
ls -la logs/
cat logs/session_*.jsonl | jq '.'
open logs/screenshot_*.png
```

### Manual Control

Send individual actions via the API:

```bash
# Take a screenshot
curl -X POST http://localhost:8000/screenshot

# Type some text  
curl -X POST http://localhost:8000/action \
  -H "Content-Type: application/json" \
  -d '{"action": "type", "text": "Hello!"}'

# Get session summary
curl http://localhost:8000/logs/summary
```

## Troubleshooting

### "Cannot connect to orchestrator"
→ Make sure `python orchestrator.py` is running in another terminal

### "Claude client not available"
→ Check your `.env` file has a valid `ANTHROPIC_API_KEY`

### "Permission denied" errors (macOS)
→ Grant Accessibility permissions in System Preferences

### Actions are not working
→ Check `logs/session_*.jsonl` for error details

## Safety Tips

- **Failsafe**: Move your mouse to any screen corner to abort
- **Watch closely**: This is attended mode - you can see everything
- **Start simple**: Test with simple tasks first
- **Review code**: Read the code before running on important systems

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore the API at http://localhost:8000/docs
3. Try more complex tasks
4. Customize the agent for your needs

Happy automating! 🤖

