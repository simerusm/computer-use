"""
Test Claude API connection
"""
import os
from dotenv import load_dotenv
from claude_client import ClaudeComputerClient
from agent import DesktopAgent

load_dotenv()

def test_claude_connection():
    """Test if Claude API is working"""
    print("=== Testing Claude API Connection ===\n")
    
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ No ANTHROPIC_API_KEY found in .env file")
        print("   Create a .env file with your API key:")
        print("   ANTHROPIC_API_KEY=your_key_here")
        return False
    
    print(f"✓ API key found: {api_key[:20]}...")
    
    # Initialize agent for screen size
    try:
        agent = DesktopAgent(log_dir="logs")
        screen_info = agent.get_screen_size()
        print(f"✓ Agent initialized (screen: {screen_info['width']}x{screen_info['height']})")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return False
    
    # Initialize Claude client
    try:
        print("\nInitializing Claude client...")
        client = ClaudeComputerClient(api_key=api_key)
        client.update_screen_size(screen_info["width"], screen_info["height"])
        print("✓ Claude client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Claude client: {e}")
        import traceback
        print(f"\nTraceback:\n{traceback.format_exc()}")
        return False
    
    # Test with a simple message (without screenshot)
    try:
        print("\nSending test message to Claude...")
        response = client.send_message("Hello! Can you respond with 'Hello back!'?")
        print("✓ Got response from Claude")
        
        if response["text_responses"]:
            print(f"\nClaude's response:")
            for text in response["text_responses"]:
                print(f"  {text}")
        
        print(f"\nStop reason: {response['stop_reason']}")
        print(f"Tool uses: {len(response['tool_uses'])}")
        
        return True
    
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        import traceback
        print(f"\nTraceback:\n{traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = test_claude_connection()
    
    if success:
        print("\n✅ All tests passed! Claude integration is working.")
    else:
        print("\n❌ Tests failed. Check the errors above.")
        print("\nCommon issues:")
        print("  1. Invalid or missing ANTHROPIC_API_KEY in .env")
        print("  2. API key doesn't have access to Claude computer use")
        print("  3. Network connection issues")

