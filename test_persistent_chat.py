#!/usr/bin/env python3
"""
Test script for persistent conversation functionality
"""
import asyncio
import json
import websockets
from app.services.claude_service import ClaudeETLAgent

async def test_persistent_conversation():
    """Test that the ClaudeETLAgent maintains conversation context across multiple messages"""
    
    print("🧪 Testing persistent conversation functionality...")
    
    # Initialize the agent
    agent = ClaudeETLAgent()
    
    try:
        # First message
        print("\n📝 Sending first message...")
        first_response = []
        async for message in agent.chat_stream("Hello! My name is Alice. What's your name?"):
            first_response.append(message)
            print(f"First response: {message.get('type', 'unknown')} - {message.get('content', '')[:100]}...")
        
        # Second message - should remember the conversation
        print("\n📝 Sending second message...")
        second_response = []
        async for message in agent.chat_stream("Do you remember my name?"):
            second_response.append(message)
            print(f"Second response: {message.get('type', 'unknown')} - {message.get('content', '')[:100]}...")
        
        # Third message - should still remember
        print("\n📝 Sending third message...")
        third_response = []
        async for message in agent.chat_stream("What did I tell you my name was?"):
            third_response.append(message)
            print(f"Third response: {message.get('type', 'unknown')} - {message.get('content', '')[:100]}...")
        
        print("\n✅ Persistent conversation test completed!")
        
        # Check if responses contain conversation context
        all_responses = first_response + second_response + third_response
        assistant_messages = [msg for msg in all_responses if msg.get('type') == 'assistant']
        
        if len(assistant_messages) >= 3:
            print("✅ Received responses for all three messages")
            
            # Check if later responses reference the conversation context
            later_responses = assistant_messages[1:]  # Skip first response
            context_mentioned = any(
                'alice' in str(msg.get('content', '')).lower() or 
                'name' in str(msg.get('content', '')).lower()
                for msg in later_responses
            )
            
            if context_mentioned:
                print("✅ Conversation context appears to be maintained!")
            else:
                print("⚠️  Conversation context may not be fully maintained")
        else:
            print("❌ Did not receive expected number of responses")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        # Clean up
        await agent.cleanup()
        print("🧹 Cleaned up agent resources")

async def test_websocket_commands():
    """Test WebSocket commands for session management"""
    
    print("\n🧪 Testing WebSocket session management commands...")
    
    try:
        # Connect to WebSocket
        uri = "ws://localhost:8000/ws/chat"
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Test status command
            await websocket.send("/status")
            response = await websocket.recv()
            print(f"Status response: {response}")
            
            # Test new session command
            await websocket.send("/new")
            response = await websocket.recv()
            print(f"New session response: {response}")
            
            # Send a test message
            await websocket.send("Hello, this is a test message")
            response = await websocket.recv()
            print(f"Test message response: {response[:200]}...")
            
            print("✅ WebSocket commands test completed!")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting persistent conversation tests...")
    
    # Run the tests
    asyncio.run(test_persistent_conversation())
    asyncio.run(test_websocket_commands())
    
    print("\n🎉 All tests completed!")
