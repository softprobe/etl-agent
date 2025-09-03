#!/usr/bin/env python3
"""
Simple script to run the FastAPI server for testing
"""

import sys
sys.path.append('.')

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Agentic ETL Engineer Server")
    print("Server will be available at: http://localhost:8000")
    print("API docs available at: http://localhost:8000/docs")
    print("WebSocket chat endpoint: ws://localhost:8000/ws/chat")
    print()
    print("To test the API, run: python test_integration.py")
    print()
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0", 
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")