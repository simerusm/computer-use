"""
Orchestrator Service - Coordinates between Claude API and Desktop Agent
"""
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
from datetime import datetime
import os
from dotenv import load_dotenv

from agent import DesktopAgent
from claude_client import ClaudeComputerClient
from logger import ActionLogger

load_dotenv()


class TaskRequest(BaseModel):
    task: str
    max_iterations: int = 10


class ActionRequest(BaseModel):
    action: str
    coordinate: Optional[List[int]] = None
    text: Optional[str] = None


app = FastAPI(title="Computer Use Orchestrator")

# Global state
agent: Optional[DesktopAgent] = None
logger: Optional[ActionLogger] = None
claude_client: Optional[ClaudeComputerClient] = None
active_connections: List[WebSocket] = []
claude_screen_width: int = 1231  # Screenshot width sent to Claude (will be set at startup)
claude_screen_height: int = 800  # Screenshot height sent to Claude (will be set at startup)


def map_coords_from_claude(x_c: int, y_c: int, claude_w: int, claude_h: int, logical_w: int, logical_h: int) -> tuple:
    """
    Defensively map coordinates from Claude space to PyAutoGUI logical space.
    
    Args:
        x_c, y_c: Coordinates from Claude
        claude_w, claude_h: Screenshot dimensions Claude sees
        logical_w, logical_h: Actual logical screen dimensions
    
    Returns:
        (x_logical, y_logical): Clamped and scaled coordinates for PyAutoGUI
    """
    # 1) Clamp to Claude/screenshot bounds FIRST (defensive)
    x_c_clamped = max(0, min(x_c, claude_w - 1))
    y_c_clamped = max(0, min(y_c, claude_h - 1))
    
    if x_c != x_c_clamped or y_c != y_c_clamped:
        print(f"   ⚠️  CLAMPED Claude coords: [{x_c}, {y_c}] → [{x_c_clamped}, {y_c_clamped}] (Claude bounds: {claude_w}x{claude_h})")
    
    # 2) Scale up to logical space
    scale_x = logical_w / claude_w
    scale_y = logical_h / claude_h
    
    x_l = int(round(x_c_clamped * scale_x))
    y_l = int(round(y_c_clamped * scale_y))
    
    # 3) Clamp to logical screen bounds (just in case)
    x_l_clamped = max(0, min(x_l, logical_w - 1))
    y_l_clamped = max(0, min(y_l, logical_h - 1))
    
    if x_l != x_l_clamped or y_l != y_l_clamped:
        print(f"   ⚠️  CLAMPED logical coords: [{x_l}, {y_l}] → [{x_l_clamped}, {y_l_clamped}] (Logical bounds: {logical_w}x{logical_h})")
    
    return x_l_clamped, y_l_clamped


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global agent, logger, claude_client, claude_screen_width, claude_screen_height
    
    print("Initializing services...")
    agent = DesktopAgent(log_dir="logs")
    logger = ActionLogger(log_dir="logs")
    print(f"✓ Agent initialized")
    
    # Initialize Claude client if API key is available
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        api_key_preview = api_key[:20] + "..." if len(api_key) > 20 else api_key
        print(f"✓ Found API key: {api_key_preview}")
        try:
            # Get logical screen size from agent
            screen_info = agent.get_screen_size()
            logical_width = screen_info['width']
            logical_height = screen_info['height']
            print(f"✓ Actual logical screen size: {logical_width}x{logical_height}")
            
            # Take a test screenshot to get Claude-optimized dimensions
            # Screenshots are scaled to fit within 1280x800 (WXGA) as recommended by Claude docs
            # Single resize from physical → Claude-optimal (no intermediate steps)
            test_screenshot = agent.screenshot()
            screenshot_width = test_screenshot['width']
            screenshot_height = test_screenshot['height']
            
            # Store globally for coordinate mapping
            claude_screen_width = screenshot_width
            claude_screen_height = screenshot_height
            
            print(f"✓ Screenshots will be: {screenshot_width}x{screenshot_height}")
            print(f"   (Fits within Claude's optimal 1280×800, aspect ratio maintained)")
            print(f"✓ Logical screen: {logical_width}x{logical_height}")
            print(f"✓ Coordinate mapping: Claude [{screenshot_width}×{screenshot_height}] → PyAutoGUI [{logical_width}×{logical_height}]")
            print(f"✓ Scale factors: X={logical_width/screenshot_width:.6f}, Y={logical_height/screenshot_height:.6f}")
            print(f"✓ Aspect ratios: {logical_width/logical_height:.4f} (logical) vs {screenshot_width/screenshot_height:.4f} (screenshot)")
            
            # IMPORTANT: Tell Claude the screen size MATCHES the screenshots we send!
            # This keeps everything in the same coordinate space for accuracy
            claude_client = ClaudeComputerClient(
                api_key=api_key,
                screen_width=screenshot_width,
                screen_height=screenshot_height
            )
            print(f"✓ Claude tool config: display_width_px={screenshot_width}, display_height_px={screenshot_height}")
            print(f"✓ Claude will return coordinates in {screenshot_width}x{screenshot_height} space")
            print(f"✓ We'll scale coordinates UP to {logical_width}x{logical_height} for PyAutoGUI")
            print(f"✓ Coordinate clamping: ENABLED (defensive against out-of-bounds)")
            logger.log_message("Claude client initialized successfully")
        except Exception as e:
            import traceback
            logger.log_error(f"Failed to initialize Claude client: {e}")
            print(f"❌ Warning: Claude client initialization failed: {e}")
            print(f"Traceback:\n{traceback.format_exc()}")
    else:
        logger.log_message("No ANTHROPIC_API_KEY found, Claude integration disabled", "warning")
        print("❌ Warning: No ANTHROPIC_API_KEY found. Set it in .env to enable Claude integration.")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Computer Use Orchestrator",
        "status": "running",
        "claude_enabled": claude_client is not None
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_ready": agent is not None,
        "logger_ready": logger is not None,
        "claude_ready": claude_client is not None
    }


@app.post("/screenshot")
async def take_screenshot():
    """Take a screenshot"""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    result = agent.screenshot()
    logger.log_action({"action": "screenshot"}, result)
    
    return result


@app.post("/action")
async def execute_action(action_request: ActionRequest):
    """Execute a single action"""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    action = action_request.dict()
    result = agent.execute_action(action)
    logger.log_action(action, result)
    
    # Broadcast to WebSocket clients
    await broadcast_message({
        "type": "action_executed",
        "action": action,
        "result": result
    })
    
    return result


@app.post("/task")
async def execute_task(task_request: TaskRequest):
    """Execute a task using Claude"""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    if not claude_client:
        raise HTTPException(status_code=503, detail="Claude client not available. Set ANTHROPIC_API_KEY in .env")
    
    logger.log_task_start(task_request.task)
    
    try:
        # Reset conversation for new task
        claude_client.reset_conversation()
        
        # Take initial screenshot
        screenshot_result = agent.screenshot()
        screenshot_base64 = screenshot_result["data"]
        
        # Enhance task with macOS-specific instructions
        macos_instructions = """
You are an expert macOS operator controlling the user’s computer through a limited set of tools:
- You can take screenshots of the screen.
- You can move and click the mouse.
- You can press keyboard keys and type text.

General rules:
- The OS is macOS with Spotlight search (Cmd+Space) and standard apps like Dictionary.
- Always work in SMALL, REASONED STEPS: plan briefly, then take one action, then re-check the screen.
- After each action, TAKE A NEW SCREENSHOT and verify that the expected change really happened before continuing.
- If the target app is not visible or focused, bring it to the front using macOS conventions (Cmd+Tab, Dock, or Spotlight).
- Never keep typing into Spotlight or Launchpad if the goal is to operate inside an app’s own UI.
- If you lose the app (it moves to the background), use Cmd+Tab or Spotlight again to refocus it.

Goal handling:
- For any task, extract a short step-by-step plan first (mentally or explicitly in text), then execute it.
- Only stop when the goal is actually achieved on screen (e.g., the Dictionary window is open and the requested word is visible in the search result).

Safety:
- Prefer reliable, minimal actions over "fancy" ones.
- If something doesn't work as expected (e.g. searching in Spotlight shows no result), STOP, re-check the screen, and adjust the plan instead of repeating the same failing action.

CRITICAL COORDINATE CONSTRAINTS:
- The screenshot resolution you see is {screenshot_result['width']}x{screenshot_result['height']} pixels.
- ALL mouse coordinates you output MUST satisfy:
  * 0 <= x < {screenshot_result['width']}
  * 0 <= y < {screenshot_result['height']}
- NEVER propose coordinates outside this range.
- If you see an element near the edge, use coordinates like (width-10, y) or (x, height-10), never exceed the bounds.

CRITICAL APP CONTEXT AWARENESS:
- ONLY interact with Google Drive when it's open in a REAL web browser tab (e.g., Chrome showing drive.google.com).
- IGNORE any "Google Drive" panels, sidebars, or file trees inside code editors (VS Code, Cursor, etc.) - these are NOT real browser tabs.
- If you see a coding environment with file listings and a Google Drive sidebar:
  * DO NOT click files there - they won't open Google Sheets
  * Instead, use Cmd+Tab or click the Chrome icon to switch to the actual browser
  * Verify you're in Chrome with drive.google.com in the address bar
- Before clicking any file in Drive, verify:
  * You're in a browser window (Chrome/Safari)
  * The URL bar shows drive.google.com or docs.google.com
  * You see the full Google Drive web interface, not a sidebar

COORDINATE SANITY CHECK:
- The dock is at the BOTTOM of the screen (y ≈ {screenshot_result['height']} - 50).
- If you're trying to click a file in Google Drive's file list, it should be in the MIDDLE area (y ≈ 300-600).
- If all your clicks are landing at y > {screenshot_result['height'] - 100}, you're hitting the dock - STOP and recalibrate.
"""
        enhanced_task = f"{macos_instructions}\n\nTask: {task_request.task}"
        
        # Send initial task to Claude
        response = claude_client.send_message(
            task=enhanced_task,
            screenshot_base64=screenshot_base64
        )
        
        iterations = 0
        task_complete = False
        execution_log = []
        
        while iterations < task_request.max_iterations and not task_complete:
            iterations += 1
            
            # Log Claude's response
            if response["text_responses"]:
                for text in response["text_responses"]:
                    logger.log_message(f"Claude: {text}")
                    execution_log.append({"type": "claude_message", "text": text})
            
            # Check if task is complete
            if response["stop_reason"] == "end_turn":
                task_complete = True
                break
            
            # Execute tool uses
            if response["tool_uses"]:
                tool_results = []
                
                for tool_use in response["tool_uses"]:
                    tool_name = tool_use["name"]
                    tool_input = tool_use["input"]
                    
                    # Debug: Log RAW tool_use block (for debugging coordinate issues)
                    print(f"\n🔍 RAW tool_use: {tool_use}")
                    
                    # Debug: Show what Claude requested
                    print(f"\n🤖 Claude tool use:")
                    print(f"   Tool: {tool_name}")
                    print(f"   Action: {tool_input.get('action', 'N/A')}")
                    if "coordinate" in tool_input:
                        print(f"   📍 RAW Coordinates from Claude: {tool_input['coordinate']}")
                        print(f"   📍 Claude screen bounds: {claude_screen_width}x{claude_screen_height}")
                    
                    logger.log_message(f"Executing tool: {tool_name}")
                    execution_log.append({
                        "type": "tool_use",
                        "tool": tool_name,
                        "input": tool_input
                    })
                    
                    # Execute computer tool
                    if tool_name == "computer":
                        action_type = tool_input.get("action")
                        
                        # DEFENSIVE COORDINATE MAPPING: Clamp and scale coordinates
                        # Claude returns coords in screenshot space, we scale to PyAutoGUI logical space
                        if "coordinate" in tool_input:
                            claude_coords = tool_input["coordinate"]
                            
                            # Get current logical screen size
                            import pyautogui
                            logical_w, logical_h = pyautogui.size()
                            
                            # Use defensive mapping with clamping
                            logical_x, logical_y = map_coords_from_claude(
                                claude_coords[0], claude_coords[1],
                                claude_screen_width, claude_screen_height,
                                logical_w, logical_h
                            )
                            
                            tool_input["coordinate"] = [logical_x, logical_y]
                            
                            # Detailed coordinate analysis
                            claude_y_percent = (claude_coords[1] / claude_screen_height) * 100
                            logical_y_percent = (logical_y / logical_h) * 100
                            
                            print(f"   ✅ Mapped coordinates: {claude_coords} (Claude {claude_screen_width}x{claude_screen_height}) → [{logical_x}, {logical_y}] (PyAutoGUI {logical_w}x{logical_h})")
                            print(f"      📊 Y-position analysis:")
                            print(f"         - Claude Y: {claude_coords[1]}/{claude_screen_height} = {claude_y_percent:.1f}% from top")
                            print(f"         - Logical Y: {logical_y}/{logical_h} = {logical_y_percent:.1f}% from top")
                            
                            # Warn if clicking too close to dock
                            if logical_y > logical_h - 100:
                                print(f"      ⚠️  WARNING: Y={logical_y} is near bottom of screen ({logical_h})")
                                print(f"         This might hit the DOCK instead of your target!")
                                print(f"         Expected file clicks: y ≈ 300-600")
                        
                        # Auto-recovery: Detect if Claude opened wrong menu and close it
                        if action_type in ["left_click", "screenshot"] and response.get("text_responses"):
                            text_response = " ".join(response["text_responses"]).lower()
                            menu_mistake_keywords = [
                                "opened a", "instead of", "instead", 
                                "battery menu", "focus menu", "wrong",
                                "not the right", "that opened"
                            ]
                            
                            if any(keyword in text_response for keyword in menu_mistake_keywords):
                                print("   🔧 Auto-recovery: Detected menu mistake, closing with Escape")
                                agent.key_press("escape")
                                import time
                                time.sleep(0.3)  # Brief pause for menu to close
                        
                        result = agent.execute_action(tool_input)
                        logger.log_action(tool_input, result)
                        
                        # Broadcast to WebSocket clients
                        await broadcast_message({
                            "type": "action_executed",
                            "action": tool_input,
                            "result": result
                        })
                        
                        # Format result for Claude
                        if result.get("type") == "screenshot":
                            # Send screenshot back to Claude
                            tool_results.append({
                                "tool_use_id": tool_use["id"],
                                "content": [
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "image/png",
                                            "data": result["data"]
                                        }
                                    }
                                ]
                            })
                        else:
                            # Send text result
                            tool_results.append({
                                "tool_use_id": tool_use["id"],
                                "content": json.dumps(result)
                            })
                    else:
                        # Other tools (bash, text_editor) - not implemented in agent
                        tool_results.append({
                            "tool_use_id": tool_use["id"],
                            "content": f"Tool {tool_name} not implemented in agent"
                        })
                
                # Continue conversation with tool results
                response = claude_client.continue_conversation(tool_results)
            else:
                # No more tool uses
                task_complete = True
        
        logger.log_task_complete(task_request.task, task_complete)
        
        return {
            "success": task_complete,
            "iterations": iterations,
            "execution_log": execution_log,
            "final_response": response
        }
    
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        logger.log_error(str(e), {"task": task_request.task})
        print(f"\n❌ Error in task execution: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs/summary")
async def get_log_summary():
    """Get summary of current session"""
    if not logger:
        raise HTTPException(status_code=500, detail="Logger not initialized")
    
    return logger.get_summary()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial status
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to orchestrator",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and receive messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


async def broadcast_message(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    disconnected = []
    
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception:
            disconnected.append(connection)
    
    # Remove disconnected clients
    for connection in disconnected:
        active_connections.remove(connection)


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("ORCHESTRATOR_HOST", "localhost")
    port = int(os.getenv("ORCHESTRATOR_PORT", "8000"))
    
    print(f"Starting Computer Use Orchestrator on {host}:{port}")
    print(f"API docs available at http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port)

