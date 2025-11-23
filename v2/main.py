"""
Simple Computer Use Agent - Refactored with modular design and comprehensive logging
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv
import anthropic

from agent import DesktopAgent
from logger import SessionLogger, ConsoleFormatter

# Load environment variables
load_dotenv()

# Configuration
TARGET_WIDTH = 1024
TARGET_HEIGHT = 768
MODEL_NAME = os.getenv("MODEL_NAME", "claude-sonnet-4-20250514")
MAX_ITERATIONS = 50  # Safety limit


class ComputerUseAgent:
    """Main agent orchestrator"""
    
    def __init__(self, target_width: int = TARGET_WIDTH, target_height: int = TARGET_HEIGHT):
        """Initialize the computer use agent"""
        # Setup API client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            ConsoleFormatter.error("Please set ANTHROPIC_API_KEY in your environment or .env file")
            exit(1)
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.agent = DesktopAgent(target_width, target_height, log_dir="logs")
        self.logger = SessionLogger(log_dir="logs")
        
        self.target_width = target_width
        self.target_height = target_height
        self.messages = []
        
        ConsoleFormatter.header("Computer Use Agent Initialized")
        ConsoleFormatter.info(f"Model: {MODEL_NAME}")
        ConsoleFormatter.info(f"Screen size: {self.agent.get_screen_size()}")
        ConsoleFormatter.info(f"Virtual size for Claude: {target_width}x{target_height}")
        print()
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """
        Execute a tool request from Claude
        
        Args:
            tool_name: Name of the tool (should be "computer")
            tool_input: Tool input parameters
            
        Returns:
            Tool execution result
        """
        if tool_name != "computer":
            return f"Unknown tool: {tool_name}"
        
        action = tool_input.get("action")
        
        # Execute action based on type
        if action == "screenshot":
            screenshot_data = self.agent.take_screenshot()
            return [{
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": screenshot_data
                }
            }]
        
        elif action == "mouse_move":
            coords = tool_input.get("coordinate")
            if coords:
                return self.agent.mouse_move(coords[0], coords[1])
            return "No coordinates provided"
        
        elif action == "left_click":
            coords = tool_input.get("coordinate")
            if coords:
                return self.agent.left_click(coords[0], coords[1])
            else:
                return self.agent.left_click()
        
        elif action == "right_click":
            coords = tool_input.get("coordinate")
            if coords:
                return self.agent.right_click(coords[0], coords[1])
            else:
                return self.agent.right_click()
        
        elif action == "double_click":
            coords = tool_input.get("coordinate")
            if coords:
                return self.agent.double_click(coords[0], coords[1])
            else:
                return self.agent.double_click()
        
        elif action == "type":
            text = tool_input.get("text", "")
            return self.agent.type_text(text)
        
        elif action == "key":
            key_sequence = tool_input.get("text", "")
            return self.agent.press_key(key_sequence)
        
        elif action == "wait":
            duration = tool_input.get("duration", 1.0)
            return self.agent.wait(duration)
        
        return f"Action {action} not implemented"
    
    def run(self, task: str):
        """
        Run the agent with a given task
        
        Args:
            task: The task description for Claude
        """
        self.logger.log_user_prompt(task)
        
        # Initialize conversation
        self.messages = [{"role": "user", "content": task}]
        
        iteration = 0
        
        while iteration < MAX_ITERATIONS:
            iteration += 1
            self.logger.log_iteration_start(iteration)
            
            # Send request to Claude
            print(f"\n[Main] Sending request to Claude (iteration {iteration})...")
            
            try:
                response = self.client.beta.messages.create(
                    model=MODEL_NAME,
                    max_tokens=1024,
                    tools=[
                        {
                            "type": "computer_20250124",
                            "name": "computer",
                            "display_width_px": self.target_width,
                            "display_height_px": self.target_height,
                            "display_number": 1,
                        }
                    ],
                    messages=self.messages,
                    betas=["computer-use-2025-01-24"]
                )
            except Exception as e:
                self.logger.log_api_error(e)
                break
            
            # Log stop reason
            self.logger.log_stop_reason(response.stop_reason)
            
            # Extract text responses (Claude's thinking)
            text_responses = [
                block.text for block in response.content 
                if hasattr(block, 'text')
            ]
            
            if text_responses:
                self.logger.log_claude_thinking(text_responses)
            
            # Add assistant response to history
            self.messages.append({"role": "assistant", "content": response.content})
            
            # Handle tool use
            if response.stop_reason == "tool_use":
                tool_results = []
                
                for block in response.content:
                    if block.type == "tool_use":
                        # Log tool use
                        self.logger.log_tool_use(block.name, block.input, block.id)
                        
                        # Execute tool
                        result = self.execute_tool(block.name, block.input)
                        
                        # Log result
                        self.logger.log_tool_result(block.id, result)
                        
                        # Add to results
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })
                
                # Add tool results to conversation
                self.messages.append({"role": "user", "content": tool_results})
            
            else:
                # Task completed or stopped
                self.logger.log_completion(response.stop_reason, iteration)
                
                if text_responses:
                    print(f"\n[Claude] Final response:")
                    for text in text_responses:
                        print(f"  {text}")
                
                break
        
        if iteration >= MAX_ITERATIONS:
            ConsoleFormatter.error(f"Reached maximum iterations ({MAX_ITERATIONS})")
            self.logger.log_event("max_iterations_reached", {"max": MAX_ITERATIONS})


def main():
    """Main entry point"""
    ConsoleFormatter.header("Simple Computer Use Agent v2")
    
    # Get task from user
    print("\nEnter your task (or press Enter for default):")
    print("Default: Open calculator via spotlight and calculate 5+3")
    print()
    
    task = input("Task: ").strip()
    
    if not task:
        task = "Open the calculator app via opening macos spotlight, typing in calculator, hitting enter, and then computing 5+3"
    
    # Create and run agent
    agent = ComputerUseAgent(TARGET_WIDTH, TARGET_HEIGHT)
    agent.run(task)


if __name__ == "__main__":
    main()
