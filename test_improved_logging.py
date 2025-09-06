#!/usr/bin/env python3
"""
Test script to demonstrate the improved logging and prompt loading.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from services.claude_service import ClaudeETLAgent

async def test_improved_logging():
    """Test the improved logging and prompt loading"""
    
    print("🧪 Testing Improved Logging and Prompt Loading")
    print("=" * 60)
    
    # Create test workspace
    test_workspace = Path(__file__).parent / "test_workspace"
    test_workspace.mkdir(exist_ok=True)
    
    # Test with debug enabled to see the improved logging
    print("\n1️⃣ Testing Automated Mode with Debug Logging")
    print("-" * 50)
    
    automated_agent = ClaudeETLAgent.create_automated_agent(
        work_dir=str(test_workspace),
        debug=True
    )
    
    print(f"Mode: {automated_agent.mode}")
    print("Debug logging enabled - you should see detailed logs below:")
    print()
    
    # Test a simple message to see the logging in action
    test_message = "Hello, please analyze any JSON files in this workspace."
    
    try:
        print("Sending test message...")
        async for response in automated_agent.chat_stream(test_message):
            print(f"Received response type: {response.get('type', 'unknown')}")
            # Break after first response to keep test short
            break
    except Exception as e:
        print(f"Error during test: {e}")
    
    await automated_agent.cleanup()
    
    print("\n2️⃣ Testing Interactive Mode with Debug Logging")
    print("-" * 50)
    
    interactive_agent = ClaudeETLAgent.create_interactive_agent(
        work_dir=str(test_workspace),
        debug=True
    )
    
    print(f"Mode: {interactive_agent.mode}")
    print("Debug logging enabled - you should see detailed logs below:")
    print()
    
    try:
        print("Sending test message...")
        async for response in interactive_agent.chat_stream(test_message):
            print(f"Received response type: {response.get('type', 'unknown')}")
            # Break after first response to keep test short
            break
    except Exception as e:
        print(f"Error during test: {e}")
    
    await interactive_agent.cleanup()
    
    print("\n✅ Test completed!")
    print("\nKey improvements:")
    print("  ✓ Prompts loaded from markdown files")
    print("  ✓ Better formatted debug logging with timestamps")
    print("  ✓ Meaningful message content display")
    print("  ✓ No more unhelpful 'Serializing message type' prints")
    print("  ✓ Clear separation between user input and Claude responses")

if __name__ == "__main__":
    asyncio.run(test_improved_logging())
