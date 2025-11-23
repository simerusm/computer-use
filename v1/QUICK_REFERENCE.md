# Quick Reference Card

## Task Template (Copy-Paste Ready)

```
GOAL: [One sentence goal]

STEPS:
1. [Action]
   Verify: [What you expect to see]

2. [Action]
   Verify: [What you expect to see]

3. [Continue...]

SUCCESS: [Final state]
```

---

## Common Task Patterns

### Pattern: Open App
```
1. Press Cmd+Space to open Spotlight
   Verify: Spotlight search bar appears
2. Type exactly: [AppName]
   Verify: App appears in results
3. Press Enter to launch
   Verify: App window opens and is active
```

### Pattern: Search in App
```
1. [Open app steps above]
2. Click in the search field [describe location]
   Verify: Cursor blinking in field
3. Type exactly: [search term]
   Verify: Text appears in field
4. Press Enter to search
   Verify: Results appear
```

### Pattern: Type Text
```
1. [Open app steps]
2. Press Cmd+N for new document (if needed)
   Verify: Blank document ready
3. Type: [your text]
   Verify: Text appears as you type
```

### Pattern: Calculator Math
```
1. [Open Calculator]
2. Type numbers and operators using keyboard: 5+3=
   Verify: Result shows 8
OR
2. Click button [5], verify 5 in display
3. Click button [+], verify operator registered
4. Click button [3], verify 3 in display
5. Click button [=], verify result is 8
```

---

## Keyboard Shortcuts (Prefer Over Clicking!)

| Action | Shortcut | Reliability |
|--------|----------|-------------|
| Open Spotlight | `Cmd+Space` | ⭐⭐⭐⭐⭐ |
| New Window/Note | `Cmd+N` | ⭐⭐⭐⭐⭐ |
| Switch Apps | `Cmd+Tab` | ⭐⭐⭐⭐⭐ |
| Close Window | `Cmd+W` | ⭐⭐⭐⭐⭐ |
| Close Menu | `Escape` | ⭐⭐⭐⭐⭐ |
| Select All | `Cmd+A` | ⭐⭐⭐⭐⭐ |
| Copy | `Cmd+C` | ⭐⭐⭐⭐⭐ |
| Paste | `Cmd+V` | ⭐⭐⭐⭐⭐ |
| Find/Search | `Cmd+F` | ⭐⭐⭐⭐⭐ |
| Screenshot | `Cmd+Shift+3` | ⭐⭐⭐⭐⭐ |

---

## Success Checklist

Before running a task, verify:
- [ ] Task is broken into numbered steps
- [ ] Each step has a "Verify:" line
- [ ] App names are exact (e.g., "Dictionary" not "dictionary")
- [ ] You specify to press Enter after typing
- [ ] You check if app is in focus/active
- [ ] You have a clear SUCCESS criteria
- [ ] max_iterations is sufficient (25-35 for complex tasks)

---

## Troubleshooting

### Problem: App doesn't open
**Fix**: Add explicit steps:
```
1. Press Cmd+Space
2. Type "[exact app name]"
3. Press Enter
```

### Problem: Claude searches wrong thing
**Fix**: Be explicit about WHERE to type:
```
Type "oxymoron" in the Dictionary search field (not in Spotlight)
```

### Problem: App loses focus
**Fix**: Add verification:
```
3. Press Enter to launch Dictionary
   Verify: Dictionary window is open and active
   If not active, use Cmd+Tab to switch to Dictionary
```

### Problem: Can't find button/field
**Fix**: Describe location:
```
Click in the search field at the top of the window
```
Or use keyboard:
```
Press Cmd+F to activate search
```

### Problem: Task incomplete
**Fix**: 
- Increase `max_iterations` (try 35-40)
- Break into smaller sub-tasks
- Add more verification steps

---

## App-Specific Tips

### Dictionary
- Search field is at the top with "Search" placeholder
- Must click in field before typing
- Press Enter to submit search

### Calculator
- Keyboard input works! Type "5+3=" 
- For clicking: Use move→verify→click pattern
- Numbers are in standard layout (789/456/123/0)

### Notes
- Cmd+N for new note (very reliable)
- Just start typing - no need to click
- Text appears immediately

### Terminal
- Type command, then press Enter
- Wait for prompt to return before next command
- Output appears below your command

### Finder
- Cmd+N for new window
- Cmd+Shift+N for new folder
- Type to search in current location

---

## Example: Fixed Dictionary Task

```
GOAL: Look up "oxymoron" in Dictionary app

STEPS:
1. Press Cmd+Space to open Spotlight
   Verify: Spotlight search bar appears at top of screen

2. Type exactly: Dictionary
   Verify: "Dictionary" appears in search field
   Verify: Dictionary.app shows in results

3. Press Enter to launch Dictionary
   Verify: Dictionary window opens
   Verify: Dictionary is the active/focused window

4. Click in the search field at the top of Dictionary window
   Verify: Cursor is blinking in the search field

5. Type exactly: oxymoron
   Verify: "oxymoron" appears in the search field

6. Press Enter to search
   Verify: Definition of "oxymoron" is displayed

SUCCESS: Dictionary showing definition of "oxymoron"
```

---

## Settings to Adjust

In `example_notepad.py`:
```python
json={"task": task, "max_iterations": 35},  # Increase for complex tasks
timeout=300.0  # Increase for slow operations
```

---

## Quick Test Commands

```bash
# Restart orchestrator (in terminal 1)
python orchestrator.py

# Run task (in terminal 2)
python example_notepad.py

# Check logs
cat logs/session_YYYYMMDD_HHMMSS.jsonl | grep "claude_message"

# View screenshots
open logs/screenshot_YYYYMMDD_HHMMSS_*.png
```

