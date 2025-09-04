#!/usr/bin/env python3
"""
Test script to verify WebSocket connection and file access
"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/chat"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("🔌 Connected to WebSocket")
            
            # Send a test message asking to analyze the JSON file
            test_message = "Please analyze the uploaded JSON files and show me the proposed BigQuery schema structure. Files: s-1234567892.json"
            
            print(f"📤 Sending message: {test_message}")
            await websocket.send(test_message)
            
            # Receive responses
            response_count = 0
            async for message in websocket:
                try:
                    response = json.loads(message)
                    response_count += 1
                    
                    print(f"📥 Response #{response_count}:")
                    print(f"   Type: {response.get('type', 'unknown')}")
                    
                    if response.get('type') == 'assistant' and response.get('content'):
                        content = response['content']
                        if isinstance(content, list):
                            for block in content:
                                if block.get('type') == 'text':
                                    print(f"   Text: {block.get('text', '')[:100]}...")
                                elif block.get('type') == 'tool_use':
                                    print(f"   Tool: {block.get('name', 'unknown')}")
                        else:
                            print(f"   Content: {str(content)[:100]}...")
                    
                    # Stop after receiving a few responses or if we get an error
                    if response.get('type') == 'error' or response_count > 10:
                        break
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse JSON response: {e}")
                    print(f"   Raw message: {message[:200]}...")
                    break
                    
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
