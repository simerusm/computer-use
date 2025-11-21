"""
Claude API client for computer use
"""
import anthropic
import base64
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class ClaudeComputerClient:
    """Client for interacting with Claude's computer use API
    
    Note: Computer use is currently in beta and requires the beta header:
    "computer-use-2025-01-24" for Claude 4 models and Claude Sonnet 3.7
    
    Compatible models:
    - claude-sonnet-4-20250514 (Claude 4)
    - claude-3-5-sonnet-20250115 (Claude Sonnet 3.7, if available)
    
    Tool versions must match: computer_20250124, text_editor_20250124, bash_20250124
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set in environment or passed to constructor")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.messages: List[Dict[str, Any]] = []
        
        # Computer use tools (updated for computer-use-2025-01-24 beta)
        self.tools = [
            {
                "type": "computer_20250124",
                "name": "computer",
                "display_width_px": 1920,
                "display_height_px": 1080,
                "display_number": 1,
            },
            {
                "type": "text_editor_20250124",
                "name": "str_replace_editor"
            },
            {
                "type": "bash_20250124",
                "name": "bash"
            }
        ]
    
    def update_screen_size(self, width: int, height: int):
        """Update the screen dimensions for the computer tool"""
        for tool in self.tools:
            if tool.get("type") == "computer_20250124":
                tool["display_width_px"] = width
                tool["display_height_px"] = height
                break
    
    def create_image_content(self, base64_image: str) -> dict:
        """Create an image content block for Claude"""
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64_image
            }
        }
    
    def send_message(self, task: str, screenshot_base64: Optional[str] = None) -> dict:
        """Send a message to Claude with optional screenshot"""
        # Build content
        content = []
        
        if screenshot_base64:
            content.append(self.create_image_content(screenshot_base64))
        
        content.append({
            "type": "text",
            "text": task
        })
        
        # Add user message
        self.messages.append({
            "role": "user",
            "content": content
        })
        
        # Call Claude API with beta endpoint for computer use
        response = self.client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            tools=self.tools,
            messages=self.messages,
            betas=["computer-use-2025-01-24"]
        )
        
        # Add assistant response to messages
        self.messages.append({
            "role": "assistant",
            "content": response.content
        })
        
        return self._parse_response(response)
    
    def continue_conversation(self, tool_results: List[Dict[str, Any]]) -> dict:
        """Continue conversation with tool results"""
        # Add tool results to messages
        tool_result_content = []
        
        for result in tool_results:
            tool_result_content.append({
                "type": "tool_result",
                "tool_use_id": result["tool_use_id"],
                "content": result["content"]
            })
        
        self.messages.append({
            "role": "user",
            "content": tool_result_content
        })
        
        # Call Claude API with beta endpoint for computer use
        response = self.client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            tools=self.tools,
            messages=self.messages,
            betas=["computer-use-2025-01-24"]
        )
        
        # Add assistant response
        self.messages.append({
            "role": "assistant",
            "content": response.content
        })
        
        return self._parse_response(response)
    
    def _parse_response(self, response) -> dict:
        """Parse Claude's response"""
        result = {
            "stop_reason": response.stop_reason,
            "tool_uses": [],
            "text_responses": []
        }
        
        for block in response.content:
            if block.type == "tool_use":
                result["tool_uses"].append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })
            elif block.type == "text":
                result["text_responses"].append(block.text)
        
        return result
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.messages = []


if __name__ == "__main__":
    # Simple test
    print("Claude Computer Client initialized")
    print("Requires ANTHROPIC_API_KEY to be set in .env file")

