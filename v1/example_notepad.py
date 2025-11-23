"""
Example: Open Notes app and type 'hello'

This is a simple example that demonstrates the computer use agent
"""
import asyncio
import httpx
import json
import time
import platform
from pathlib import Path


async def run_notepad_example():
    """Run the example task: Open Notes and type 'hello'"""
    
    base_url = "http://localhost:8000"
    
    print("=== Computer Use Agent Example ===")
    print("Task: Open Notes app and type 'hello'\n")
    
    # Check health
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{base_url}/health")
            health = response.json()
            print(f"✓ Orchestrator health: {health}")
            
            if not health.get("claude_ready"):
                print("\n⚠️  Warning: Claude integration not available.")
                print("   Will demonstrate manual actions instead.\n")
                await run_manual_example(client, base_url)
                return
            
            # Run Claude-powered task
            print("\n🤖 Starting Claude-powered task execution...")
            print("   Claude will analyze the screen and execute actions autonomously.\n")
            
            # Determine OS and task
            os_name = platform.system()
            if os_name == "Darwin":  # macOS
                task = """
GOAL: Open the Google Sheets spreadsheet called "hello" in Google Drive and write the number 1 in cell A1.

APPROACH: Browser-based workflow with careful focus management and wait times for page loads.

STEPS:

1. Open Google Chrome browser using Spotlight
   - Press Cmd+Space to open Spotlight
   - Type exactly: Google
   - Press Enter to launch Google
   - Take a screenshot to verify Google window opened and is active

2. Navigate to Google Drive
   - Press Cmd+L to focus the address bar (cursor should appear in address bar)
   - Type exactly: drive.google.com
   - Press Enter to navigate
   - Wait for page to load (you'll see Google Drive interface or login page)
   - Take a screenshot to verify page loaded

3. Handle login if needed
   - If you see a login page, you may need to click "Sign in" or use saved credentials
   - If already logged in, you should see the Google Drive file list
   - Take a screenshot to confirm you're in Google Drive

4. Find the spreadsheet called "hello"
   - Look for a file named "hello" in the file list (it might be a spreadsheet icon)
   - Option A: If visible, click on the file named "hello"
   - Option B: If not visible, use Cmd+F to search, type "hello", then click the result
   - Take a screenshot to verify you found the file

5. Open the spreadsheet
   - Double-click on "hello" or click once then press Enter
   - Wait for Google Sheets to load (you'll see the spreadsheet grid)
   - Take a screenshot to verify the spreadsheet is open

6. Click on cell A1
   - Look for cell A1 (top-left cell of the grid, column A, row 1)
   - Click on cell A1
   - Verify the cell is selected (it will have a blue border or highlight)
   - Take a screenshot to confirm A1 is selected

7. Type the number 1
   - Type: 1
   - Press Enter to confirm the entry
   - Verify the number 1 appears in cell A1
   - Take a screenshot to confirm

SUCCESS CRITERIA: 
- Google is open with Google Sheets showing
- The spreadsheet "hello" is open
- Cell A1 contains the number 1

IMPORTANT NOTES:
- Allow time for web pages to load between steps
- If Google Drive requires login, you may need to enter credentials
- If you can't find the "hello" spreadsheet, it may not exist yet
- Web pages may take 3-5 seconds to load - be patient
- If Google opens a "Start Page" or previous session, that's okay, just navigate to drive.google.com

RECOVERY STRATEGIES:
- If login is required but credentials aren't saved, you may need to stop and inform the user
- If the spreadsheet doesn't exist, you could create a new one, but that's beyond the current task
- If page doesn't load, try refreshing with Cmd+R
"""
            else:  # Windows or others
                task = "Press the Windows key, type 'notepad', press Enter to open Notepad, then type 'hello' in it"
            
            print(f"Task:\n{task}\n")
            
            # Execute task via Claude (increased iterations for complex tasks)
            # Browser-based tasks need more iterations due to page loads and navigation
            task_response = await client.post(
                f"{base_url}/task",
                json={"task": task, "max_iterations": 50},
                timeout=600.0  # 10 minutes for complex web workflows
            )
            
            if task_response.status_code != 200:
                print(f"\n❌ Error: Task execution failed (status {task_response.status_code})")
                error_detail = task_response.json().get("detail", "Unknown error")
                print(f"   Details: {error_detail}")
                return
            
            result = task_response.json()
            
            print(f"\n✓ Task completed!")
            print(f"  Iterations: {result['iterations']}")
            print(f"  Success: {result['success']}")
            
            # Show execution log
            print("\n=== Execution Log ===")
            for entry in result["execution_log"]:
                if entry["type"] == "claude_message":
                    print(f"💭 Claude: {entry['text']}")
                elif entry["type"] == "tool_use":
                    print(f"🔧 Tool: {entry['tool']} - {entry['input'].get('action', 'N/A')}")
            
            # Get session summary
            summary_response = await client.get(f"{base_url}/logs/summary")
            summary = summary_response.json()
            
            print(f"\n=== Session Summary ===")
            print(f"Session ID: {summary['session_id']}")
            print(f"Total actions: {summary['total_actions']}")
            print(f"Log file: {summary['log_file']}")
            print(f"\nAction breakdown:")
            for action_type, count in summary['action_types'].items():
                print(f"  {action_type}: {count}")
        
        except httpx.ConnectError:
            print("❌ Error: Cannot connect to orchestrator.")
            print("   Make sure the orchestrator is running:")
            print("   python orchestrator.py")
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error: {e.response.status_code}")
            try:
                error_detail = e.response.json()
                print(f"   Details: {error_detail}")
            except:
                print(f"   Response: {e.response.text}")
        except Exception as e:
            import traceback
            print(f"❌ Error: {e}")
            print(f"\nFull traceback:\n{traceback.format_exc()}")


async def run_manual_example(client: httpx.AsyncClient, base_url: str):
    """Run manual example without Claude integration"""
    print("🔧 Running manual action sequence...\n")
    
    # Give user time to switch focus away from terminal
    print("⏰ Starting in 3 seconds...")
    print("   (Click somewhere else or minimize this terminal now!)")
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    print("   Starting now!\n")
    
    # Take screenshot
    print("1. Taking initial screenshot...")
    response = await client.post(f"{base_url}/screenshot")
    screenshot = response.json()
    print(f"   ✓ Screenshot saved: {screenshot['path']}")
    print(f"   Screen size: {screenshot['width']}x{screenshot['height']}")
    
    # Detect OS
    os_name = platform.system()
    
    if os_name == "Darwin":  # macOS
        print("\n2. Opening Spotlight to search for Notes...")
        # Press Cmd+Space to open Spotlight
        await client.post(
            f"{base_url}/action",
            json={"action": "key", "text": "command+space"}
        )
        time.sleep(1)
        
        print("3. Typing 'Notes'...")
        await client.post(
            f"{base_url}/action",
            json={"action": "type", "text": "Notes"}
        )
        time.sleep(0.5)
        
        print("4. Pressing Enter to open Notes...")
        await client.post(
            f"{base_url}/action",
            json={"action": "key", "text": "return"}
        )
        time.sleep(2)
        
        print("5. Creating new note (Cmd+N)...")
        await client.post(
            f"{base_url}/action",
            json={"action": "key", "text": "command+n"}
        )
        time.sleep(1)
    
    else:  # Windows or other
        print("\n2. Opening Start Menu...")
        await client.post(
            f"{base_url}/action",
            json={"action": "key", "text": "win"}
        )
        time.sleep(1)
        
        print("3. Typing 'notepad'...")
        await client.post(
            f"{base_url}/action",
            json={"action": "type", "text": "notepad"}
        )
        time.sleep(0.5)
        
        print("4. Pressing Enter to open Notepad...")
        await client.post(
            f"{base_url}/action",
            json={"action": "key", "text": "return"}
        )
        time.sleep(2)
    
    print("\n6. Typing 'hello'...")
    response = await client.post(
        f"{base_url}/action",
        json={"action": "type", "text": "hello"}
    )
    result = response.json()
    print(f"   ✓ Typed {result['length']} characters")
    
    print("\n7. Taking final screenshot...")
    response = await client.post(f"{base_url}/screenshot")
    screenshot = response.json()
    print(f"   ✓ Screenshot saved: {screenshot['path']}")
    
    # Get summary
    response = await client.get(f"{base_url}/logs/summary")
    summary = response.json()
    
    print(f"\n=== Session Summary ===")
    print(f"Total actions: {summary['total_actions']}")
    print(f"Log file: {summary['log_file']}")


def main():
    """Main entry point"""
    print("Starting example...\n")
    print("Note: Make sure the orchestrator is running first:")
    print("  python orchestrator.py\n")
    
    print("⚠️  IMPORTANT: The agent will control your mouse and keyboard!")
    print("   After you see the countdown, click away from this terminal")
    print("   or minimize it so the agent can control your desktop.\n")
    
    time.sleep(2)
    
    try:
        asyncio.run(run_notepad_example())
    except KeyboardInterrupt:
        print("\n\nExample interrupted by user.")


if __name__ == "__main__":
    main()

