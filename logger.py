"""
Logging utilities for tracking actions and screenshots
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class ActionLogger:
    """Logger for tracking agent actions and screenshots"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create session log file
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"session_{self.session_id}.jsonl"
        self.actions: List[Dict[str, Any]] = []
        
        # Initialize log file
        self._write_log({
            "type": "session_start",
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        })
    
    def _write_log(self, entry: Dict[str, Any]):
        """Write a log entry to the file"""
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def log_action(self, action: Dict[str, Any], result: Dict[str, Any]):
        """Log an action and its result"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": result
        }
        
        # Don't log full base64 screenshot data to keep logs manageable
        if result.get("type") == "screenshot" and "data" in result:
            log_result = result.copy()
            log_result["data"] = f"<base64 image: {len(result['data'])} chars>"
            log_entry["result"] = log_result
        
        self.actions.append(log_entry)
        self._write_log(log_entry)
    
    def log_message(self, message: str, level: str = "info"):
        """Log a message"""
        log_entry = {
            "type": "message",
            "level": level,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self._write_log(log_entry)
    
    def log_error(self, error: str, context: Dict[str, Any] = None):
        """Log an error"""
        log_entry = {
            "type": "error",
            "error": error,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        self._write_log(log_entry)
    
    def log_task_start(self, task: str):
        """Log the start of a task"""
        log_entry = {
            "type": "task_start",
            "task": task,
            "timestamp": datetime.now().isoformat()
        }
        self._write_log(log_entry)
    
    def log_task_complete(self, task: str, success: bool):
        """Log task completion"""
        log_entry = {
            "type": "task_complete",
            "task": task,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        self._write_log(log_entry)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the session"""
        return {
            "session_id": self.session_id,
            "log_file": str(self.log_file),
            "total_actions": len(self.actions),
            "action_types": self._count_action_types()
        }
    
    def _count_action_types(self) -> Dict[str, int]:
        """Count actions by type"""
        counts = {}
        for action in self.actions:
            action_type = action.get("result", {}).get("type", "unknown")
            counts[action_type] = counts.get(action_type, 0) + 1
        return counts
    
    def print_summary(self):
        """Print a summary of the session"""
        summary = self.get_summary()
        print(f"\n=== Session Summary ===")
        print(f"Session ID: {summary['session_id']}")
        print(f"Log file: {summary['log_file']}")
        print(f"Total actions: {summary['total_actions']}")
        print(f"\nAction breakdown:")
        for action_type, count in summary['action_types'].items():
            print(f"  {action_type}: {count}")

