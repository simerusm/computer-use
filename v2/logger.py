"""
Logger - Handles comprehensive logging of agent actions and Claude responses
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class SessionLogger:
    """Logger for agent sessions"""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize logger"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create session log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = self.log_dir / f"session_{timestamp}.jsonl"
        self.action_count = 0
        self.iteration_count = 0
        
        print(f"[Logger] Session log: {self.session_file}")
        
        # Log session start
        self.log_event("session_start", {
            "timestamp": datetime.now().isoformat(),
            "session_file": str(self.session_file)
        })
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event to the session file"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        with open(self.session_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def log_user_prompt(self, prompt: str):
        """Log the initial user prompt"""
        print(f"\n{'='*60}")
        print(f"USER PROMPT:")
        print(f"{'='*60}")
        print(f"{prompt}")
        print(f"{'='*60}\n")
        
        self.log_event("user_prompt", {"prompt": prompt})
    
    def log_iteration_start(self, iteration: int):
        """Log the start of an iteration"""
        self.iteration_count = iteration
        print(f"\n{'='*60}")
        print(f"ITERATION {iteration}")
        print(f"{'='*60}")
        
        self.log_event("iteration_start", {"iteration": iteration})
    
    def log_claude_thinking(self, text_responses: List[str]):
        """Log Claude's text responses (thinking/reasoning)"""
        if not text_responses:
            return
        
        print(f"\n[Claude] Thinking:")
        print(f"{'─'*60}")
        for i, text in enumerate(text_responses, 1):
            # Truncate very long responses for console
            display_text = text if len(text) <= 500 else text[:500] + "..."
            print(f"{display_text}")
            if i < len(text_responses):
                print(f"{'─'*60}")
        print(f"{'─'*60}")
        
        self.log_event("claude_thinking", {
            "iteration": self.iteration_count,
            "text_responses": text_responses
        })
    
    def log_tool_use(self, tool_name: str, tool_input: Dict[str, Any], tool_id: str):
        """Log a tool use request from Claude"""
        action = tool_input.get("action", "unknown")
        
        print(f"\n[Claude] Tool Use:")
        print(f"  Tool: {tool_name}")
        print(f"  Action: {action}")
        
        if "coordinate" in tool_input:
            print(f"  Coordinate: {tool_input['coordinate']}")
        if "text" in tool_input:
            text_preview = tool_input['text'][:50] + "..." if len(tool_input['text']) > 50 else tool_input['text']
            print(f"  Text: '{text_preview}'")
        
        self.log_event("tool_use", {
            "iteration": self.iteration_count,
            "tool_name": tool_name,
            "action": action,
            "tool_input": tool_input,
            "tool_id": tool_id
        })
    
    def log_tool_result(self, tool_id: str, result: Any):
        """Log the result of a tool execution"""
        result_str = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
        print(f"[Agent] Tool result: {result_str}")
        
        self.log_event("tool_result", {
            "iteration": self.iteration_count,
            "tool_id": tool_id,
            "result": result if not isinstance(result, list) else "screenshot_data"
        })
    
    def log_api_error(self, error: Exception):
        """Log an API error"""
        print(f"\n{'='*60}")
        print(f"❌ API ERROR:")
        print(f"{'='*60}")
        print(f"{error}")
        print(f"{'='*60}\n")
        
        self.log_event("api_error", {
            "iteration": self.iteration_count,
            "error": str(error),
            "error_type": type(error).__name__
        })
    
    def log_completion(self, stop_reason: str, total_iterations: int):
        """Log task completion"""
        print(f"\n{'='*60}")
        print(f"TASK COMPLETED")
        print(f"{'='*60}")
        print(f"Stop reason: {stop_reason}")
        print(f"Total iterations: {total_iterations}")
        print(f"Session log: {self.session_file}")
        print(f"{'='*60}\n")
        
        self.log_event("session_complete", {
            "stop_reason": stop_reason,
            "total_iterations": total_iterations
        })
    
    def log_stop_reason(self, stop_reason: str):
        """Log the stop reason from Claude"""
        print(f"\n[Claude] Stop reason: {stop_reason}")
        
        self.log_event("stop_reason", {
            "iteration": self.iteration_count,
            "stop_reason": stop_reason
        })


class ConsoleFormatter:
    """Helper for formatting console output"""
    
    @staticmethod
    def header(text: str, width: int = 60):
        """Print a header"""
        print(f"\n{'='*width}")
        print(f"{text:^{width}}")
        print(f"{'='*width}")
    
    @staticmethod
    def section(text: str, width: int = 60):
        """Print a section divider"""
        print(f"\n{'─'*width}")
        print(f"{text}")
        print(f"{'─'*width}")
    
    @staticmethod
    def success(text: str):
        """Print success message"""
        print(f"✓ {text}")
    
    @staticmethod
    def error(text: str):
        """Print error message"""
        print(f"✗ {text}")
    
    @staticmethod
    def info(text: str, indent: int = 0):
        """Print info message"""
        print(f"{'  '*indent}• {text}")

