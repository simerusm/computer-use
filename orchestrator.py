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


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global agent, logger, claude_client
    
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
            claude_client = ClaudeComputerClient(api_key=api_key)
            # Update screen size
            screen_info = agent.get_screen_size()
            claude_client.update_screen_size(screen_info["width"], screen_info["height"])
            logger.log_message("Claude client initialized successfully")
            print(f"✓ Claude client initialized (screen: {screen_info['width']}x{screen_info['height']})")
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
        
        # Send initial task to Claude
        response = claude_client.send_message(
            task=task_request.task,
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
                    
                    logger.log_message(f"Executing tool: {tool_name}")
                    execution_log.append({
                        "type": "tool_use",
                        "tool": tool_name,
                        "input": tool_input
                    })
                    
                    # Execute computer tool
                    if tool_name == "computer":
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

