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
coordinate_scale_factor: float = 1.0  # For scaling Claude's coordinates to actual screen size


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global agent, logger, claude_client, coordinate_scale_factor
    
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
            test_screenshot = agent.screenshot()
            screenshot_width = test_screenshot['width']
            screenshot_height = test_screenshot['height']
            coordinate_scale_factor = test_screenshot['scale_factor']
            
            print(f"✓ Screenshots scaled to: {screenshot_width}x{screenshot_height} (fits in Claude's optimal 1280x800)")
            print(f"✓ Scale factor: {coordinate_scale_factor:.3f} (screenshot/logical)")
            
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
        
        # Update coordinate scale factor for this session
        global coordinate_scale_factor
        coordinate_scale_factor = screenshot_result["scale_factor"]
        
        # Enhance task with macOS-specific instructions
        macos_instructions = """
Important macOS behaviors to remember:
- If you accidentally open a menu or popup (like battery menu, focus menu, etc.), press Escape to close it before trying again
- Clicking elsewhere while a menu is open will just close the menu, not open the new target
- Menu bar clicks often open menus that must be closed with Escape first

CRITICAL: Before clicking anything, ALWAYS:
1. First use mouse_move to position the cursor where you want to click
2. Take a screenshot to verify the cursor is in the correct position
3. If the cursor position looks correct, proceed with the click
4. If not correct, adjust the position and verify again before clicking
This two-step approach (move → verify → click) prevents misclicks.
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
                    
                    # Debug: Show what Claude requested
                    print(f"\n🤖 Claude tool use:")
                    print(f"   Tool: {tool_name}")
                    print(f"   Action: {tool_input.get('action', 'N/A')}")
                    if "coordinate" in tool_input:
                        print(f"   📍 Coordinates: {tool_input['coordinate']}")
                    
                    logger.log_message(f"Executing tool: {tool_name}")
                    execution_log.append({
                        "type": "tool_use",
                        "tool": tool_name,
                        "input": tool_input
                    })
                    
                    # Execute computer tool
                    if tool_name == "computer":
                        action_type = tool_input.get("action")
                        
                        # COORDINATE SCALING: Claude returns coordinates in screenshot space (1231x800)
                        # We need to scale UP to logical space (1512x982) for PyAutoGUI
                        if "coordinate" in tool_input and coordinate_scale_factor != 1.0:
                            claude_coords = tool_input["coordinate"]
                            # Scale UP: divide by scale_factor (which is < 1.0)
                            logical_x = int(claude_coords[0] / coordinate_scale_factor)
                            logical_y = int(claude_coords[1] / coordinate_scale_factor)
                            tool_input["coordinate"] = [logical_x, logical_y]
                            print(f"   📐 Coordinate scaling: {claude_coords} (Claude space) → [{logical_x}, {logical_y}] (PyAutoGUI space, scale: {1/coordinate_scale_factor:.2f}x)")
                        elif "coordinate" in tool_input:
                            coords = tool_input["coordinate"]
                            print(f"   📐 Coordinates (no scaling needed): {coords}")
                        
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
                            # Update scale factor for this screenshot
                            coordinate_scale_factor = result.get("scale_factor", 1.0)
                            
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

