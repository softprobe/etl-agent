#!/usr/bin/env python3
"""
Simple test script to verify debug tracing functionality
"""

import asyncio
import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent))
from app.services.claude_service import ClaudeETLAgent

async def test_debug_functionality():
    """Test the debug tracing capability"""
    print("Testing ClaudeETLAgent debug functionality...")
    
    # Initialize agent with debug enabled
    agent = ClaudeETLAgent(work_dir="uploads", debug=True)
    
    try:
        print("\n1. Testing simple message...")
        response_count = 0
        async for response in agent.chat_stream("Hello, can you help me?"):
            response_count += 1
            print(f"Response {response_count}: {response.get('type', 'unknown')}")
            # Only show first few responses to avoid overwhelming output
            if response_count >= 3:
                break
        
        print(f"\n2. Printing conversation history...")
        agent.print_conversation_history()
        
        print(f"\n3. Testing history clearing...")
        agent.clear_conversation_history()
        agent.print_conversation_history()
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent.cleanup()
        print("✅ Debug test completed")

if __name__ == '__main__':
    asyncio.run(test_debug_functionality())