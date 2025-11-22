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
Open spotlight search using keyboard shortcut.
Open the notes application.
Create a new note and write the word 'hello'
"""
            else:  # Windows or others
                task = "Press the Windows key, type 'notepad', press Enter to open Notepad, then type 'hello' in it"
            
            print(f"Task: {task}")
            
            # Execute task via Claude
            task_response = await client.post(
                f"{base_url}/task",
                json={"task": task, "max_iterations": 25},
                timeout=240.0
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

