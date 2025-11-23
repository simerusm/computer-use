# Quick Start Guide - v2

Get up and running in 2 minutes! ⚡

---

## Step 1: Install Dependencies

```bash
cd v2
pip install -r requirements.txt
```

**What gets installed:**
- `anthropic` - Claude API client
- `pyautogui` - Desktop automation
- `pillow` - Image processing
- `python-dotenv` - Environment variables

---

## Step 2: Set API Key

Create a `.env` file:

```bash
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

**Get your key:** https://console.anthropic.com/

---

## Step 3: Run It!

```bash
python main.py
```

**You'll see:**
```
============================================================
           Simple Computer Use Agent v2
============================================================

  • Model: claude-sonnet-4-20250514
  • Screen size: (1800, 1169)
  • Virtual size for Claude: 1024x768

Enter your task (or press Enter for default):
Default: Open calculator via spotlight and calculate 5+3

Task: 
```

Press **Enter** for the default task, or type your own!

---

## Step 4: Watch It Work! 👀

The agent will:
1. Take screenshots
2. Send to Claude
3. Execute actions (mouse, keyboard)
4. Log everything to console + files

**Look for:**
- 📸 Screenshot actions
- 🤖 Claude's thinking
- 🖱️ Mouse movements
- ⌨️ Keyboard actions
- ✅ Success confirmations

---

## Step 5: Check the Logs

After completion:

```bash
# List all sessions (newest first)
ls -lt logs/

# View latest session log
ls -t logs/ | head -1 | xargs -I {} cat logs/{}/session.jsonl | jq .

# View screenshots from latest session
ls -t logs/ | head -1 | xargs -I {} open logs/{}/screenshot_*.png

# Or view a specific session
cat logs/session_20251122_143022/session.jsonl | jq .
open logs/session_20251122_143022/screenshot_*.png
```

---

## Example Tasks to Try

### Easy (Start Here)
```
Open calculator and compute 5+3
```

### Medium
```
Open Notes app and type 'Hello World'
```

```
Take a screenshot of my desktop
```

### Advanced
```
Open Safari and navigate to google.com
```

```
Open Dictionary app and search for 'computer'
```

---

## Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "API key not found"
Make sure `.env` file exists:
```bash
cat .env
```

Should show:
```
ANTHROPIC_API_KEY=sk-...
```

### "Can't find agent.py"
Make sure you're in the v2 directory:
```bash
cd v2
ls -la  # Should see agent.py, logger.py, main.py
```

### Coordinates are off
Check console output for:
```
[Agent] Coordinate scaling: ...
```

This shows the transformation from Claude space to screen space.

### Claude is hallucinating
Try simpler tasks first:
- ✅ Calculator
- ✅ Notes
- ❌ Complex web navigation (needs refinement)

---

## What You Should See

### Successful Run
```
============================================================
                       ITERATION 1
============================================================

[Main] Sending request to Claude (iteration 1)...

[Claude] Stop reason: tool_use

[Claude] Thinking:
────────────────────────────────────────────────────────────
I'll take a screenshot first to see the current state...
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
[Agent]   Mapped keys: ['command', 'space']
[Agent]   ✓ Pressed command+space

... [continues] ...

============================================================
                      TASK COMPLETED
============================================================
Stop reason: end_turn
Total iterations: 8
Session log: logs/session_20251122_143022.jsonl
============================================================
```

---

## Next Steps

1. ✅ Try the default calculator task
2. ✅ Try a simple task of your own
3. ✅ Check the logs in `logs/`
4. ✅ Read `README.md` for details
5. ✅ Read `STRUCTURE.md` to understand the code

---

## Tips for Success

1. **Start simple** - Calculator, Notes, Spotlight
2. **Read the console** - It shows everything that's happening
3. **Check screenshots** - See what Claude saw
4. **Review session logs** - Understand the full flow
5. **Be patient** - Claude takes time to think

---

## Common Questions

**Q: How do I stop it?**  
A: Press `Ctrl+C` in the terminal

**Q: Can I change the resolution?**  
A: Yes, edit `TARGET_WIDTH` and `TARGET_HEIGHT` in `main.py`

**Q: Where are the logs?**  
A: In the `logs/` directory

**Q: Can I see what Claude saw?**  
A: Yes! Check `logs/screenshot_*.png`

**Q: Why is it clicking the wrong place?**  
A: Check coordinate scaling in console output. Might need resolution adjustment.

**Q: Can I use a different model?**  
A: Yes, set `MODEL_NAME` in `.env`:
```bash
echo "MODEL_NAME=claude-3-5-sonnet-20250115" >> .env
```

---

## Help & Documentation

- 📖 **Full docs:** `README.md`
- 📐 **Code structure:** `STRUCTURE.md`
- 📋 **What changed:** `REFACTORING_SUMMARY.md`
- 🐛 **Issues:** Check console output and `logs/session_*.jsonl`

---

**That's it! You're ready to go! 🚀**

Run `python main.py` and let Claude control your computer!

